<template>
  <section id="activities" class="star-calendar">
    <!-- 背景装饰 -->
    <div class="calendar-background">
      <div class="bg-constellation">
        <div v-for="i in 20" :key="i" class="constellation-star" :style="getStarStyle(i)"></div>
      </div>
      <div class="bg-nebula"></div>
    </div>

    <div class="container">
      <!-- 标题区域 -->
      <div class="section-header">
        <h2 class="section-title">
          <span class="title-accent">星历</span>活动板
        </h2>
        <p class="section-subtitle">
          记录VRC Division的精彩时刻与重要里程碑
        </p>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <span>正在加载活动数据...</span>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-state">
          <span class="error-message">{{ error }}</span>
          <button @click="loadActivities" class="retry-btn">重试</button>
        </div>

        <!-- 统计信息 -->
        <div v-else class="calendar-stats">
          <div class="stat-item">
            <span class="stat-number">{{ activities.length }}</span>
            <span class="stat-label">个活动</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ totalParticipants }}</span>
            <span class="stat-label">人次参与</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ uniqueParticipants }}</span>
            <span class="stat-label">位成员</span>
          </div>
        </div>
      </div>

      <!-- 时间轴容器 -->
      <div class="timeline-container">
        <!-- 时间轴背景线 -->
        <div class="timeline-track">
          <div class="track-line"></div>
          <div class="track-glow"></div>
        </div>

        <!-- 导航按钮 -->
        <button
          class="nav-btn nav-btn--prev"
          @click="navigateTimeline('prev')"
          :disabled="currentIndex === 0"
          aria-label="查看上一个活动"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- 活动卡片栈 -->
        <div class="timeline-stack" ref="timelineStack">
          <div 
            v-for="(activity, index) in activities" 
            :key="activity.id"
            class="activity-card"
            :class="{
              'activity-card--active': index === currentIndex,
              'activity-card--prev': index < currentIndex,
              'activity-card--next': index > currentIndex
            }"
            :style="getCardStyle(index)"
            @click="selectActivity(index)"
            @keydown.enter="selectActivity(index)"
            @keydown.escape="closeActivityDetail"
            tabindex="0"
            :aria-label="`活动: ${activity.title}`"
            role="button"
          >
            <!-- 卡片内容 -->
            <div class="card-content">
              <!-- 日期标签 -->
              <div class="activity-date">
                <span class="date-day">{{ formatDay(activity.date) }}</span>
                <span class="date-month">{{ formatMonth(activity.date) }}</span>
                <span class="date-year">{{ formatYear(activity.date) }}</span>
              </div>

              <!-- 活动信息 -->
              <div class="activity-info">
                <h3 class="activity-title">{{ activity.title }}</h3>
                <p class="activity-description">{{ activity.description }}</p>
                
                <!-- 活动标签 -->
                <div class="activity-tags">
                  <span 
                    v-for="tag in activity.tags" 
                    :key="tag"
                    class="activity-tag"
                    :class="`activity-tag--${getTagType(tag)}`"
                  >
                    {{ tag }}
                  </span>
                </div>

                <!-- 参与者头像 -->
                <div v-if="activity.participants" class="activity-participants">
                  <div class="participants-avatars">
                    <img
                      v-for="(participant, pIndex) in activity.participants.slice(0, 5)"
                      :key="participant.id"
                      :src="participant.avatar_url"
                      :alt="participant.name"
                      class="participant-avatar"
                      :style="{ zIndex: 5 - pIndex }"
                    >
                    <span
                      v-if="activity.participants.length > 5"
                      class="participants-more"
                    >
                      +{{ activity.participants.length - 5 }}
                    </span>
                  </div>
                  <span class="participants-count">
                    {{ activity.participants_total }} 人参与
                  </span>
                </div>
              </div>

              <!-- 卡片装饰 -->
              <div class="card-decoration">
                <div class="decoration-line"></div>
                <div class="decoration-dots">
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>
              </div>
            </div>

            <!-- 悬停效果 -->
            <div class="card-glow"></div>
          </div>
        </div>

        <!-- 导航按钮 -->
        <button 
          class="nav-btn nav-btn--next"
          @click="navigateTimeline('next')"
          :disabled="currentIndex === activities.length - 1"
          aria-label="查看下一个活动"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <!-- 时间轴指示器 -->
      <div class="timeline-indicators">
        <button 
          v-for="(activity, index) in activities"
          :key="activity.id"
          class="timeline-indicator"
          :class="{ 'timeline-indicator--active': index === currentIndex }"
          @click="selectActivity(index)"
          :aria-label="`跳转到活动 ${index + 1}`"
        >
          <span class="indicator-dot"></span>
        </button>
      </div>

      <!-- 键盘提示 -->
      <div class="keyboard-hints">
        <span class="hint">
          <kbd>←</kbd> <kbd>→</kbd> 切换活动
        </span>
        <span class="hint">
          <kbd>Enter</kbd> 选择
        </span>
        <span class="hint">
          <kbd>Esc</kbd> 关闭
        </span>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { activityApi, type Activity, type ActivityStats } from '@/services/api'

