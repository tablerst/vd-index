/**
 * VD Index 主题颜色配置
 * 基于颜色科学算法生成的深色/浅色主题色板
 */

import {
  generateLightThemePalette,
  convertToLightTheme,
  convertTransparentColor
} from './colorScience'

// 原始深色主题色板
export const DARK_THEME_BASE = {
  primary: '#AA83FF',      // 紫色主色
  secondary: '#D4DEC7',    // 绿色辅助色
  accent: '#3F7DFB',       // 蓝色强调色
  baseDark: '#0E1016',     // 深色背景
  baseLight: '#FFFFFF'     // 白色背景
}

// 使用科学算法生成的浅色主题色板
export const LIGHT_THEME_PALETTE = generateLightThemePalette(DARK_THEME_BASE)

/**
 * 完整的主题颜色配置
 */
export interface ThemeColors {
  // 核心主题色彩
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
  
  // 背景色系统
  baseDark: string
  baseLight: string
  surface1: string
  surface2: string
  surface3: string
  surfaceHover: string
  surfacePressed: string
  
  // 文本颜色系统
  textPrimary: string
  textSecondary: string
  textTertiary: string
  textQuaternary: string
  textDisabled: string
  textAccent: string
  textInverse: string
  
  // 边框和分割线
  borderPrimary: string
  borderSecondary: string
  borderFocus: string
  divider: string
  
  // 玻璃态效果
  glassBg: string
  glassBgStrong: string
  glassBorder: string
  
  // 特殊效果颜色
  starColor: string
  nebulaColor: string
  cosmicDust: string
  particlePrimary: string
  particleSecondary: string
  particleAccent: string
  
  // 状态颜色
  error: string
  warning: string
  success: string
  info: string
}

/**
 * 深色主题配色
 */
export const DARK_THEME_COLORS: ThemeColors = {
  // 核心主题色彩
  primary: DARK_THEME_BASE.primary,
  primaryHover: '#B99AFD',
  primaryPressed: '#8F6BFF',
  primaryLight: 'rgba(170, 131, 255, 0.1)',
  primaryLighter: 'rgba(170, 131, 255, 0.05)',
  
  secondary: DARK_THEME_BASE.secondary,
  secondaryHover: '#E8F2DB',
  secondaryPressed: '#C0CA9F',
  secondaryLight: 'rgba(212, 222, 199, 0.1)',
  secondaryLighter: 'rgba(212, 222, 199, 0.05)',
  
  accent: DARK_THEME_BASE.accent,
  accentHover: '#5A8FFC',
  accentPressed: '#2A6BFA',
  accentLight: 'rgba(63, 125, 251, 0.1)',
  
  // 背景色系统
  baseDark: DARK_THEME_BASE.baseDark,
  baseLight: DARK_THEME_BASE.baseLight,
  surface1: 'rgba(255, 255, 255, 0.05)',
  surface2: 'rgba(255, 255, 255, 0.08)',
  surface3: 'rgba(255, 255, 255, 0.12)',
  surfaceHover: 'rgba(255, 255, 255, 0.15)',
  surfacePressed: 'rgba(255, 255, 255, 0.06)',
  
  // 文本颜色系统
  textPrimary: 'rgba(255, 255, 255, 0.95)',
  textSecondary: 'rgba(255, 255, 255, 0.7)',
  textTertiary: 'rgba(255, 255, 255, 0.5)',
  textQuaternary: 'rgba(255, 255, 255, 0.3)',
  textDisabled: 'rgba(255, 255, 255, 0.2)',
  textAccent: DARK_THEME_BASE.secondary,
  textInverse: 'rgba(0, 0, 0, 0.95)',
  
  // 边框和分割线
  borderPrimary: 'rgba(255, 255, 255, 0.12)',
  borderSecondary: 'rgba(255, 255, 255, 0.08)',
  borderFocus: DARK_THEME_BASE.primary,
  divider: 'rgba(255, 255, 255, 0.12)',
  
  // 玻璃态效果
  glassBg: 'rgba(255, 255, 255, 0.08)',
  glassBgStrong: 'rgba(255, 255, 255, 0.12)',
  glassBorder: 'rgba(255, 255, 255, 0.12)',
  
  // 特殊效果颜色
  starColor: 'rgba(255, 255, 255, 0.8)',
  nebulaColor: 'rgba(170, 131, 255, 0.3)',
  cosmicDust: 'rgba(212, 222, 199, 0.2)',
  particlePrimary: DARK_THEME_BASE.primary,
  particleSecondary: DARK_THEME_BASE.secondary,
  particleAccent: DARK_THEME_BASE.accent,
  
  // 状态颜色
  error: '#FF4150',
  warning: '#FFB020',
  success: '#4CAF50',
  info: '#2196F3'
}

