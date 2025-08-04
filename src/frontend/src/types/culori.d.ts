/**
 * Culori库的TypeScript声明文件
 * 为OKLCH色彩系统提供类型支持
 */

declare module 'culori' {
  // 颜色对象接口
  interface ColorObject {
    mode: string
    alpha?: number
  }

  // RGB颜色对象
  interface RGBColor extends ColorObject {
    mode: 'rgb'
    r: number
    g: number
    b: number
  }

  // OKLCH颜色对象
  interface OKLCHColor extends ColorObject {
    mode: 'oklch'
    l: number  // 明度 0-1
    c: number  // 色度 0-0.4
    h: number  // 色相 0-360
  }

  // 颜色转换函数类型
  type ColorConverter = (color: string | ColorObject) => ColorObject | undefined

  // 主要导出函数
  export function oklch(color: string | ColorObject): OKLCHColor
  export function rgb(color: string | ColorObject | OKLCHColor): RGBColor
  export function formatHex(color: ColorObject | RGBColor): string

  // 其他常用函数
  export function parse(color: string): ColorObject | undefined
  export function converter(mode: string): ColorConverter
}