// 使用API中定义的接口类型
// Activity 和 ParticipantInfo 已在 api.ts 中定义

// 响应式数据
const currentIndex = ref(0)
const timelineStack = ref<HTMLElement>()
const activities = ref<Activity[]>([])
const activityStats = ref<ActivityStats | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

// 计算属性
const totalParticipants = computed(() => {
  return activityStats.value?.total_participants || 0
})

const uniqueParticipants = computed(() => {
  return activityStats.value?.unique_participants || 0
})

// 导航时间轴
const navigateTimeline = (direction: 'prev' | 'next') => {
  if (direction === 'prev' && currentIndex.value > 0) {
    currentIndex.value--
  } else if (direction === 'next' && currentIndex.value < activities.value.length - 1) {
    currentIndex.value++
  }
}

// 选择活动
const selectActivity = (index: number) => {
  currentIndex.value = index
}

// 关闭活动详情
const closeActivityDetail = () => {
  // 这里可以添加关闭详情的逻辑
}

// 获取卡片样式
const getCardStyle = (index: number) => {
  const offset = index - currentIndex.value
  const translateX = offset * 20
  const translateZ = -Math.abs(offset) * 50
  const opacity = Math.max(0.3, 1 - Math.abs(offset) * 0.3)
  const scale = Math.max(0.8, 1 - Math.abs(offset) * 0.1)
  
  return {
    transform: `translateX(${translateX}px) translateZ(${translateZ}px) scale(${scale})`,
    opacity: opacity,
    zIndex: 10 - Math.abs(offset)
  }
}

// 格式化日期
const formatDay = (dateString: string): string => {
  return activityApi.formatDateShort(dateString).day
}

const formatMonth = (dateString: string): string => {
  return activityApi.formatDateShort(dateString).month
}

// 加载活动数据
const loadActivities = async () => {
  try {
    loading.value = true
    error.value = null

    // 并行加载活动列表和统计信息
    const [activitiesData, statsData] = await Promise.all([
      activityApi.getAllActivities(),
      activityApi.getStats()
    ])

    activities.value = activitiesData
    activityStats.value = statsData

    console.log('活动数据加载成功:', {
      activities: activitiesData.length,
      stats: statsData
    })
  } catch (err) {
    console.error('加载活动数据失败:', err)
    error.value = err instanceof Error ? err.message : '加载活动数据失败'
  } finally {
    loading.value = false
  }
}

const formatYear = (dateString: string): string => {
  return new Date(dateString).getFullYear().toString()
}

// 获取标签类型
const getTagType = (tag: string): string => {
  const tagTypes: Record<string, string> = {
    '里程碑': 'milestone',
    '技术': 'tech',
    '设计': 'design',
    '音乐': 'music',
    '户外': 'outdoor',
    '社区': 'community',
    '分享': 'share',
    '比赛': 'competition',
    '娱乐': 'entertainment',
    '团建': 'team'
  }
  return tagTypes[tag] || 'default'
}

