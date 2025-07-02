<template>
  <section id="members" class="members-galaxy" ref="sectionRef">
    <!-- 深空背景 -->
    <DeepSpaceBackground />

    <!-- 交互式信息控件 -->
    <GalaxyInfoWidget
      :total-members="totalMembers"
      :total-pages="totalPages"
      v-model:search-query="searchQuery"
    />

    <!-- 进度条 -->
    <ProgressBar
      :current="currentSlide + 1"
      :total="totalPages"
      :visible="sectionVisible"
    />

    <!-- 分页箭头 -->
    <PaginationArrows
      :current-page="currentSlide + 1"
      :total-pages="totalPages"
      @prev-page="goToPrevPage"
      @next-page="goToNextPage"
    />

    <!-- Swiper 横向滑动容器 -->
    <div class="galaxy-container">
      <swiper
        :modules="[Navigation, Mousewheel]"
        :slides-per-view="1"
        :space-between="0"
        :mousewheel="{ forceToAxis: true, sensitivity: 0.5 }"
        :keyboard="{ enabled: true }"
        :speed="900"
        :effect="'slide'"
        :grab-cursor="true"
        @slide-change="onSlideChange"
        @swiper="onSwiperInit"
        class="galaxy-swiper"
      >
        <swiper-slide
          v-for="(pageMembers, pageIndex) in paginatedMembers"
          :key="pageIndex"
          class="galaxy-slide-container"
        >
          <GalaxySlide
            :members="pageMembers"
            :index="pageIndex"
            @member-select="handleMemberSelect"
            @member-hover="handleMemberHover"
            @member-leave="handleMemberLeave"
          />
        </swiper-slide>
      </swiper>
    </div>

    <!-- 成员详情弹窗 -->
    <div
      v-if="showMemberInfo && selectedMember"
      class="member-modal"
      @click.self="closeMemberInfo"
      role="dialog"
      aria-modal="true"
      :aria-labelledby="`member-${selectedMember.id}-title`"
    >
      <div class="modal-content" ref="modalContent">
        <!-- Three.js 星粒子背景 -->
        <MemberStarfield />

        <!-- 关闭按钮 -->
        <button
          class="modal-close"
          @click="closeMemberInfo"
          aria-label="关闭成员信息"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>

        <!-- 头像 -->
        <div class="profile-avatar">
          <img :src="selectedMember.avatarURL" :alt="selectedMember.groupNick || selectedMember.qqNick || selectedMember.name">
        </div>

        <!-- 名称区 -->
        <h3 :id="`member-${selectedMember.id}-title`" class="profile-name">
          {{ selectedMember.groupNick || selectedMember.qqNick || selectedMember.name }}
        </h3>
        <p class="profile-subname" v-if="selectedMember.qqNick && selectedMember.groupNick">
          QQ：{{ selectedMember.qqNick }}
        </p>

        <!-- 角色徽章 -->
        <div class="profile-role" v-if="selectedMember.role !== undefined">
          <span class="role-badge" :class="`role-${selectedMember.role}`">
            {{ getRoleText(selectedMember.role) }}
          </span>
        </div>

        <!-- 入群时间 -->
        <div class="join-date" v-if="selectedMember.joinDate">
          <CalendarIcon class="cal-icon" />
          <span>{{ formatDate(selectedMember.joinDate) }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Navigation, Mousewheel } from 'swiper/modules'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useMembersStore } from '../stores/members'
import { useDeviceDetection } from '../composables/useDeviceDetection'
// import { usePerformanceMonitor } from '../composables/usePerformanceMonitor' // 暂时注释
import ProgressBar from './ProgressBar.vue'
import GalaxySlide from './GalaxySlide.vue'
import GalaxyInfoWidget from './GalaxyInfoWidget.vue'
import DeepSpaceBackground from './DeepSpaceBackground.vue'
import PaginationArrows from './PaginationArrows.vue'
import MemberStarfield from './MemberStarfield.vue'
import CalendarIcon from './icons/CalendarIcon.vue'

// 注册GSAP插件
gsap.registerPlugin(ScrollTrigger)

// Swiper 样式在 main.scss 中导入

interface Member {
  id: number
  name: string
  avatarURL: string
  bio?: string
  joinDate?: string
  contribution?: number
  role?: number
  groupNick?: string
  qqNick?: string
}

const membersStore = useMembersStore()
const { responsiveConfig } = useDeviceDetection()
// const { metrics: performanceMetrics } = usePerformanceMonitor(45) // 暂时注释未使用的性能监控

const sectionRef = ref<HTMLElement>()
const modalContent = ref<HTMLDivElement>()
const swiperRef = ref()
const selectedMember = ref<Member | null>(null)
const showMemberInfo = ref(false)
const currentSlide = ref(0)
const sectionVisible = ref(false)
const searchQuery = ref('')
const isTransitioning = ref(false)

