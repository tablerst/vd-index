import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/main.scss'
import './styles/fluent-theme.scss'
import './styles/tailwind.css'
// Swiper global styles: ensure layout rules (wrapper flex, slides sizing) are present
import 'swiper/css'
import 'swiper/css/navigation'




const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
