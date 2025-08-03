<template>
  <nav class="glass-navigation" :class="{ 'glass-navigation--scrolled': isScrolled }">
    <div class="container">
      <div class="nav-content">
        <!-- LOGO -->
        <div class="nav-logo">
          <a href="#" class="logo-link" aria-label="VRC Division 首页">
            <div class="logo-icon">
              <img src="/VD_LOGO.png" alt="VRC Division Logo" width="32" height="32" />
            </div>
            <span class="logo-text">VRC Division</span>
          </a>
        </div>

        <!-- 主导航 -->
        <div class="nav-menu" :class="{ 'nav-menu--open': isMobileMenuOpen }">
          <ul class="nav-list">
            <li class="nav-item">
              <a href="#hero" class="nav-link" @click="scrollToSection('hero')">
                首页
              </a>
            </li>
            <li class="nav-item">
              <a href="#members" class="nav-link" @click="scrollToSection('members')">
                成员
              </a>
            </li>
            <li class="nav-item">
              <a href="#activities" class="nav-link" @click="scrollToSection('activities')">
                活动
              </a>
            </li>
            <li class="nav-item">
              <a href="/badge-preview" target="_blank" class="nav-link" rel="noopener noreferrer">
                徽章预览
              </a>
            </li>
            <li class="nav-item">
              <a href="#about" class="nav-link" @click="scrollToSection('about')">
                关于
              </a>
            </li>
          </ul>
        </div>

        <!-- 右侧操作区 -->
        <div class="nav-actions">
          <!-- 语言切换 -->
          <div class="language-switcher">
            <button
              class="language-btn interactive"
              @click="toggleLanguage"
              :aria-label="`切换到${currentLanguage === 'zh' ? 'English' : '中文'}`"
            >
              <span class="language-text">{{ currentLanguage === 'zh' ? '中' : 'EN' }}</span>
              <div class="language-indicator"></div>
            </button>
          </div>

          <!-- 主题切换 -->
          <div class="theme-switcher">
            <n-switch
              :value="isDarkTheme"
              @update:value="handleThemeChange"
              size="medium"
              :rail-style="railStyle"
              :checked-value="true"
              :unchecked-value="false"
            >
              <template #checked>
                <n-icon size="14" color="#FFFFFF">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 3a6 6 0 0 0 9 5.2A9 9 0 1 1 8.8 3A6 6 0 0 0 12 3Z"/>
                  </svg>
                </n-icon>
              </template>
              <template #unchecked>
                <n-icon size="14" color="#FFD700">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2.25a.75.75 0 0 1 .75.75v2.25a.75.75 0 0 1-1.5 0V3a.75.75 0 0 1 .75-.75ZM7.5 12a4.5 4.5 0 1 1 9 0 4.5 4.5 0 0 1-9 0ZM18.894 6.166a.75.75 0 0 0-1.06-1.06l-1.591 1.59a.75.75 0 1 0 1.06 1.061l1.591-1.59ZM21.75 12a.75.75 0 0 1-.75.75h-2.25a.75.75 0 0 1 0-1.5H21a.75.75 0 0 1 .75.75ZM17.834 18.894a.75.75 0 0 0 1.06-1.06l-1.59-1.591a.75.75 0 1 0-1.061 1.06l1.59 1.591ZM12 18a.75.75 0 0 1 .75.75V21a.75.75 0 0 1-1.5 0v-2.25A.75.75 0 0 1 12 18ZM7.758 17.303a.75.75 0 0 0-1.061-1.06l-1.591 1.59a.75.75 0 0 0 1.06 1.061l1.591-1.59ZM6 12a.75.75 0 0 1-.75.75H3a.75.75 0 0 1 0-1.5h2.25A.75.75 0 0 1 6 12ZM6.697 7.757a.75.75 0 0 0 1.06-1.06l-1.59-1.591a.75.75 0 0 0-1.061 1.06l1.59 1.591Z"/>
                  </svg>
                </n-icon>
              </template>
            </n-switch>
          </div>

          <!-- 移动端菜单按钮 -->
          <button 
            class="mobile-menu-btn interactive"
            @click="toggleMobileMenu"
            :aria-label="isMobileMenuOpen ? '关闭菜单' : '打开菜单'"
            :aria-expanded="isMobileMenuOpen"
          >
            <span class="hamburger-line" :class="{ 'hamburger-line--active': isMobileMenuOpen }"></span>
            <span class="hamburger-line" :class="{ 'hamburger-line--active': isMobileMenuOpen }"></span>
            <span class="hamburger-line" :class="{ 'hamburger-line--active': isMobileMenuOpen }"></span>
          </button>
        </div>
      </div>
    </div>

    <!-- 移动端菜单遮罩 -->
    <div 
      class="mobile-overlay" 
      :class="{ 'mobile-overlay--active': isMobileMenuOpen }"
      @click="closeMobileMenu"
    ></div>
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { NSwitch, NIcon } from 'naive-ui'
import { useThemeStore } from '@/stores/theme'

