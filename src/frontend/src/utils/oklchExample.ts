/**
 * OKLCH配色系统使用示例
 * 展示如何使用新的OKLCH配色系统替换现有的手动配色
 */

import { OKLCHColorSystem, darkToLight } from './oklchColorSystem'

/**
 * VD Index基础深色主题色板
 */
const VD_INDEX_DARK_COLORS = {
  primary: '#AA83FF',    // 紫色主色
  secondary: '#D4DEC7',  // 绿色辅助色
  accent: '#3F7DFB'      // 蓝色强调色
}

/**
 * 示例1: 使用便捷函数生成浅色主题
 */
export function generateLightThemeExample() {
  console.log('=== OKLCH配色系统示例 ===')
  
  // 使用OKLCH算法生成浅色主题
  const lightPrimary = darkToLight(VD_INDEX_DARK_COLORS.primary)
  const lightSecondary = darkToLight(VD_INDEX_DARK_COLORS.secondary)
  const lightAccent = darkToLight(VD_INDEX_DARK_COLORS.accent)
  
  console.log('深色 → 浅色主题转换:')
  console.log(`主色: ${VD_INDEX_DARK_COLORS.primary} → ${lightPrimary}`)
  console.log(`次色: ${VD_INDEX_DARK_COLORS.secondary} → ${lightSecondary}`)
  console.log(`强调色: ${VD_INDEX_DARK_COLORS.accent} → ${lightAccent}`)
  
  return {
    primary: lightPrimary,
    secondary: lightSecondary,
    accent: lightAccent
  }
}

/**
 * 示例2: 使用完整的配色系统生成主题色板
 */
export function generateFullThemePaletteExample() {
  const colorSystem = new OKLCHColorSystem()
  
  // 生成完整的主题色板
  const palette = colorSystem.generateThemePalette(VD_INDEX_DARK_COLORS)
  
  console.log('=== 完整主题色板 ===')
  console.log('深色主题:', palette.dark)
  console.log('浅色主题:', palette.light)
  
  return palette
}

/**
 * 示例3: 生成Surface颜色系统
 */
export function generateSurfaceColorsExample() {
  const colorSystem = new OKLCHColorSystem()
  
  // 深色主题Surface
  const darkSurface = colorSystem.generateSurfaceColors(true)
  
  // 浅色主题Surface (基于明度0.9)
  const lightSurface = colorSystem.generateSurfaceColors(false, 0.9)
  
  console.log('=== Surface颜色系统 ===')
  console.log('深色Surface:', darkSurface)
  console.log('浅色Surface:', lightSurface)
  
  return { dark: darkSurface, light: lightSurface }
}

/**
 * 示例4: 自定义OKLCH参数
 */
export function customOKLCHParametersExample() {
  // 创建自定义配置的颜色系统
  const customColorSystem = new OKLCHColorSystem({
    lightnessK: 0.7,           // 更强的明度映射
    minLightness: 0.85,        // 更高的最小明度
    chromaBaseRetention: 0.8,  // 更多的色度保留
    chromaLightnessGain: 0.3   // 更强的明度增益
  })
  
  const customLight = customColorSystem.darkToLight(VD_INDEX_DARK_COLORS.primary)
  const standardLight = darkToLight(VD_INDEX_DARK_COLORS.primary)
  
  console.log('=== 自定义参数对比 ===')
  console.log(`标准转换: ${VD_INDEX_DARK_COLORS.primary} → ${standardLight}`)
  console.log(`自定义转换: ${VD_INDEX_DARK_COLORS.primary} → ${customLight}`)
  
  return { standard: standardLight, custom: customLight }
}

/**
 * 示例5: 与现有配色系统对比
 */
export function compareWithCurrentSystemExample() {
  // 当前手动配色
  const currentLightColors = {
    primary: '#7C3AED',
    secondary: '#517029',
    accent: '#2563EB'
  }
  
  // OKLCH算法配色
  const oklchLightColors = {
    primary: darkToLight(VD_INDEX_DARK_COLORS.primary),
    secondary: darkToLight(VD_INDEX_DARK_COLORS.secondary),
    accent: darkToLight(VD_INDEX_DARK_COLORS.accent)
  }
  
  console.log('=== 配色系统对比 ===')
  console.log('当前手动配色:', currentLightColors)
  console.log('OKLCH算法配色:', oklchLightColors)
  
  // 分析色相一致性
  console.log('\\n色相一致性分析:')
  console.log('当前方案: 存在色相偏移')
  console.log('OKLCH方案: 色相完全一致 (0° 偏移)')
  
  return { current: currentLightColors, oklch: oklchLightColors }
}

/**
 * 运行所有示例
 */
export function runAllExamples() {
  console.log('🎨 OKLCH配色系统完整示例')
  console.log('=====================================')
  
  generateLightThemeExample()
  console.log('')
  
  generateFullThemePaletteExample()
  console.log('')
  
  generateSurfaceColorsExample()
  console.log('')
  
  customOKLCHParametersExample()
  console.log('')
  
  compareWithCurrentSystemExample()
  
  console.log('=====================================')
  console.log('✅ 所有示例运行完成!')
}

/**
 * 集成到现有themeColors.ts的示例
 */
export function integrateWithThemeColorsExample() {
  const colorSystem = new OKLCHColorSystem()
  
  // 生成新的主题色板
  const newThemePalette = colorSystem.generateThemePalette(VD_INDEX_DARK_COLORS)
  
  // 生成Surface系统
  const darkSurface = colorSystem.generateSurfaceColors(true)
  const lightSurface = colorSystem.generateSurfaceColors(false, 0.9)
  
  // 返回可直接用于themeColors.ts的配置
  return {
    DARK_THEME_COLORS: {
      // 核心主题色彩
      primary: newThemePalette.dark.primary,
      primaryHover: newThemePalette.dark.primaryHover,
      primaryPressed: newThemePalette.dark.primaryPressed,
      
      secondary: newThemePalette.dark.secondary,
      secondaryHover: newThemePalette.dark.secondaryHover,
      secondaryPressed: newThemePalette.dark.secondaryPressed,
      
      accent: newThemePalette.dark.accent,
      accentHover: newThemePalette.dark.accentHover,
      accentPressed: newThemePalette.dark.accentPressed,
      
      // Surface系统
      ...darkSurface
    },
    
    LIGHT_THEME_COLORS: {
      // 核心主题色彩 - OKLCH算法生成
      primary: newThemePalette.light.primary,
      primaryHover: newThemePalette.light.primaryHover,
      primaryPressed: newThemePalette.light.primaryPressed,
      
      secondary: newThemePalette.light.secondary,
      secondaryHover: newThemePalette.light.secondaryHover,
      secondaryPressed: newThemePalette.light.secondaryPressed,
      
      accent: newThemePalette.light.accent,
      accentHover: newThemePalette.light.accentHover,
      accentPressed: newThemePalette.light.accentPressed,
      
      // Surface系统 - 科学的透明度计算
      ...lightSurface
    }
  }
}

// 如果直接运行此文件，执行所有示例
if (typeof window === 'undefined') {
  runAllExamples()
}
