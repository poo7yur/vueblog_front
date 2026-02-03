<template>
  <div class="create-space-container">
    <!-- 左侧：我的订阅列表（pageSize=20） -->
    <div class="left-sidebar">
      <div class="sidebar-header">
        <h2>我的订阅列表</h2>
        <el-button type="primary" circle size="small" @click="showCreateDialog = true">+</el-button>
      </div>
      <div class="essay-list">
        <div class="essay-item" v-for="essay in myEssayList" :key="essay.id"
          :class="{ active: currentEssay?.id === essay.id }" @click="handleEssayClick(essay)">
          {{ essay.title }}
          <!-- 已分享标签 -->
          <span v-if="essay.isShare === 1" class="share-tag">✓</span>
        </div>
      </div>
      <div class="no-data" v-if="myEssayList.length === 0">暂无已创作订阅</div>

      <!-- 分页栏 -->
      <div class="list-pagination">
        <span class="total">共 {{ total }} 条</span>
        <div class="pagination-btns">
            <!-- 上一页 -->
            <el-button
              :disabled="pageNum === 1"
              circle
              @click="changePage(-1)"
            >
              <el-icon><ArrowLeft /></el-icon>
            </el-button>

            <!-- 下一页 -->
            <el-button
              :disabled="pageNum === totalPage"
              circle
              @click="changePage(1)"
            >
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
      </div>
    </div>

    <!-- 右侧：订阅详情区（移除编辑功能） -->
    <div class="right-content">
      <div class="content-header" v-if="currentEssay">
        <!-- 仅保留标题展示，移除编辑模式输入框 -->
        <div class="title-wrapper">
          <h3>{{ currentEssay.title }}</h3>
        </div>
        <div class="operation-btns">
          <!-- 移除编辑按钮 -->
          <el-button type="success" @click="handlePublish" :disabled="currentEssay.isShare === 1"
            :class="{ 'disabled-btn': currentEssay.isShare === 1 }">
            发布
          </el-button>
          <el-button type="danger" @click="handleDelete">
            删除
          </el-button>
        </div>
      </div>

      <!-- 仅保留订阅预览区 -->
      <div class="content-body" v-if="currentEssay && essayContent">
        <div class="essay-content" v-html="essayContent"></div>
      </div>

      <div class="empty-tip" v-else>
        请选择左侧订阅查看详情
      </div>
    </div>
    
    <!-- 新建订阅弹窗 -->
    <el-dialog v-model="showCreateDialog" title="新建订阅" width="400px" @close="newTitle = ''">
      <el-input v-model="newTitle" placeholder="请输入链接" maxlength="100" show-word-limit />
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateEssay">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowRight ,ArrowLeft } from '@element-plus/icons-vue'

// 全局拦截器
axios.interceptors.request.use(config => {
  config.headers = config.headers || {}
  config.headers.token = localStorage.getItem('userToken') || ''
  return config
})

// 响应式数据（移除编辑相关变量）
const myEssayList = ref([]) // 我的订阅列表（pageSize=20）
const currentEssay = ref(null) // 当前选中的订阅
const essayContent = ref('') // 订阅原始内容

/* 分页相关 */
const pageNum = ref(1)
const pageSize = ref(20)
const total = ref(0)
const typevalue = 1
const totalPage = computed(() => Math.ceil(total.value / pageSize.value))

/* 新建订阅弹窗 */
const showCreateDialog = ref(false)
const newTitle = ref('')

onMounted(() => {
  fetchMyEssayList()
})

/* --------------------新建订阅 -------------------- */
const handleCreateEssay = async () => {
  if (!newTitle.value.trim()) {
    ElMessage.warning('请输入链接')
    return
  }
  try {
    await axios.post(
      '/saveLink',
      { linkUrl: newTitle.value.trim() },
      { headers: { 'Content-Type': 'application/json' } }
    )
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    newTitle.value = ''

    setTimeout(() => {
      fetchMyEssayList(1) // 3秒后刷新，获取更新后的title
    }, 3000)

  } catch (e) {
    ElMessage.error('创建失败：' + e.message)
  }
}

