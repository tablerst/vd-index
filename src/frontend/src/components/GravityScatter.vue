<template>
  <section id="members" class="gravity-scatter">
    <div class="container">
      <!-- 标题区域 -->
      <div class="section-header">
        <h2 class="section-title">
          <span class="title-accent">成员</span>星云
        </h2>
        <p class="section-subtitle">
          探索VRC Division中的每一颗闪亮星球
        </p>
      </div>

      <!-- 3D 点云容器 -->
      <div class="scatter-container" ref="scatterContainer">
        <canvas ref="scatterCanvas" class="scatter-canvas"></canvas>
        
        <!-- 加载状态 -->
        <div v-if="isLoading" class="scatter-loading">
          <div class="loading-spinner"></div>
          <p class="loading-text">正在加载成员星云...</p>
        </div>
        
        <!-- 降级方案 -->
        <div v-if="!webglSupported" class="scatter-fallback">
          <div class="fallback-grid">
            <div 
              v-for="member in visibleMembers" 
              :key="member.id"
              class="member-card"
              @click="selectMember(member)"
              @keydown.enter="selectMember(member)"
              @keydown.escape="closeMemberInfo"
              tabindex="0"
              :aria-label="`${member.name} 的星球`"
              role="button"
            >
              <div class="member-avatar">
                <img :src="member.avatarURL" :alt="member.name" loading="lazy">
              </div>
              <div class="member-name">{{ member.name }}</div>
            </div>
          </div>
        </div>

        <!-- 成员信息卡片 -->
        <div 
          v-if="selectedMember" 
          class="member-info-card"
          :class="{ 'member-info-card--visible': showMemberInfo }"
          @click.stop
        >
          <button 
            class="close-btn"
            @click="closeMemberInfo"
            aria-label="关闭成员信息"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
          
          <div class="member-avatar-large">
            <img :src="selectedMember.avatarURL" :alt="selectedMember.name">
          </div>
          
          <h3 class="member-name-large">{{ selectedMember.name }}</h3>
          
          <div class="member-details">
            <p class="member-bio">{{ selectedMember.bio || '这个成员还没有添加个人简介' }}</p>
            <div class="member-stats">
              <div class="stat-item">
                <span class="stat-label">加入时间</span>
                <span class="stat-value">{{ formatJoinDate(selectedMember.joinDate) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">贡献度</span>
                <span class="stat-value">{{ selectedMember.contribution || 0 }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 控制面板 -->
        <div class="scatter-controls">
          <button 
            class="control-btn"
            @click="toggleAnimation"
            :aria-label="isAnimating ? '暂停动画' : '开始动画'"
          >
            <svg v-if="isAnimating" width="20" height="20" viewBox="0 0 20 20" fill="none">
              <rect x="6" y="4" width="2" height="12" fill="currentColor"/>
              <rect x="12" y="4" width="2" height="12" fill="currentColor"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M8 5L15 10L8 15V5Z" fill="currentColor"/>
            </svg>
          </button>
          
          <button 
            class="control-btn"
            @click="resetView"
            aria-label="重置视角"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 4L16 16M16 4L4 16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- 分页信息 -->
      <div class="pagination-info">
        <p class="members-count">
          已显示 {{ visibleMembers.length }} / {{ totalMembers }} 位成员
        </p>
        <div v-if="hasMoreMembers" class="load-more">
          <button 
            class="load-more-btn interactive"
            @click="loadMoreMembers"
            :disabled="isLoadingMore"
          >
            <span v-if="!isLoadingMore">加载更多成员</span>
            <span v-else>加载中...</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 滚动哨兵 -->
    <div ref="scrollSentinel" class="scroll-sentinel"></div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { initGravityScatter, disposeGravityScatter, addMembersToScatter } from '../utils/gravityScatter3d'
import { useMembersStore } from '../stores/members'

interface Member {
  id: number
  name: string
  avatarURL: string
  bio?: string
  joinDate?: string
  contribution?: number
}

const membersStore = useMembersStore()

const scatterContainer = ref<HTMLElement>()
const scatterCanvas = ref<HTMLCanvasElement>()
const scrollSentinel = ref<HTMLElement>()

const isLoading = ref(true)
const isLoadingMore = ref(false)
const webglSupported = ref(true)
const isAnimating = ref(true)
const selectedMember = ref<Member | null>(null)
const showMemberInfo = ref(false)

// 计算属性
const visibleMembers = computed(() => membersStore.visibleMembers)
const totalMembers = computed(() => membersStore.totalMembers)
const hasMoreMembers = computed(() => membersStore.hasMoreMembers)

// 检测 WebGL 支持
const checkWebGLSupport = (): boolean => {
  try {
    const canvas = document.createElement('canvas')
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl')
    return !!gl
  } catch (e) {
    return false
  }
}

// 初始化 3D 点云
const initializeScatter = async () => {
  if (!webglSupported.value || !scatterCanvas.value) {
    isLoading.value = false
    return
  }

  try {
    await initGravityScatter(scatterCanvas.value, {
      onMemberHover: handleMemberHover,
      onMemberClick: handleMemberClick,
      onMemberLeave: handleMemberLeave
    })
    
    // 加载初始成员数据
    await loadInitialMembers()
    isLoading.value = false
  } catch (error) {
    console.warn('Failed to initialize 3D scatter, falling back to grid view:', error)
    webglSupported.value = false
    isLoading.value = false
  }
}

// 加载初始成员
const loadInitialMembers = async () => {
  await membersStore.loadMembers()
  if (webglSupported.value && visibleMembers.value.length > 0) {
    addMembersToScatter(visibleMembers.value)
  }
}

// 加载更多成员
const loadMoreMembers = async () => {
  if (isLoadingMore.value || !hasMoreMembers.value) return
  
  isLoadingMore.value = true
  const newMembers = await membersStore.loadMoreMembers()
  
  if (webglSupported.value && newMembers.length > 0) {
    addMembersToScatter(newMembers)
  }
  
  isLoadingMore.value = false
}

// 成员交互处理
const handleMemberHover = (_member: Member) => {
  // 可以在这里添加悬停效果
}

const handleMemberClick = (member: Member) => {
  selectMember(member)
}

const handleMemberLeave = () => {
  // 可以在这里添加离开效果
}

// 选择成员
const selectMember = (member: Member) => {
  selectedMember.value = member
  showMemberInfo.value = true
}

// 关闭成员信息
const closeMemberInfo = () => {
  showMemberInfo.value = false
  setTimeout(() => {
    selectedMember.value = null
  }, 300)
}

// 切换动画
const toggleAnimation = () => {
  isAnimating.value = !isAnimating.value
  // 这里可以调用 3D 场景的动画控制函数
}

// 重置视角
const resetView = () => {
  // 这里可以调用 3D 场景的视角重置函数
}

// 格式化加入日期
const formatJoinDate = (dateString?: string): string => {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 设置 Intersection Observer 监听滚动
const setupIntersectionObserver = () => {
  if (!scrollSentinel.value) return
  
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && hasMoreMembers.value && !isLoadingMore.value) {
          // 使用 requestIdleCallback 在空闲时加载
          if ('requestIdleCallback' in window) {
            requestIdleCallback(() => loadMoreMembers())
          } else {
            setTimeout(() => loadMoreMembers(), 100)
          }
        }
      })
    },
    { threshold: 0.1 }
  )
  
  observer.observe(scrollSentinel.value)
  
  return observer
}

