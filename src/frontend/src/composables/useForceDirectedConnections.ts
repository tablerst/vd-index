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
          newLinks.push({
            source: node.id,
            target: targetNode.id,
            strength: finalConfig.linkStrength,
            distance: finalConfig.linkDistance,
            active: Math.random() > 0.7, // 30% 的连接线激活
            brightness: 0.3 + Math.random() * 0.5,
            pulsePhase: Math.random() * Math.PI * 2
          })
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

    // 应用速度和阻尼
    nodes.forEach(node => {
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
    })
  }

  // 更新连接线状态
  const updateLinks = () => {
    links.value.forEach(link => {
      // 更新脉冲相位
      link.pulsePhase += 0.02 + Math.random() * 0.01
      
      // 随机激活/去激活连接线
      if (Math.random() < 0.005) {
        link.active = !link.active
      }
      
      // 更新亮度
      if (link.active) {
        link.brightness = Math.min(0.8, link.brightness + 0.02)
      } else {
        link.brightness = Math.max(0.1, link.brightness - 0.01)
      }
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
