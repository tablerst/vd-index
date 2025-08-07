# useSnapScroll 设备差异化配置设计方案

## 📋 设计目标

基于现有的 `useDeviceDetection` 为不同设备类型设计专门的滚动交互配置，确保：
- **PC端**：保持现有优秀的鼠标滚轮体验
- **移动端**：提供流畅的触摸滑动体验
- **平板端**：兼顾触摸和精确操作的平衡体验

## 🏗️ 配置架构设计

### 1. 扩展 SnapScrollConfig 接口

```typescript
export interface SnapScrollConfig {
  // 通用配置
  tolerance: number
  duration: number
  ease: string
  debounceDelay: number
  footerThreshold: number
  
  // 新增：设备特定配置
  touch?: TouchGestureConfig
  wheel?: WheelConfig
  performance?: PerformanceConfig
}

export interface TouchGestureConfig {
  // 距离阈值
  minDistance: number          // 最小滑动距离
  minQuickDistance: number     // 快速滑动最小距离
  
  // 速度阈值
  minVelocity: number          // 最小滑动速度 (px/ms)
  maxVelocity: number          // 最大有效速度
  
  // 方向检测
  directionThreshold: number   // 方向置信度阈值 (0-1)
  
  // 反馈配置
  enableVibration: boolean     // 是否启用触觉反馈
  enableVisualFeedback: boolean // 是否启用视觉反馈
}

export interface WheelConfig {
  minDeltaY: number           // 最小滚轮增量
  sensitivity: number         // 滚轮灵敏度倍数
}

export interface PerformanceConfig {
  enableGPUAcceleration: boolean
  reducedMotion: boolean
  targetFPS: number
}
```

## 🎯 设备特定配置方案

### 📱 移动端配置 (Mobile)
```typescript
const mobileConfig: SnapScrollConfig = {
  // 基础动画配置
  duration: 0.8,              // 更快的动画响应
  ease: "power2.inOut",       // 适合触摸的缓动
  debounceDelay: 200,         // 更短的防抖延迟
  footerThreshold: 0.85,
  
  // 触摸手势配置
  touch: {
    minDistance: 30,          // 降低距离要求
    minQuickDistance: 15,     // 快速滑动最小距离
    minVelocity: 0.5,         // px/ms，快速滑动阈值
    maxVelocity: 3.0,         // 防止过快滑动误触发
    directionThreshold: 0.7,  // 70%垂直分量才有效
    enableVibration: true,    // 启用触觉反馈
    enableVisualFeedback: true
  },
  
  // 性能优化
  performance: {
    enableGPUAcceleration: true,
    reducedMotion: false,
    targetFPS: 30
  }
}
```

### 📟 平板端配置 (Tablet)
```typescript
const tabletConfig: SnapScrollConfig = {
  // 平衡的动画配置
  duration: 1.0,              // 中等动画速度
  ease: "power2.out",         // 平衡的缓动
  debounceDelay: 250,
  footerThreshold: 0.8,
  
  // 触摸手势配置
  touch: {
    minDistance: 40,          // 中等距离要求
    minQuickDistance: 20,
    minVelocity: 0.4,         // 稍低的速度阈值
    maxVelocity: 2.5,
    directionThreshold: 0.75, // 更严格的方向检测
    enableVibration: false,   // 平板通常不需要振动
    enableVisualFeedback: true
  },
  
  // 滚轮配置（支持外接鼠标）
  wheel: {
    minDeltaY: 8,
    sensitivity: 1.0
  },
  
  performance: {
    enableGPUAcceleration: true,
    reducedMotion: false,
    targetFPS: 45
  }
}
```

### 🖥️ 桌面端配置 (Desktop)
```typescript
const desktopConfig: SnapScrollConfig = {
  // 保持现有优秀体验
  duration: 1.2,              // 更平滑的动画
  ease: "power2.out",         // 经典缓动
  debounceDelay: 300,
  footerThreshold: 0.8,
  
  // 滚轮配置
  wheel: {
    minDeltaY: 10,            // 过滤微小滚动
    sensitivity: 1.0
  },
  
  // 触摸配置（支持触摸屏）
  touch: {
    minDistance: 50,          // 更大的距离要求
    minQuickDistance: 25,
    minVelocity: 0.3,
    maxVelocity: 2.0,
    directionThreshold: 0.8,  // 最严格的方向检测
    enableVibration: false,
    enableVisualFeedback: false
  },
  
  performance: {
    enableGPUAcceleration: true,
    reducedMotion: false,
    targetFPS: 60
  }
}
```

