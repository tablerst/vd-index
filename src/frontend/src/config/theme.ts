/**
 * Naive UI 主题配置
 * 基于首页 Nebula Linear 主题色彩体系
 * 统一整个应用的视觉风格
 */
import type { GlobalTheme } from 'naive-ui'

// VD 官网首页「Nebula Linear」主题色彩体系
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

// 通用配置
const common = {
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

  // 使用首页的缓动函数
  cubicBezierEaseInOut: 'cubic-bezier(0.22, 1, 0.36, 1)',
  cubicBezierEaseOut: 'cubic-bezier(0.19, 1, 0.22, 1)',
  cubicBezierEaseIn: 'cubic-bezier(0.16, 0.84, 0.44, 1)',

  ...nebulaColors
}

// 组件特定配置
const Button = {
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
  itemTextColor: 'rgba(255, 255, 255, 0.7)',
  itemTextColorHover: '#FFFFFF',
  itemTextColorPressed: '#AA83FF',
  separatorColor: 'rgba(255, 255, 255, 0.5)',
  fontSize: '14px'
}

// 导出主题配置
export const nebulaTheme: GlobalTheme = {
  common,
  Button,
  Card,
  Input,
  DataTable,
  Form,
  Select,
  Menu,
  Breadcrumb
}

export default nebulaTheme
