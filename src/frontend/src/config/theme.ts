/**
 * Naive UI 主题配置
 * 基于 Microsoft Fluent Design System
 */
import type { GlobalTheme } from 'naive-ui'

// Fluent Design System 颜色配置
const fluentColors = {
  // 主色调
  primary: '#0078D4',
  primaryHover: '#106EBE',
  primaryPressed: '#005A9E',
  primarySuppl: '#DEECF9',
  
  // 信息色
  info: '#0078D4',
  infoHover: '#106EBE',
  infoPressed: '#005A9E',
  infoSuppl: '#DEECF9',
  
  // 成功色
  success: '#107C10',
  successHover: '#0E6B0E',
  successPressed: '#0C5A0C',
  successSuppl: '#DFF6DD',
  
  // 警告色
  warning: '#FF8C00',
  warningHover: '#E67E00',
  warningPressed: '#CC7000',
  warningSuppl: '#FFF4CE',
  
  // 错误色
  error: '#D13438',
  errorHover: '#BC2F32',
  errorPressed: '#A72A2D',
  errorSuppl: '#FDE7E9',
  
  // 中性色
  textBase: '#323130',
  textPlaceholder: '#A19F9D',
  textDisabled: '#A19F9D',
  iconColor: '#605E5C',
  iconColorHover: '#323130',
  iconColorPressed: '#201F1E',
  iconColorDisabled: '#A19F9D',
  
  // 背景色
  bodyColor: '#FFFFFF',
  cardColor: '#FFFFFF',
  modalColor: '#FFFFFF',
  popoverColor: '#FFFFFF',
  tableColor: '#FFFFFF',
  
  // 边框色
  borderColor: '#EDEBE9',
  tableHeaderColor: '#F8F9FA',
  
  // 分割线
  dividerColor: '#EDEBE9',
  
  // 代码色
  codeColor: '#F3F2F1',
  
  // 标签色
  tagColor: '#F3F2F1',
  
  // 输入框
  inputColor: '#FFFFFF',
  inputColorDisabled: '#F8F9FA',
  
  // 按钮
  buttonColor2: '#F8F9FA',
  buttonColor2Hover: '#F3F2F1',
  buttonColor2Pressed: '#EDEBE9',
  
  // 滚动条
  scrollbarColor: 'rgba(161, 159, 157, 0.2)',
  scrollbarColorHover: 'rgba(161, 159, 157, 0.3)',
  
  // 遮罩
  modalMaskColor: 'rgba(32, 31, 30, 0.6)',
  drawerMaskColor: 'rgba(32, 31, 30, 0.6)',
  popoverMaskColor: 'rgba(32, 31, 30, 0.6)'
}

// 通用配置
const common = {
  fontFamily: '"Segoe UI", "Microsoft YaHei", -apple-system, BlinkMacSystemFont, sans-serif',
  fontSize: '14px',
  fontSizeMini: '12px',
  fontSizeTiny: '12px',
  fontSizeSmall: '14px',
  fontSizeMedium: '14px',
  fontSizeLarge: '16px',
  fontSizeHuge: '18px',
  
  lineHeight: '1.6',
  
  borderRadius: '4px',
  borderRadiusSmall: '2px',
  
  heightMini: '22px',
  heightTiny: '28px',
  heightSmall: '32px',
  heightMedium: '36px',
  heightLarge: '40px',
  heightHuge: '46px',
  
  cubicBezierEaseInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  cubicBezierEaseOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
  cubicBezierEaseIn: 'cubic-bezier(0.4, 0, 1, 1)',
  
  ...fluentColors
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
  
  borderRadiusTiny: '2px',
  borderRadiusSmall: '4px',
  borderRadiusMedium: '4px',
  borderRadiusLarge: '6px',
  
  // Primary 按钮
  colorPrimary: '#0078D4',
  colorHoverPrimary: '#106EBE',
  colorPressedPrimary: '#005A9E',
  colorFocusPrimary: '#0078D4',
  colorDisabledPrimary: '#F3F2F1',
  textColorPrimary: '#FFFFFF',
  textColorHoverPrimary: '#FFFFFF',
  textColorPressedPrimary: '#FFFFFF',
  textColorFocusPrimary: '#FFFFFF',
  textColorDisabledPrimary: '#A19F9D',

  // Secondary 按钮
  color: 'transparent',
  colorHover: '#F8F9FA',
  colorPressed: '#F3F2F1',
  colorFocus: 'transparent',
  colorDisabled: '#F8F9FA',
  textColor: '#323130',
  textColorHover: '#323130',
  textColorPressed: '#323130',
  textColorFocus: '#323130',
  textColorDisabled: '#A19F9D',
  border: '1px solid #EDEBE9',
  borderHover: '1px solid #0078D4',
  borderPressed: '1px solid #005A9E',
  borderFocus: '1px solid #0078D4',
  borderDisabled: '1px solid #EDEBE9',

  // Ghost 按钮
  colorGhost: 'transparent',
  colorHoverGhost: 'rgba(0, 120, 212, 0.1)',
  colorPressedGhost: 'rgba(0, 120, 212, 0.2)',

  // 阴影
  boxShadowFocus: '0 0 0 2px #DEECF9',

  // 波纹效果
  rippleColor: '#0078D4'
}

const Card = {
  borderRadius: '8px',
  color: '#FFFFFF',
  colorModal: '#FFFFFF',
  colorPopover: '#FFFFFF',
  colorTarget: '#FFFFFF',
  colorEmbedded: '#F8F9FA',
  textColor: '#323130',
  titleTextColor: '#323130',
  borderColor: '#EDEBE9',
  actionColor: '#F8F9FA',
  titleFontWeight: '600',
  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1), 0 0px 2px rgba(0, 0, 0, 0.06)',
  paddingMedium: '20px 24px',
  paddingLarge: '24px 32px',
  paddingHuge: '32px 40px'
}

const Input = {
  borderRadius: '4px',
  color: '#FFFFFF',
  colorDisabled: '#F8F9FA',
  colorFocus: '#FFFFFF',
  textColor: '#323130',
  textColorDisabled: '#A19F9D',
  placeholderColor: '#A19F9D',
  placeholderColorDisabled: '#A19F9D',
  border: '1px solid #EDEBE9',
  borderHover: '1px solid #0078D4',
  borderDisabled: '1px solid #EDEBE9',
  borderFocus: '1px solid #0078D4',
  boxShadowFocus: '0 0 0 2px #DEECF9',
  caretColor: '#0078D4',
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
  borderRadius: '8px',
  borderColor: '#EDEBE9',
  thColor: '#F8F9FA',
  tdColor: '#FFFFFF',
  tdColorHover: '#F8F9FA',
  tdColorStriped: '#FAFAFA',
  thTextColor: '#323130',
  tdTextColor: '#323130',
  thFontWeight: '600',
  borderColorModal: '#EDEBE9',
  borderColorPopover: '#EDEBE9',
  thColorModal: '#F8F9FA',
  tdColorModal: '#FFFFFF',
  tdColorHoverModal: '#F8F9FA',
  tdColorStripedModal: '#FAFAFA',
  boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'
}

// 导出主题配置
export const fluentTheme: GlobalTheme = {
  common,
  Button,
  Card,
  Input,
  DataTable
}

export default fluentTheme
