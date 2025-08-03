/**
 * Naive UI 主题配置
 * 基于首页 Nebula Linear 主题色彩体系
 * 统一整个应用的视觉风格
 */
import type { GlobalTheme } from 'naive-ui'

// VD 官网首页「Nebula Linear」主题色彩体系 (未使用，已注释)
/*
const nebulaColors = {
  // 主色调 - 紫色系
  primary: '#AA83FF',
  primaryHover: '#B99AFD',
  primaryPressed: '#8F6BFF',
  primarySuppl: 'rgba(170, 131, 255, 0.1)',

  // 信息色 - 蓝色系
  info: '#3F7DFB',
  infoHover: '#5A8FFC',
  infoPressed: '#2A6BFA',
  infoSuppl: 'rgba(63, 125, 251, 0.1)',

  // 成功色 - 绿色系
  success: '#D4DEC7',
  successHover: '#E8F2DB',
  successPressed: '#C0CA9F',
  successSuppl: 'rgba(212, 222, 199, 0.1)',

  // 警告色
  warning: '#FFB020',
  warningHover: '#FFC040',
  warningPressed: '#FF9500',
  warningSuppl: 'rgba(255, 176, 32, 0.1)',

  // 错误色
  error: '#FF4150',
  errorHover: '#FF6B78',
  errorPressed: '#FF1728',
  errorSuppl: 'rgba(255, 65, 80, 0.1)',

  // 中性色 - 深色主题
  textBase: 'rgba(255, 255, 255, 0.95)',
  textPlaceholder: 'rgba(255, 255, 255, 0.5)',
  textDisabled: 'rgba(255, 255, 255, 0.3)',
  iconColor: 'rgba(255, 255, 255, 0.7)',
  iconColorHover: 'rgba(255, 255, 255, 0.9)',
  iconColorPressed: 'rgba(255, 255, 255, 0.8)',
  iconColorDisabled: 'rgba(255, 255, 255, 0.3)',

  // 背景色 - 深色主题
  bodyColor: '#0E1016',
  cardColor: 'rgba(255, 255, 255, 0.08)',
  modalColor: 'rgba(255, 255, 255, 0.08)',
  popoverColor: 'rgba(255, 255, 255, 0.08)',
  tableColor: 'rgba(255, 255, 255, 0.05)',

  // 边框色
  borderColor: 'rgba(255, 255, 255, 0.12)',
  tableHeaderColor: 'rgba(255, 255, 255, 0.08)',

  // 分割线
  dividerColor: 'rgba(255, 255, 255, 0.12)',

  // 代码色
  codeColor: 'rgba(255, 255, 255, 0.05)',

  // 标签色
  tagColor: 'rgba(255, 255, 255, 0.08)',

  // 输入框
  inputColor: 'rgba(255, 255, 255, 0.08)',
  inputColorDisabled: 'rgba(255, 255, 255, 0.05)',

  // 按钮
  buttonColor2: 'rgba(255, 255, 255, 0.08)',
  buttonColor2Hover: 'rgba(255, 255, 255, 0.12)',
  buttonColor2Pressed: 'rgba(255, 255, 255, 0.06)',

  // 滚动条
  scrollbarColor: 'rgba(255, 255, 255, 0.2)',
  scrollbarColorHover: 'rgba(255, 255, 255, 0.3)',

  // 遮罩
  modalMaskColor: 'rgba(14, 16, 22, 0.8)',
  drawerMaskColor: 'rgba(14, 16, 22, 0.8)',
  popoverMaskColor: 'rgba(14, 16, 22, 0.6)'
}
*/

