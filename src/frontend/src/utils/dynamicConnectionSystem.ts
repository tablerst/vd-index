/**
 * 动态连接线系统 - 按需创建/销毁连接线，大幅提升性能
 */

export interface DynamicConnection {
  id: string
  sourceId: string
  targetId: string
  
  // 生命周期状态
  state: 'creating' | 'active' | 'fading' | 'destroyed'
  createdAt: number
  activatedAt: number
  fadeStartAt: number
  destroyAt: number
  
  // 视觉属性
  alpha: number
  targetAlpha: number
  
  // 动画属性
  breathingPhase: number
  breathingSpeed: number
  colorIndex: number
}

export interface ConnectionSystemConfig {
  // 连接线数量控制
  maxActiveConnections: number      // 最大同时活跃连接线数量
  minActiveConnections: number      // 最小保持活跃连接线数量
  
  // 生命周期时间控制
  creationDuration: number          // 创建阶段持续时间 (ms)
  activeDuration: number            // 活跃阶段持续时间 (ms)
  fadeDuration: number              // 淡出阶段持续时间 (ms)
  
  // 创建频率控制
  creationInterval: number          // 创建新连接线的间隔 (ms)
  creationBatchSize: number         // 每次创建的连接线数量
  
  // 选择策略
  preferCloseConnections: boolean   // 是否优先选择距离近的连接
  avoidRecentConnections: boolean   // 是否避免重复最近的连接
  recentConnectionMemory: number    // 记住最近连接的时间 (ms)
}

export class DynamicConnectionSystem {
  private connections: Map<string, DynamicConnection> = new Map()
  private recentConnections: Set<string> = new Set()
  private lastCreationTime = 0
  private memberPositions: Map<string, { x: number, y: number, r: number }> = new Map()
  
  private config: ConnectionSystemConfig = {
    maxActiveConnections: 8,
    minActiveConnections: 3,
    creationDuration: 800,
    activeDuration: 4000,
    fadeDuration: 1200,
    creationInterval: 2500,
    creationBatchSize: 2,
    preferCloseConnections: true,
    avoidRecentConnections: true,
    recentConnectionMemory: 8000
  }

  constructor(config?: Partial<ConnectionSystemConfig>) {
    if (config) {
      this.config = { ...this.config, ...config }
    }
  }

  /**
   * 更新成员位置信息
   */
  updateMemberPositions(positions: Map<string, { x: number, y: number, r: number }>) {
    this.memberPositions = new Map(positions)
  }

  /**
   * 获取所有活跃连接线
   */
  getActiveConnections(): DynamicConnection[] {
    return Array.from(this.connections.values()).filter(
      conn => conn.state !== 'destroyed'
    )
  }

  /**
   * 主更新循环
   */
  update(currentTime: number): void {
    // 更新现有连接线状态
    this.updateExistingConnections(currentTime)
    
    // 清理已销毁的连接线
    this.cleanupDestroyedConnections()
    
    // 创建新连接线（如果需要）
    this.createNewConnectionsIfNeeded(currentTime)
    
    // 清理过期的最近连接记录
    this.cleanupRecentConnections(currentTime)
  }

  /**
   * 更新现有连接线状态
   */
  private updateExistingConnections(currentTime: number): void {
    for (const connection of this.connections.values()) {
      this.updateConnectionState(connection, currentTime)
      this.updateConnectionVisuals(connection, currentTime)
    }
  }

  /**
   * 更新单个连接线的状态
   */
  private updateConnectionState(connection: DynamicConnection, currentTime: number): void {
    switch (connection.state) {
      case 'creating':
        if (currentTime - connection.createdAt >= this.config.creationDuration) {
          connection.state = 'active'
          connection.activatedAt = currentTime
          connection.fadeStartAt = currentTime + this.config.activeDuration
        }
        break
        
      case 'active':
        if (currentTime >= connection.fadeStartAt) {
          connection.state = 'fading'
        }
        break
        
      case 'fading':
        if (currentTime - connection.fadeStartAt >= this.config.fadeDuration) {
          connection.state = 'destroyed'
          connection.destroyAt = currentTime
        }
        break
    }
  }

