/**
 * 对比度验证工具
 * 确保所有颜色组合满足WCAG可访问性标准
 */

import { getContrastRatio, hexToRgb } from './colorScience'
import { LIGHT_THEME_COLORS, DARK_THEME_COLORS } from './themeColors'

export interface ContrastResult {
  ratio: number
  isAACompliant: boolean    // 4.5:1
  isAAACompliant: boolean   // 7:1
  level: 'fail' | 'aa' | 'aaa'
}

/**
 * 检查颜色对比度
 */
export function checkContrast(foreground: string, background: string): ContrastResult {
  // 处理rgba颜色，提取hex部分
  const cleanForeground = extractHexFromColor(foreground)
  const cleanBackground = extractHexFromColor(background)
  
  const ratio = getContrastRatio(cleanForeground, cleanBackground)
  const isAACompliant = ratio >= 4.5
  const isAAACompliant = ratio >= 7
  
  let level: 'fail' | 'aa' | 'aaa' = 'fail'
  if (isAAACompliant) level = 'aaa'
  else if (isAACompliant) level = 'aa'
  
  return {
    ratio,
    isAACompliant,
    isAAACompliant,
    level
  }
}

/**
 * 从颜色字符串中提取十六进制值
 */
function extractHexFromColor(color: string): string {
  // 如果是rgba格式，转换为hex
  if (color.startsWith('rgba(')) {
    const values = color.match(/rgba?\(([^)]+)\)/)?.[1].split(',')
    if (values && values.length >= 3) {
      const r = parseInt(values[0].trim())
      const g = parseInt(values[1].trim())
      const b = parseInt(values[2].trim())
      return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
    }
  }
  
  // 如果是rgb格式，转换为hex
  if (color.startsWith('rgb(')) {
    const values = color.match(/rgb?\(([^)]+)\)/)?.[1].split(',')
    if (values && values.length >= 3) {
      const r = parseInt(values[0].trim())
      const g = parseInt(values[1].trim())
      const b = parseInt(values[2].trim())
      return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
    }
  }
  
  // 如果已经是hex格式，直接返回
  if (color.startsWith('#')) {
    return color
  }
  
  // 默认返回黑色
  return '#000000'
}

/**
 * 验证主题的所有关键颜色组合
 */
export function validateThemeContrast(isDark: boolean = true) {
  const colors = isDark ? DARK_THEME_COLORS : LIGHT_THEME_COLORS
  const results: Array<{
    name: string
    foreground: string
    background: string
    result: ContrastResult
  }> = []

  // 主要文本对比度检查
  const textChecks = [
    { name: '主要文本 vs 主背景', fg: colors.textPrimary, bg: colors.baseDark },
    { name: '次要文本 vs 主背景', fg: colors.textSecondary, bg: colors.baseDark },
    { name: '三级文本 vs 主背景', fg: colors.textTertiary, bg: colors.baseDark },
    { name: '主要文本 vs 表面1', fg: colors.textPrimary, bg: colors.surface1 },
    { name: '主要文本 vs 表面2', fg: colors.textSecondary, bg: colors.surface2 },
    { name: '主要文本 vs 表面3', fg: colors.textPrimary, bg: colors.surface3 },
  ]

  // 主题色对比度检查
  const themeChecks = [
    { name: '主色 vs 主背景', fg: colors.primary, bg: colors.baseDark },
    { name: '辅助色 vs 主背景', fg: colors.secondary, bg: colors.baseDark },
    { name: '强调色 vs 主背景', fg: colors.accent, bg: colors.baseDark },
    { name: '白色文本 vs 主色', fg: '#FFFFFF', bg: colors.primary },
    { name: '黑色文本 vs 辅助色', fg: '#000000', bg: colors.secondary },
  ]

  // 状态色对比度检查
  const statusChecks = [
    { name: '错误色 vs 主背景', fg: colors.error, bg: colors.baseDark },
    { name: '警告色 vs 主背景', fg: colors.warning, bg: colors.baseDark },
    { name: '成功色 vs 主背景', fg: colors.success, bg: colors.baseDark },
    { name: '信息色 vs 主背景', fg: colors.info, bg: colors.baseDark },
  ]

  const allChecks = [...textChecks, ...themeChecks, ...statusChecks]

  allChecks.forEach(check => {
    const result = checkContrast(check.fg, check.bg)
    results.push({
      name: check.name,
      foreground: check.fg,
      background: check.bg,
      result
    })
  })

  return results
}

/**
 * 生成对比度报告
 */
export function generateContrastReport() {
  console.log('🎨 VD Index 主题对比度验证报告')
  console.log('=' .repeat(50))
  
  console.log('\n📊 深色主题对比度检查:')
  const darkResults = validateThemeContrast(true)
  printContrastResults(darkResults)
  
  console.log('\n📊 浅色主题对比度检查:')
  const lightResults = validateThemeContrast(false)
  printContrastResults(lightResults)
  
  // 统计
  const darkPassed = darkResults.filter(r => r.result.isAACompliant).length
  const lightPassed = lightResults.filter(r => r.result.isAACompliant).length
  
  console.log('\n📈 统计结果:')
  console.log(`深色主题: ${darkPassed}/${darkResults.length} 通过 AA 标准 (${(darkPassed/darkResults.length*100).toFixed(1)}%)`)
  console.log(`浅色主题: ${lightPassed}/${lightResults.length} 通过 AA 标准 (${(lightPassed/lightResults.length*100).toFixed(1)}%)`)
  
  return {
    dark: darkResults,
    light: lightResults,
    darkPassRate: darkPassed / darkResults.length,
    lightPassRate: lightPassed / lightResults.length
  }
}

/**
 * 打印对比度结果
 */
function printContrastResults(results: Array<{
  name: string
  foreground: string
  background: string
  result: ContrastResult
}>) {
  results.forEach(item => {
    const { name, result } = item
    const status = result.level === 'aaa' ? '🟢 AAA' : 
                   result.level === 'aa' ? '🟡 AA' : '🔴 FAIL'
    console.log(`${status} ${name}: ${result.ratio.toFixed(2)}:1`)
  })
}

/**
 * 获取推荐的文本颜色
 */
export function getRecommendedTextColor(backgroundColor: string): string {
  const whiteContrast = checkContrast('#FFFFFF', backgroundColor)
  const blackContrast = checkContrast('#000000', backgroundColor)
  
  return whiteContrast.ratio > blackContrast.ratio ? '#FFFFFF' : '#000000'
}

/**
 * 调整颜色以满足对比度要求
 */
export function adjustColorForContrast(
  foregroundColor: string, 
  backgroundColor: string, 
  targetRatio: number = 4.5
): string {
  // 这是一个简化的实现，实际可能需要更复杂的算法
  const currentRatio = getContrastRatio(foregroundColor, backgroundColor)
  
  if (currentRatio >= targetRatio) {
    return foregroundColor // 已经满足要求
  }
  
  // 如果对比度不够，建议使用纯黑或纯白
  const whiteRatio = getContrastRatio('#FFFFFF', backgroundColor)
  const blackRatio = getContrastRatio('#000000', backgroundColor)
  
  if (whiteRatio >= targetRatio) {
    return '#FFFFFF'
  } else if (blackRatio >= targetRatio) {
    return '#000000'
  }
  
  // 如果都不满足，返回对比度更高的那个
  return whiteRatio > blackRatio ? '#FFFFFF' : '#000000'
}

// 导出验证函数供需要时调用
export { generateContrastReport }