// 通用配置
const common = {
  name: 'common' as const,
  baseColor: '#0E1016',
  primaryColor: '#AA83FF',
  primaryColorHover: '#B99AFD',
  primaryColorPressed: '#8F6BFF',
  primaryColorSuppl: 'rgba(170, 131, 255, 0.1)',
  infoColor: '#3F7DFB',
  infoColorHover: '#5A8FFC',
  infoColorPressed: '#2A6BFA',
  infoColorSuppl: 'rgba(63, 125, 251, 0.1)',
  successColor: '#D4DEC7',
  successColorHover: '#E8F2DB',
  successColorPressed: '#C0CA9F',
  successColorSuppl: 'rgba(212, 222, 199, 0.1)',
  warningColor: '#FFB020',
  warningColorHover: '#FFC040',
  warningColorPressed: '#FF9500',
  warningColorSuppl: 'rgba(255, 176, 32, 0.1)',
  errorColor: '#FF4150',
  errorColorHover: '#FF6B78',
  errorColorPressed: '#FF1728',
  errorColorSuppl: 'rgba(255, 65, 80, 0.1)',
  textColorBase: 'rgba(255, 255, 255, 0.95)',
  textColor1: 'rgba(255, 255, 255, 0.95)',
  textColor2: 'rgba(255, 255, 255, 0.82)',
  textColor3: 'rgba(255, 255, 255, 0.52)',
  textColorDisabled: 'rgba(255, 255, 255, 0.3)',
  placeholderColor: 'rgba(255, 255, 255, 0.5)',
  placeholderColorDisabled: 'rgba(255, 255, 255, 0.3)',
  iconColor: 'rgba(255, 255, 255, 0.7)',
  iconColorHover: 'rgba(255, 255, 255, 0.9)',
  iconColorPressed: 'rgba(255, 255, 255, 0.8)',
  iconColorDisabled: 'rgba(255, 255, 255, 0.3)',
  opacity1: '0.82',
  opacity2: '0.72',
  opacity3: '0.38',
  opacity4: '0.24',
  opacity5: '0.18',
  dividerColor: 'rgba(255, 255, 255, 0.12)',
  borderColor: 'rgba(255, 255, 255, 0.12)',
  closeIconColor: 'rgba(255, 255, 255, 0.52)',
  closeIconColorHover: 'rgba(255, 255, 255, 0.82)',
  closeIconColorPressed: 'rgba(255, 255, 255, 0.72)',
  clearColor: 'rgba(255, 255, 255, 0.52)',
  clearColorHover: 'rgba(255, 255, 255, 0.82)',
  clearColorPressed: 'rgba(255, 255, 255, 0.72)',
  scrollbarColor: 'rgba(255, 255, 255, 0.2)',
  scrollbarColorHover: 'rgba(255, 255, 255, 0.3)',
  scrollbarWidth: '5px',
  scrollbarHeight: '5px',
  scrollbarBorderRadius: '5px',
  progressRailColor: 'rgba(255, 255, 255, 0.12)',
  railColor: 'rgba(255, 255, 255, 0.12)',
  popoverColor: 'rgba(255, 255, 255, 0.08)',
  tableColor: 'rgba(255, 255, 255, 0.05)',
  cardColor: 'rgba(255, 255, 255, 0.08)',
  modalColor: 'rgba(255, 255, 255, 0.08)',
  bodyColor: '#0E1016',
  tagColor: 'rgba(255, 255, 255, 0.08)',
  avatarColor: 'rgba(255, 255, 255, 0.12)',
  invertedColor: '#0E1016',
  inputColor: 'rgba(255, 255, 255, 0.08)',
  codeColor: 'rgba(255, 255, 255, 0.05)',
  tabColor: 'rgba(255, 255, 255, 0.08)',
  actionColor: 'rgba(255, 255, 255, 0.08)',
  tableHeaderColor: 'rgba(255, 255, 255, 0.08)',
  hoverColor: 'rgba(255, 255, 255, 0.08)',
  tableColorHover: 'rgba(255, 255, 255, 0.08)',
  tableColorStriped: 'rgba(255, 255, 255, 0.03)',
  pressedColor: 'rgba(255, 255, 255, 0.06)',
  opacityDisabled: '0.5',
  inputColorDisabled: 'rgba(255, 255, 255, 0.05)',
  buttonColor2: 'rgba(255, 255, 255, 0.08)',
  buttonColor2Hover: 'rgba(255, 255, 255, 0.12)',
  buttonColor2Pressed: 'rgba(255, 255, 255, 0.06)',
  boxShadow1: '0 1px 2px -2px rgba(0, 0, 0, 0.8), 0 3px 6px 0 rgba(0, 0, 0, 0.34), 0 5px 12px 4px rgba(0, 0, 0, 0.12)',
  boxShadow2: '0 3px 6px -4px rgba(0, 0, 0, 0.8), 0 6px 16px 0 rgba(0, 0, 0, 0.32), 0 9px 28px 8px rgba(0, 0, 0, 0.05)',
  boxShadow3: '0 6px 16px -9px rgba(0, 0, 0, 0.8), 0 9px 28px 0 rgba(0, 0, 0, 0.44), 0 12px 48px 16px rgba(0, 0, 0, 0.05)',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  fontSize: '14px',
  fontSizeMini: '12px',
  fontSizeTiny: '12px',
  fontSizeSmall: '14px',
  fontSizeMedium: '14px',
  fontSizeLarge: '16px',
  fontSizeHuge: '18px',
  lineHeight: '1.6',
  borderRadius: '8px',
  borderRadiusSmall: '4px',
  heightMini: '22px',
  heightTiny: '28px',
  heightSmall: '32px',
  heightMedium: '36px',
  heightLarge: '40px',
  heightHuge: '46px',
  cubicBezierEaseInOut: 'cubic-bezier(0.22, 1, 0.36, 1)',
  cubicBezierEaseOut: 'cubic-bezier(0.19, 1, 0.22, 1)',
  cubicBezierEaseIn: 'cubic-bezier(0.16, 0.84, 0.44, 1)',

  // 添加缺少的属性
  closeColorHover: 'rgba(255, 255, 255, 0.12)',
  closeColorPressed: 'rgba(255, 255, 255, 0.08)',
  fontFamilyMono: 'ui-monospace, SFMono-Regular, "SF Mono", Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
  fontWeight: '400',
  fontWeightStrong: '600'
}

