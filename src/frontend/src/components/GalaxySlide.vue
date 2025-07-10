<template>
  <div class="galaxy-slide" ref="slideRef">
    <!-- 连接线Canvas -->
    <canvas ref="connectionsCanvas" class="connections-canvas" :width="canvasSize.width"
      :height="canvasSize.height"></canvas>

    <!-- 成员星球 -->
    <div class="members-nebula">
      <div v-for="(member, index) in members" :key="member.id" class="member-star"
        :class="{ 'member-star--selected': selectedMember?.id === member.id }" :style="getMemberStarStyle(index)"
        @click="selectMember(member)" @mouseenter="(event) => handleMemberHover(member, event)"
        @mousemove="updateTooltipPosition" @mouseleave="handleMemberLeave" @keydown.enter="selectMember(member)"
        @keydown.escape="closeMemberInfo" tabindex="0" :aria-label="`${member.name} 的星球`" role="button">
        <div class="member-avatar">
          <img :src="member.avatarURL" :alt="member.name" loading="lazy">
          <div class="avatar-glow"></div>
        </div>
        <div class="member-tooltip" v-if="hoveredMember?.id === member.id" :style="{
          left: `${tooltipPosition.x}px`,
          top: `${tooltipPosition.y}px`
        }">
          <div class="tooltip-content">
            <h4 class="member-name">{{ member.name }}</h4>
            <p class="member-bio" v-if="member.bio">{{ member.bio }}</p>
            <div class="member-meta" v-if="member.joinDate">
              <span class="join-date">加入于 {{ formatDate(member.joinDate) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useDeviceDetection } from '../composables/useDeviceDetection'
import type { Member } from '../stores/members'

// 连接线数据结构
interface ConnectionLink {
  id: string
  source: string  // 源头像成员ID
  target: string  // 目标头像成员ID
  lastActivationTime: number // 本轮激活起点
}

// 节点数据结构
interface Node {
  id: string
  x: number
  y: number
  r: number // 半径
}

interface Props {
  members: Member[]
  index: number
}

/* ======== 连线节奏参数 ======== */
const BATCH_INTERVAL       = 3000  // 每 3 s 推出下一批
const DISPLAY_DURATION     = 5000  // 一条线完整 0→1→0 用时 5 s
const LINKS_PER_BATCH      = 8     // 每批点亮数量
// ===============================

const props = defineProps<Props>()

// 设备检测
const { responsiveConfig, deviceInfo } = useDeviceDetection()

const slideRef = ref<HTMLElement>()
const connectionsCanvas = ref<HTMLCanvasElement>()
const selectedMember = ref<Member | null>(null)
const hoveredMember = ref<Member | null>(null)
const tooltipPosition = ref({ x: 0, y: 0 })

// Canvas尺寸 - 改为使用slide容器尺寸
const canvasSize = ref({ width: 0, height: 0 })

const updateCanvasSize = () => {
  if (!slideRef.value || !connectionsCanvas.value) return
  const rect = slideRef.value.getBoundingClientRect()

  // ① 处理 HiDPI，保证 1 物理像素 = 1 画布像素
  const dpr = window.devicePixelRatio || 1
  const canvas  = connectionsCanvas.value
  canvas.width  = rect.width  * dpr
  canvas.height = rect.height * dpr
  canvas.style.width  = `${rect.width}px`
  canvas.style.height = `${rect.height}px`

  // 只需在尺寸变化时 scale 一次即可
  const ctx = canvas.getContext('2d')
  ctx?.setTransform(dpr, 0, 0, dpr, 0, 0)

  canvasSize.value = { width: rect.width, height: rect.height }
}

// 发射事件
const emit = defineEmits<{
  memberSelect: [member: Member]
  memberHover: [member: Member, event: MouseEvent]
  memberLeave: []
}>()

// 响应式Vogel螺旋布局算法
const getVogelSpiralPosition = (index: number, total: number) => {
  const goldenAngle = Math.PI * (3 - Math.sqrt(5)) // 黄金角度
  const angle = index * goldenAngle

  // 根据设备类型调整螺旋半径
  const spiralRadius = responsiveConfig.value.spiralRadius
  const radius = Math.sqrt(index / total) * spiralRadius

  const x = 50 + radius * Math.cos(angle)
  const y = 50 + radius * Math.sin(angle)

  // 根据设备类型调整边界
  const margin = deviceInfo.value.isMobile ? 15 : 10
  return {
    x: Math.max(margin, Math.min(100 - margin, x)),
    y: Math.max(margin, Math.min(100 - margin, y))
  }
}

// 生成成员星球样式
const getMemberStarStyle = (index: number) => {
  const memberCount = props.members.length
  const seed = (index + props.index * 50) * 0.618033988749895

  const position = getVogelSpiralPosition(index, memberCount)

  // 响应式头像大小
  const distanceFromCenter = Math.sqrt(
    Math.pow(position.x - 50, 2) + Math.pow(position.y - 50, 2)
  )
  const { avatarSize } = responsiveConfig.value
  const baseSize = Math.max(avatarSize.min, avatarSize.max - distanceFromCenter * 0.3)
  const sizeVariation = (Math.sin(seed * 13) * 0.5 + 0.5) * 8 - 4
  const size = Math.max(avatarSize.min, Math.min(avatarSize.max, baseSize + sizeVariation))

  // 响应式浮动动画参数
  const { spacing, animationIntensity } = responsiveConfig.value
  const floatDistance = (spacing.min + (distanceFromCenter / 35) * spacing.max) * animationIntensity
  const floatAngle = (Math.sin(seed * 23) * 0.5 + 0.5) * 360
  const rotateDeg = (Math.sin(seed * 29) * 0.5 + 0.5 - 0.5) * 12 * animationIntensity
  const delay = (Math.sin(seed * 31) * 0.5 + 0.5) * 3
  const duration = 8 + (Math.sin(seed * 37) * 0.5 + 0.5) * 12

  return {
    left: `${position.x}%`,
    top: `${position.y}%`,
    width: `${size}px`,
    height: `${size}px`,
    '--float-distance': `${floatDistance}px`,
    '--float-angle': `${floatAngle}deg`,
    '--rotate-deg': `${rotateDeg}deg`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    zIndex: Math.floor(10 + (50 - distanceFromCenter))
  }
}

// 成员交互处理
const selectMember = (member: Member) => {
  selectedMember.value = member
  emit('memberSelect', member)
}

const handleMemberHover = (member: Member, event: MouseEvent) => {
  hoveredMember.value = member
  updateTooltipPosition(event)
  emit('memberHover', member, event)
}

const handleMemberLeave = () => {
  hoveredMember.value = null
  emit('memberLeave')
}

const updateTooltipPosition = (event: MouseEvent) => {
  if (!hoveredMember.value) return

  const rect = slideRef.value?.getBoundingClientRect()
  if (!rect) return

  tooltipPosition.value = {
    x: event.clientX - rect.left + 15,
    y: event.clientY - rect.top - 10
  }
}

const closeMemberInfo = () => {
  selectedMember.value = null
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 统一动画时间管理
const animationTime = ref(0)

// 连接线管理
const connectionLinks = ref<ConnectionLink[]>([])

/* 批调度器：每 3 s 把上一批之外的线随机点亮 */
let lastBatchTime = 0

const scheduleNextBatch = (now: number) => {
  if (now - lastBatchTime < BATCH_INTERVAL) return
  lastBatchTime = now

  // 可选池：上一轮 5 s 波段已结束的线
  const pool = connectionLinks.value.filter(
    l => now - l.lastActivationTime > DISPLAY_DURATION
  )
  if (!pool.length) return

  // 随机洗牌
  for (let i = pool.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[pool[i], pool[j]] = [pool[j], pool[i]]
  }

  pool.slice(0, LINKS_PER_BATCH).forEach(l => {
    l.lastActivationTime = now      // 重新起一轮三角波
  })
}



// 节点数据管理
const nodes = ref<Node[]>([])

// 根据当前帧更新节点位置
const updateNodePositions = () => {
  const slideEl = slideRef.value
  if (!slideEl) return

  // 整个 slide 的矩形，用来把视口坐标换算成画布内部坐标
  const slideRect = slideEl.getBoundingClientRect()

  // 所有头像 DOM
  const avatarEls = slideEl.querySelectorAll<HTMLElement>('.member-star')

  avatarEls.forEach((el, idx) => {
    // 头像自身矩形（含 transform 后的位置）
    const box = el.getBoundingClientRect()

    // 头像中心点相对于 slide 左上角的坐标（CSS 像素）
    const cx = box.left + box.width / 2 - slideRect.left
    const cy = box.top + box.height / 2 - slideRect.top
    const r  = box.width / 2

    // 写入 / 复用节点对象
    const n = nodes.value[idx] ||
      (nodes.value[idx] = { id: props.members[idx].id.toString(), x: 0, y: 0, r: 0 })

    n.x = cx
    n.y = cy
    n.r = r
  })
}

// 生成连接线
const generateConnectionLinks = () => {
  console.log('🔗 [连接线生成] 开始生成连接线，成员数量:', props.members.length)

  const newLinks: ConnectionLink[] = []
  const maxConnections = 3 // 每个成员最多连接3条线

  props.members.forEach((member, i) => {
    // 计算到其他成员的距离
    const distances = props.members
      .map((otherMember, j) => {
        if (i === j) return null

        const pos1 = getVogelSpiralPosition(i, props.members.length)
        const pos2 = getVogelSpiralPosition(j, props.members.length)
        const distance = Math.sqrt(
          Math.pow(pos1.x - pos2.x, 2) + Math.pow(pos1.y - pos2.y, 2)
        )

        return { index: j, member: otherMember, distance }
      })
      .filter(item => item !== null)
      .sort((a, b) => a!.distance - b!.distance)
      .slice(0, maxConnections)

    distances.forEach(({ member: targetMember }) => {
      // 避免重复连接
      const linkExists = newLinks.some(link =>
        (link.source === member.id.toString() && link.target === targetMember.id.toString()) ||
        (link.source === targetMember.id.toString() && link.target === member.id.toString())
      )

      if (!linkExists) {
        const newLink: ConnectionLink = {
          id: `${member.id}-${targetMember.id}`,
          source: member.id.toString(),
          target: targetMember.id.toString(),
          lastActivationTime: -Infinity     // 还没进入任何批次
        }
        newLinks.push(newLink)
      }
    })
  })

  connectionLinks.value = newLinks
  console.log('✅ [连接线生成] 生成完成，连接线数量:', newLinks.length)
}

/* ======== 更新连线（仅负责计算 α） ======== */
const updateConnectionLinks = () => {
  const now = performance.now()

  scheduleNextBatch(now)            // 可能启动下一批

  connectionLinks.value.forEach(link => {
    const t = (now - link.lastActivationTime) / DISPLAY_DURATION
    if (t >= 0 && t <= 1) {
      // 三角波：0-1-0
      const tri = 1 - Math.abs(t * 2 - 1)
      // 把 α 临时存在 link 里供 draw 使用
      ;(link as any).alpha = tri * 0.8           // 0-0.8-0
    } else {
      ;(link as any).alpha = 0
    }
  })
}
// 首次拿到有效 canvasSize 后 / 窗口尺寸变化时刷新
watch(canvasSize, () => {
  if (canvasSize.value.width > 0 && canvasSize.value.height > 0) {
    generateConnectionLinks()
  }
}, { immediate: true })

// 绘制连接线
const drawConnections = () => {
  const canvas = connectionsCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // 清除画布
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  let drawnConnections = 0
  let totalActiveConnections = 0

  /* ======== 绘制连线 ======== */
  connectionLinks.value.forEach((link, index) => {
    const alpha = (link as any).alpha || 0
    if (alpha < 0.05) return          // 不足阈值直接跳过

    // 查找对应的成员头像位置
    const sourceMemberIndex = props.members.findIndex(m => m.id.toString() === link.source)
    const targetMemberIndex = props.members.findIndex(m => m.id.toString() === link.target)

    if (sourceMemberIndex === -1 || targetMemberIndex === -1) return

    // 直接使用nodes中已经计算好的实时位置（确保与头像完全同步）
    const sourceNode = nodes.value[sourceMemberIndex]
    const targetNode = nodes.value[targetMemberIndex]

    if (!sourceNode || !targetNode) return

    // 头像中心位置（已包含所有偏移和动画）
    const sourceCenterX = sourceNode.x
    const sourceCenterY = sourceNode.y
    const targetCenterX = targetNode.x
    const targetCenterY = targetNode.y

    totalActiveConnections++

    // 计算头像中心之间的距离和方向
    const dx = targetCenterX - sourceCenterX
    const dy = targetCenterY - sourceCenterY
    const dist = Math.sqrt(dx * dx + dy * dy)

    if (dist < 1) return // 避免除零错误

    // 单位方向向量（始终指向目标头像中心）
    const ux = dx / dist
    const uy = dy / dist

    // 使用nodes中存储的头像半径（确保与实际头像大小同步）
    const sourceRadius = sourceNode.r || 25  // 默认半径25px
    const targetRadius = targetNode.r || 25

    // 连接线起点：从源头像边缘开始
    const sx = sourceCenterX + ux * sourceRadius
    const sy = sourceCenterY + uy * sourceRadius

    // 连接线终点：到达目标头像边缘
    const tx = targetCenterX - ux * targetRadius
    const ty = targetCenterY - uy * targetRadius

    // 检查头像是否过近
    const realTimeDistance = Math.sqrt((tx - sx) * (tx - sx) + (ty - sy) * (ty - sy))
    if (realTimeDistance < sourceRadius + targetRadius) {
      return // 头像重叠时跳过绘制
    }

    // 连接线监控（仅在开发模式下）
    if (import.meta.env.DEV && index < 2 && drawnConnections < 2) {
      console.log(`🎯 [连接线${index}] 头像中心连接:`, {
        source: `成员${link.source}`,
        target: `成员${link.target}`,
        direction: `(${ux.toFixed(3)}, ${uy.toFixed(3)})`,
        distance: dist.toFixed(1),
        alpha: alpha.toFixed(3)
      })
    }

    // 绘制曲线连接线
    ctx.beginPath()
    ctx.strokeStyle = `rgba(170, 131, 255, ${alpha})`
    ctx.lineWidth = 2
    ctx.lineCap = 'round'

    // 计算控制点（创建弯曲效果）
    const midX = (sx + tx) / 2
    const midY = (sy + ty) / 2
    const offset = Math.min(dist * 0.2, 50) // 弯曲程度
    const perpX = -uy * offset
    const perpY = ux * offset
    const cpX = midX + perpX
    const cpY = midY + perpY

    // 绘制二次贝塞尔曲线
    ctx.moveTo(sx, sy)
    ctx.quadraticCurveTo(cpX, cpY, tx, ty)
    ctx.stroke()

    drawnConnections++
  })

  // 连接线绘制统计（开发模式）
  if (import.meta.env.DEV && Math.random() < 0.1) {
    console.log(`📈 [连接线绘制] 总激活: ${totalActiveConnections}, 实际绘制: ${drawnConnections}, 绘制率: ${((drawnConnections / Math.max(totalActiveConnections, 1)) * 100).toFixed(1)}%`)
  }
}

// 监听成员变化，重新生成连接线
watch(() => props.members, () => {
  nextTick(() => {
    generateConnectionLinks() // 成员列表变化时，重新生成连接线
  })
}, { immediate: true })

// 统一动画循环
let animationId: number | null = null
let frameCount = 0

const animate = () => {
  // 每帧更新动画时间
  animationTime.value = performance.now()

  // 每帧更新节点位置（包含浮动偏移）
  updateNodePositions()

  // 每帧更新连接线状态（呼吸效果和激活管理）
  updateConnectionLinks()

  // 每 10 帧重新生成一次连接线，避免性能问题
  if (++frameCount % 600 === 0) {
    generateConnectionLinks()
  }

  // 每帧绘制连接线（确保跟随头像实时位置）
  drawConnections()

  animationId = requestAnimationFrame(animate)
}

// 生命周期管理
onMounted(() => {
  nextTick(() => {
    updateCanvasSize()

    // 生成初始连接线
    generateConnectionLinks()

    // 立即激活一些连接线，首屏就能看到效果
    const now = performance.now()
    connectionLinks.value.forEach((link, index) => {
      if (index < 3) { // 激活前3条连接线
        link.lastActivationTime = now
      }
    })

    // 启动统一的动画循环
    animate()
  })
  window.addEventListener('resize', updateCanvasSize)
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
  window.removeEventListener('resize', updateCanvasSize)
})
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;

.galaxy-slide {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.connections-canvas {
  position: absolute;
  inset: 0;
  /* 等价于 top:0; right:0; bottom:0; left:0 */
  pointer-events: none;
  z-index: 1;
}

.members-nebula {
  position: relative;
  width: 100%;
  height: 100%;
  z-index: 2;
}

.member-star {
  position: absolute;
  transform: translate(-50%, -50%);
  animation: gentleFloat ease-in-out infinite;
  cursor: pointer;
  pointer-events: all;
  transition: all var(--transition-base) var(--ease-hover);

  &:hover {
    z-index: 20;
    transform: translate(-50%, -50%) scale(1.2);
    animation-play-state: paused;

    .member-avatar {
      box-shadow: var(--shadow-mixed-glow), 0 0 30px rgba(170, 131, 255, 0.4);
      border-color: var(--secondary);
      transform: scale(1.05);
    }

    .avatar-glow {
      opacity: 1;
      transform: scale(2.2);
    }
  }

  &--selected {
    .member-avatar {
      border-color: var(--primary);
      box-shadow: var(--shadow-mixed-glow), 0 0 40px rgba(212, 222, 199, 0.6);
    }
  }
}

.member-avatar {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid rgba(170, 131, 255, 0.3);
  overflow: hidden;
  transition: all var(--transition-base) var(--ease-hover);
  background: var(--glass-bg);

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform var(--transition-base) var(--ease-hover);
  }
}

.avatar-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(170, 131, 255, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0;
  transform: scale(1);
  transition: all var(--transition-base) var(--ease-hover);
  pointer-events: none;
}

.member-tooltip {
  position: fixed;
  z-index: 1000;
  pointer-events: none;
  transform: translateY(-100%);
}

.tooltip-content {
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 12px;
  box-shadow: var(--shadow-glass);
  max-width: 200px;
}

.member-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.member-bio {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 6px;
  line-height: 1.4;
}

.member-meta {
  font-size: 11px;
  color: var(--text-tertiary);
}

@keyframes gentleFloat {

  0%,
  100% {
    transform: translate(-50%, -50%) translateX(calc(cos(var(--float-angle)) * var(--float-distance))) translateY(calc(sin(var(--float-angle)) * var(--float-distance))) rotate(var(--rotate-deg));
  }

  50% {
    transform: translate(-50%, -50%) translateX(calc(cos(var(--float-angle) + 180deg) * var(--float-distance))) translateY(calc(sin(var(--float-angle) + 180deg) * var(--float-distance))) rotate(calc(var(--rotate-deg) * -1));
  }
}
</style>