// 响应式成员数量配置
const membersPerPage = computed(() => responsiveConfig.value.membersPerPage)

// 计算属性
const totalMembers = computed(() => membersStore.totalMembers)
const allMembers = computed(() => membersStore.visibleMembers)

// 过滤成员（基于搜索）
const filteredMembers = computed(() => {
  if (!searchQuery.value.trim()) {
    return allMembers.value
  }
  return allMembers.value.filter(member =>
    member.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

// 分页成员
const paginatedMembers = computed(() => {
  const members = filteredMembers.value
  const pages = []
  const perPage = membersPerPage.value
  for (let i = 0; i < members.length; i += perPage) {
    pages.push(members.slice(i, i + perPage))
  }
  return pages
})

const totalPages = computed(() => paginatedMembers.value.length)

// Swiper 事件处理
const onSwiperInit = (swiper: any) => {
  swiperRef.value = swiper
}

const onSlideChange = (swiper: any) => {
  const previousSlide = currentSlide.value
  currentSlide.value = swiper.activeIndex

  // GSAP切屏动效
  animateSlideTransition(previousSlide, currentSlide.value)
}

// 分页控制方法
const goToPrevPage = () => {
  if (swiperRef.value && currentSlide.value > 0) {
    swiperRef.value.slidePrev()
  }
}

const goToNextPage = () => {
  if (swiperRef.value && currentSlide.value < totalPages.value - 1) {
    swiperRef.value.slideNext()
  }
}

// GSAP切屏动画
const animateSlideTransition = (fromIndex: number, toIndex: number) => {
  if (isTransitioning.value) return

  isTransitioning.value = true

  const slides = document.querySelectorAll('.galaxy-slide-container')
  const currentSlideEl = slides[toIndex]
  const previousSlideEl = slides[fromIndex]

  if (!currentSlideEl) {
    isTransitioning.value = false
    return
  }

  // 获取当前滑动页面的成员星球
  const currentStars = currentSlideEl.querySelectorAll('.member-star')

  // 创建时间线
  const tl = gsap.timeline({
    onComplete: () => {
      isTransitioning.value = false
    }
  })

  // 如果有前一个滑动页面，添加退出动画
  if (previousSlideEl) {
    const previousStars = previousSlideEl.querySelectorAll('.member-star')

    tl.to(previousStars, {
      scale: 0.8,
      opacity: 0.3,
      rotationY: toIndex > fromIndex ? -45 : 45,
      duration: 0.4,
      ease: "power2.out",
      stagger: {
        amount: 0.2,
        from: "random"
      }
    }, 0)
  }

  // 当前滑动页面的进入动画
  gsap.set(currentStars, {
    scale: 0.6,
    opacity: 0,
    rotationY: toIndex > fromIndex ? 45 : -45,
    z: -100
  })

  tl.to(currentStars, {
    scale: 1,
    opacity: 1,
    rotationY: 0,
    z: 0,
    duration: 0.6,
    ease: "power4.out",
    stagger: {
      amount: 0.3,
      from: "center"
    }
  }, 0.2)

  // 添加视差效果
  tl.fromTo(currentSlideEl,
    {
      filter: "blur(5px)",
      scale: 1.05
    },
    {
      filter: "blur(0px)",
      scale: 1,
      duration: 0.8,
      ease: "power3.out"
    }, 0.1)
}

// 成员交互处理
const handleMemberSelect = (member: Member) => {
  selectedMember.value = member
  showMemberInfo.value = true

  // 使用GSAP实现高性能打开动画
  nextTick(() => {
    openMemberModal()
  })
}

// 弹窗打开动画
const openMemberModal = () => {
  if (!modalContent.value) return

  const tl = gsap.timeline()

  // 遮罩淡入
  tl.fromTo('.member-modal',
    { opacity: 0 },
    { opacity: 1, duration: 0.25, ease: 'power2.out' }
  )

  // 内容缩放和位移动画
  tl.fromTo(modalContent.value,
    {
      scale: 0.8,
      y: 40,
      opacity: 0,
      rotationY: -15
    },
    {
      scale: 1,
      y: 0,
      opacity: 1,
      rotationY: 0,
      duration: 0.45,
      ease: 'power3.out'
    },
    0.1 // 稍微延迟开始
  )

  // 星粒子背景淡入
  tl.fromTo('.starfield-canvas',
    { opacity: 0 },
    { opacity: 0.8, duration: 0.3, ease: 'power2.out' },
    0.2
  )
}

const handleMemberHover = (_member: Member, _event: MouseEvent) => {
  // 处理悬停逻辑
}

const handleMemberLeave = () => {
  // 处理离开逻辑
}

const closeMemberInfo = () => {
  if (!modalContent.value) {
    showMemberInfo.value = false
    selectedMember.value = null
    return
  }

  // 使用GSAP实现关闭动画
  const tl = gsap.timeline({
    onComplete: () => {
      showMemberInfo.value = false
      selectedMember.value = null
    }
  })

  // 内容缩放和淡出
  tl.to(modalContent.value, {
    scale: 0.9,
    y: 20,
    opacity: 0,
    rotationY: 15,
    duration: 0.3,
    ease: 'power2.in'
  })

  // 遮罩淡出
  tl.to('.member-modal', {
    opacity: 0,
    duration: 0.2,
    ease: 'power2.in'
  }, 0.1)
}

const formatDate = (dateString?: string) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 获取群权限显示文本
const getRoleText = (role?: number): string => {
  if (role === undefined) return ''
  switch (role) {
    case 0: return '群主'
    case 1: return '管理员'
    case 2: return '群员'
    default: return '未知'
  }
}

// 获取简化的个人简介函数已移除，因为当前未使用
// 如果将来需要，可以从 git 历史中恢复

// 滚动监听和ScrollTrigger设置
const setupSectionObserver = () => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        sectionVisible.value = entry.isIntersecting
      })
    },
    { threshold: 0.1 }
  )

  if (sectionRef.value) {
    observer.observe(sectionRef.value)
  }

  return observer
}