// 组件特定配置
const Button = {
  name: 'Button' as const,
  paddingTiny: '0 8px',
  paddingSmall: '0 12px',
  paddingMedium: '0 16px',
  paddingLarge: '0 20px',
  paddingRoundTiny: '0 10px',
  paddingRoundSmall: '0 14px',
  paddingRoundMedium: '0 18px',
  paddingRoundLarge: '0 22px',

  fontWeightStrong: '600',

  borderRadiusTiny: '4px',
  borderRadiusSmall: '8px',
  borderRadiusMedium: '8px',
  borderRadiusLarge: '12px',

  // Primary 按钮 - 紫色主题
  colorPrimary: '#AA83FF',
  colorHoverPrimary: '#B99AFD',
  colorPressedPrimary: '#8F6BFF',
  colorFocusPrimary: '#AA83FF',
  colorDisabledPrimary: 'rgba(255, 255, 255, 0.05)',
  textColorPrimary: '#FFFFFF',
  textColorHoverPrimary: '#FFFFFF',
  textColorPressedPrimary: '#FFFFFF',
  textColorFocusPrimary: '#FFFFFF',
  textColorDisabledPrimary: 'rgba(255, 255, 255, 0.3)',

  // Secondary 按钮 - 玻璃态效果
  color: 'transparent',
  colorHover: 'rgba(255, 255, 255, 0.08)',
  colorPressed: 'rgba(255, 255, 255, 0.06)',
  colorFocus: 'transparent',
  colorDisabled: 'rgba(255, 255, 255, 0.05)',
  textColor: 'rgba(255, 255, 255, 0.95)',
  textColorHover: 'rgba(255, 255, 255, 0.95)',
  textColorPressed: 'rgba(255, 255, 255, 0.95)',
  textColorFocus: 'rgba(255, 255, 255, 0.95)',
  textColorDisabled: 'rgba(255, 255, 255, 0.3)',
  border: '1px solid rgba(255, 255, 255, 0.12)',
  borderHover: '1px solid #AA83FF',
  borderPressed: '1px solid #8F6BFF',
  borderFocus: '1px solid #AA83FF',
  borderDisabled: '1px solid rgba(255, 255, 255, 0.08)',

  // Ghost 按钮
  colorGhost: 'transparent',
  colorHoverGhost: 'rgba(170, 131, 255, 0.1)',
  colorPressedGhost: 'rgba(170, 131, 255, 0.2)',

  // 阴影 - 紫色发光效果
  boxShadowFocus: '0 0 0 2px rgba(170, 131, 255, 0.3)',

  // 波纹效果
  rippleColor: '#AA83FF'
}

