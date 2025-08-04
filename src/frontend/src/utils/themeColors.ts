/**
 * VD Index 主题颜色配置
 * 基于OKLCH色彩空间的科学配色系统
 *
 * 核心特性：
 * - Material You明度曲线映射
 * - 色相完全一致 (0° 偏移)
 * - 智能色度压缩防发灰
 * - 动态Surface规则
 */

import { OKLCHColorSystem } from './oklchColorSystem'

// 原始深色主题色板
export const DARK_THEME_BASE = {
  primary: '#AA83FF',      // 紫色主色
  secondary: '#D4DEC7',    // 绿色辅助色
  accent: '#3F7DFB',       // 蓝色强调色
  baseDark: '#0E1016',     // 深色背景
  baseLight: '#FFFFFF'     // 白色背景
}

// 创建OKLCH配色系统实例
const oklchColorSystem = new OKLCHColorSystem()

// 使用OKLCH算法生成完整主题色板
export const THEME_PALETTE = oklchColorSystem.generateThemePalette(DARK_THEME_BASE)

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
 * 深色主题配色 - 基于OKLCH算法生成
 */
export const DARK_THEME_COLORS: ThemeColors = {
  // 核心主题色彩 - 使用OKLCH生成的精确色板
  primary: THEME_PALETTE.dark.primary,
  primaryHover: THEME_PALETTE.dark.primaryHover,
  primaryPressed: THEME_PALETTE.dark.primaryPressed,
  primaryLight: 'rgba(170, 131, 255, 0.1)',
  primaryLighter: 'rgba(170, 131, 255, 0.05)',

  secondary: THEME_PALETTE.dark.secondary,
  secondaryHover: THEME_PALETTE.dark.secondaryHover,
  secondaryPressed: THEME_PALETTE.dark.secondaryPressed,
  secondaryLight: 'rgba(212, 222, 199, 0.1)',
  secondaryLighter: 'rgba(212, 222, 199, 0.05)',

  accent: THEME_PALETTE.dark.accent,
  accentHover: THEME_PALETTE.dark.accentHover,
  accentPressed: THEME_PALETTE.dark.accentPressed,
  accentLight: 'rgba(63, 125, 251, 0.1)',
  
  // 背景色系统 - 使用OKLCH科学Surface规则
  baseDark: DARK_THEME_BASE.baseDark,
  baseLight: DARK_THEME_BASE.baseLight,
  // 使用OKLCH动态Surface系统 (深色主题)
  ...oklchColorSystem.generateSurfaceColors(true),
  
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
  borderFocus: THEME_PALETTE.dark.primary,  // 使用OKLCH主色
  divider: 'rgba(255, 255, 255, 0.12)',

  // 玻璃态效果
  glassBg: 'rgba(255, 255, 255, 0.08)',
  glassBgStrong: 'rgba(255, 255, 255, 0.12)',
  glassBorder: 'rgba(255, 255, 255, 0.12)',

  // 特殊效果颜色 - 使用OKLCH色板确保一致性
  starColor: 'rgba(255, 255, 255, 0.8)',
  nebulaColor: `${THEME_PALETTE.dark.primary}4D`,    // 30% 透明度
  cosmicDust: `${THEME_PALETTE.dark.secondary}33`,   // 20% 透明度
  particlePrimary: THEME_PALETTE.dark.primary,
  particleSecondary: THEME_PALETTE.dark.secondary,
  particleAccent: THEME_PALETTE.dark.accent,

  // 状态颜色
  error: '#FF4150',
  warning: '#FFB020',
  success: '#4CAF50',
  info: THEME_PALETTE.dark.accent  // 使用OKLCH强调色
}

/**
 * 浅色主题配色 - 基于OKLCH算法科学生成
 *
 * 核心优势：
 * - 色相完全一致 (0° 偏移)
 * - Material You明度曲线映射
 * - 智能色度压缩防发灰
 * - 科学的对比度保证
 */
