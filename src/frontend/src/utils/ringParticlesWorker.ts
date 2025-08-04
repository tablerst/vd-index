// Web Worker for ring particles using OffscreenCanvas
let canvas: OffscreenCanvas;
let ctx: OffscreenCanvasRenderingContext2D;
let particles: Array<{
  baseX: number; baseY: number; baseZ: number;
  x: number; y: number; z: number;
  angle: number; angleY: number; angleZ: number;
  radius: number;
  baseSize: number; baseOpacity: number;
  color: string; layer: number; pulse: number;
  speed: number; speedY: number; speedZ: number;
}> = [];
let animationId: number;
let width = 0;
let height = 0;
let running = true;
let center = { x: 0, y: 0 };
const distance = 600;

// 性能优化变量
let reducedMotion = false;
let isMobile = false;
let lastFrameTime = 0;
let targetFPS = 45; // 目标帧率，可动态调整
let frameInterval = 1000 / targetFPS;
let performanceLevel = 'medium'; // 'low', 'medium', 'high'
let adaptiveQuality = true; // 自适应质量
let frameSkipCounter = 0;
let fpsHistory: number[] = [];
const fpsHistorySize = 30;

// 主题颜色配置
let themeColors = {
  primary: '#AA83FF',
  secondary: '#D4DEC7',
  accent: '#3F7DFB'
};

// Polyfill requestAnimationFrame in worker
self.requestAnimationFrame = (cb) => setTimeout(() => cb(Date.now()), 1000 / 60) as any;
self.cancelAnimationFrame = (id: number) => clearTimeout(id as any);

// Deterministic random
function deterministicRandom(seed: number) {
  return (Math.sin(seed * 0.618033988749895) * 0.5 + 0.5);
}
// 3D rotation
function rotate3D(x: number, y: number, z: number, rotX: number, rotY: number, rotZ: number) {
  // X axis
  let ny = y * Math.cos(rotX) - z * Math.sin(rotX);
  let nz = y * Math.sin(rotX) + z * Math.cos(rotX);
  y = ny; z = nz;
  // Y axis
  let nx = x * Math.cos(rotY) + z * Math.sin(rotY);
  nz = -x * Math.sin(rotY) + z * Math.cos(rotY);
  x = nx; z = nz;
  // Z axis
  nx = x * Math.cos(rotZ) - y * Math.sin(rotZ);
  ny = x * Math.sin(rotZ) + y * Math.cos(rotZ);
  x = nx; y = ny;
  return { x, y, z };
}
// 3D projection
function project3D(x: number, y: number, z: number) {
  const scale = distance / (distance + z);
  return { x: x * scale, y: y * scale, scale };
}

// 动态性能调整
function adjustPerformance() {
  if (!adaptiveQuality || fpsHistory.length < 10) return;

  const avgFPS = fpsHistory.reduce((a, b) => a + b) / fpsHistory.length;

  if (avgFPS < 25 && performanceLevel !== 'low') {
    performanceLevel = 'low';
    targetFPS = 30;
    frameInterval = 1000 / targetFPS;
    console.log('Performance adjusted to LOW, avgFPS:', avgFPS);
    recreateParticles();
  } else if (avgFPS < 35 && performanceLevel === 'high') {
    performanceLevel = 'medium';
    targetFPS = 40;
    frameInterval = 1000 / targetFPS;
    console.log('Performance adjusted to MEDIUM, avgFPS:', avgFPS);
    recreateParticles();
  } else if (avgFPS > 50 && performanceLevel === 'low') {
    performanceLevel = 'medium';
    targetFPS = 45;
    frameInterval = 1000 / targetFPS;
    console.log('Performance adjusted to MEDIUM, avgFPS:', avgFPS);
    recreateParticles();
  }
}

// 重新创建粒子（性能调整时使用）
function recreateParticles() {
  particles = [];
  createParticles();
}