const isScrolled = ref(false)
const isMobileMenuOpen = ref(false)
const currentLanguage = ref<'zh' | 'en'>('zh')

// 主题store
const themeStore = useThemeStore()

// 主题状态，使用computed确保响应式
const isDarkTheme = computed(() => themeStore.isDark)

// 滚动监听
const handleScroll = () => {
  isScrolled.value = window.scrollY > 50
}

// 切换语言
const toggleLanguage = () => {
  currentLanguage.value = currentLanguage.value === 'zh' ? 'en' : 'zh'
  // 这里可以添加实际的语言切换逻辑
}

// 主题切换处理
const handleThemeChange = (value: boolean) => {
  console.log('Theme switch clicked, new value:', value)
  themeStore.toggleTheme()
}

// Switch组件的轨道样式
const railStyle = ({ focused, checked }: { focused: boolean; checked: boolean }) => {
  const style: Record<string, string> = {}
  if (checked) {
    style.background = 'linear-gradient(135deg, #AA83FF 0%, #8F6BFF 100%)'
    style.boxShadow = '0 0 8px rgba(170, 131, 255, 0.3)'
  } else {
    style.background = 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)'
    style.boxShadow = '0 0 8px rgba(255, 215, 0, 0.3)'
  }
  if (focused) {
    style.boxShadow = '0 0 0 2px rgba(170, 131, 255, 0.3)'
  }
  return style
}

// 切换移动端菜单
const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
  
  // 防止背景滚动
  if (isMobileMenuOpen.value) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
}

// 关闭移动端菜单
const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
  document.body.style.overflow = ''
}

// 滚动到指定区域
const scrollToSection = (sectionId: string) => {
  const element = document.getElementById(sectionId)
  if (element) {
    element.scrollIntoView({ 
      behavior: 'smooth',
      block: 'start'
    })
  }
  closeMobileMenu()
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  
  // 键盘导航支持
  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && isMobileMenuOpen.value) {
      closeMobileMenu()
    }
  }
  
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  document.body.style.overflow = ''
})
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;

.glass-navigation {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: var(--z-fixed);
  transition: all var(--transition-base);
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    @include glass-effect(0.05, 10px);
    transition: all var(--transition-base);
  }
  
  &--scrolled::before {
    @include glass-effect(0.08, 14px);
    border-bottom: var(--border-glass);
  }
}

.nav-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) 0;
  position: relative;
  z-index: 2;
  
  @include media-down(md) {
    padding: var(--spacing-sm) 0;
  }
}