/* -------------------- 分页切换 -------------------- */
const changePage = delta => {
  const target = pageNum.value + delta
  if (target < 1 || target > totalPage.value) return
  fetchMyEssayList(target)
}

// 请求我的订阅列表
const fetchMyEssayList = async (targetPage = 1) => {
  try {
    const res = await axios.post(
      '/queryEssay',
      { pageNum: targetPage, pageSize: pageSize.value ,type :typevalue }, 
      { headers: { 'Content-Type': 'application/json' } }
    )
    if (res.data.code === 0) {
      myEssayList.value = res.data.data.list
      total.value = res.data.data.total
      pageNum.value = targetPage
    } else {
      ElMessage.error('获取我的订阅失败：' + res.data.msg)
    }
  } catch (err) {
    ElMessage.error('接口请求异常：' + err.message)
    console.error(err)
  }
}

// 请求订阅详情（接收后端文件流，转换为文本内容）
const fetchEssayDetail = async (essay) => {
  currentEssay.value = essay
  essayContent.value = '正在加载订阅内容...'

  try {
    const res = await axios.post(
      '/getEssayContent',
      { storagePath: essay.storagePath },
      {
        headers: { 'Content-Type': 'application/json' },
        responseType: 'blob'
      }
    )

    // 将blob流转换为文本
    const reader = new FileReader()
    reader.onload = () => {
      essayContent.value = reader.result
    }
    reader.onerror = (err) => {
      throw new Error('文件流解析失败：' + err.message)
    }
    reader.readAsText(res.data, 'utf-8')

  } catch (err) {
    // 处理接口异常（包括后端返回的错误信息）
    if (err.response?.data) {
      const errorReader = new FileReader()
      errorReader.onload = () => {
        essayContent.value = '加载失败：' + errorReader.result
        ElMessage.error('获取订阅内容失败：' + errorReader.result)
      }
      errorReader.readAsText(err.response.data, 'utf-8')
    } else {
      essayContent.value = '加载异常：' + err.message
      ElMessage.error('获取订阅内容失败：' + err.message)
    }
    console.error('获取订阅内容异常：', err)
  }
}

// 处理订阅点击（移除编辑状态确认逻辑）
const handleEssayClick = async (targetEssay) => {
  await fetchEssayDetail(targetEssay)
}

// 发布订阅
const handlePublish = async () => {
  if (currentEssay.value.isShare === 1) {
    ElMessage.warning('已分享的订阅不可重复发布')
    return
  }

  try {
    const res = await axios.post(
      '/publishEssay',
      { id: currentEssay.value.id, status: 1 },
      { headers: { 'Content-Type': 'application/json' } }
    )
    if (res.data.code === 0) {
      ElMessage.success('订阅发布成功！')
      fetchMyEssayList()
    } else {
      ElMessage.error('发布失败：' + res.data.msg)
    }
  } catch (err) {
    ElMessage.error('发布接口异常：' + err.message)
  }
}

// 删除订阅
const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      '此操作将永久删除该订阅，是否继续？',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const res = await axios.post(
      '/deleteEssay',
      { id: currentEssay.value.id },
      { headers: { 'Content-Type': 'application/json' } }
    )

    if (res.data.code === 0) {
      ElMessage.success('订阅删除成功！')
      // 重置当前选中订阅和内容，刷新列表
      currentEssay.value = null
      essayContent.value = ''
      fetchMyEssayList()
    } else {
      ElMessage.error('删除失败：' + res.data.msg)
    }
  } catch (err) {
    if (err !== 'cancel' && err.type !== 'cancel') {
      ElMessage.error('删除接口异常：' + (err.message || '取消删除'))
    }
  }
}
</script>