const Card = {
  name: 'Card' as const,
  borderRadius: '12px',
  color: 'rgba(255, 255, 255, 0.08)',
  colorModal: 'rgba(255, 255, 255, 0.08)',
  colorPopover: 'rgba(255, 255, 255, 0.08)',
  colorTarget: 'rgba(255, 255, 255, 0.08)',
  colorEmbedded: 'rgba(255, 255, 255, 0.05)',
  textColor: 'rgba(255, 255, 255, 0.95)',
  titleTextColor: 'rgba(255, 255, 255, 0.95)',
  borderColor: 'rgba(255, 255, 255, 0.12)',
  actionColor: 'rgba(255, 255, 255, 0.08)',
  titleFontWeight: '600',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3), 0 0 20px rgba(170, 131, 255, 0.1)',
  paddingMedium: '20px 24px',
  paddingLarge: '24px 32px',
  paddingHuge: '32px 40px'
}

const Input = {
  name: 'Input' as const,
  borderRadius: '8px',
  color: 'rgba(255, 255, 255, 0.08)',
  colorDisabled: 'rgba(255, 255, 255, 0.05)',
  colorFocus: 'rgba(255, 255, 255, 0.12)',
  colorFocusWarning: 'rgba(255, 255, 255, 0.12)',
  colorFocusError: 'rgba(255, 255, 255, 0.12)',

  // 文字颜色 - 确保在深色背景上可见
  textColor: '#FFFFFF',
  textColorDisabled: 'rgba(255, 255, 255, 0.3)',
  placeholderColor: 'rgba(255, 255, 255, 0.6)',
  placeholderColorDisabled: 'rgba(255, 255, 255, 0.3)',

  // 边框颜色
  border: '1px solid rgba(255, 255, 255, 0.15)',
  borderHover: '1px solid #AA83FF',
  borderDisabled: '1px solid rgba(255, 255, 255, 0.08)',
  borderFocus: '1px solid #AA83FF',
  borderWarning: '1px solid rgba(255, 255, 255, 0.15)',
  borderError: '1px solid rgba(255, 255, 255, 0.15)',

  // 焦点效果
  boxShadowFocus: '0 0 0 2px rgba(170, 131, 255, 0.3)',
  caretColor: '#AA83FF',

  // 尺寸
  paddingSmall: '0 12px',
  paddingMedium: '0 12px',
  paddingLarge: '0 16px',
  fontSizeSmall: '14px',
  fontSizeMedium: '14px',
  fontSizeLarge: '16px',
  heightSmall: '32px',
  heightMedium: '36px',
  heightLarge: '40px'
}