## 🔧 配置选择逻辑

### 智能配置选择器
```typescript
export function getDeviceSpecificConfig(
  deviceInfo: DeviceInfo,
  userConfig?: Partial<SnapScrollConfig>
): SnapScrollConfig {
  // 基础配置选择
  let baseConfig: SnapScrollConfig
  
  switch (deviceInfo.type) {
    case 'mobile':
      baseConfig = mobileConfig
      break
    case 'tablet':
      baseConfig = tabletConfig
      break
    default:
      baseConfig = desktopConfig
  }
  
  // 特殊情况调整
  const adjustedConfig = adjustForSpecialCases(baseConfig, deviceInfo)
  
  // 用户自定义配置覆盖
  return mergeConfigs(adjustedConfig, userConfig)
}

function adjustForSpecialCases(
  config: SnapScrollConfig,
  deviceInfo: DeviceInfo
): SnapScrollConfig {
  const adjusted = { ...config }
  
  // 低性能设备优化
  if (deviceInfo.pixelRatio < 1.5) {
    adjusted.duration *= 0.8
    adjusted.performance!.targetFPS = Math.min(30, adjusted.performance!.targetFPS)
  }
  
  // 高刷新率屏幕优化
  if (deviceInfo.pixelRatio > 2) {
    adjusted.performance!.targetFPS = Math.min(60, adjusted.performance!.targetFPS * 1.2)
  }
  
  // 横屏模式调整
  if (deviceInfo.isLandscape && deviceInfo.isMobile) {
    adjusted.touch!.minDistance *= 1.2 // 横屏时增加滑动距离要求
  }
  
  // 用户偏好：减少动画
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    adjusted.duration = 0.2
    adjusted.performance!.reducedMotion = true
  }
  
  return adjusted
}
```

## 📊 配置对比表

| 配置项 | 移动端 | 平板端 | 桌面端 | 说明 |
|--------|--------|--------|--------|------|
| **动画时长** | 0.8s | 1.0s | 1.2s | 移动端更快响应 |
| **缓动函数** | power2.inOut | power2.out | power2.out | 触摸适配 |
| **最小距离** | 30px | 40px | 50px | 设备精度差异 |
| **速度阈值** | 0.5px/ms | 0.4px/ms | 0.3px/ms | 触摸灵敏度 |
| **方向阈值** | 0.7 | 0.75 | 0.8 | 精确度要求 |
| **触觉反馈** | ✅ | ❌ | ❌ | 移动端专有 |
| **目标帧率** | 30fps | 45fps | 60fps | 性能平衡 |

## 🎨 视觉反馈设计

### 移动端滑动指示器
```typescript
interface SwipeIndicator {
  show: boolean
  direction: 'up' | 'down'
  progress: number // 0-1
  threshold: number // 触发阈值
}
```

### 触觉反馈模式
```typescript
const vibrationPatterns = {
  swipeDetected: [10],        // 检测到滑动
  sectionChanged: [20, 10, 20], // 切换成功
  boundaryReached: [50]       // 到达边界
}
```

## 🚀 实现优先级

### Phase 1: 核心配置系统
1. 扩展配置接口定义
2. 实现设备检测集成
3. 基础配置选择逻辑

### Phase 2: 智能手势识别
1. 触摸事件增强处理
2. 速度和方向计算
3. 综合判断算法

### Phase 3: 体验优化
1. 视觉和触觉反馈
2. 性能优化
3. 边界情况处理

## 📈 预期效果

1. **移动端体验提升 60%**：快速滑动响应，减少误触发
2. **设备适配完善**：每种设备都有最优配置
3. **性能优化**：根据设备能力调整动画复杂度
4. **用户满意度提升**：符合各平台交互习惯