// 设置ScrollTrigger视差效果
const setupScrollTrigger = () => {
  if (!sectionRef.value) return

  // 整个section的进入动画
  gsap.fromTo(sectionRef.value,
    {
      opacity: 0,
      y: 100,
      scale: 0.95
    },
    {
      opacity: 1,
      y: 0,
      scale: 1,
      duration: 1.2,
      ease: "power3.out",
      scrollTrigger: {
        trigger: sectionRef.value,
        start: "top 80%",
        end: "top 20%",
        toggleActions: "play none none reverse"
      }
    }
  )

  // 信息区域的视差效果
  const galaxyInfo = sectionRef.value.querySelector('.galaxy-info')
  if (galaxyInfo) {
    gsap.fromTo(galaxyInfo,
      {
        x: -100,
        opacity: 0
      },
      {
        x: 0,
        opacity: 1,
        duration: 0.8,
        ease: "power2.out",
        scrollTrigger: {
          trigger: sectionRef.value,
          start: "top 70%",
          end: "top 30%",
          toggleActions: "play none none reverse"
        }
      }
    )
  }

  // 进度条的视差效果
  const progressBar = document.querySelector('.progress-bar')
  if (progressBar) {
    gsap.fromTo(progressBar,
      {
        y: -50,
        opacity: 0
      },
      {
        y: 0,
        opacity: 1,
        duration: 0.6,
        ease: "power2.out",
        scrollTrigger: {
          trigger: sectionRef.value,
          start: "top 60%",
          end: "top 40%",
          toggleActions: "play none none reverse"
        }
      }
    )
  }

  // 成员星球的交错动画
  const memberStars = sectionRef.value.querySelectorAll('.member-star')
  if (memberStars.length > 0) {
    gsap.fromTo(memberStars,
      {
        scale: 0,
        opacity: 0,
        rotationY: 180
      },
      {
        scale: 1,
        opacity: 1,
        rotationY: 0,
        duration: 0.8,
        ease: "back.out(1.7)",
        stagger: {
          amount: 1.5,
          from: "random"
        },
        scrollTrigger: {
          trigger: sectionRef.value,
          start: "top 50%",
          end: "top 10%",
          toggleActions: "play none none reverse"
        }
      }
    )
  }
}

// 键盘导航支持
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && showMemberInfo.value) {
    closeMemberInfo()
  }
}

// 存储需要清理的资源
let observer: IntersectionObserver | null = null
let handlePerformanceLow: ((event: CustomEvent) => void) | null = null

onMounted(async () => {
  // 加载初始成员数据
  try {
    await membersStore.loadMembers()
  } catch (error) {
    console.error('Failed to load initial members:', error)
  }

  // 设置滚动监听
  observer = setupSectionObserver()

  // 等待DOM更新后设置ScrollTrigger
  await nextTick()
  setTimeout(() => {
    setupScrollTrigger()
  }, 100)

  document.addEventListener('keydown', handleKeyDown)

  // 性能优化事件监听
  handlePerformanceLow = (event: CustomEvent) => {
    console.warn('Performance is low:', event.detail)
    // 可以在这里实现自动优化逻辑
    // 例如：减少粒子数量、降低动画复杂度等
  }

  window.addEventListener('performance-low', handlePerformanceLow as EventListener)
})

