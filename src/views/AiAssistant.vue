<template>
  <!-- 浮动机器人 -->
<div
    class="ai-assistant-float"
    :style="{ left: posX + 'px', top: posY + 'px' }"
    @mousedown="startDrag"
    @click="toggleRobot"
  >
    <img :src="robotImg" alt="robot" class="robot-img" />
  </div>

  <!-- 对话框（使用 element-ui 风格） -->
  <div class="chat-modal" v-if="showModal">
     <div class="chat-box">
      <div class="chat-header">
        <span>Awesom-o 4000</span>
        <button class="close-btn" @click.stop="closeChat">×</button>
      </div>

      <div class="chat-content">
        <!-- 未登录提示 -->
        <div v-if="!isLoggedIn" class="tip-not-login">
          请登录后使用
        </div>

        <!-- 已登录区域 -->
        <template v-else>
          <!-- 欢迎语 -->
          <div class="bot-message" v-if="firstTip">
            主人 awesom-o 4000 为你服务
          </div>

          <!-- 用户消息 -->
          <div class="user-message" v-if="userInput">
            {{ userInput }}
          </div>

          <!-- AI 回答 -->
          <div class="bot-message" v-if="answerContent">
            {{ answerContent }}
            <button
              v-if="thinkContent"
              class="think-btn"
              @click="showThink = !showThink"
            >
              {{ showThink ? "隐藏思考过程" : "查看思考过程" }}
            </button>
            <div v-if="showThink" class="think-content">
              {{ thinkContent }}
            </div>
          </div>

          <!-- 加载中 -->
          <div class="loading" v-if="loading">思考中...</div>
        </template>
      </div>

      <!-- 输入框 -->
      <div class="chat-input">
        <input
          v-model="inputMsg"
          type="text"
          placeholder="请输入问题..."
          @keyup.enter="sendMessage"
        />
        <button @click="sendMessage">发送</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 图片路径（本地静态图片）
const robotClose = require('@/assets/close.png')
const robotOpen = require('@/assets/open.png')

// 状态
const robotImg = ref(robotClose)
const showModal = ref(false)
const firstTip = ref(true)
const inputMsg = ref('')
const userInput = ref('')
const answerContent = ref('')
const thinkContent = ref('')
const showThink = ref(false)
const loading = ref(false)

// 拖拽位置
const posX = ref(window.innerWidth - 100)
const posY = ref(window.innerHeight - 150)

// 登录状态
const isLoggedIn = ref(!!localStorage.getItem('userToken'))

// 机器人开机
function toggleRobot() {
  if (!showModal.value) {
    showModal.value = true
    robotImg.value = robotOpen
  }
}

// 机器人关机
function closeChat() {
  showModal.value = false
  robotImg.value = robotClose
}

// 发送消息
async function sendMessage() {
  if (!isLoggedIn.value) {
    alert('请登录后使用')
    return
  }

  if (!inputMsg.value.trim()) return
  userInput.value = inputMsg.value
  const msg = encodeURIComponent(inputMsg.value)
  inputMsg.value = ''

  loading.value = true
  answerContent.value = ''
  thinkContent.value = ''
  showThink.value = false

  try {
    const res = await fetch(`/ai/chat?msg=${msg}`)
    const data = await res.json()
    if (data.code === 0) {
      answerContent.value = data.data.summaryContent
      thinkContent.value = data.data.thinkContent
    }
  } catch (err) {
    answerContent.value = '服务连接失败，请稍后再试'
  } finally {
    loading.value = false
  }
}

// 拖拽功能
let isDragging = false
let startX, startY, initX, initY

function startDrag(e) {
  isDragging = true
  startX = e.clientX
  startY = e.clientY
  initX = posX.value
  initY = posY.value
  document.addEventListener('mousemove', dragMove)
  document.addEventListener('mouseup', dragEnd)
  e.preventDefault()
}

function dragMove(e) {
  if (!isDragging) return
  posX.value = initX + e.clientX - startX
  posY.value = initY + e.clientY - startY
}

function dragEnd() {
  isDragging = false
  document.removeEventListener('mousemove', dragMove)
  document.removeEventListener('mouseup', dragEnd)
}

onMounted(() => {
  posX.value = window.innerWidth - 100
  posY.value = window.innerHeight - 150
})
</script>

<style scoped>
/* 浮动机器人 */
.ai-assistant-float {
  position: fixed;
  z-index: 9999;
  cursor: move;
  user-select: none;
  /* 确保容器本身没有背景 */
  background: transparent; 
}

.robot-img {
  width: 60px;
  height: 60px;
  object-fit: contain;
  /* 移除可能导致“背景不透明”视觉错觉的属性 */
  background-color: transparent; 
}
/* 对话框 - Element UI 风格 */
.chat-modal {
  position: fixed;
  z-index: 9998;
  bottom: 80px;
  right: 20px;
}
.chat-box {
  width: 360px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e6e6e6;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.chat-header {
  padding: 12px 15px;
  background: #409eff;
  color: #fff;
  font-weight: 500;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.close-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
}

/* 内容 */
.chat-content {
  padding: 15px;
  max-height: 350px;
  overflow-y: auto;
  flex: 1;
}
.tip-not-login {
  color: #f56c6c;
  padding: 10px;
  text-align: center;
  font-size: 14px;
}
.user-message {
  text-align: right;
  background: #e1f5fe;
  padding: 8px 12px;
  border-radius: 16px;
  margin: 6px 0;
  max-width: 75%;
  margin-left: auto;
}
.bot-message {
  background: #f5f7fa;
  padding: 8px 12px;
  border-radius: 16px;
  margin: 6px 0;
  max-width: 75%;
}
.loading {
  color: #909399;
  font-size: 14px;
  padding: 6px 0;
}

/* 思考过程 */
.think-btn {
  margin-top: 6px;
  font-size: 12px;
  color: #409eff;
  background: none;
  border: none;
  cursor: pointer;
}
.think-content {
  margin-top: 8px;
  font-size: 12px;
  color: #666;
  background: #fafafa;
  padding: 8px;
  border-radius: 6px;
  white-space: pre-wrap;
}

/* 输入框 */
.chat-input {
  display: flex;
  padding: 10px;
  border-top: 1px solid #e6e6e6;
}
.chat-input input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  outline: none;
}
.chat-input button {
  margin-left: 8px;
  padding: 8px 14px;
  background: #409eff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .chat-box {
    width: 85vw;
    max-width: 320px;
  }
  .robot-img {
    width: 40px;
    height: 40px;
  }
}
</style>