export const LIGHT_THEME_COLORS: ThemeColors = {
  // 核心主题色彩 - 使用OKLCH算法生成，确保色相一致性
  primary: THEME_PALETTE.light.primary,           // OKLCH算法生成，色相完全一致
  primaryHover: THEME_PALETTE.light.primaryHover, // 科学的明度调整
  primaryPressed: THEME_PALETTE.light.primaryPressed, // 智能色度压缩
  primaryLight: `${THEME_PALETTE.light.primary}20`,   // 12.5% 透明度
  primaryLighter: `${THEME_PALETTE.light.primary}10`, // 6.25% 透明度

  secondary: THEME_PALETTE.light.secondary,         // 保持原绿色色系，OKLCH优化
  secondaryHover: THEME_PALETTE.light.secondaryHover,   // 科学的悬停状态
  secondaryPressed: THEME_PALETTE.light.secondaryPressed, // 科学的按下状态
  secondaryLight: `${THEME_PALETTE.light.secondary}20`,     // 12.5% 透明度
  secondaryLighter: `${THEME_PALETTE.light.secondary}10`,   // 6.25% 透明度

  accent: THEME_PALETTE.light.accent,              // OKLCH算法生成的蓝色
  accentHover: THEME_PALETTE.light.accentHover,    // 科学的悬停状态
  accentPressed: THEME_PALETTE.light.accentPressed, // 科学的按下状态
  accentLight: `${THEME_PALETTE.light.accent}20`,        // 12.5% 透明度

  // 背景色系统 - 使用OKLCH科学Surface规则
  baseDark: '#FFFFFF',          // 纯白背景
  baseLight: '#F8FAFC',         // 极浅灰背景，增加层次
  // 使用OKLCH动态Surface系统 (基于明度0.9的科学计算)
  ...oklchColorSystem.generateSurfaceColors(false, 0.9),
  
  // 文本颜色系统 - 使用足够深的颜色确保可读性
  textPrimary: '#1F2937',       // 深灰色，接近黑色，确保最佳可读性
  textSecondary: '#4B5563',     // 中灰色，良好的次要文本对比度
  textTertiary: '#6B7280',      // 浅灰色，用于辅助信息
  textQuaternary: '#9CA3AF',    // 更浅的灰色，用于占位符
  textDisabled: '#D1D5DB',      // 禁用状态的浅灰色
  textAccent: '#517029',        // 使用科学优化的绿色作为强调文本
  textInverse: '#FFFFFF',       // 反向文本（深色背景上的白色）

  // 边框和分割线 - 使用足够深的颜色确保可见性
  borderPrimary: '#D1D5DB',     // 明确的边框色，替代透明度
  borderSecondary: '#E5E7EB',   // 次要边框色
  borderFocus: THEME_PALETTE.light.primary,  // 焦点边框使用OKLCH主色
  divider: '#E5E7EB',           // 分割线颜色

  // 玻璃态效果 - 基于OKLCH Surface规则优化
  glassBg: 'rgba(248, 250, 252, 0.8)',      // 使用浅灰色玻璃，而非白色
  glassBgStrong: 'rgba(241, 245, 249, 0.9)', // 更强的玻璃效果
  glassBorder: 'rgba(203, 213, 225, 0.6)',   // 可见的玻璃边框
  
  // 特殊效果颜色 - 基于OKLCH算法生成，确保色相一致性
  starColor: 'rgba(107, 114, 128, 0.8)',     // 使用深灰色星星，确保可见性
  nebulaColor: `${THEME_PALETTE.light.primary}26`,   // 使用OKLCH主色的15%透明度
  cosmicDust: `${THEME_PALETTE.light.secondary}1F`,  // 使用OKLCH次色的12%透明度
  particlePrimary: THEME_PALETTE.light.primary,      // 直接使用OKLCH主色
  particleSecondary: THEME_PALETTE.light.secondary,  // 直接使用OKLCH次色
  particleAccent: THEME_PALETTE.light.accent,        // 直接使用OKLCH强调色

  // 状态颜色 - 使用足够深的颜色确保对比度
  error: '#DC2626',         // 深红色，确保在白背景下可见
  warning: '#D97706',       // 深橙色
  success: '#16A34A',       // 成功状态使用标准绿色（保持语义清晰）
  info: THEME_PALETTE.light.accent  // 使用OKLCH强调色作为信息色
}

/**
 * 获取主题颜色配置
 */
export function getThemeColors(isDark: boolean): ThemeColors {
  return isDark ? DARK_THEME_COLORS : LIGHT_THEME_COLORS
}
