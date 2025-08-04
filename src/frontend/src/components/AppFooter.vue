<template>
  <footer id="about" class="app-footer">
    <!-- 几何线条装饰 -->
    <div class="geometric-lines">
      <svg class="line-pattern" viewBox="0 0 1200 100" preserveAspectRatio="none">
        <defs>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:rgba(170, 131, 255, 0.3)"/>
            <stop offset="50%" style="stop-color:rgba(212, 222, 199, 0.5)"/>
            <stop offset="100%" style="stop-color:rgba(63, 125, 251, 0.3)"/>
          </linearGradient>
        </defs>
        
        <!-- 主线条 -->
        <path 
          d="M0,50 Q300,10 600,50 T1200,50" 
          stroke="url(#lineGradient)" 
          stroke-width="2" 
          fill="none"
          class="animated-line"
        />
        
        <!-- 辅助线条 -->
        <path 
          d="M0,30 Q400,70 800,30 T1200,30" 
          stroke="rgba(170, 131, 255, 0.2)" 
          stroke-width="1" 
          fill="none"
          class="animated-line animated-line--delay-1"
        />
        
        <path 
          d="M0,70 Q200,30 600,70 T1200,70" 
          stroke="rgba(212, 222, 199, 0.3)" 
          stroke-width="1" 
          fill="none"
          class="animated-line animated-line--delay-2"
        />
      </svg>
    </div>

    <div class="container">
      <div class="footer-content">
        <!-- 左侧：品牌信息 -->
        <div class="footer-brand">
          <div class="brand-logo">
            <img src="/VD_LOGO.png" alt="VRC Division Logo" width="40" height="40" />
          </div>
          
          <div class="brand-text">
            <h3 class="brand-name">VRC Division</h3>
            <p class="brand-slogan">愿大家在VRC Division中收获自己的快乐</p>
          </div>
        </div>

        <!-- 中间：导航链接 -->
        <div class="footer-nav">
          <div class="nav-section">
            <h4 class="nav-title">探索</h4>
            <ul class="nav-list">
              <li><a href="#hero" class="nav-link">首页</a></li>
              <li><a href="#members" class="nav-link">成员星云</a></li>
              <li><a href="#activities" class="nav-link">星历活动</a></li>
              <li><a href="#about" class="nav-link">关于我们</a></li>
            </ul>
          </div>

          <div class="nav-section">
            <h4 class="nav-title">社区</h4>
            <ul class="nav-list">
              <li><a href="#" class="nav-link">加入群聊</a></li>
              <li><a href="#" class="nav-link">群规说明</a></li>
              <li><a href="#" class="nav-link">活动报名</a></li>
              <li><a href="#" class="nav-link">意见反馈</a></li>
            </ul>
          </div>
        </div>

        <!-- 右侧：社交链接 -->
        <div class="footer-social">
          <h4 class="social-title">连接我们</h4>
          <div class="social-links">
            <a 
              href="#" 
              class="social-link interactive"
              aria-label="GitHub"
              title="GitHub"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
              </svg>
            </a>
            
            <a 
              href="#" 
              class="social-link interactive"
              aria-label="Discord"
              title="Discord"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
              </svg>
            </a>
            
            <a 
              href="#" 
              class="social-link interactive"
              aria-label="Twitter"
              title="Twitter"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
              </svg>
            </a>
            
            <a 
              href="#" 
              class="social-link interactive"
              aria-label="邮箱"
              title="邮箱"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
            </a>
          </div>
          
          <!-- 联系信息 -->
          <div class="contact-info">
            <p class="contact-item">
              <span class="contact-label">邮箱:</span>
              <a href="mailto:hello@vrc-division.com" class="contact-link">hello@vrc-division.com</a>
            </p>
          </div>
        </div>
      </div>

      <!-- 分割线 -->
      <div class="footer-divider">
        <div class="divider-line"></div>
        <div class="divider-dots">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
        <div class="divider-line"></div>
      </div>

      <!-- 底部版权信息 -->
      <div class="footer-bottom">
        <div class="copyright">
          <p>&copy; {{ currentYear }} VRC Division. 保留所有权利.</p>
          <p class="build-info">
            使用 <span class="tech-highlight">Vue 3</span> + 
            <span class="tech-highlight">Three.js</span> + 
            <span class="tech-highlight">❤️</span> 构建
          </p>
        </div>
        
        <div class="footer-links">
          <a href="#" class="footer-link">隐私政策</a>
          <span class="separator">·</span>
          <a href="#" class="footer-link">服务条款</a>
          <span class="separator">·</span>
          <a href="#" class="footer-link">Cookie 政策</a>
        </div>
      </div>
    </div>

    <!-- 回到顶部按钮 -->
    <button 
      class="back-to-top interactive"
      @click="scrollToTop"
      :class="{ 'back-to-top--visible': showBackToTop }"
      aria-label="回到顶部"
    >
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M10 15L10 5M5 10L10 5L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
  </footer>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'

const showBackToTop = ref(false)

// 当前年份
const currentYear = computed(() => new Date().getFullYear())

// 滚动到顶部
const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