// 组件卸载时的清理函数
onUnmounted(() => {
  observer?.disconnect()
  document.removeEventListener('keydown', handleKeyDown)
  if (handlePerformanceLow) {
    window.removeEventListener('performance-low', handlePerformanceLow as EventListener)
  }
  ScrollTrigger.killAll() // 清理所有ScrollTrigger
})
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;

.members-galaxy {
  position: relative;
  min-height: 100vh;
  background: var(--base-dark);
  overflow: hidden;
}

.galaxy-info {
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 100;
  max-width: 300px;
  padding: 20px;
  background: rgba(14, 16, 22, 0.9);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(170, 131, 255, 0.2);
  border-radius: 16px;
  opacity: 0;
  transform: translateX(-20px);
  transition: all var(--transition-base) var(--ease-hover);

  &--visible {
    opacity: 1;
    transform: translateX(0);
  }

  @include media-down(md) {
    top: 10px;
    left: 10px;
    max-width: 250px;
    padding: 16px;
  }
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;

  @include media-down(md) {
    font-size: 20px;
  }
}

.title-accent {
  color: var(--secondary);
}

.section-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 16px;
  line-height: 1.4;
}

.member-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 12px;
  background: rgba(170, 131, 255, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(170, 131, 255, 0.2);
}

.stat-number {
  font-size: 18px;
  font-weight: 600;
  color: var(--secondary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

.search-controls {
  margin-top: 16px;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  background: rgba(170, 131, 255, 0.1);
  border: 1px solid rgba(170, 131, 255, 0.3);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  transition: all var(--transition-base);

  &::placeholder {
    color: var(--text-tertiary);
  }

  &:focus {
    outline: none;
    border-color: var(--secondary);
    box-shadow: 0 0 0 2px rgba(170, 131, 255, 0.2);
  }
}

.galaxy-container {
  position: relative;
  width: 100%;
  height: 100vh;
}

.galaxy-swiper {
  width: 100%;
  height: 100%;
}

.galaxy-slide-container {
  width: 100%;
  height: 100%;
}

// 成员详情弹窗样式
.member-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0; // 初始透明，由GSAP控制
}

.modal-content {
  position: relative;
  max-width: 420px;
  width: 90%;
  background: linear-gradient(135deg,
    rgba(170, 131, 255, 0.15) 0%,
    rgba(212, 222, 199, 0.1) 50%,
    rgba(63, 125, 251, 0.15) 100%
  );
  backdrop-filter: blur(25px);
  border: 1px solid rgba(170, 131, 255, 0.3);
  border-radius: 20px;
  padding: 32px 28px;
  box-shadow:
    0 20px 40px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset,
    0 0 30px rgba(170, 131, 255, 0.2);
  text-align: center;
  overflow: hidden;

  // 初始状态，由GSAP控制
  opacity: 0;
  transform: scale(0.8) translateY(40px) rotateY(-15deg);
}

.modal-close {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.3s var(--ease-hover);
  backdrop-filter: blur(10px);

  &:hover {
    color: var(--text-primary);
    background: rgba(170, 131, 255, 0.2);
    border-color: rgba(170, 131, 255, 0.4);
    transform: scale(1.05);
  }
}

.profile-avatar {
  width: 72px;
  height: 72px;
  margin: 0 auto 20px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid rgba(170, 131, 255, 0.4);
  box-shadow:
    0 8px 20px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  position: relative;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s var(--ease-hover);
  }

  &:hover img {
    transform: scale(1.05);
  }
}

.profile-name {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.profile-subname {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 16px;
  opacity: 0.8;
}

.profile-role {
  margin-bottom: 20px;
  text-align: center;
}

.join-date {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  font-size: 14px;
  color: var(--text-primary);
  backdrop-filter: blur(10px);
  transition: all 0.3s var(--ease-hover);

  &:hover {
    background: rgba(170, 131, 255, 0.15);
    border-color: rgba(170, 131, 255, 0.3);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(170, 131, 255, 0.2);
  }

  .cal-icon {
    transition: transform 0.4s var(--ease-hover);
    color: var(--primary);
  }

  &:hover .cal-icon {
    transform: rotateY(180deg) scale(1.1);
  }
}

.role-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.role-badge.role-0 {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: #000;
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
}

.role-badge.role-1 {
  background: linear-gradient(135deg, #4CAF50, #66BB6A);
  color: #fff;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.role-badge.role-2 {
  background: linear-gradient(135deg, #4169E1, #1E90FF);
  color: #fff;
  box-shadow: 0 2px 8px rgba(65, 105, 225, 0.3);
}

// 响应式设计
@media (max-width: 768px) {
  .modal-content {
    max-width: 350px;
    padding: 24px 20px;
  }

  .profile-avatar {
    width: 64px;
    height: 64px;
  }

  .profile-name {
    font-size: 20px;
  }

  .join-date {
    padding: 10px 14px;
    font-size: 13px;
  }
}
</style>