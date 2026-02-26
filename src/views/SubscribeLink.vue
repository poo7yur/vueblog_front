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
          <div class="essay-title">{{ essay.title }}</div>
          <span class="category-tag" :style="{ backgroundColor: essay.tagColor }" :title="essay.category">
          </span>
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
          <el-button :disabled="pageNum === 1" circle @click="changePage(-1)">
            <el-icon>
              <ArrowLeft />
            </el-icon>
          </el-button>

          <!-- 下一页 -->
          <el-button :disabled="pageNum === totalPage" circle @click="changePage(1)">
            <el-icon>
              <ArrowRight />
            </el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 右侧：订阅详情区 -->
    <div class="right-content">
      <div class="content-header" v-if="currentEssay">
        <!-- 仅保留标题展示，移除编辑模式输入框 -->
        <div class="title-wrapper">
          <h3>{{ currentEssay.title }}</h3>
          <!-- 右侧也展示创建者（可选） -->
          <div class="content-creator">{{ currentEssay.createUser }}</div>
        </div>
        <div class="operation-btns">
          <!-- 发布按钮：禁用条件增加「非本人」判断 -->
          <el-button type="success" @click="handlePublish"
            :disabled="currentEssay.isShare === 1 || currentUser !== currentEssay.createUser"
            :class="{ 'disabled-btn': currentEssay.isShare === 1 || currentUser !== currentEssay.createUser }">
            发布
          </el-button>
          <!-- 删除按钮：增加「非本人」禁用判断 -->
          <el-button type="danger" @click="handleDelete" :disabled="currentUser !== currentEssay.createUser"
            :class="{ 'disabled-btn': currentUser !== currentEssay.createUser }">
            删除
          </el-button>
        </div>
      </div>


      <!-- 标签选择区 - 新增折叠/展开功能 -->
      <div class="tag-selector-container"  v-if="currentEssay && currentUser === currentEssay.createUser">
        <!-- 折叠/展开控制栏 -->
        <div class="tag-collapse-header" @click="toggleTagCollapse">
          <span class="tag-collapse-title"></span>
          <el-icon class="collapse-icon" :class="{ 'rotate': isTagCollapsed }">
            <TriangleDown />
          </el-icon>
        </div>
        <!-- 标签列表 - 折叠/展开切换 -->
        <div class="tag-dot-list" v-show="!isTagCollapsed">
          <!-- 已加载的标签圆点（显示名称+颜色） -->
          <div v-for="tag in tagList" :key="tag.tagId" class="tag-item" @click="handleTagClick(tag)"
            @mouseenter="hoveredTagId = tag.tagId" @mouseleave="hoveredTagId = ''">
            <div class="tag-dot" :style="{ backgroundColor: tag.color }"
              :class="{ 'active': currentEssay.tagId === tag.tagId, 'shake': hoveredTagId === tag.tagId }">
              <!-- 删除按钮 - 仅当isPublic=0时显示 -->
              <span class="tag-delete-btn" v-if="hoveredTagId === tag.tagId && tag.isPublic === 0"
                @click.stop="handleDeleteTag(tag.tagId)">-</span>
            </div>
            <span class="tag-name">{{ tag.tagName }}</span>
          </div>
          <!-- 新增标签按钮 -->
          <div class="tag-add-btn" @click="showAddTagDialog = true">
            <span>+</span>
            <span class="tag-add-text">新增标签</span>
          </div>
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
    <!-- 新增标签弹窗 -->
    <el-dialog v-model="showAddTagDialog" title="新增标签" width="400px" @close="resetAddTagForm">
      <el-form :model="addTagForm" label-width="80px">
        <el-form-item label="标签名称">
          <el-input v-model="addTagForm.tagName" placeholder="请输入标签名称" maxlength="20" show-word-limit />
        </el-form-item>
        <el-form-item label="标签颜色">
          <el-color-picker v-model="addTagForm.color" :predefine="predefineColors" class="tag-color-picker" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddTagDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddTag">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowRight, ArrowLeft } from '@element-plus/icons-vue'

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
// 新增：获取当前登录用户
const currentUser = ref(localStorage.getItem('currentUser') || '')

/* 分页相关 */
const pageNum = ref(1)
const pageSize = ref(20)
const total = ref(0)
const typevalue = 1
const totalPage = computed(() => Math.ceil(total.value / pageSize.value))

/* 新建订阅弹窗 */
const showCreateDialog = ref(false)
const newTitle = ref('')

/* 标签相关 */
const tagList = ref([]) // 标签列表
const hoveredTagId = ref('') // 悬浮的标签ID
const showAddTagDialog = ref(false) // 新增标签弹窗
// 新增：标签选择区折叠状态（默认折叠）
const isTagCollapsed = ref(true)
// 新增标签表单
const addTagForm = ref({
  tagName: '',
  color: '#9547ec'
})
// 预定义颜色
const predefineColors = ref([
  '#9547ec', '#2397e4', '#f56c6c', '#0bd43e', '#999999',
  '#ff9500', '#ff3b30', '#007aff', '#34c759', '#5856d6'
])