// 生成星星样式
const getStarStyle = (_index: number) => {
  const size = Math.random() * 3 + 1
  const x = Math.random() * 100
  const y = Math.random() * 100
  const delay = Math.random() * 5
  const duration = Math.random() * 3 + 2

  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${x}%`,
    top: `${y}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
}

// 键盘事件处理
const handleKeyDown = (e: KeyboardEvent) => {
  switch (e.key) {
    case 'ArrowLeft':
      e.preventDefault()
      navigateTimeline('prev')
      break
    case 'ArrowRight':
      e.preventDefault()
      navigateTimeline('next')
      break
    case 'Enter':
      e.preventDefault()
      // 可以添加选择当前活动的逻辑
      break
    case 'Escape':
      e.preventDefault()
      closeActivityDetail()
      break
  }
}

onMounted(async () => {
  document.addEventListener('keydown', handleKeyDown)
  await loadActivities()
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;

.star-calendar {
  padding: var(--spacing-3xl) 0;
  background: var(--base-dark);
  position: relative;
  min-height: 100vh;
  overflow: hidden;

  @include media-down(md) {
    padding: var(--spacing-2xl) 0;
  }
}

.calendar-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;

  .bg-constellation {
    position: absolute;
    width: 100%;
    height: 100%;

    .constellation-star {
      position: absolute;
      background: var(--secondary);
      border-radius: 50%;
      opacity: 0.6;
      animation: starTwinkle ease-in-out infinite;
    }
  }

  .bg-nebula {
    position: absolute;
    top: 20%;
    left: 10%;
    width: 80%;
    height: 60%;
    background: radial-gradient(
      ellipse at center,
      rgba(212, 222, 199, 0.1) 0%,
      rgba(170, 131, 255, 0.05) 40%,
      transparent 70%
    );
    border-radius: 50%;
    animation: nebulaFloat 20s ease-in-out infinite;
  }
}

.section-header {
  text-align: center;
  margin-bottom: var(--spacing-3xl);
  position: relative;
  z-index: 1;

  .section-title {
    font-size: var(--font-size-4xl);
    font-weight: var(--font-weight-bold);
    margin-bottom: var(--spacing-md);

    @include media-down(md) {
      font-size: var(--font-size-3xl);
    }

    .title-accent {
      background: var(--mixed-gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }

  .section-subtitle {
    font-size: var(--font-size-lg);
    color: var(--text-secondary);
    max-width: 600px;
    margin: 0 auto var(--spacing-xl);
  }
}

.calendar-stats {
  display: flex;
  justify-content: center;
  gap: var(--spacing-2xl);
  margin-top: var(--spacing-xl);

  @include media-down(sm) {
    gap: var(--spacing-lg);
  }

  .stat-item {
    text-align: center;
    padding: var(--spacing-md);
    @include glass-effect();
    border-radius: var(--radius-lg);
    min-width: 100px;
    transition: all var(--transition-base) var(--ease-hover);

    &:hover {
      transform: translateY(-4px);
      box-shadow: var(--shadow-green-glow);
    }

    .stat-number {
      display: block;
      font-size: var(--font-size-2xl);
      font-weight: var(--font-weight-bold);
      background: var(--secondary-gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      line-height: 1;
    }

    .stat-label {
      font-size: var(--font-size-sm);
      color: var(--text-secondary);
      margin-top: var(--spacing-xs);
    }
  }
}

.timeline-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-2xl);
  perspective: 1000px;
  position: relative;
  z-index: 1;

  @include media-down(md) {
    gap: var(--spacing-md);
  }
}

.timeline-track {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 2px;
  transform: translateY(-50%);
  z-index: -1;

  .track-line {
    width: 100%;
    height: 100%;
    background: linear-gradient(
      90deg,
      transparent 0%,
      var(--secondary) 20%,
      var(--primary) 50%,
      var(--secondary) 80%,
      transparent 100%
    );
    opacity: 0.6;
  }

  .track-glow {
    position: absolute;
    top: -2px;
    left: 0;
    right: 0;
    height: 6px;
    background: linear-gradient(
      90deg,
      transparent 0%,
      rgba(212, 222, 199, 0.3) 20%,
      rgba(170, 131, 255, 0.3) 50%,
      rgba(212, 222, 199, 0.3) 80%,
      transparent 100%
    );
    filter: blur(2px);
    animation: trackPulse 3s ease-in-out infinite;
  }
}

.nav-btn {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-full);
  // 使用自定义玻璃态效果，确保圆形
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: none; // 移除边框确保完美圆形
  color: var(--text-primary);
  transition: all var(--transition-base) var(--ease-hover);
  // 添加flex布局确保内容居中
  display: flex;
  align-items: center;
  justify-content: center;
  // 确保按钮保持圆形
  flex-shrink: 0;

  // SVG图标样式
  svg {
    width: 24px;
    height: 24px;
    transition: all var(--transition-base);
    flex-shrink: 0;
  }

  &:hover:not(:disabled) {
    @include magnetic-hover(4px);
    box-shadow: var(--shadow-glow);
  }

  &:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  @include media-down(sm) {
    width: 40px;
    height: 40px;
    // 确保移动端也保持圆形
    min-width: 40px;
    min-height: 40px;

    // 移动端调整SVG图标尺寸
    svg {
      width: 18px;
      height: 18px;
    }
  }
}

.timeline-stack {
  position: relative;
  width: 400px;
  height: 300px;
  transform-style: preserve-3d;

  @include media-down(md) {
    width: 320px;
    height: 280px;
  }

  @include media-down(sm) {
    width: 100%;
    max-width: 280px;
    height: 320px; // 增加高度以容纳更多内容
  }
}

.activity-card {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  @include glass-effect();
  border-radius: var(--radius-xl);
  padding: var(--spacing-lg);
  cursor: pointer;
  transition: all var(--transition-base) var(--ease-hover);
  transform-style: preserve-3d;
  overflow: hidden; // 防止内容溢出

  @include media-down(sm) {
    padding: var(--spacing-md); // 移动端减少内边距
  }

  &:hover {
    .card-glow {
      opacity: 1;
    }
  }

  &:focus-visible {
    outline: 3px solid var(--secondary);
    outline-offset: 2px;
  }

  &--active {
    z-index: 10;
  }
}

.card-content {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  z-index: 2;
}

.activity-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: var(--spacing-md);
  
  .date-day {
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-bold);
    color: var(--primary);
    line-height: 1;
  }
  
  .date-month {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
    margin-top: 2px;
  }
  
  .date-year {
    font-size: var(--font-size-xs);
    color: var(--text-muted);
  }
}

