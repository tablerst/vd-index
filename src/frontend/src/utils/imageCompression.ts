// Image compression utility with intelligent compression strategies
// Support WebP format with JPEG fallback, ensure file size < 500KB

import imageCompression from 'browser-image-compression'

export interface CompressionResult {
  file: File
  originalSize: number
  compressedSize: number
  compressionRatio: number
  format: string
}

export interface CompressionOptions {
  maxSizeMB?: number
  maxWidthOrHeight?: number
  useWebWorker?: boolean
  preserveExif?: boolean
  onProgress?: (progress: number) => void
}

// Check if WebP is supported by the browser
export function isWebPSupported(): boolean {
  const canvas = document.createElement('canvas')
  canvas.width = 1
  canvas.height = 1
  return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0
}

// Convert file size to human readable format
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Smart compression with multiple strategies
export async function compressImageSmart(
  file: File,
  options: CompressionOptions = {}
): Promise<CompressionResult> {
  const {
    maxSizeMB = 0.5,
    maxWidthOrHeight = 2048,
    useWebWorker = true,
    preserveExif = false,
    onProgress
  } = options

  const originalSize = file.size
  const originalSizeMB = originalSize / (1024 * 1024)

  // If file is already small enough and in good format, return as-is
  if (originalSizeMB <= maxSizeMB && 
      (file.type === 'image/webp' || file.type === 'image/jpeg' || file.type === 'image/png')) {
    return {
      file,
      originalSize,
      compressedSize: originalSize,
      compressionRatio: 1,
      format: file.type
    }
  }

  const webpSupported = isWebPSupported()
  let compressedFile: File | null = null
  let finalFormat = ''

  // Strategy 1: Try WebP with high quality
  if (webpSupported) {
    try {
      onProgress?.(25)
      compressedFile = await imageCompression(file, {
        maxSizeMB,
        maxWidthOrHeight,
        fileType: 'image/webp',
        useWebWorker,
        preserveExif,
        initialQuality: 0.9
      })
      finalFormat = 'image/webp'
      
      // If still too large, try with lower quality
      if (compressedFile.size > maxSizeMB * 1024 * 1024) {
        onProgress?.(50)
        compressedFile = await imageCompression(file, {
          maxSizeMB,
          maxWidthOrHeight,
          fileType: 'image/webp',
          useWebWorker,
          preserveExif,
          initialQuality: 0.8
        })
      }

      // Last try with even lower quality
      if (compressedFile.size > maxSizeMB * 1024 * 1024) {
        onProgress?.(75)
        compressedFile = await imageCompression(file, {
          maxSizeMB,
          maxWidthOrHeight,
          fileType: 'image/webp',
          useWebWorker,
          preserveExif,
          initialQuality: 0.7
        })
      }
    } catch (error) {
      console.warn('WebP compression failed, falling back to JPEG:', error)
      compressedFile = null
    }
  }

  // Strategy 2: Fallback to JPEG if WebP failed or not supported
  if (!compressedFile) {
    try {
      onProgress?.(webpSupported ? 75 : 25)
      compressedFile = await imageCompression(file, {
        maxSizeMB,
        maxWidthOrHeight,
        fileType: 'image/jpeg',
        useWebWorker,
        preserveExif,
        initialQuality: 0.9
      })
      finalFormat = 'image/jpeg'

      // Try with lower quality if needed
      if (compressedFile.size > maxSizeMB * 1024 * 1024) {
        onProgress?.(webpSupported ? 90 : 50)
        compressedFile = await imageCompression(file, {
          maxSizeMB,
          maxWidthOrHeight,
          fileType: 'image/jpeg',
          useWebWorker,
          preserveExif,
          initialQuality: 0.8
        })
      }

      if (compressedFile.size > maxSizeMB * 1024 * 1024) {
        onProgress?.(webpSupported ? 95 : 75)
        compressedFile = await imageCompression(file, {
          maxSizeMB,
          maxWidthOrHeight,
          fileType: 'image/jpeg',
          useWebWorker,
          preserveExif,
          initialQuality: 0.7
        })
      }
    } catch (error) {
      console.error('JPEG compression also failed:', error)
      throw new Error(`图片压缩失败: ${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  onProgress?.(100)

  if (!compressedFile) {
    throw new Error('图片压缩失败，请稍后重试')
  }

  const compressedSize = compressedFile.size
  const compressionRatio = originalSize > 0 ? compressedSize / originalSize : 1

  return {
    file: compressedFile,
    originalSize,
    compressedSize,
    compressionRatio,
    format: finalFormat
  }
}

// Batch compress multiple files
export async function compressImagesBatch(
  files: File[],
  options: CompressionOptions = {},
  onProgressBatch?: (fileIndex: number, fileProgress: number, totalProgress: number) => void
): Promise<CompressionResult[]> {
  const results: CompressionResult[] = []
  const totalFiles = files.length

  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    
    try {
      const result = await compressImageSmart(file, {
        ...options,
        onProgress: (progress) => {
          const totalProgress = ((i * 100) + progress) / totalFiles
          onProgressBatch?.(i, progress, totalProgress)
        }
      })
      results.push(result)
    } catch (error) {
      console.error(`Failed to compress file ${file.name}:`, error)
      // For failed compressions, use original file
      results.push({
        file,
        originalSize: file.size,
        compressedSize: file.size,
        compressionRatio: 1,
        format: file.type
      })
    }
  }

  return results
}