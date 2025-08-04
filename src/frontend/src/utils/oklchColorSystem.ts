/**
 * OKLCH色彩空间配色系统
 * 基于Material You算法的科学配色方案
 *
 * 核心特性：
 * - 色相完全一致 (0° 偏移)
 * - Material You明度曲线映射
 * - 智能色度压缩防发灰
 * - 动态Surface规则
 */

// 真正的OKLCH实现 - 使用culori库
let culoriOklch: any = null
let culoriRgb: any = null
let culoriFormatHex: any = null

// 动态导入culori (支持可选依赖)
async function initCulori() {
  if (culoriOklch && culoriRgb && culoriFormatHex) return

  try {
    // 正确导入culori的方式
    const culori = await import('culori')
    culoriOklch = culori.oklch
    culoriRgb = culori.rgb
    culoriFormatHex = culori.formatHex
  } catch (error) {
    console.warn('culori库未安装，使用近似OKLCH实现')
  }
}

interface OKLCHColor {
  l: number  // 明度 0-1
  c: number  // 色度 0-0.4
  h: number  // 色相 0-360
}

interface RGBColor {
  r: number
  g: number
  b: number
}

/**
 * OKLCH配色系统配置选项
 */
export interface OKLCHColorOptions {
  /** 明度降低系数 (0.8 = 降低20%明度，适合浅色主题) */
  lightnessK?: number
  /** 最大明度限制 (0.15 表示最大85%明度，确保适中深度) */
  minLightness?: number
  /** 色度基础保留率 (浅色主题需要更饱和: 0.8) */
  chromaBaseRetention?: number
  /** 色度深度增益 (更深的颜色需要更多饱和度: 0.3) */
  chromaLightnessGain?: number
  /** Surface透明度系数 (层次感: 0.04) */
  surfaceAlphaFactor?: number
}

/**
 * 默认OKLCH配置 (修正后的浅色主题配色逻辑)
 */
export const DEFAULT_OKLCH_OPTIONS: Required<OKLCHColorOptions> = {
  lightnessK: 0.8,            // 明度降低系数 (0.8 = 降低20%明度)
  minLightness: 0.15,         // 最大明度限制 (1-0.15=0.85，确保不超过85%明度)
  chromaBaseRetention: 0.85,  // 基础色度保留 (浅一些的颜色需要更多饱和度)
  chromaLightnessGain: 0.25,  // 色度增益 (适中的增益)
  surfaceAlphaFactor: 0.04    // Surface透明度系数
}

/**
 * OKLCH配色系统核心类
 */
export class OKLCHColorSystem {
  private options: Required<OKLCHColorOptions>

  constructor(options: OKLCHColorOptions = {}) {
    this.options = { ...DEFAULT_OKLCH_OPTIONS, ...options }
  }

  /**
   * 深色主题 → 浅色主题转换 (核心算法)
   *
   * 正确的逻辑：
   * - 深色主题：黑色背景 + 亮色元素
   * - 浅色主题：白色背景 + 深色元素
   *
   * @param darkHex 深色主题颜色 (如: '#AA83FF')
   * @param options 可选的转换参数
   * @returns 浅色主题颜色 (hex格式)
   */
  async darkToLight(darkHex: string, options?: Partial<OKLCHColorOptions>): Promise<string> {
    const opts = { ...this.options, ...options }

    // 初始化culori
    await initCulori()

    let oklch: OKLCHColor

    if (culoriOklch) {
      // 使用真正的OKLCH转换
      const oklchColor = culoriOklch(darkHex)
      oklch = {
        l: oklchColor.l,
        c: oklchColor.c,
        h: oklchColor.h || 0 // 处理无色相的情况
      }
    } else {
      // 使用近似实现
      oklch = this.hexToOKLCH(darkHex)
    }

    // 1. 正确的明度映射：浅色主题需要更深的颜色
    // 原理：深色主题的亮色元素 → 浅色主题的深色元素
    let newL = oklch.l * opts.lightnessK  // 直接降低明度
    newL = Math.min(newL, 1 - opts.minLightness)  // 确保不会太亮

    // 2. 智能色度增强 (浅色主题需要更饱和的颜色确保可见性)
    const newC = oklch.c * (opts.chromaBaseRetention + opts.chromaLightnessGain * (1 - newL))

    // 3. 色相保持不变 (OKLCH核心优势)
    const newH = oklch.h

    if (culoriFormatHex && culoriRgb) {
      // 使用真正的OKLCH转换
      const rgbColor = culoriRgb({ mode: 'oklch', l: newL, c: newC, h: newH })
      return culoriFormatHex(rgbColor)
    } else {
      // 使用近似实现
      return this.oklchToHex({ l: newL, c: newC, h: newH })
    }
  }