onMounted(() => {
  webglSupported.value = checkWebGLSupport()
  
  // 延迟初始化以确保 DOM 完全加载
  setTimeout(() => {
    initializeScatter()
  }, 100)
  
  // 设置滚动监听
  const observer = setupIntersectionObserver()
  
  // 键盘导航支持
  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && showMemberInfo.value) {
      closeMemberInfo()
    }
  }
  
  document.addEventListener('keydown', handleKeyDown)
  
  // 清理函数
  onUnmounted(() => {
    if (webglSupported.value) {
      disposeGravityScatter()
    }
    observer?.disconnect()
    document.removeEventListener('keydown', handleKeyDown)
  })
})
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;

.gravity-scatter {
  padding: var(--spacing-3xl) 0;
  position: relative;
  background: var(--base-dark);
  
  @include media-down(md) {
    padding: var(--spacing-2xl) 0;
  }
}

.section-header {
  text-align: center;
  margin-bottom: var(--spacing-3xl);
  
  .section-title {
    font-size: var(--font-size-4xl);
    font-weight: var(--font-weight-bold);
    margin-bottom: var(--spacing-md);
    
    @include media-down(md) {
      font-size: var(--font-size-3xl);
    }
    
    .title-accent {
      background: var(--primary-gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }
  
  .section-subtitle {
    font-size: var(--font-size-lg);
    color: var(--text-secondary);
    max-width: 600px;
    margin: 0 auto;
  }
}

.scatter-container {
  position: relative;
  width: 100%;
  height: 600px;
  border-radius: var(--radius-xl);
  overflow: hidden;
  @include glass-effect();
  
  @include media-down(md) {
    height: 400px;
  }
}

.scatter-canvas {
  width: 100%;
  height: 100%;
}

.scatter-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: var(--text-secondary);
  
  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(170, 131, 255, 0.3);
    border-top: 3px solid var(--primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto var(--spacing-md);
  }
}

.scatter-fallback {
  width: 100%;
  height: 100%;
  padding: var(--spacing-lg);
  overflow-y: auto;
  
  .fallback-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: var(--spacing-md);
    
    @include media-down(sm) {
      grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    }
  }
}

