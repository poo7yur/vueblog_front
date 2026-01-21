import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // 引入路由
import ElementPlus from 'element-plus' // 引入Element Plus
import 'element-plus/dist/index.css' // 引入Element Plus样式
import axios from 'axios' // 引入Axios

const app = createApp(App)

// 全局挂载Axios，方便组件中直接使用
app.config.globalProperties.$axios = axios
// 配置Axios默认请求头（匹配后台接口要求）
axios.defaults.headers.post['Content-Type'] = 'application/json'

app.use(router)
app.use(ElementPlus)
app.mount('#app')