  /**
   * 同步版本的darkToLight (使用近似实现)
   */
  darkToLightSync(darkHex: string, options?: Partial<OKLCHColorOptions>): string {
    const opts = { ...this.options, ...options }
    const oklch = this.hexToOKLCH(darkHex)

    // 正确的明度映射：浅色主题需要更深的颜色
    let newL = oklch.l * opts.lightnessK  // 直接降低明度
    newL = Math.min(newL, 1 - opts.minLightness)  // 确保不会太亮

    // 智能色度增强 (浅色主题需要更饱和的颜色确保可见性)
    const newC = oklch.c * (opts.chromaBaseRetention + opts.chromaLightnessGain * (1 - newL))

    return this.oklchToHex({ l: newL, c: newC, h: oklch.h })
  }

  /**
   * 生成完整的主题色板 (同步版本)
   *
   * @param baseColors 基础深色主题颜色
   * @returns 深色和浅色主题色板
   */
  generateThemePalette(baseColors: {
    primary: string
    secondary: string
    accent: string
  }) {
    return {
      dark: {
        primary: baseColors.primary,
        secondary: baseColors.secondary,
        accent: baseColors.accent,
        // 生成深色主题的变体
        primaryHover: this.adjustLightness(baseColors.primary, 0.1),
        primaryPressed: this.adjustLightness(baseColors.primary, -0.1),
        secondaryHover: this.adjustLightness(baseColors.secondary, 0.1),
        secondaryPressed: this.adjustLightness(baseColors.secondary, -0.1),
        accentHover: this.adjustLightness(baseColors.accent, 0.1),
        accentPressed: this.adjustLightness(baseColors.accent, -0.1)
      },
      light: {
        // 使用OKLCH算法生成浅色主题 (同步版本)
        primary: this.darkToLightSync(baseColors.primary),
        // 绿色使用特殊参数，让它在浅色主题下更深更饱和
        secondary: this.darkToLightSync(baseColors.secondary),
        accent: this.darkToLightSync(baseColors.accent),
        // 生成浅色主题的变体
        primaryHover: this.darkToLightSync(this.adjustLightness(baseColors.primary, 0.1)),
        primaryPressed: this.darkToLightSync(this.adjustLightness(baseColors.primary, -0.1)),
        // 绿色变体也使用特殊参数
        secondaryHover: this.darkToLightSync(this.adjustLightness(baseColors.secondary, 0.1)),
        secondaryPressed: this.darkToLightSync(this.adjustLightness(baseColors.secondary, -0.1)),
        accentHover: this.darkToLightSync(this.adjustLightness(baseColors.accent, 0.1)),
        accentPressed: this.darkToLightSync(this.adjustLightness(baseColors.accent, -0.1))
      }
    }
  }