// 监听滚动事件
const handleScroll = () => {
  showBackToTop.value = window.scrollY > 500
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped lang="scss">
@use '../styles/variables.scss' as *;

.app-footer {
  position: relative;
  background: var(--base-dark);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: var(--spacing-3xl);
  padding-bottom: var(--spacing-xl);
  
  @include media-down(md) {
    padding-top: var(--spacing-2xl);
  }
}

.geometric-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100px;
  overflow: hidden;
  
  .line-pattern {
    width: 100%;
    height: 100%;
  }
  
  .animated-line {
    stroke-dasharray: 5, 10;
    animation: lineFlow 20s linear infinite;
    
    &--delay-1 {
      animation-delay: -5s;
    }
    
    &--delay-2 {
      animation-delay: -10s;
    }
  }
}

.footer-content {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  gap: var(--spacing-3xl);
  margin-bottom: var(--spacing-2xl);
  
  @include media-down(lg) {
    grid-template-columns: 1fr;
    gap: var(--spacing-2xl);
    text-align: center;
  }
}

.footer-brand {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  
  @include media-down(lg) {
    justify-content: center;
  }
  
  .brand-logo img {
    transition: transform var(--transition-base);
    border-radius: var(--radius-sm);

    &:hover {
      transform: rotate(10deg) scale(1.1);
    }
  }
  
  .brand-text {
    .brand-name {
      font-size: var(--font-size-lg);
      font-weight: var(--font-weight-bold);
      margin-bottom: var(--spacing-xs);
      background: var(--primary-gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    
    .brand-slogan {
      font-size: var(--font-size-sm);
      color: var(--text-secondary);
      line-height: var(--line-height-relaxed);
    }
  }
}

.footer-nav {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-xl);

  @include media-down(md) {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }
  
  .nav-section {
    .nav-title {
      font-size: var(--font-size-md);
      font-weight: var(--font-weight-semibold);
      margin-bottom: var(--spacing-md);
      color: var(--text-primary);
    }
    
    .nav-list {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
      
      .nav-link {
        color: var(--text-secondary);
        font-size: var(--font-size-sm);
        transition: all var(--transition-base);
        
        &:hover {
          color: var(--primary);
          transform: translateX(4px);
        }
      }
    }
  }
}

.footer-social {
  .social-title {
    font-size: var(--font-size-md);
    font-weight: var(--font-weight-semibold);
    margin-bottom: var(--spacing-md);
    color: var(--text-primary);
  }
  
  .social-links {
    display: flex;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
    
    @include media-down(lg) {
      justify-content: center;
    }
    
    .social-link {
      width: 40px;
      height: 40px;
      border-radius: var(--radius-full);
      @include glass-effect();
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--transition-base) var(--ease-hover);
      
      &:hover {
        color: var(--text-primary);
        @include magnetic-hover(4px);
        box-shadow: var(--shadow-glow);
      }
    }
  }
  
  .contact-info {
    .contact-item {
      font-size: var(--font-size-sm);
      color: var(--text-secondary);
      margin-bottom: var(--spacing-xs);
      
      .contact-label {
        font-weight: var(--font-weight-medium);
      }
      
      .contact-link {
        color: var(--accent-blue);
        
        &:hover {
          color: var(--primary);
        }
      }
    }
  }
}

.footer-divider {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin: var(--spacing-2xl) 0;
  
  .divider-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(
      to right,
      transparent,
      rgba(255, 255, 255, 0.1),
      transparent
    );
  }
  
  .divider-dots {
    display: flex;
    gap: var(--spacing-xs);
    
    .dot {
      width: 4px;
      height: 4px;
      border-radius: var(--radius-full);
      background: var(--secondary);
      opacity: 0.6;
    }
  }
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  @include media-down(md) {
    flex-direction: column;
    gap: var(--spacing-md);
    text-align: center;
  }
  
  .copyright {
    color: var(--text-muted);
    font-size: var(--font-size-sm);
    
    .build-info {
      margin-top: var(--spacing-xs);
      
      .tech-highlight {
        color: var(--primary);
        font-weight: var(--font-weight-medium);
      }
    }
  }
  
  .footer-links {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    
    .footer-link {
      color: var(--text-muted);
      font-size: var(--font-size-sm);
      transition: color var(--transition-base);
      
      &:hover {
        color: var(--text-secondary);
      }
    }
    
    .separator {
      color: var(--text-muted);
      opacity: 0.5;
    }
  }
}

.back-to-top {
  position: fixed;
  bottom: var(--spacing-xl);
  right: var(--spacing-xl);
  width: 48px;
  height: 48px;
  border-radius: var(--radius-full);
  @include glass-effect();
  color: var(--text-primary);
  opacity: 0;
  visibility: hidden;
  transform: translateY(20px);
  transition: all var(--transition-base) var(--ease-hover);
  z-index: var(--z-fixed);
  
  &--visible {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
  }
  
  &:hover {
    @include magnetic-hover(4px);
    box-shadow: var(--shadow-glow);
  }
  
  @include media-down(sm) {
    bottom: var(--spacing-lg);
    right: var(--spacing-lg);
    width: 40px;
    height: 40px;
  }
}

// 动画定义
@keyframes lineFlow {
  0% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: 100;
  }
}
</style>