  /**
   * 更新连接线的视觉效果
   */
  private updateConnectionVisuals(connection: DynamicConnection, currentTime: number): void {
    // 更新呼吸动画
    connection.breathingPhase += connection.breathingSpeed
    const breathingIntensity = (Math.sin(connection.breathingPhase) + 1) / 2

    // 根据状态计算目标透明度
    let baseAlpha = 0
    
    switch (connection.state) {
      case 'creating':
        // 淡入效果
        const createProgress = (currentTime - connection.createdAt) / this.config.creationDuration
        baseAlpha = Math.min(createProgress, 1)
        break
        
      case 'active':
        // 完全活跃，带呼吸效果
        baseAlpha = 0.3 + breathingIntensity * 0.7 // 0.3-1.0 范围
        break
        
      case 'fading':
        // 淡出效果
        const fadeProgress = (currentTime - connection.fadeStartAt) / this.config.fadeDuration
        const remainingAlpha = 1 - Math.min(fadeProgress, 1)
        baseAlpha = remainingAlpha * (0.3 + breathingIntensity * 0.7)
        break
        
      case 'destroyed':
        baseAlpha = 0
        break
    }

    // 平滑过渡到目标透明度
    connection.targetAlpha = baseAlpha
    const alphaSpeed = 0.1
    connection.alpha += (connection.targetAlpha - connection.alpha) * alphaSpeed
  }

  /**
   * 清理已销毁的连接线
   */
  private cleanupDestroyedConnections(): void {
    for (const [id, connection] of this.connections.entries()) {
      if (connection.state === 'destroyed') {
        this.connections.delete(id)
      }
    }
  }

  /**
   * 根据需要创建新连接线
   */
  private createNewConnectionsIfNeeded(currentTime: number): void {
    const activeCount = this.getActiveConnections().length
    
    // 检查是否需要创建新连接线
    const shouldCreate = (
      activeCount < this.config.minActiveConnections ||
      (activeCount < this.config.maxActiveConnections && 
       currentTime - this.lastCreationTime >= this.config.creationInterval)
    )

    if (!shouldCreate) return

    const membersArray = Array.from(this.memberPositions.keys())
    if (membersArray.length < 2) return

    // 创建新连接线
    const connectionsToCreate = Math.min(
      this.config.creationBatchSize,
      this.config.maxActiveConnections - activeCount
    )

    for (let i = 0; i < connectionsToCreate; i++) {
      this.createRandomConnection(currentTime, membersArray)
    }

    this.lastCreationTime = currentTime
  }

  /**
   * 创建随机连接线
   */
  private createRandomConnection(currentTime: number, memberIds: string[]): void {
    const candidates = this.generateConnectionCandidates(memberIds)
    if (candidates.length === 0) return

    // 选择最佳候选连接
    const selectedCandidate = this.selectBestCandidate(candidates)
    if (!selectedCandidate) return

    const { sourceId, targetId } = selectedCandidate
    const connectionId = `${sourceId}-${targetId}`

    // 创建新连接线
    const connection: DynamicConnection = {
      id: connectionId,
      sourceId,
      targetId,
      state: 'creating',
      createdAt: currentTime,
      activatedAt: 0,
      fadeStartAt: currentTime + this.config.creationDuration + this.config.activeDuration,
      destroyAt: 0,
      alpha: 0,
      targetAlpha: 0,
      breathingPhase: Math.random() * Math.PI * 2,
      breathingSpeed: 0.02 + Math.random() * 0.02,
      colorIndex: Math.floor(Math.random() * 3) // 0-2 对应三种主题色
    }

    this.connections.set(connectionId, connection)
    
    // 记录到最近连接
    this.recentConnections.add(connectionId)
    this.recentConnections.add(`${targetId}-${sourceId}`) // 双向记录
  }