const DataTable = {
  name: 'DataTable' as const,
  borderRadius: '12px',
  borderColor: 'rgba(255, 255, 255, 0.12)',
  thColor: 'rgba(255, 255, 255, 0.08)',
  tdColor: 'rgba(255, 255, 255, 0.05)',
  tdColorHover: 'rgba(255, 255, 255, 0.08)',
  tdColorStriped: 'rgba(255, 255, 255, 0.03)',
  thTextColor: 'rgba(255, 255, 255, 0.95)',
  tdTextColor: 'rgba(255, 255, 255, 0.95)',
  thFontWeight: '600',
  borderColorModal: 'rgba(255, 255, 255, 0.12)',
  borderColorPopover: 'rgba(255, 255, 255, 0.12)',
  thColorModal: 'rgba(255, 255, 255, 0.08)',
  tdColorModal: 'rgba(255, 255, 255, 0.05)',
  tdColorHoverModal: 'rgba(255, 255, 255, 0.08)',
  tdColorStripedModal: 'rgba(255, 255, 255, 0.03)',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
}

// Form 组件配置
const Form = {
  name: 'Form' as const,
  labelTextColor: '#FFFFFF',
  labelFontWeight: '500',
  labelFontSize: '14px',
  feedbackTextColor: 'rgba(255, 255, 255, 0.7)',
  feedbackTextColorError: '#FF6B6B',
  feedbackTextColorWarning: '#FFB020',
  feedbackFontSize: '12px'
}

// Select 组件配置
const Select = {
  name: 'Select' as const,
  color: 'rgba(255, 255, 255, 0.08)',
  colorActive: 'rgba(255, 255, 255, 0.12)',
  border: '1px solid rgba(255, 255, 255, 0.15)',
  borderHover: '1px solid #AA83FF',
  borderActive: '1px solid #AA83FF',
  borderFocus: '1px solid #AA83FF',
  boxShadowFocus: '0 0 0 2px rgba(170, 131, 255, 0.3)',
  textColor: '#FFFFFF',
  placeholderColor: 'rgba(255, 255, 255, 0.6)',
  borderRadius: '8px'
}

// Menu 组件配置
const Menu = {
  name: 'Menu' as const,
  color: 'transparent',
  itemTextColor: '#FFFFFF',
  itemTextColorHover: '#FFFFFF',
  itemTextColorActive: '#FFFFFF',
  itemTextColorChildActive: '#FFFFFF',
  itemColorHover: 'rgba(255, 255, 255, 0.05)',
  itemColorActive: 'rgba(170, 131, 255, 0.2)',
  itemColorActiveHover: 'rgba(170, 131, 255, 0.3)',
  itemHeight: '42px',
  itemMarginBottom: '4px',
  itemBorderRadius: '8px',
  itemFontSize: '14px',
  groupTextColor: 'rgba(255, 255, 255, 0.7)',
  dividerColor: 'rgba(255, 255, 255, 0.12)'
}

// Breadcrumb 组件配置
const Breadcrumb = {
  name: 'Breadcrumb' as const,
  itemTextColor: 'rgba(255, 255, 255, 0.7)',
  itemTextColorHover: '#FFFFFF',
  itemTextColorPressed: '#AA83FF',
  separatorColor: 'rgba(255, 255, 255, 0.5)',
  fontSize: '14px'
}

const Tag = {
  name: 'Tag' as const,
  // 标签组件样式 - 深色主题适配
  borderRadius: '6px',
  // 默认标签
  color: 'rgba(255, 255, 255, 0.1)',
  textColor: 'rgba(255, 255, 255, 0.9)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  // 主要标签
  colorPrimary: 'rgba(170, 131, 255, 0.2)',
  textColorPrimary: '#AA83FF',
  borderPrimary: '1px solid rgba(170, 131, 255, 0.4)',
  // 信息标签
  colorInfo: 'rgba(63, 125, 251, 0.2)',
  textColorInfo: '#3F7DFB',
  borderInfo: '1px solid rgba(63, 125, 251, 0.4)',
  // 成功标签
  colorSuccess: 'rgba(212, 222, 199, 0.2)',
  textColorSuccess: '#D4DEC7',
  borderSuccess: '1px solid rgba(212, 222, 199, 0.4)',
  // 警告标签
  colorWarning: 'rgba(255, 176, 32, 0.2)',
  textColorWarning: '#FFB020',
  borderWarning: '1px solid rgba(255, 176, 32, 0.4)',
  // 错误标签
  colorError: 'rgba(255, 65, 80, 0.2)',
  textColorError: '#FF4150',
  borderError: '1px solid rgba(255, 65, 80, 0.4)',
  // 可关闭标签
  closeIconColor: 'rgba(255, 255, 255, 0.6)',
  closeIconColorHover: 'rgba(255, 255, 255, 0.9)',
  closeIconColorPressed: 'rgba(255, 255, 255, 0.7)'
}

