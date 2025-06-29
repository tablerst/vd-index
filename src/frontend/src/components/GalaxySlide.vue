<template>
  <div class="galaxy-slide" ref="slideRef">
    <!-- 连接线Canvas -->
    <canvas 
      ref="connectionsCanvas"
      class="connections-canvas"
      :width="canvasSize.width"
      :height="canvasSize.height"
    ></canvas>

    <!-- 成员星球 -->
    <div class="members-nebula">
      <div
        v-for="(member, index) in members"
        :key="member.id"
        class="member-star"
        :class="{ 'member-star--selected': selectedMember?.id === member.id }"
        :style="getMemberStarStyle(index)"
        @click="selectMember(member)"
        @mouseenter="(event) => handleMemberHover(member, event)"
        @mousemove="updateTooltipPosition"
        @mouseleave="handleMemberLeave"
        @keydown.enter="selectMember(member)"
        @keydown.escape="closeMemberInfo"
        tabindex="0"
        :aria-label="`${member.name} 的星球`"
        role="button"
      >
        <div class="member-avatar">
          <img :src="member.avatarURL" :alt="member.name" loading="lazy">
          <div class="avatar-glow"></div>
        </div>
        <div
          class="member-tooltip"
          v-if="hoveredMember?.id === member.id"
          :style="{
            left: `${tooltipPosition.x}px`,
            top: `${tooltipPosition.y}px`
          }"
        >
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
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useForceDirectedConnections, type Node } from '../composables/useForceDirectedConnections'
import { useDeviceDetection } from '../composables/useDeviceDetection'
import type { Member } from '../stores/members'

interface Props {
  members: Member[]
  index: number
}

const props = defineProps<Props>()

// 设备检测
const { responsiveConfig, deviceInfo } = useDeviceDetection()

const slideRef = ref<HTMLElement>()
const connectionsCanvas = ref<HTMLCanvasElement>()
const selectedMember = ref<Member | null>(null)
const hoveredMember = ref<Member | null>(null)
const tooltipPosition = ref({ x: 0, y: 0 })

// Canvas尺寸
const canvasSize = computed(() => ({
  width: window.innerWidth,
  height: window.innerHeight
}))

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

// 创建节点数据
const nodes = computed(() => {
  return props.members.map((member, index) => {
    const style = getMemberStarStyle(index)
    return {
      id: member.id.toString(),
      x: (parseFloat(style.left as string) / 100) * canvasSize.value.width,
      y: (parseFloat(style.top as string) / 100) * canvasSize.value.height,
      fx: (parseFloat(style.left as string) / 100) * canvasSize.value.width, // 固定位置
      fy: (parseFloat(style.top as string) / 100) * canvasSize.value.height
    } as Node
  })
})

// 使用力导向连接系统
const {
  links,
  // getConnectionPath, // 暂时注释未使用的函数
  start: startForceSimulation,
  stop: stopForceSimulation
} = useForceDirectedConnections(nodes.value, {
  linkStrength: 0.05,
  linkDistance: 120,
  chargeStrength: -20,
  maxConnections: 2
})

// 连接线绘制
const drawConnections = () => {
  const canvas = connectionsCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // 绘制力导向连接线
  links.value.forEach(link => {
    const sourceNode = nodes.value.find(n => n.id === link.source)
    const targetNode = nodes.value.find(n => n.id === link.target)

    if (!sourceNode || !targetNode) return

    // 计算脉冲效果
    const pulse = Math.sin(link.pulsePhase) * 0.3 + 0.7
    const alpha = link.brightness * pulse * (link.active ? 1 : 0.3)

    // 绘制主连接线
    ctx.beginPath()
    ctx.moveTo(sourceNode.x, sourceNode.y)

    // 创建贝塞尔曲线
    const dx = targetNode.x - sourceNode.x
    const dy = targetNode.y - sourceNode.y
    const distance = Math.sqrt(dx * dx + dy * dy)
    const offset = distance * 0.15
    const midX = (sourceNode.x + targetNode.x) / 2
    const midY = (sourceNode.y + targetNode.y) / 2
    const perpX = -dy / distance * offset
    const perpY = dx / distance * offset
    const cpX = midX + perpX
    const cpY = midY + perpY

    ctx.quadraticCurveTo(cpX, cpY, targetNode.x, targetNode.y)

    // 渐变色
    const gradient = ctx.createLinearGradient(
      sourceNode.x, sourceNode.y,
      targetNode.x, targetNode.y
    )
    gradient.addColorStop(0, `rgba(170, 131, 255, ${alpha})`)
    gradient.addColorStop(0.5, `rgba(212, 222, 199, ${alpha * 0.8})`)
    gradient.addColorStop(1, `rgba(170, 131, 255, ${alpha})`)

    ctx.strokeStyle = gradient
    ctx.lineWidth = link.active ? 2 : 1
    ctx.lineCap = 'round'
    ctx.stroke()

    // 添加光晕效果
    if (link.active && alpha > 0.5) {
      ctx.beginPath()
      ctx.moveTo(sourceNode.x, sourceNode.y)
      ctx.quadraticCurveTo(cpX, cpY, targetNode.x, targetNode.y)
      ctx.strokeStyle = `rgba(170, 131, 255, ${alpha * 0.2})`
      ctx.lineWidth = 6
      ctx.stroke()
    }
  })
}

// 监听成员变化，重新绘制连接线
watch(() => props.members, () => {
  nextTick(() => {
    drawConnections()
  })
}, { immediate: true })

// 动画循环
let animationId: number
const animate = () => {
  drawConnections()
  animationId = requestAnimationFrame(animate)
}

onMounted(() => {
  nextTick(() => {
    startForceSimulation()
    animate()
  })
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  stopForceSimulation()
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
  top: 0;
  left: 0;
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
  0%, 100% {
    transform: translate(-50%, -50%) 
               translateX(calc(cos(var(--float-angle)) * var(--float-distance))) 
               translateY(calc(sin(var(--float-angle)) * var(--float-distance)))
               rotate(var(--rotate-deg));
  }
  50% {
    transform: translate(-50%, -50%) 
               translateX(calc(cos(var(--float-angle) + 180deg) * var(--float-distance))) 
               translateY(calc(sin(var(--float-angle) + 180deg) * var(--float-distance)))
               rotate(calc(var(--rotate-deg) * -1));
  }
}
</style>