  /**
   * 生成连接候选列表
   */
  private generateConnectionCandidates(memberIds: string[]): Array<{sourceId: string, targetId: string, distance: number}> {
    const candidates: Array<{sourceId: string, targetId: string, distance: number}> = []

    for (let i = 0; i < memberIds.length; i++) {
      for (let j = i + 1; j < memberIds.length; j++) {
        const sourceId = memberIds[i]
        const targetId = memberIds[j]
        const connectionId = `${sourceId}-${targetId}`
        const reverseId = `${targetId}-${sourceId}`

        // 跳过已存在的连接
        if (this.connections.has(connectionId) || this.connections.has(reverseId)) {
          continue
        }

        // 跳过最近的连接（如果启用）
        if (this.config.avoidRecentConnections && 
            (this.recentConnections.has(connectionId) || this.recentConnections.has(reverseId))) {
          continue
        }

        // 计算距离
        const sourcePos = this.memberPositions.get(sourceId)
        const targetPos = this.memberPositions.get(targetId)
        
        if (!sourcePos || !targetPos) continue

        const distance = Math.sqrt(
          Math.pow(sourcePos.x - targetPos.x, 2) + 
          Math.pow(sourcePos.y - targetPos.y, 2)
        )

        candidates.push({ sourceId, targetId, distance })
      }
    }

    return candidates
  }

  /**
   * 选择最佳连接候选
   */
  private selectBestCandidate(candidates: Array<{sourceId: string, targetId: string, distance: number}>): {sourceId: string, targetId: string} | null {
    if (candidates.length === 0) return null

    if (this.config.preferCloseConnections) {
      // 优先选择距离较近的连接，但加入随机性
      candidates.sort((a, b) => a.distance - b.distance)
      const topCandidates = candidates.slice(0, Math.min(5, candidates.length))
      return topCandidates[Math.floor(Math.random() * topCandidates.length)]
    } else {
      // 完全随机选择
      return candidates[Math.floor(Math.random() * candidates.length)]
    }
  }

  /**
   * 清理过期的最近连接记录
   */
  private cleanupRecentConnections(_currentTime: number): void {
    // 简单的清理策略：定期清空所有记录
    if (this.recentConnections.size > 20) {
      this.recentConnections.clear()
    }
  }

  /**
   * 获取连接线的颜色 - 动态读取CSS变量以支持主题切换
   */
  getConnectionColor(connection: DynamicConnection): { r: number, g: number, b: number } {
    // 动态读取CSS变量
    const root = getComputedStyle(document.documentElement)
    const primaryColor = root.getPropertyValue('--primary').trim()
    const secondaryColor = root.getPropertyValue('--secondary').trim()
    const accentColor = root.getPropertyValue('--accent-blue').trim()

    const colors = [
      this.hexToRgb(primaryColor || '#AA83FF'),   // 主色
      this.hexToRgb(secondaryColor || '#D4DEC7'), // 次色
      this.hexToRgb(accentColor || '#3F7DFB')     // 强调色
    ]
    return colors[connection.colorIndex] || colors[0]
  }

  /**
   * 十六进制颜色转RGB
   */
  private hexToRgb(hex: string): { r: number, g: number, b: number } {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : { r: 170, g: 131, b: 255 } // 默认紫色
  }

  /**
   * 更新配置
   */
  updateConfig(newConfig: Partial<ConnectionSystemConfig>): void {
    this.config = { ...this.config, ...newConfig }
  }

  /**
   * 重置系统
   */
  reset(): void {
    this.connections.clear()
    this.recentConnections.clear()
    this.lastCreationTime = 0
  }

  /**
   * 获取系统统计信息
   */
  getStats() {
    const connections = this.getActiveConnections()
    const stateCount = connections.reduce((acc, conn) => {
      acc[conn.state] = (acc[conn.state] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return {
      totalConnections: connections.length,
      stateDistribution: stateCount,
      recentConnectionsCount: this.recentConnections.size,
      config: this.config
    }
  }
}