const Transfer = {
  name: 'Transfer' as const,
  // 穿梭框组件样式 - 深色主题适配
  borderRadius: '8px',
  // 列表容器
  listColor: 'rgba(255, 255, 255, 0.08)',
  headerColor: 'rgba(255, 255, 255, 0.12)',
  // 文字颜色
  titleTextColor: 'rgba(255, 255, 255, 0.9)',
  itemTextColor: 'rgba(255, 255, 255, 0.8)',
  itemTextColorDisabled: 'rgba(255, 255, 255, 0.3)',
  // 边框
  borderColor: 'rgba(255, 255, 255, 0.15)',
  // 选中状态
  itemColorPending: 'rgba(170, 131, 255, 0.1)',
  itemColorPendingHover: 'rgba(170, 131, 255, 0.15)',
  // 按钮样式
  extraTextColor: 'rgba(255, 255, 255, 0.7)'
}

// 白色主题配置
const lightCommon = {
  ...common,
  // 白色主题背景
  baseColor: '#FFFFFF',
  bodyColor: '#FFFFFF',

  // 文本颜色 - 浅色主题
  textColorBase: 'rgba(0, 0, 0, 0.95)',
  textColor1: 'rgba(0, 0, 0, 0.95)',
  textColor2: 'rgba(0, 0, 0, 0.7)',
  textColor3: 'rgba(0, 0, 0, 0.5)',
  textColorDisabled: 'rgba(0, 0, 0, 0.3)',

  // 图标颜色
  iconColor: 'rgba(0, 0, 0, 0.7)',
  iconColorHover: 'rgba(0, 0, 0, 0.9)',
  iconColorPressed: 'rgba(0, 0, 0, 0.8)',
  iconColorDisabled: 'rgba(0, 0, 0, 0.3)',

  // 背景色 - 浅色主题
  cardColor: 'rgba(0, 0, 0, 0.08)',
  modalColor: 'rgba(255, 255, 255, 0.95)',
  popoverColor: 'rgba(255, 255, 255, 0.95)',
  tableColor: 'rgba(0, 0, 0, 0.05)',

  // 边框色
  borderColor: 'rgba(0, 0, 0, 0.12)',
  tableHeaderColor: 'rgba(0, 0, 0, 0.08)',

  // 分割线
  dividerColor: 'rgba(0, 0, 0, 0.12)',

  // 代码色
  codeColor: 'rgba(0, 0, 0, 0.05)',

  // 标签色
  tagColor: 'rgba(0, 0, 0, 0.08)',

  // 其他颜色
  tabColor: 'rgba(0, 0, 0, 0.08)',
  actionColor: 'rgba(0, 0, 0, 0.08)',
  hoverColor: 'rgba(0, 0, 0, 0.08)',
  tableColorHover: 'rgba(0, 0, 0, 0.08)',
  tableColorStriped: 'rgba(0, 0, 0, 0.03)',
  pressedColor: 'rgba(0, 0, 0, 0.06)',
  inputColorDisabled: 'rgba(0, 0, 0, 0.05)',
  buttonColor2: 'rgba(0, 0, 0, 0.08)',
  buttonColor2Hover: 'rgba(0, 0, 0, 0.12)',
  buttonColor2Pressed: 'rgba(0, 0, 0, 0.06)',

  // 阴影 - 浅色主题
  boxShadow1: '0 1px 2px -2px rgba(0, 0, 0, 0.16), 0 3px 6px 0 rgba(0, 0, 0, 0.12), 0 5px 12px 4px rgba(0, 0, 0, 0.09)',
  boxShadow2: '0 3px 6px -4px rgba(0, 0, 0, 0.16), 0 6px 16px 0 rgba(0, 0, 0, 0.12), 0 9px 28px 8px rgba(0, 0, 0, 0.05)',
  boxShadow3: '0 6px 16px -9px rgba(0, 0, 0, 0.16), 0 9px 28px 0 rgba(0, 0, 0, 0.12), 0 12px 48px 16px rgba(0, 0, 0, 0.05)',

  // 关闭按钮
  closeColorHover: 'rgba(0, 0, 0, 0.12)',
  closeColorPressed: 'rgba(0, 0, 0, 0.08)',
}

