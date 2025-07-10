import { ref, computed } from 'vue'

export interface Node {
  id: string
  x: number
  y: number
  vx?: number
  vy?: number
  fx?: number // 固定位置 x
  fy?: number // 固定位置 y
}

export interface Link {
  source: string
  target: string
  strength: number
  distance: number
  active: boolean
  brightness: number
  pulsePhase: number
  breathingPhase: number // 呼吸相位
  breathingCycle: number // 呼吸周期长度（毫秒）
  breathingOffset: number // 呼吸偏移
  lastActivationTime: number // 上次激活时间
  activationStart?: number // 激活开始时间
  activationDuration?: number // 激活持续时间
}

export interface ForceConfig {
  linkStrength: number
  linkDistance: number
  chargeStrength: number
  centerStrength: number
  velocityDecay: number
  maxConnections: number
}

export function useForceDirectedConnections(
  nodes: Node[],
  config: Partial<ForceConfig> = {}
) {
  const defaultConfig: ForceConfig = {
    linkStrength: 0.1,
    linkDistance: 100,
    chargeStrength: -30,
    centerStrength: 0.1,
    velocityDecay: 0.4,
    maxConnections: 3
  }

  const finalConfig = { ...defaultConfig, ...config }
  
  const links = ref<Link[]>([])
  const animationId = ref<number>()
  const isRunning = ref(false)

  // 计算两点之间的距离
  const distance = (a: Node, b: Node): number => {
    return Math.sqrt(Math.pow(a.x - b.x, 2) + Math.pow(a.y - b.y, 2))
  }

  // 生成连接线
  const generateLinks = () => {
    // 保存现有连接线的激活状态
    const existingActivations = new Map<string, { active: boolean, activationStart?: number, activationDuration?: number }>()
    links.value.forEach(link => {
      const key = `${link.source}-${link.target}`
      const reverseKey = `${link.target}-${link.source}`
      if (link.active && link.activationStart) {
        existingActivations.set(key, {
          active: link.active,
          activationStart: link.activationStart,
          activationDuration: link.activationDuration
        })
        existingActivations.set(reverseKey, {
          active: link.active,
          activationStart: link.activationStart,
          activationDuration: link.activationDuration
        })
      }
    })

    const newLinks: Link[] = []

    nodes.forEach((node, i) => {
      // 计算到其他节点的距离
      const distances = nodes
        .map((otherNode, j) => ({
          index: j,
          node: otherNode,
          distance: i === j ? Infinity : distance(node, otherNode)
        }))
        .sort((a, b) => a.distance - b.distance)
        .slice(0, finalConfig.maxConnections)

      distances.forEach(({ node: targetNode }) => {
        // 避免重复连接
        const linkExists = newLinks.some(link =>
          (link.source === node.id && link.target === targetNode.id) ||
          (link.source === targetNode.id && link.target === node.id)
        )

        if (!linkExists && node.id !== targetNode.id) {
          const linkKey = `${node.id}-${targetNode.id}`
          const existingActivation = existingActivations.get(linkKey)

          const newLink = {
            source: node.id,
            target: targetNode.id,
            strength: finalConfig.linkStrength,
            distance: finalConfig.linkDistance,
            active: existingActivation?.active || Math.random() > 0.7, // 保留现有激活状态或30%随机激活
            brightness: 0.0, // 初始亮度为0
            pulsePhase: Math.random() * Math.PI * 2,
            breathingPhase: Math.random() * Math.PI * 2, // 随机呼吸相位
            breathingCycle: 6000 + Math.random() * 4000, // 6-10秒的呼吸周期（更慢更自然）
            breathingOffset: Math.random() * 5000, // 随机偏移（增加变化）
            lastActivationTime: performance.now(),
            activationStart: existingActivation?.activationStart, // 保留现有激活开始时间
            activationDuration: existingActivation?.activationDuration // 保留现有激活持续时间
          }
          newLinks.push(newLink)
        }
      })
    })

    links.value = newLinks
  }

  // 应用力的计算
  const applyForces = () => {
    const nodeMap = new Map(nodes.map(node => [node.id, node]))

    // 初始化速度
    nodes.forEach(node => {
      if (node.vx === undefined) node.vx = 0
      if (node.vy === undefined) node.vy = 0
    })

    // 连接力
    links.value.forEach(link => {
      const source = nodeMap.get(link.source)
      const target = nodeMap.get(link.target)
      
      if (!source || !target) return

      const dx = target.x - source.x
      const dy = target.y - source.y
      const dist = Math.sqrt(dx * dx + dy * dy) || 1
      
      // 弹簧力
      const force = (dist - link.distance) * link.strength
      const fx = (dx / dist) * force
      const fy = (dy / dist) * force

      source.vx! += fx
      source.vy! += fy
      target.vx! -= fx
      target.vy! -= fy
    })

    // 排斥力
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const nodeA = nodes[i]
        const nodeB = nodes[j]
        
        const dx = nodeB.x - nodeA.x
        const dy = nodeB.y - nodeA.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        
        if (dist < 150) { // 只在近距离时应用排斥力
          const force = finalConfig.chargeStrength / (dist * dist)
          const fx = (dx / dist) * force
          const fy = (dy / dist) * force

          nodeA.vx! -= fx
          nodeA.vy! -= fy
          nodeB.vx! += fx
          nodeB.vy! += fy
        }
      }
    }

    // 中心力（保持节点在合理范围内）
    const centerX = window.innerWidth / 2
    const centerY = window.innerHeight / 2
    
    nodes.forEach(node => {
      const dx = centerX - node.x
      const dy = centerY - node.y
      
      node.vx! += dx * finalConfig.centerStrength * 0.01
      node.vy! += dy * finalConfig.centerStrength * 0.01
    })

    // 应用速度和阻尼，并监控节点位置变化
    let movedNodes = 0
    let totalVelocity = 0

    nodes.forEach((node, index) => {
      const oldX = node.x
      const oldY = node.y

      if (node.fx !== undefined) {
        node.x = node.fx
        node.vx = 0
      } else {
        node.vx! *= finalConfig.velocityDecay
        node.x += node.vx!
      }

      if (node.fy !== undefined) {
        node.y = node.fy
        node.vy = 0
      } else {
        node.vy! *= finalConfig.velocityDecay
        node.y += node.vy!
      }

      // 边界约束
      const margin = 50
      if (node.fx === undefined) {
        node.x = Math.max(margin, Math.min(window.innerWidth - margin, node.x))
      }
      if (node.fy === undefined) {
        node.y = Math.max(margin, Math.min(window.innerHeight - margin, node.y))
      }

      // 📊 监控节点移动（用于连接线动态指向验证）
      const deltaX = node.x - oldX
      const deltaY = node.y - oldY
      const velocity = Math.sqrt(deltaX*deltaX + deltaY*deltaY)

      if (velocity > 0.1) {  // 只记录有明显移动的节点
        movedNodes++
        totalVelocity += velocity

        // 📍 开发模式下记录关键节点位置变化
        if (import.meta.env.DEV && index < 1 && velocity > 2) {
          console.log(`🚀 [节点${node.id}] 位置更新:`, {
            to: `(${node.x.toFixed(1)}, ${node.y.toFixed(1)})`,
            velocity: velocity.toFixed(2)
          })
        }
      }
    })

    // 📈 开发模式下的运动状态监控
    if (import.meta.env.DEV && movedNodes > 5 && Math.random() < 0.02) {
      const avgVelocity = totalVelocity / movedNodes
      console.log(`📈 [节点运动] 移动节点: ${movedNodes}/${nodes.length}, 平均速度: ${avgVelocity.toFixed(2)}`)
    }
  }

  // 缓动函数：实现弱-强-弱的呼吸效果
  const easeInOutSine = (t: number): number => {
    return -(Math.cos(Math.PI * t) - 1) / 2
  }

  // 更新连接线状态
  const updateLinks = () => {
    const currentTime = performance.now()

    links.value.forEach(link => {
      // 更新脉冲相位（保持原有的脉冲效果）
      link.pulsePhase += 0.02 + Math.random() * 0.01

      // 计算呼吸效果
      const breathingTime = (currentTime + link.breathingOffset) % link.breathingCycle
      const breathingProgress = breathingTime / link.breathingCycle

      // 使用缓动函数创建弱-强-弱的呼吸效果
      const breathingIntensity = easeInOutSine(breathingProgress)

      // 基于呼吸强度和激活状态的平滑亮度变化
      // 保持随机激活机制，但让激活的连接线有平滑的呼吸效果

      // 基于呼吸强度决定是否应该激活（更平滑的激活逻辑）
      const activationThreshold = 0.6 // 较高的阈值，只有在呼吸强度较高时才激活
      const shouldBeActive = breathingIntensity > activationThreshold

      // 平滑切换激活状态（但不会突然切换）
      if (shouldBeActive && !link.active) {
        // 只有在呼吸强度足够高时才可能激活
        if (Math.random() < 0.02) { // 2% 的概率激活
          link.active = true
          link.lastActivationTime = currentTime
        }
      } else if (!shouldBeActive && link.active) {
        // 呼吸强度低时逐渐去激活
        if (Math.random() < 0.01) { // 1% 的概率去激活
          link.active = false
          link.lastActivationTime = currentTime
        }
      }

      // 计算目标亮度：激活的连接线有呼吸效果，未激活的保持暗淡
      let targetBrightness = 0.0
      if (link.active) {
        // 激活的连接线：基于呼吸强度的平滑亮度变化
        const minBrightness = 0.01  // 激活时的最低亮度（更低的最小值）
        const maxBrightness = 1.0   // 激活时的最高亮度
        targetBrightness = minBrightness + breathingIntensity * (maxBrightness - minBrightness)
      } else {
        // 未激活的连接线：保持很低的亮度或完全不可见
        targetBrightness = 0.0
      }

      // 平滑的亮度过渡
      const brightnessSpeed = link.active ? 0.02 : 0.01 // 激活时变化稍快
      if (Math.abs(link.brightness - targetBrightness) > 0.01) {
        link.brightness += (targetBrightness - link.brightness) * brightnessSpeed
      } else {
        link.brightness = targetBrightness
      }

      // 更新呼吸相位
      link.breathingPhase = breathingProgress * Math.PI * 2
    })
  }

  // 动画循环
  const animate = () => {
    if (!isRunning.value) return

    applyForces()
    updateLinks()
    
    animationId.value = requestAnimationFrame(animate)
  }

  // 开始模拟
  const start = () => {
    if (isRunning.value) return

    generateLinks()
    isRunning.value = true
    animate()
  }

  // 停止模拟
  const stop = () => {
    isRunning.value = false
    if (animationId.value) {
      cancelAnimationFrame(animationId.value)
    }
  }

  // 重新生成连接
  const regenerate = () => {
    generateLinks()
  }

  // 获取连接线路径
  const getConnectionPath = computed(() => {
    return (sourceId: string, targetId: string) => {
      const nodeMap = new Map(nodes.map(node => [node.id, node]))
      const source = nodeMap.get(sourceId)
      const target = nodeMap.get(targetId)
      
      if (!source || !target) return ''

      // 创建贝塞尔曲线路径
      const dx = target.x - source.x
      const dy = target.y - source.y
      const distance = Math.sqrt(dx * dx + dy * dy)
      
      // 控制点偏移
      const offset = distance * 0.2
      const midX = (source.x + target.x) / 2
      const midY = (source.y + target.y) / 2
      
      // 垂直于连线的方向
      const perpX = -dy / distance * offset
      const perpY = dx / distance * offset
      
      const cp1X = midX + perpX
      const cp1Y = midY + perpY
      
      return `M ${source.x} ${source.y} Q ${cp1X} ${cp1Y} ${target.x} ${target.y}`
    }
  })

  return {
    links: computed(() => links.value),
    getConnectionPath,
    start,
    stop,
    regenerate,
    isRunning: computed(() => isRunning.value)
  }
}
