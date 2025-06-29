import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const isDev = mode === 'development'
  const isProd = mode === 'production'
  
  return {
    plugins: [vue()],
    base: './', // 使用相对路径，便于部署到子目录
    
    // 开发服务器配置
    server: {
      host: '0.0.0.0',
      port: 5173,
      cors: true,
      // 代理API请求到后端
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false
        }
      }
    },
    
    // 构建配置
    build: {
      // 统一输出到 dist 目录，由部署脚本负责移动文件
      outDir: 'dist',
      assetsDir: 'assets',
      emptyOutDir: true,
      
      // 优化构建
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['vue', 'pinia'],
            three: ['three', 'gsap']
          }
        }
      },
      
      // 生产环境优化
      minify: isProd ? 'terser' : false,
      sourcemap: isDev
    },
    
    // 路径解析
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    }
  }
})

