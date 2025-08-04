/**
 * 颜色科学工具 - 基于HSL/OKLCH的主题转换算法
 * 实现深色→浅色主题的科学化颜色映射
 */

export interface HSL {
  h: number // 色相 0-360
  s: number // 饱和度 0-1
  l: number // 明度 0-1
}

export interface RGB {
  r: number // 红 0-255
  g: number // 绿 0-255
  b: number // 蓝 0-255
}

/**
 * 十六进制颜色转RGB
 */
export function hexToRgb(hex: string): RGB {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  if (!result) throw new Error(`Invalid hex color: ${hex}`)
  
  return {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  }
}

/**
 * RGB转HSL
 */
export function rgbToHsl(rgb: RGB): HSL {
  const r = rgb.r / 255
  const g = rgb.g / 255
  const b = rgb.b / 255

  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  let h = 0
  let s = 0
  const l = (max + min) / 2

  if (max !== min) {
    const d = max - min
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min)
    
    switch (max) {
      case r: h = (g - b) / d + (g < b ? 6 : 0); break
      case g: h = (b - r) / d + 2; break
      case b: h = (r - g) / d + 4; break
    }
    h /= 6
  }

  return { h: h * 360, s, l }
}

/**
 * HSL转RGB
 */
export function hslToRgb(hsl: HSL): RGB {
  const h = hsl.h / 360
  const s = hsl.s
  const l = hsl.l

  let r, g, b

  if (s === 0) {
    r = g = b = l // 无饱和度，灰色
  } else {
    const hue2rgb = (p: number, q: number, t: number) => {
      if (t < 0) t += 1
      if (t > 1) t -= 1
      if (t < 1/6) return p + (q - p) * 6 * t
      if (t < 1/2) return q
      if (t < 2/3) return p + (q - p) * (2/3 - t) * 6
      return p
    }

    const q = l < 0.5 ? l * (1 + s) : l + s - l * s
    const p = 2 * l - q
    r = hue2rgb(p, q, h + 1/3)
    g = hue2rgb(p, q, h)
    b = hue2rgb(p, q, h - 1/3)
  }

  return {
    r: Math.round(r * 255),
    g: Math.round(g * 255),
    b: Math.round(b * 255)
  }
}

/**
 * RGB转十六进制
 */
export function rgbToHex(rgb: RGB): string {
  const toHex = (n: number) => {
    const hex = Math.round(n).toString(16)
    return hex.length === 1 ? '0' + hex : hex
  }
  return `#${toHex(rgb.r)}${toHex(rgb.g)}${toHex(rgb.b)}`
}

/**
 * 十六进制颜色转HSL
 */
export function hexToHsl(hex: string): HSL {
  return rgbToHsl(hexToRgb(hex))
}

/**
 * HSL转十六进制
 */
export function hslToHex(hsl: HSL): string {
  return rgbToHex(hslToRgb(hsl))
}

/**
 * 计算相对亮度 (WCAG标准)
 */