.nav-logo {
  .logo-link {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    text-decoration: none;
    color: var(--text-primary);
    font-weight: var(--font-weight-bold);
    font-size: var(--font-size-lg);
    transition: all var(--transition-base);
    
    &:hover {
      transform: translateY(-2px);

      .logo-icon img {
        transform: rotate(10deg) scale(1.1);
      }
    }
  }
  
  .logo-icon {
    display: flex;
    align-items: center;
    justify-content: center;

    img {
      transition: transform var(--transition-base) var(--ease-hover);
      border-radius: var(--radius-sm);
    }
  }
  
  .logo-text {
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
}

.nav-menu {
  @include media-down(md) {
    position: fixed;
    top: 0;
    right: -100%;
    width: 280px;
    height: 100vh;
    @include glass-effect();
    padding: var(--spacing-3xl) var(--spacing-lg);
    transition: right var(--transition-base) var(--ease-hover);
    
    &--open {
      right: 0;
    }
  }
}

.nav-list {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
  
  @include media-down(md) {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-lg);
    margin-top: var(--spacing-2xl);
  }
}

.nav-item {
  .nav-link {
    position: relative;
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: var(--font-weight-medium);
    padding: var(--spacing-sm) 0;
    transition: all var(--transition-base);
    
    &::before {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      width: 0;
      height: 2px;
      background: var(--primary-gradient);
      transition: width var(--transition-base) var(--ease-hover);
    }
    
    &:hover {
      color: var(--text-primary);

      &::before {
        width: 100%;
      }
    }

    &.router-link-active {
      color: var(--text-primary);

      &::before {
        width: 100%;
      }
    }

    &:focus-visible {
      outline: 2px solid var(--secondary);
      outline-offset: 4px;
      border-radius: var(--radius-sm);
    }
  }
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.language-switcher {
  .language-btn {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: var(--radius-full);
    @include glass-effect();
    color: var(--text-primary);
    font-weight: var(--font-weight-medium);
    font-size: var(--font-size-sm);
    transition: all var(--transition-base) var(--ease-hover);
    
    &:hover {
      @include magnetic-hover(4px);
      box-shadow: var(--shadow-green-glow);
      
      .language-indicator {
        transform: scale(1.2);
        opacity: 1;
      }
    }
    
    .language-indicator {
      position: absolute;
      top: -2px;
      right: -2px;
      width: 8px;
      height: 8px;
      background: var(--secondary);
      border-radius: var(--radius-full);
      transition: all var(--transition-base);
      opacity: 0.7;
    }
  }
}

.theme-switcher {
  display: flex;
  align-items: center;

  :deep(.n-switch) {
    --n-rail-height: 24px;
    --n-rail-width: 48px;
    --n-button-width: 20px;
    --n-button-height: 20px;

    .n-switch__rail {
      border: 1px solid var(--glass-border);
      transition: all var(--transition-base) var(--ease-hover);

      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(170, 131, 255, 0.2);
      }
    }

    .n-switch__button {
      background: var(--glass-bg);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--glass-border);
      transition: all var(--transition-base) var(--ease-hover);

      &:hover {
        transform: scale(1.1);
      }
    }
  }

  @include media-down(md) {
    order: -1; // 在移动端将主题切换放在最前面
  }
}

.mobile-menu-btn {
  display: none;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  @include glass-effect();
  transition: all var(--transition-base);

  @include media-down(md) {
    display: flex;
  }
  
  &:hover {
    @include magnetic-hover(4px);
    box-shadow: var(--shadow-glow);
  }
  
  .hamburger-line {
    width: 20px;
    height: 2px;
    background: var(--text-primary);
    margin: 2px 0;
    transition: all var(--transition-base) var(--ease-hover);
    transform-origin: center;
    
    &:nth-child(1) {
      &.hamburger-line--active {
        transform: rotate(45deg) translate(5px, 5px);
      }
    }
    
    &:nth-child(2) {
      &.hamburger-line--active {
        opacity: 0;
      }
    }
    
    &:nth-child(3) {
      &.hamburger-line--active {
        transform: rotate(-45deg) translate(7px, -6px);
      }
    }
  }
}

.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  visibility: hidden;
  transition: all var(--transition-base);
  z-index: 1;
  
  &--active {
    opacity: 1;
    visibility: visible;
  }
  
  @include media-up(md) {
    display: none;
  }
}
</style>