.activity-info {
  flex: 1;
  
  .activity-title {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    margin-bottom: var(--spacing-sm);
    color: var(--text-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;

    @include media-down(sm) {
      font-size: var(--font-size-md);
    }
  }
  
  .activity-description {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
    line-height: var(--line-height-relaxed);
    margin-bottom: var(--spacing-md);
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 3; // 限制最多显示3行
    -webkit-box-orient: vertical;

    @include media-down(sm) {
      -webkit-line-clamp: 2; // 移动端限制为2行
      font-size: var(--font-size-xs);
    }
  }
}

.activity-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);

  @include media-down(sm) {
    margin-bottom: var(--spacing-sm);
    gap: 4px; // 减少间距
  }

  .activity-tag {
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-full);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
    white-space: nowrap; // 防止标签文字换行

    @include media-down(sm) {
      padding: 2px var(--spacing-xs); // 减少内边距
      font-size: 10px; // 更小的字体
    }

    &--milestone { background: rgba(170, 131, 255, 0.2); color: var(--primary); }
    &--tech { background: rgba(63, 125, 251, 0.2); color: var(--accent-blue); }
    &--design { background: rgba(212, 222, 199, 0.2); color: var(--secondary); }
    &--music { background: rgba(255, 65, 80, 0.2); color: var(--error-alert); }
    &--outdoor { background: rgba(16, 185, 129, 0.2); color: #10B981; }
    &--default { background: rgba(255, 255, 255, 0.1); color: var(--text-secondary); }
  }
}

