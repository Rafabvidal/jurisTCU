import { VueQueryPlugin } from '@tanstack/vue-query'
import { MotionPlugin } from '@vueuse/motion'
import { createPinia } from 'pinia'
import { createApp } from 'vue'

import '@/shared/styles/main.css'
import App from './App.vue'
import queryClient from './plugins/tanstack.ts'
import router from './router'


const app = createApp(App)
.use(createPinia())
.use(router)
.use(MotionPlugin)
.use(VueQueryPlugin, { queryClient })

app.mount('#app')