// 获取基于性能等级的粒子配置
function getParticleConfig() {
  const baseRingRadius = Math.min(width, height) * 0.35;

  // 根据设备性能调整粒子数量
  let particleMultiplier = 1;

  // 性能等级调整
  if (performanceLevel === 'low') {
    particleMultiplier = 0.4;
  } else if (performanceLevel === 'medium') {
    particleMultiplier = 0.7;
  } else {
    particleMultiplier = 1.0;
  }

  // 设备类型调整
  if (isMobile) {
    particleMultiplier *= 0.6; // 移动端减少40%粒子
  }
  if (reducedMotion) {
    particleMultiplier *= 0.5; // 减少动画时再减少50%
  }

  // 三层，根据性能调整数量
  const configs = [
    Math.floor(120 * particleMultiplier),
    Math.floor(80 * particleMultiplier),
    Math.floor(50 * particleMultiplier)
  ];

  return { baseRingRadius, configs };
}

// 创建分层粒子
function createParticles() {
  const { baseRingRadius, configs } = getParticleConfig();
  configs.forEach((count, idx) => {
    for (let i = 0; i < count; i++) {
      const seed = (i + idx * 1000) * 0.618033988749895;
      const tor = deterministicRandom(seed * (23 - idx * 2)) * Math.PI * 2;
      const pol = deterministicRandom(seed * (29 - idx * 2)) * Math.PI * 2;
      const off = deterministicRandom(seed * (31 - idx * 2)) * (0.1) + (0.7 + idx * 0.1);
      const tube = deterministicRandom(seed * (37 - idx * 2)) * baseRingRadius * (0.08 + idx * 0.02);
      const majorR = baseRingRadius * off;
      const x3d = (majorR + tube * Math.cos(pol)) * Math.cos(tor);
      const y3d = (majorR + tube * Math.cos(pol)) * Math.sin(tor);
      const z3d = tube * Math.sin(pol);
      const size = deterministicRandom(seed * 41) * (2 - idx * 0.5) + (1 - idx * 0.3);
      const speed = deterministicRandom(seed * 43) * (0.006 - idx * 0.002) + 0.002;
      const speedY = deterministicRandom(seed * 47) * (0.004 - idx * 0.001) + 0.001;
      const speedZ = deterministicRandom(seed * 49) * (0.003 - idx * 0.001) + 0.001;
      const opacity = deterministicRandom(seed * 51) * (0.6 - idx * 0.15) + (0.4 - idx * 0.1);
      particles.push({
        baseX: x3d, baseY: y3d, baseZ: z3d,
        x: x3d, y: y3d, z: z3d, // 初始时不加center，等待updateCenter调用
        angle: tor, angleY: pol, angleZ: deterministicRandom(seed * 53) * Math.PI * 2,
        radius: majorR,
        baseSize: size, baseOpacity: opacity,
        color: [themeColors.secondary, themeColors.primary, themeColors.accent][idx],
        layer: idx + 1, pulse: deterministicRandom(seed * 57) * Math.PI * 2,
        speed, speedY, speedZ
      });
    }
  });
}
// 动画循环
function animate() {
  if (!running) return;

  // 性能优化：帧率控制
  const now = Date.now();
  if (now - lastFrameTime < frameInterval) {
    animationId = requestAnimationFrame(animate);
    return;
  }

  // FPS监控
  const deltaTime = now - lastFrameTime;
  const currentFPS = 1000 / deltaTime;
  fpsHistory.push(currentFPS);
  if (fpsHistory.length > fpsHistorySize) {
    fpsHistory.shift();
  }

  // 每30帧检查一次性能
  frameSkipCounter++;
  if (frameSkipCounter >= 30) {
    frameSkipCounter = 0;
    adjustPerformance();
  }
  lastFrameTime = now;

  ctx.clearRect(0, 0, width, height);
  const time = now * 0.001;

  // 减少动画时降低旋转速度
  const motionMultiplier = reducedMotion ? 0.3 : 1;
  const rotX = time * 0.015 * motionMultiplier;
  const rotY = time * 0.025 * motionMultiplier;
  const rotZ = time * 0.01 * motionMultiplier;
  particles.forEach(p => {
    p.angle += p.speed;
    p.angleY += p.speedY;
    p.angleZ += p.speedZ;
    // 重新计算3D坐标
    const tube = p.radius * 0.2 * (1 + 0.3 * Math.sin(p.angleZ));
    const x3d = (p.radius + tube * Math.cos(p.angleY)) * Math.cos(p.angle);
    const y3d = (p.radius + tube * Math.cos(p.angleY)) * Math.sin(p.angle);
    const z3d = tube * Math.sin(p.angleY) + p.radius * 0.1 * Math.sin(p.angleZ);
    const rotated = rotate3D(x3d, y3d, z3d, rotX, rotY, rotZ);
    const projected = project3D(rotated.x, rotated.y, rotated.z);
    const finalX = projected.x + center.x;
    const finalY = projected.y + center.y;
    const scale = projected.scale;
    const pulse = 0.7 + 0.3 * Math.sin(time * 1.5 + p.pulse);
    const size = p.baseSize * scale * pulse;
    const alpha = p.baseOpacity * scale;
    // 绘制粒子
    ctx.globalAlpha = alpha;
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.arc(finalX, finalY, size, 0, Math.PI * 2);
    ctx.fill();
  });
  animationId = requestAnimationFrame(animate);
}
// 初始化canvas及particles
function init(off: OffscreenCanvas, w: number, h: number) {
  try {
    canvas = off; width = w; height = h;
    canvas.width = w; canvas.height = h;

    const context = canvas.getContext('2d');
    if (!context) {
      throw new Error('Failed to get 2D context from OffscreenCanvas');
    }
    ctx = context;

    running = true;
    createParticles();
    animate();

    console.log('Ring particles worker initialized successfully');
    // 通知主线程初始化成功
    self.postMessage({ type: 'initialized' });
  } catch (error) {
    console.error('Failed to initialize ring particles worker:', error);
    self.postMessage({ type: 'error', error: error instanceof Error ? error.message : String(error) });
  }
}
function resize(w: number, h: number) {
  width = w; height = h;
  // 确保 canvas 已经初始化
  if (canvas) {
    canvas.width = w; canvas.height = h;
    createParticles();
  }
}
function pause() { running = false; if (animationId) cancelAnimationFrame(animationId); }
function resume() { if (!running) { running = true; animate(); } }
function dispose() { running = false; if (animationId) cancelAnimationFrame(animationId); self.close(); }
// 更新中心位置
function updateCenter(x: number, y: number) {
  center.x = x;
  center.y = y;

  // 重新计算所有粒子的屏幕位置
  particles.forEach(p => {
    p.x = p.baseX + center.x;
    p.y = p.baseY + center.y;
  });
}