export function getRelativeLuminance(rgb: RGB): number {
  const rsRGB = rgb.r / 255
  const gsRGB = rgb.g / 255
  const bsRGB = rgb.b / 255

  const r = rsRGB <= 0.03928 ? rsRGB / 12.92 : Math.pow((rsRGB + 0.055) / 1.055, 2.4)
  const g = gsRGB <= 0.03928 ? gsRGB / 12.92 : Math.pow((gsRGB + 0.055) / 1.055, 2.4)
  const b = bsRGB <= 0.03928 ? bsRGB / 12.92 : Math.pow((bsRGB + 0.055) / 1.055, 2.4)

  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

/**
 * 计算对比度比值 (WCAG标准)
 */
export function getContrastRatio(color1: string, color2: string): number {
  const rgb1 = hexToRgb(color1)
  const rgb2 = hexToRgb(color2)
  
  const l1 = getRelativeLuminance(rgb1)
  const l2 = getRelativeLuminance(rgb2)
  
  const lighter = Math.max(l1, l2)
  const darker = Math.min(l1, l2)
  
  return (lighter + 0.05) / (darker + 0.05)
}

/**
 * 深色→浅色主题转换算法
 * 基于明度映射和饱和度调节
 */
export function convertToLightTheme(
  darkHex: string, 
  options: {
    lightnessK?: number    // 明度映射系数 (0.6-0.8)
    saturationK?: number   // 饱和度调节系数 (0.6-0.8)
    minLightness?: number  // 最小明度 (0.75-0.95)
    maxSaturation?: number // 最大饱和度 (0.6-0.8)
  } = {}
): string {
  const {
    lightnessK = 0.7,
    saturationK = 0.7,
    minLightness = 0.8,
    maxSaturation = 0.7
  } = options

  const hsl = hexToHsl(darkHex)
  
  // 明度映射：L_light = 1 - (1 - L_dark) × k
  let newL = 1 - (1 - hsl.l) * lightnessK
  newL = Math.max(newL, minLightness) // 确保最小明度
  
  // 饱和度调节：S_light = S_dark × k
  let newS = hsl.s * saturationK
  newS = Math.min(newS, maxSaturation) // 限制最大饱和度
  
  return hslToHex({
    h: hsl.h,
    s: newS,
    l: newL
  })
}

/**
 * 为浅色主题优化透明度颜色
 */
export function convertTransparentColor(
  darkColor: string,
  alpha: number,
  isLightTheme: boolean = false
): string {
  if (isLightTheme) {
    // 浅色主题：使用黑色基调，降低透明度
    const hsl = hexToHsl(darkColor)
    const newHsl: HSL = {
      h: hsl.h,
      s: hsl.s * 0.6, // 降低饱和度
      l: Math.min(hsl.l * 0.3, 0.2) // 大幅降低明度
    }
    const newAlpha = alpha * 0.6 // 降低透明度
    const rgb = hslToRgb(newHsl)
    return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${newAlpha})`
  } else {
    // 深色主题：保持原有逻辑
    const rgb = hexToRgb(darkColor)
    return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha})`
  }
}

/**
 * 生成完整的主题色板
 */
export interface ThemeColorPalette {
  primary: string
  primaryHover: string
  primaryPressed: string
  primaryLight: string
  primaryLighter: string
  secondary: string
  secondaryHover: string
  secondaryPressed: string
  secondaryLight: string
  secondaryLighter: string
  accent: string
  accentHover: string
  accentPressed: string
  accentLight: string
}

export function generateLightThemePalette(darkPalette: {
  primary: string
  secondary: string
  accent: string
}): ThemeColorPalette {
  const primary = convertToLightTheme(darkPalette.primary, { 
    lightnessK: 0.65, 
    saturationK: 0.75,
    minLightness: 0.75 
  })
  
  const secondary = convertToLightTheme(darkPalette.secondary, { 
    lightnessK: 0.7, 
    saturationK: 0.8,
    minLightness: 0.8 
  })
  
  const accent = convertToLightTheme(darkPalette.accent, { 
    lightnessK: 0.6, 
    saturationK: 0.7,
    minLightness: 0.7 
  })

  return {
    primary,
    primaryHover: convertToLightTheme(primary, { lightnessK: 0.9 }),
    primaryPressed: convertToLightTheme(primary, { lightnessK: 0.8 }),
    primaryLight: convertTransparentColor(primary, 0.15, true),
    primaryLighter: convertTransparentColor(primary, 0.08, true),
    
    secondary,
    secondaryHover: convertToLightTheme(secondary, { lightnessK: 0.9 }),
    secondaryPressed: convertToLightTheme(secondary, { lightnessK: 0.8 }),
    secondaryLight: convertTransparentColor(secondary, 0.15, true),
    secondaryLighter: convertTransparentColor(secondary, 0.08, true),
    
    accent,
    accentHover: convertToLightTheme(accent, { lightnessK: 0.9 }),
    accentPressed: convertToLightTheme(accent, { lightnessK: 0.8 }),
    accentLight: convertTransparentColor(accent, 0.15, true)
  }
}