.activity-participants {
  margin-top: auto;

  @include media-down(sm) {
    margin-top: var(--spacing-sm); // 减少顶部间距
  }

  .participants-avatars {
    display: flex;
    align-items: center;
    margin-bottom: var(--spacing-xs);

    .participant-avatar {
      width: 24px;
      height: 24px;
      border-radius: var(--radius-full);
      border: 2px solid var(--base-dark);
      margin-left: -8px;

      @include media-down(sm) {
        width: 20px; // 移动端更小的头像
        height: 20px;
        margin-left: -6px;
      }

      &:first-child {
        margin-left: 0;
      }
    }

    .participants-more {
      width: 24px;
      height: 24px;
      border-radius: var(--radius-full);
      background: var(--glass-bg);
      border: 2px solid var(--base-dark);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: var(--font-size-xs);
      color: var(--text-secondary);
      margin-left: -8px;

      @include media-down(sm) {
        width: 20px;
        height: 20px;
        margin-left: -6px;
        font-size: 10px;
      }
    }
  }

  .participants-count {
    font-size: var(--font-size-xs);
    color: var(--text-muted);

    @include media-down(sm) {
      font-size: 10px;
    }
  }
}

.card-decoration {
  position: absolute;
  top: var(--spacing-md);
  right: var(--spacing-md);
  
  .decoration-line {
    width: 30px;
    height: 2px;
    background: var(--primary-gradient);
    margin-bottom: var(--spacing-xs);
  }
  
  .decoration-dots {
    display: flex;
    gap: 4px;
    
    .dot {
      width: 4px;
      height: 4px;
      border-radius: var(--radius-full);
      background: var(--secondary);
      opacity: 0.6;
    }
  }
}

.card-glow {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: var(--primary-gradient);
  border-radius: var(--radius-xl);
  opacity: 0;
  transition: opacity var(--transition-base);
  z-index: -1;
  filter: blur(8px);
}

.timeline-indicators {
  display: flex;
  justify-content: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-xl);
  
  .timeline-indicator {
    width: 12px;
    height: 12px;
    border-radius: var(--radius-full);
    background: transparent;
    border: 2px solid rgba(255, 255, 255, 0.3);
    transition: all var(--transition-base);
    
    &--active {
      border-color: var(--primary);
      
      .indicator-dot {
        background: var(--primary);
      }
    }
    
    &:hover {
      border-color: var(--secondary);
    }
    
    .indicator-dot {
      width: 4px;
      height: 4px;
      border-radius: var(--radius-full);
      background: transparent;
      transition: background var(--transition-base);
    }
  }
}

.keyboard-hints {
  display: flex;
  justify-content: center;
  gap: var(--spacing-lg);
  color: var(--text-muted);
  font-size: var(--font-size-xs);
  
  @include media-down(sm) {
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-sm);
  }
  
  .hint {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    
    kbd {
      padding: 2px 6px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: var(--radius-sm);
      font-size: var(--font-size-xs);
      font-family: var(--font-family-mono);
    }
  }
}

// 新增动画定义
@keyframes starTwinkle {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}

@keyframes nebulaFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(2deg); }
}

@keyframes trackPulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.8; }
}

// 加载状态样式
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-lg);
  color: var(--text-muted);

  .loading-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-top: 2px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
}

// 错误状态样式
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-lg);

  .error-message {
    color: var(--error-color, #ff6b6b);
    text-align: center;
  }

  .retry-btn {
    padding: var(--spacing-xs) var(--spacing-sm);
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: background var(--transition-base);

    &:hover {
      background: var(--primary-hover);
    }
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