// 设置性能选项
function setPerformanceOptions(options: {
  reducedMotion?: boolean;
  isMobile?: boolean;
  performanceLevel?: string;
  adaptiveQuality?: boolean;
}) {
  if (options.reducedMotion !== undefined) {
    reducedMotion = options.reducedMotion;
  }
  if (options.isMobile !== undefined) {
    isMobile = options.isMobile;
  }
  if (options.performanceLevel !== undefined) {
    performanceLevel = options.performanceLevel;
  }
  if (options.adaptiveQuality !== undefined) {
    adaptiveQuality = options.adaptiveQuality;
  }

  console.log('Performance options updated:', { reducedMotion, isMobile, performanceLevel, adaptiveQuality });

  // 重新创建粒子以应用新的性能设置
  createParticles();
}

// 更新主题颜色
function updateThemeColors(colors: { primary: string; secondary: string; accent: string }) {
  themeColors = { ...colors };
  // 更新现有粒子的颜色
  particles.forEach((particle) => {
    const layerIndex = particle.layer - 1;
    particle.color = [themeColors.secondary, themeColors.primary, themeColors.accent][layerIndex] || themeColors.primary;
  });
}

// Message handler
self.onmessage = (e: MessageEvent) => {
  try {
    const d = e.data;
    console.log('Ring particles worker received message:', d.type);

    switch (d.type) {
      case 'init':
        console.log('Initializing ring particles worker with canvas:', d.width, 'x', d.height);
        return init(d.canvas, d.width, d.height);
      case 'resize':
        console.log('Resizing ring particles worker:', d.width, 'x', d.height);
        return resize(d.width, d.height);
      case 'updateCenter': return updateCenter(d.x, d.y);
      case 'updateThemeColors': return updateThemeColors(d.colors);
      case 'setPerformance': return setPerformanceOptions(d.options);
      case 'pause': return pause();
      case 'resume': return resume();
      case 'dispose': return dispose();
      default:
        console.warn('Unknown message type in ring particles worker:', d.type);
    }
  } catch (error) {
    console.error('Error in ring particles worker message handler:', error);
    // 发送错误信息回主线程
    self.postMessage({ type: 'error', error: error instanceof Error ? error.message : String(error) });
  }
};