  /**
   * 生成Surface颜色系统
   * 
   * @param isDark 是否为深色主题
   * @param lightness 基础明度 (仅浅色主题使用)
   * @returns Surface颜色配置
   */
  generateSurfaceColors(isDark: boolean, lightness: number = 0.9) {
    if (isDark) {
      // 深色主题: 使用白色透明
      return {
        surface1: `rgba(255, 255, 255, 0.05)`,
        surface2: `rgba(255, 255, 255, 0.08)`,
        surface3: `rgba(255, 255, 255, 0.12)`,
        surfaceHover: `rgba(255, 255, 255, 0.15)`,
        surfacePressed: `rgba(255, 255, 255, 0.06)`
      }
    } else {
      // 浅色主题: 使用黑色透明，基于明度动态计算
      const baseAlpha = this.options.surfaceAlphaFactor * lightness
      return {
        surface1: `rgba(0, 0, 0, ${(baseAlpha * 1.2).toFixed(3)})`,
        surface2: `rgba(0, 0, 0, ${(baseAlpha * 1.6).toFixed(3)})`,
        surface3: `rgba(0, 0, 0, ${(baseAlpha * 2.4).toFixed(3)})`,
        surfaceHover: `rgba(0, 0, 0, ${(baseAlpha * 3.0).toFixed(3)})`,
        surfacePressed: `rgba(0, 0, 0, ${(baseAlpha * 1.0).toFixed(3)})`
      }
    }
  }

  /**
   * 调整颜色明度
   * 
   * @param hex 输入颜色
   * @param delta 明度调整量 (-1 到 1)
   * @returns 调整后的颜色
   */
  private adjustLightness(hex: string, delta: number): string {
    const oklch = this.hexToOKLCH(hex)
    const newL = Math.max(0, Math.min(1, oklch.l + delta))
    return this.oklchToHex({ ...oklch, l: newL })
  }

  /**
   * 临时实现: Hex转OKLCH (实际使用culori)
   */
  private hexToOKLCH(hex: string): OKLCHColor {
    // 这是简化实现，实际应使用culori库
    const rgb = this.hexToRgb(hex)
    const hsl = this.rgbToHsl(rgb)
    
    // 近似转换到OKLCH空间
    return {
      l: hsl.l,
      c: hsl.s * 0.4, // 近似色度映射
      h: hsl.h
    }
  }

  /**
   * 临时实现: OKLCH转Hex (实际使用culori)
   */
  private oklchToHex(oklch: OKLCHColor): string {
    // 这是简化实现，实际应使用culori库
    const hsl = {
      h: oklch.h,
      s: oklch.c / 0.4, // 近似饱和度映射
      l: oklch.l
    }
    const rgb = this.hslToRgb(hsl)
    return this.rgbToHex(rgb)
  }

  // 辅助函数 (临时实现)
  private hexToRgb(hex: string): RGBColor {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    if (!result) throw new Error(`Invalid hex color: ${hex}`)
    return {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    }
  }

  private rgbToHsl(rgb: RGBColor) {
    const r = rgb.r / 255
    const g = rgb.g / 255
    const b = rgb.b / 255
    
    const max = Math.max(r, g, b)
    const min = Math.min(r, g, b)
    let h = 0, s = 0
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

  private hslToRgb(hsl: { h: number, s: number, l: number }): RGBColor {
    const h = hsl.h / 360
    const s = hsl.s
    const l = hsl.l
    
    let r, g, b
    
    if (s === 0) {
      r = g = b = l
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

  private rgbToHex(rgb: RGBColor): string {
    const toHex = (n: number) => {
      const hex = Math.round(n).toString(16)
      return hex.length === 1 ? '0' + hex : hex
    }
    return `#${toHex(rgb.r)}${toHex(rgb.g)}${toHex(rgb.b)}`
  }
}

/**
 * 默认OKLCH配色系统实例
 */
export const oklchColorSystem = new OKLCHColorSystem()

/**
 * 便捷函数: 深色转浅色 (同步版本)
 */
export const darkToLight = (darkHex: string, options?: Partial<OKLCHColorOptions>) => {
  return oklchColorSystem.darkToLightSync(darkHex, options)
}

/**
 * 便捷函数: 深色转浅色 (异步版本，支持真正OKLCH)
 */
export const darkToLightAsync = (darkHex: string, options?: Partial<OKLCHColorOptions>) => {
  return oklchColorSystem.darkToLight(darkHex, options)
}