onMounted(() => {
  fetchMyEssayList()
  fetchTagList()
})


/* -------------------- 标签相关接口 -------------------- */
// 1. 获取标签列表
const fetchTagList = async () => {
  try {
    const res = await axios.get('/listTags')
    if (res.data.code === 0) {
      tagList.value = res.data.data
    } else {
      ElMessage.error('获取标签列表失败：' + res.data.msg)
    }
  } catch (err) {
    ElMessage.error('获取标签列表异常：' + err.message)
    console.error(err)
  }
}

// 2. 绑定标签到文章
const bindTagToEssay = async (essayId, tagId) => {
  try {
    const res = await axios.post(
      '/bindTag',
      { id: essayId, tagId: tagId },
      { headers: { 'Content-Type': 'application/json' } }
    )
    if (res.data.code === 0) {
      ElMessage.success('标签绑定成功')
      // 更新当前文章的标签信息
      currentEssay.value.tagId = tagId
      // 找到对应的标签颜色并更新
      const tag = tagList.value.find(t => t.tagId === tagId)
      if (tag) {
        currentEssay.value.tagColor = tag.color
        currentEssay.value.category = tag.tagName
      }
      // 刷新文章列表
      fetchMyEssayList(pageNum.value)
    } else {
      ElMessage.error('标签绑定失败：' + res.data.msg)
    }
  } catch (err) {
    ElMessage.error('标签绑定异常：' + err.message)
    console.error(err)
  }
}

// 3. 新增标签
const addNewTag = async (tagForm) => {
  try {
    const res = await axios.post(
      '/addTag',
      { tagName: tagForm.tagName.trim(), color: tagForm.color },
      { headers: { 'Content-Type': 'application/json' } }
    )
    if (res.data.code === 0) {
      ElMessage.success('标签新增成功')
      showAddTagDialog.value = false
      // 刷新标签列表
      fetchTagList()
    } else {
      ElMessage.error('标签新增失败：' + res.data.msg)
    }
  } catch (err) {
    ElMessage.error('标签新增异常：' + err.message)
    console.error(err)
  }
}

// 4. 删除标签 - 增加isPublic=0权限校验
const deleteTag = async (tagId) => {
  // 先校验标签是否可删除（isPublic=0）
  const tag = tagList.value.find(t => t.tagId === tagId)
  if (tag && tag.isPublic === 1) {
    ElMessage.warning('系统标签不可删除')
    return
  }

  try {
    const res = await axios.get(`/deleteTag?tagId=${tagId}`)
    if (res.data.code === 0) {
      ElMessage.success('标签删除成功')
      // 如果当前文章绑定了该标签，清空绑定
      if (currentEssay.value && currentEssay.value.tagId === tagId) {
        currentEssay.value.tagId = ''
        currentEssay.value.tagColor = ''
        currentEssay.value.category = ''
      }
      // 刷新标签列表和文章列表
      fetchTagList()
      fetchMyEssayList(pageNum.value)
    } else {
      ElMessage.error('标签删除失败：' + res.data.msg)
    }
  } catch (err) {
    ElMessage.error('标签删除异常：' + err.message)
    console.error(err)
  }
}

/* -------------------- 标签相关事件处理 -------------------- */
// 点击标签圆点
const handleTagClick = (tag) => {
  if (!currentEssay.value) return

  // 判断是否和当前标签相同
  if (currentEssay.value.tagId === tag.tagId) {
    ElMessage.info('当前文章已绑定该标签')
    return
  }

  // 不同则绑定新标签
  bindTagToEssay(currentEssay.value.id, tag.tagId)
}

