import { createApp } from 'vue'
import router from './router.js'
import Home from './views/Home.vue'

const app = createApp(Home)
app.use(router)
app.mount('#app')
