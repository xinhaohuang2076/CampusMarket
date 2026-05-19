import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// 全局错误捕获 — 前端运行时错误会打印到 console
app.config.errorHandler = (err, instance, info) => {
  console.error('[Vue Error]', err)
  console.error('  Component:', instance?.$options?.name || instance?.$el?.tagName)
  console.error('  Info:', info)
}

app.use(router)
app.mount('#app')