/**
 * 浅色主题配色 - 基于科学算法生成
 */
export const LIGHT_THEME_COLORS: ThemeColors = {
  // 核心主题色彩 - 使用科学算法转换
  primary: LIGHT_THEME_PALETTE.primary,
  primaryHover: LIGHT_THEME_PALETTE.primaryHover,
  primaryPressed: LIGHT_THEME_PALETTE.primaryPressed,
  primaryLight: LIGHT_THEME_PALETTE.primaryLight,
  primaryLighter: LIGHT_THEME_PALETTE.primaryLighter,
  
  secondary: LIGHT_THEME_PALETTE.secondary,
  secondaryHover: LIGHT_THEME_PALETTE.secondaryHover,
  secondaryPressed: LIGHT_THEME_PALETTE.secondaryPressed,
  secondaryLight: LIGHT_THEME_PALETTE.secondaryLight,
  secondaryLighter: LIGHT_THEME_PALETTE.secondaryLighter,
  
  accent: LIGHT_THEME_PALETTE.accent,
  accentHover: LIGHT_THEME_PALETTE.accentHover,
  accentPressed: LIGHT_THEME_PALETTE.accentPressed,
  accentLight: LIGHT_THEME_PALETTE.accentLight,
  
  // 背景色系统 - 反转逻辑
  baseDark: DARK_THEME_BASE.baseLight,  // 白色背景
  baseLight: '#F8F9FA',                 // 浅灰背景
  surface1: 'rgba(0, 0, 0, 0.04)',      // 极浅的黑色透明
  surface2: 'rgba(0, 0, 0, 0.06)',
  surface3: 'rgba(0, 0, 0, 0.08)',
  surfaceHover: 'rgba(0, 0, 0, 0.12)',
  surfacePressed: 'rgba(0, 0, 0, 0.03)',
  
  // 文本颜色系统 - 反转
  textPrimary: 'rgba(0, 0, 0, 0.95)',
  textSecondary: 'rgba(0, 0, 0, 0.7)',
  textTertiary: 'rgba(0, 0, 0, 0.5)',
  textQuaternary: 'rgba(0, 0, 0, 0.3)',
  textDisabled: 'rgba(0, 0, 0, 0.2)',
  textAccent: LIGHT_THEME_PALETTE.secondary,
  textInverse: 'rgba(255, 255, 255, 0.95)',
  
  // 边框和分割线
  borderPrimary: 'rgba(0, 0, 0, 0.12)',
  borderSecondary: 'rgba(0, 0, 0, 0.08)',
  borderFocus: LIGHT_THEME_PALETTE.primary,
  divider: 'rgba(0, 0, 0, 0.08)',
  
  // 玻璃态效果
  glassBg: 'rgba(255, 255, 255, 0.7)',      // 浅色主题用白色玻璃
  glassBgStrong: 'rgba(255, 255, 255, 0.85)',
  glassBorder: 'rgba(0, 0, 0, 0.08)',
  
  // 特殊效果颜色 - 科学调整
  starColor: convertTransparentColor('#000000', 0.4, true),
  nebulaColor: convertTransparentColor(LIGHT_THEME_PALETTE.primary, 0.15, true),
  cosmicDust: convertTransparentColor(LIGHT_THEME_PALETTE.secondary, 0.1, true),
  particlePrimary: convertTransparentColor(LIGHT_THEME_PALETTE.primary, 0.7, true),
  particleSecondary: convertTransparentColor(LIGHT_THEME_PALETTE.secondary, 0.6, true),
  particleAccent: convertTransparentColor(LIGHT_THEME_PALETTE.accent, 0.5, true),
  
  // 状态颜色 - 适度调整
  error: convertToLightTheme('#FF4150', { lightnessK: 0.8, saturationK: 0.8 }),
  warning: convertToLightTheme('#FFB020', { lightnessK: 0.7, saturationK: 0.8 }),
  success: convertToLightTheme('#4CAF50', { lightnessK: 0.8, saturationK: 0.8 }),
  info: convertToLightTheme('#2196F3', { lightnessK: 0.8, saturationK: 0.8 })
}

/**
 * 获取主题颜色配置
 */
export function getThemeColors(isDark: boolean): ThemeColors {
  return isDark ? DARK_THEME_COLORS : LIGHT_THEME_COLORS
}