<style scoped>
.create-space-container {
  display: flex;
  height: calc(100vh - 60px);
  padding: 20px;
  gap: 20px;
  /* 修复：防止布局挤压 */
  box-sizing: border-box;
}

/* 左侧侧边栏（修复宽度缩小问题） */
.left-sidebar {
  width: 300px;
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  /* 核心修复：固定盒模型，避免padding影响宽度 */
  box-sizing: border-box;
  /* 防止被挤压 */
  flex-shrink: 0;
}

.left-sidebar h2 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.essay-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.essay-item {
  padding: 12px 15px;
  background-color: #fff;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  position: relative;
}

.essay-item:hover {
  background-color: #e3f2fd;
}

.essay-item.active {
  background-color: #3498db;
  color: #fff;
}

/* 已分享标签样式 */
.share-tag {
  position: absolute;
  right: 10px;
  font-size: 0.8rem;
  color: #999;
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
}

.no-data {
  text-align: center;
  padding: 20px;
  color: #95a5a6;
  font-size: 1rem;
}

/* 分页栏样式 */
.list-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid #eee;
  margin-top: auto;
}

.total {
  font-size: 13px;
  color: #666;
}

.pagination-btns {
  display: flex;
  gap: 8px;
}

/* 右侧内容区 */
.right-content {
  flex: 1;
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 30px;
  display: flex;
  flex-direction: column;
  /* 修复：盒模型 */
  box-sizing: border-box;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.title-wrapper {
  flex: 1;
}

.content-header h3 {
  font-size: 1.6rem;
  color: #2c3e50;
  margin: 0;
}

.operation-btns {
  display: flex;
  gap: 10px;
}

/* 禁用发布按钮的样式 */
.disabled-btn {
  background-color: #e9ecef !important;
  border-color: #e9ecef !important;
  color: #6c757d !important;
  cursor: not-allowed !important;
}

/* 订阅预览区 */
.content-body {
  flex: 1;
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  overflow-y: auto;
}

.essay-content {
  font-size: 1rem;
  line-height: 1.8;
  color: #333;
  width: 100%;
  max-width: 100%;
  overflow-x: auto; /* 允许横向滚动 */
}

.empty-tip {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #95a5a6;
  font-size: 1.2rem;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
}

/* ========== 移动端适配（768px以下） ========== */
@media (max-width: 768px) {
  .create-space-container {
    flex-direction: column;
    height: auto;
    padding: 10px;
    gap: 15px;
  }

  .left-sidebar {
    width: 100%;
    height: auto;
    padding: 15px;
    max-height: 40vh;
    flex-shrink: 1;
  }

  .left-sidebar h2 {
    font-size: 1.2rem;
    margin-bottom: 10px;
    padding-bottom: 8px;
  }

  .essay-item {
    padding: 10px 12px;
    font-size: 0.9rem;
  }

  .no-data {
    padding: 15px;
    font-size: 0.9rem;
  }

  .right-content {
    padding: 15px;
    min-height: 50vh;
  }

  .content-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
    margin-bottom: 15px;
    padding-bottom: 15px;
  }

  .content-header h3 {
    font-size: 1.2rem;
  }

  .operation-btns {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }

  .operation-btns el-button {
    flex: 1;
    min-width: 80px;
    font-size: 0.8rem;
    padding: 8px 0;
  }

  .content-body {
    padding: 15px;
  }

  .empty-tip {
    font-size: 1rem;
  }

  .total {
    font-size: 12px;
  }

  .pagination-btns el-button {
    width: 32px;
    height: 32px;
    padding: 0;
  }

  :deep(.essay-content > *:first-child) {
   max-width: 100% !important;
   margin: 0 !important;
   padding: 0 !important;
 }

  :deep(.el-dialog) {
    width: 90% !important;
    padding: 0 10px;
  }

  :deep(.el-dialog__header) {
    padding: 15px 10px;
  }

  :deep(.el-dialog__body) {
    padding: 10px;
  }

  :deep(.el-dialog__footer) {
    padding: 10px;
  }
}
</style>