// 处理删除标签 - 增加权限校验提示
const handleDeleteTag = async (tagId) => {
  // 先校验标签是否可删除
  const tag = tagList.value.find(t => t.tagId === tagId)
  if (tag && tag.isPublic === 1) {
    ElMessage.warning('系统标签不可删除')
    return
  }

  try {
    await ElMessageBox.confirm(
      '此操作将永久删除该标签，是否继续？',
      '删除标签确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await deleteTag(tagId)
  } catch (err) {
    if (err !== 'cancel' && err.type !== 'cancel') {
      ElMessage.error('删除操作异常：' + err.message)
    }
  }
}

// 处理新增标签
const handleAddTag = () => {
  if (!addTagForm.value.tagName.trim()) {
    ElMessage.warning('请输入标签名称')
    return
  }
  addNewTag(addTagForm.value)
}

// 重置新增标签表单
const resetAddTagForm = () => {
  addTagForm.value = {
    tagName: '',
    color: '#9547ec'
  }
}

// 新增：切换标签选择区折叠/展开状态
const toggleTagCollapse = () => {
  isTagCollapsed.value = !isTagCollapsed.value
}

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
      { pageNum: targetPage, pageSize: pageSize.value, type: typevalue },
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
  // 增加非本人判断（双重防护）
  if (currentUser.value !== currentEssay.value.createUser) {
    ElMessage.warning('非创建者不可发布')
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
  // 增加非本人判断（双重防护）
  if (currentUser.value !== currentEssay.value.createUser) {
    ElMessage.warning('非创建者不可删除')
    return
  }

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
  position: relative;
  padding-right: 60px;
}

.essay-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
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
  top: 15px;
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


/* 标签选择器样式 - 新增折叠功能样式 */
.tag-selector-container {
  margin: 15px 0;
  padding: 10px;
  background-color: #fff;
  border-radius: 4px;
}

/* 标签折叠/展开头部 */
.tag-collapse-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.tag-collapse-header:hover {
  background-color: #f5f5f5;
}

.tag-collapse-title {
  font-size: 0.95rem;
  color: #333;
  font-weight: 500;
}

.collapse-icon {
  font-size: 16px;
  color: #666;
  transition: transform 0.3s ease;
}

.rotate {
  transform: rotate(180deg);
}

/* 标签列表样式优化 */
.tag-dot-list {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
  padding: 10px 0;
}

/* 标签项（圆点+名称） */
.tag-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 5px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.tag-item:hover {
  background-color: #f0f8ff;
}

.tag-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.tag-dot.active {
  border-color: #333;
  transform: scale(1.1);
}

/* 抖动动画 - 适配移动端 */
@keyframes shake {
  0% {
    transform: rotate(0deg);
  }

  25% {
    transform: rotate(-5deg);
  }

  50% {
    transform: rotate(0deg);
  }

  75% {
    transform: rotate(5deg);
  }

  100% {
    transform: rotate(0deg);
  }
}

.tag-dot.shake {
  animation: shake 0.5s infinite;
  /* 移动端动画优化 */
  animation-duration: 0.3s;
}

/* 标签名称 */
.tag-name {
  font-size: 0.9rem;
  color: #333;
  white-space: nowrap;
}

/* 标签删除按钮 */
.tag-delete-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: #f56c6c;
  color: #fff;
  font-size: 12px;
  text-align: center;
  line-height: 16px;
  cursor: pointer;
  font-weight: bold;
  /* 移动端适配 */
  width: 14px;
  height: 14px;
  font-size: 10px;
  line-height: 14px;
}

/* 新增标签按钮 */
.tag-add-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  width: fit-content;
  padding: 5px 10px;
  border-radius: 4px;
  border: 2px dashed #ccc;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-add-btn:hover {
  border-color: #3498db;
  background-color: #f0f8ff;
}

.tag-add-btn span:first-child {
  font-size: 14px;
  color: #666;
  line-height: 1;
}

.tag-add-text {
  font-size: 0.85rem;
  color: #666;
}

/* 颜色选择器样式 */
.tag-color-picker {
  width: 100%;
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
  margin: 0 0 8px 0;
}

/* 右侧创建者样式 */
.content-creator {
  font-size: 0.9rem;
  color: #666;
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
  overflow-x: auto;
  /* 允许横向滚动 */
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

:deep(.el-button.is-disabled) {
  background-color: #e9ecef !important;
  border-color: #e9ecef !important;
  color: #6c757d !important;
  cursor: not-allowed !important;
}

/* 兼容编辑按钮禁用样式 */
:deep(.el-button--primary.is-disabled) {
  background-color: #e9ecef !important;
  border-color: #e9ecef !important;
  color: #6c757d !important;
}

/* 兼容删除按钮禁用样式 */
:deep(.el-button--danger.is-disabled) {
  background-color: #e9ecef !important;
  border-color: #e9ecef !important;
  color: #6c757d !important;
}

.category-tag {
  position: absolute;
  right: 35px;
  top: 50%;
  transform: translateY(-50%);
  width: 12px;
  height: 12px;
  border-radius: 50%;
  color: transparent;
  padding: 0;
  margin: 0;
  z-index: 2;
  /* 层级高于分享标签 */
  display: inline-block;
  /* 强制显示 */
}

/* 文章项 hover 时标签同步变色（可选） */
.essay-item:hover .category-tag {
  opacity: 0.9;
}

/* 选中文章时标签样式适配 */
.essay-item.active .category-tag {
  box-shadow: 0 0 0 1px #fff;
  /* 选中时加白色边框突出 */
}

/* 已分享标签样式微调（适配分类标签位置） */
.share-tag {
  position: absolute;
  right: 10px;
  font-size: 0.8rem;
  color: #999;
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  z-index: 0;
  /* 确保分类标签在上方 */
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


  /* 标签选择器移动端适配 */
  .tag-collapse-title {
    font-size: 0.9rem;
  }

  .tag-dot-list {
    gap: 12px;
    padding: 8px 0;
  }

  .tag-item {
    gap: 6px;
    padding: 4px 6px;
  }

  .tag-dot {
    width: 20px;
    height: 20px;
  }

  .tag-name {
    font-size: 0.85rem;
  }

  .tag-add-btn {
    gap: 4px;
    padding: 4px 8px;
  }

  .tag-add-text {
    font-size: 0.8rem;
  }

  .category-tag {
    right: 30px;
    width: 10px;
    height: 10px;
  }

  .share-tag {
    right: 8px;
    font-size: 0.7rem;
    padding: 1px 4px;
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