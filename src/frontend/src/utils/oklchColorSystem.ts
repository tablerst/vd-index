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

// 导入culori库
import { oklch, rgb, formatHex } from 'culori'

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
  darkToLight(darkHex: string, options?: Partial<OKLCHColorOptions>): string {
    const opts = { ...this.options, ...options }

    // 使用culori进行OKLCH转换
    const oklchColor = oklch(darkHex)

    // 1. 正确的明度映射：浅色主题需要更深的颜色
    // 原理：深色主题的亮色元素 → 浅色主题的深色元素
    let newL = oklchColor.l * opts.lightnessK  // 直接降低明度
    newL = Math.min(newL, 1 - opts.minLightness)  // 确保不会太亮

    // 2. 智能色度增强 (浅色主题需要更饱和的颜色确保可见性)
    const newC = oklchColor.c * (opts.chromaBaseRetention + opts.chromaLightnessGain * (1 - newL))

    // 3. 色相保持不变 (OKLCH核心优势)
    const newH = oklchColor.h || 0

    // 转换回RGB并格式化为hex
    const rgbColor = rgb({ mode: 'oklch', l: newL, c: newC, h: newH })
    return formatHex(rgbColor)
  }

  /**
   * 同步版本的darkToLight (现在直接调用主方法)
   */
  darkToLightSync(darkHex: string, options?: Partial<OKLCHColorOptions>): string {
    return this.darkToLight(darkHex, options)
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
    const oklchColor = oklch(hex)
    const newL = Math.max(0, Math.min(1, oklchColor.l + delta))
    const rgbColor = rgb({ mode: 'oklch', l: newL, c: oklchColor.c, h: oklchColor.h || 0 })
    return formatHex(rgbColor)
  }


}

/**
 * 默认OKLCH配色系统实例
 */
export const oklchColorSystem = new OKLCHColorSystem()

/**
 * 便捷函数: 深色转浅色
 */
export const darkToLight = (darkHex: string, options?: Partial<OKLCHColorOptions>) => {
  return oklchColorSystem.darkToLight(darkHex, options)
}