.member-card {
  @include glass-effect();
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
  text-align: center;
  transition: all var(--transition-base) var(--ease-hover);
  cursor: pointer;
  
  &:hover {
    transform: translateY(-4px) scale(1.05);
    box-shadow: var(--shadow-glow);
  }
  
  &:focus-visible {
    outline: 3px solid var(--secondary);
    outline-offset: 2px;
  }
  
  .member-avatar {
    width: 60px;
    height: 60px;
    border-radius: var(--radius-full);
    overflow: hidden;
    margin: 0 auto var(--spacing-sm);
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
  
  .member-name {
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
  }
}

.member-info-card {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0.9);
  width: 320px;
  max-width: 90vw;
  @include glass-effect();
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl);
  text-align: center;
  opacity: 0;
  visibility: hidden;
  transition: all var(--transition-base) var(--ease-out-expo);
  z-index: 10;
  
  &--visible {
    opacity: 1;
    visibility: visible;
    transform: translate(-50%, -50%) scale(1);
  }
  
  .close-btn {
    position: absolute;
    top: var(--spacing-md);
    right: var(--spacing-md);
    width: 32px;
    height: 32px;
    border-radius: var(--radius-full);
    @include glass-effect();
    color: var(--text-secondary);
    transition: all var(--transition-base);
    
    &:hover {
      color: var(--text-primary);
      background: rgba(255, 255, 255, 0.15);
    }
  }
  
  .member-avatar-large {
    width: 80px;
    height: 80px;
    border-radius: var(--radius-full);
    overflow: hidden;
    margin: 0 auto var(--spacing-md);
    border: 3px solid var(--primary);
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
  
  .member-name-large {
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
    margin-bottom: var(--spacing-md);
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .member-details {
    text-align: left;
    
    .member-bio {
      color: var(--text-secondary);
      margin-bottom: var(--spacing-md);
      line-height: var(--line-height-relaxed);
    }
    
    .member-stats {
      display: grid;
      gap: var(--spacing-sm);
      
      .stat-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        .stat-label {
          color: var(--text-muted);
          font-size: var(--font-size-sm);
        }
        
        .stat-value {
          color: var(--text-primary);
          font-weight: var(--font-weight-medium);
        }
      }
    }
  }
}

.scatter-controls {
  position: absolute;
  bottom: var(--spacing-md);
  right: var(--spacing-md);
  display: flex;
  gap: var(--spacing-sm);
  
  .control-btn {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-full);
    @include glass-effect();
    color: var(--text-primary);
    transition: all var(--transition-base);
    
    &:hover {
      @include magnetic-hover(4px);
      box-shadow: var(--shadow-glow);
    }
  }
}

.pagination-info {
  margin-top: var(--spacing-xl);
  text-align: center;
  
  .members-count {
    color: var(--text-secondary);
    margin-bottom: var(--spacing-md);
  }
  
  .load-more-btn {
    @include glass-effect();
    padding: var(--spacing-md) var(--spacing-xl);
    border-radius: var(--radius-lg);
    color: var(--text-primary);
    font-weight: var(--font-weight-medium);
    transition: all var(--transition-base);
    
    &:hover:not(:disabled) {
      @include magnetic-hover(4px);
      box-shadow: var(--shadow-green-glow);
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
}

.scroll-sentinel {
  height: 1px;
  margin-top: var(--spacing-lg);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