// 白色主题卡片配置
const lightCard = {
  ...Card,
  color: 'rgba(0, 0, 0, 0.08)',
  colorModal: 'rgba(255, 255, 255, 0.95)',
  colorPopover: 'rgba(255, 255, 255, 0.95)',
  colorTarget: 'rgba(0, 0, 0, 0.08)',
  colorEmbedded: 'rgba(0, 0, 0, 0.05)',
  textColor: 'rgba(0, 0, 0, 0.95)',
  titleTextColor: 'rgba(0, 0, 0, 0.95)',
  borderColor: 'rgba(0, 0, 0, 0.12)',
  actionColor: 'rgba(0, 0, 0, 0.08)',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1), 0 0 20px rgba(170, 131, 255, 0.05)',
}

// 白色主题输入框配置
const lightInput = {
  ...Input,
  color: 'rgba(0, 0, 0, 0.05)',
  colorFocus: 'rgba(0, 0, 0, 0.08)',
  colorDisabled: 'rgba(0, 0, 0, 0.03)',
  textColor: 'rgba(0, 0, 0, 0.95)',
  textColorDisabled: 'rgba(0, 0, 0, 0.3)',
  placeholderColor: 'rgba(0, 0, 0, 0.5)',
  placeholderColorDisabled: 'rgba(0, 0, 0, 0.25)',
  borderColor: 'rgba(0, 0, 0, 0.15)',
  borderColorHover: 'rgba(0, 0, 0, 0.25)',
  borderColorFocus: '#AA83FF',
  borderColorDisabled: 'rgba(0, 0, 0, 0.1)',
  boxShadowFocus: '0 0 0 2px rgba(170, 131, 255, 0.2)',
}

// 白色主题菜单配置
const lightMenu = {
  ...Menu,
  color: 'transparent',
  itemTextColor: 'rgba(0, 0, 0, 0.95)',
  itemTextColorHover: 'rgba(0, 0, 0, 0.95)',
  itemTextColorActive: 'rgba(0, 0, 0, 0.95)',
  itemTextColorChildActive: 'rgba(0, 0, 0, 0.95)',
  itemColorHover: 'rgba(0, 0, 0, 0.05)',
  itemColorActive: 'rgba(170, 131, 255, 0.15)',
  itemColorActiveHover: 'rgba(170, 131, 255, 0.2)',
  groupTextColor: 'rgba(0, 0, 0, 0.7)',
  dividerColor: 'rgba(0, 0, 0, 0.12)'
}

// 导出深色主题配置
export const nebulaTheme: GlobalTheme = {
  name: 'nebulaTheme',
  common,
  Button,
  Card,
  Input,
  DataTable,
  Form,
  Select,
  Menu,
  Breadcrumb,
  Tag,
  Transfer
}

// 导出白色主题配置
export const nebulaLightTheme: GlobalTheme = {
  name: 'nebulaLightTheme',
  common: lightCommon,
  Button,
  Card: lightCard,
  Input: lightInput,
  DataTable,
  Form,
  Select,
  Menu: lightMenu,
  Breadcrumb,
  Tag,
  Transfer
}

export default nebulaTheme
