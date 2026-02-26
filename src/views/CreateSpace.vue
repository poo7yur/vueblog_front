<template>
  <div class="create-space-container">
    <!-- 左侧：我的文章列表（pageSize=20） -->
    <div class="left-sidebar">
      <div class="sidebar-header">
        <h2>我的文章列表</h2>
        <el-button type="primary" circle size="small" @click="showCreateDialog = true">+</el-button>
      </div>
      <div class="essay-list">
        <div class="essay-item" v-for="essay in myEssayList" :key="essay.id"
          :class="{ active: currentEssay?.id === essay.id }" @click="handleEssayClick(essay)">
          {{ essay.title }}
          <span class="category-tag" :style="{ backgroundColor: essay.tagColor }" :title="essay.category">
          </span>
          <!-- 已分享标签 -->
          <span v-if="essay.isShare === 1" class="share-tag">✓</span>
        </div>
      </div>
      <div class="no-data" v-if="myEssayList.length === 0">暂无已创作文章</div>

      <!-- 修复：将分页栏移入左侧侧边栏内部 -->
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

    <!-- 右侧：文章详情/编辑区 -->
    <div class="right-content">
      <div class="content-header" v-if="currentEssay">
        <!-- 修复：编辑模式显示标题输入框，非编辑显示文本 -->
        <div class="title-wrapper">
          <h3 v-if="!isEditing">{{ currentEssay.title }}</h3>
          <el-input v-else v-model="currentTitle" placeholder="请输入文章标题" maxlength="50" show-word-limit
            class="title-input" />
        </div>
        <div class="operation-btns">
          <el-button type="primary" @click="toggleEditMode"
            :disabled="(isEditing && !isContentChanged && currentTitle === currentEssay.title) || currentUser !== currentEssay.createUser">
            {{ isEditing ? '退出编辑' : '编辑' }}
          </el-button>
          <el-button type="success" @click="handlePublish" :disabled="currentEssay.isShare === 1 || isEditing"
            :class="{ 'disabled-btn': currentEssay.isShare === 1 }">
            发布
          </el-button>
          <el-button type="danger" @click="handleDelete"
            :disabled="isEditing || currentUser !== currentEssay.createUser">
            删除
          </el-button>
        </div>
      </div>

      <!-- 标签选择区 - 新增折叠/展开功能 -->
      <div class="tag-selector-container" v-if="currentEssay && currentUser === currentEssay.createUser">
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

      <!-- 富文本编辑区（编辑模式显示） -->
      <div class="editor-container" v-if="isEditing && currentEssay">
        <div id="editor-toolbar"></div>
        <div id="editor-content"></div>
      </div>

      <!-- 文章预览区（非编辑模式显示） -->
      <div class="content-body" v-else-if="currentEssay && essayContent">
        <div class="essay-content" v-html="essayContent"></div>
      </div>

      <div class="empty-tip" v-else>
        请选择左侧文章查看详情
      </div>
    </div>
    <!-- 新建文章弹窗 -->
    <el-dialog v-model="showCreateDialog" title="新建文章" width="400px" @close="newTitle = ''">
      <el-input v-model="newTitle" placeholder="请输入标题" maxlength="50" show-word-limit />
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
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
// 引入wangEditor
import { createEditor, createToolbar } from '@wangeditor/editor'
import '@wangeditor/editor/dist/css/style.css'
import { ArrowRight, ArrowLeft, TriangleDown } from '@element-plus/icons-vue'

// 全局拦截器
axios.interceptors.request.use(config => {
  config.headers = config.headers || {}
  config.headers.token = localStorage.getItem('userToken') || 'eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyTmFtZSI6InZ1ZWJsb2ciLCJ1c2VySWQiOiJyNGpnc2RiczgwYXVmbXBkaXMiLCJzdWIiOiJ2dWVibG9nIiwiaWF0IjoxNzcyMDgzNDU1LCJleHAiOjE3NzIwOTA2NTV9.xa8x1iNieo6y6ozQ06PJg3vQ9gAkRmBZeeEatPzyxcc'
  return config
})

// 响应式数据
const myEssayList = ref([]) // 我的文章列表（pageSize=20）
const currentEssay = ref(null) // 当前选中的文章
const currentUser = ref(localStorage.getItem('currentUser') || '')
const essayContent = ref('') // 文章原始内容
const originContent = ref('') // 编辑前的原始内容（用于对比是否修改）
const isEditing = ref(false) // 是否处于编辑模式
const isContentChanged = ref(false) // 内容是否被修改
// 新增：当前编辑的标题（用于编辑模式修改标题）
const currentTitle = ref('')
const originTitle = ref('') // 编辑前的原始标题
let editor = null // 富文本编辑器实例
let toolbar = null // 工具栏实例

/* 分页相关 */
const pageNum = ref(1)
const pageSize = ref(20)
const total = ref(0)
const totalPage = computed(() => Math.ceil(total.value / pageSize.value))

/* 新建文章弹窗 */
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

// 页面挂载时，请求我的文章列表（pageSize=20）和标签列表
onMounted(() => {
  fetchMyEssayList()
  fetchTagList()
})

// 页面卸载时销毁编辑器实例
onUnmounted(() => {
  if (editor) {
    editor.destroy()
    editor = null
  }
  if (toolbar) {
    toolbar.destroy()
    toolbar = null
  }
})

// 监听编辑模式切换，初始化/销毁编辑器
watch(isEditing, async (newVal) => {
  if (newVal && currentEssay.value) {
    // 等待 DOM 渲染完成后再初始化编辑器
    await nextTick()
    initEditor()
    // 初始化编辑标题
    currentTitle.value = currentEssay.value.title
    originTitle.value = currentEssay.value.title
  } else {
    destroyEditor()
  }
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

/* --------------------新建文章 -------------------- */
const handleCreateEssay = async () => {
  if (!newTitle.value.trim()) {
    ElMessage.warning('请输入标题')
    return
  }
  try {
    await axios.post(
      '/createEssay',
      { title: newTitle.value.trim() },
      { headers: { 'Content-Type': 'application/json' } }
    )
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    newTitle.value = ''
    // 刷新列表并回到第一页
    await fetchMyEssayList(1)
    // 自动选中新创建的文章（后端返回列表第一条即为最新）
    if (myEssayList.value.length) {
      await handleEssayClick(myEssayList.value[0])
    }
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

// 1. 请求我的文章列表（修复：接收分页参数，更新total）
const fetchMyEssayList = async (targetPage = 1) => {
  try {
    const res = await axios.post(
      '/queryEssay',
      { pageNum: targetPage, pageSize: pageSize.value }, // 修复：使用传入的分页参数
      { headers: { 'Content-Type': 'application/json' } }
    )
    if (res.data.code === 0) {
      myEssayList.value = res.data.data.list
      total.value = res.data.data.total // 修复：更新总条数
      pageNum.value = targetPage // 修复：更新当前页码
    } else {
      ElMessage.error('获取我的文章失败：' + res.data.msg)
    }
  } catch (err) {
    ElMessage.error('接口请求异常：' + err.message)
    console.error(err)
  }
}

// 2. 请求文章详情（接收后端文件流，转换为文本内容）
const fetchEssayDetail = async (essay) => {
  currentEssay.value = essay
  essayContent.value = '正在加载文章内容...'

  try {
    const res = await axios.post(
      '/getEssayContent',
      { storagePath: essay.storagePath },
      {
        headers: { 'Content-Type': 'application/json' },
        responseType: 'blob' // 关键：指定响应类型为二进制流
      }
    )

    // 将blob流转换为文本
    const reader = new FileReader()
    reader.onload = () => {
      essayContent.value = reader.result // 转换后的文本内容
      originContent.value = reader.result // 保存原始内容用于对比
    }
    reader.onerror = (err) => {
      throw new Error('文件流解析失败：' + err.message)
    }
    reader.readAsText(res.data, 'utf-8') // 按utf-8编码解析

  } catch (err) {
    // 处理接口异常（包括后端返回的错误信息）
    if (err.response?.data) {
      // 尝试解析后端返回的错误信息（blob格式）
      const errorReader = new FileReader()
      errorReader.onload = () => {
        essayContent.value = '加载失败：' + errorReader.result
        ElMessage.error('获取文章内容失败：' + errorReader.result)
      }
      errorReader.readAsText(err.response.data, 'utf-8')
    } else {
      essayContent.value = '加载异常：' + err.message
      ElMessage.error('获取文章内容失败：' + err.message)
    }
    console.error('获取文章内容异常：', err)
  }
}

// 3. 初始化富文本编辑器
const initEditor = () => {
  // 校验 DOM 元素是否存在
  const toolbarDom = document.getElementById('editor-toolbar')
  const contentDom = document.getElementById('editor-content')
  if (!toolbarDom || !contentDom) {
    ElMessage.error('编辑器容器未找到，初始化失败')
    isEditing.value = false
    return
  }

  // 配置编辑器
  const editorConfig = {
    placeholder: '请输入文章内容...',
    onChange: (editor) => {
      // 实时对比内容是否修改
      const currentHtml = editor.getHtml()
      isContentChanged.value = currentHtml !== originContent.value || currentTitle.value !== originTitle.value
      // 实时同步编辑内容（可选）
      essayContent.value = currentHtml
    },

    //excludeKeys: ['fullScreen', 'group-video', 'group-audio', 'insertLink']
  }

  // 配置工具栏（核心修复：修正所有错误的key名称，适配wangEditor v5+）
  const toolbarConfig = {
    // 自定义工具栏菜单（贴近语雀，使用官方正确的key）
    toolbarKeys: [
      'headerSelect', // 标题
      '|',
      'fontSize', // 字号
      '|',
      'bold', // 加粗
      'italic', // 斜体
      'underline', // 下划线
      'through', // 核心修复：删除线 正确key是 through 而非 strikeThrough
      '|',
      'color', // 文字颜色
      'bgColor', // 背景色
      '|',
      'justifyLeft', // 左对齐
      'justifyCenter', // 居中
      'justifyRight', // 右对齐
      'justifyJustify', // 两端对齐
      '|',
      'bulletedList', // 核心修复：无序列表 正确key是 bulletedList 而非 insertUnorderedList
      'numberedList', // 核心修复：有序列表 正确key是 numberedList 而非 insertOrderedList
      '|',
      'insertTable', // 插入表格
      'insertImage', // 插入图片
      '|',
      'undo', // 撤销
      'redo' // 重做
    ]
  }

  try {
    // 创建编辑器实例
    editor = createEditor({
      selector: '#editor-content',
      html: essayContent.value, // 填充已有内容
      config: editorConfig,
      mode: 'default'
    })

    // 创建工具栏实例
    toolbar = createToolbar({
      editor,
      selector: '#editor-toolbar',
      config: toolbarConfig,
      mode: 'default'
    })
  } catch (err) {
    ElMessage.error('编辑器初始化失败：' + err.message)
    isEditing.value = false
    destroyEditor()
  }
}

// 销毁富文本编辑器
const destroyEditor = () => {
  if (editor) {
    editor.destroy()
    editor = null
  }
  if (toolbar) {
    toolbar.destroy()
    toolbar = null
  }
  isContentChanged.value = false // 重置内容修改标记
}

// 4. 处理文章点击（修复：确保编辑中切换有确认提示）
const handleEssayClick = async (targetEssay) => {
  // 修复：增加判断，确保currentEssay存在时才判断编辑状态
  if (isEditing.value && isContentChanged.value && currentEssay.value && currentEssay.value.id !== targetEssay.id) {
    try {
      await ElMessageBox.confirm(
        `是否放弃当前编辑的【${currentEssay.value.title}】内容，切换到【${targetEssay.title}】？`,
        '切换文章确认',
        {
          confirmButtonText: '确认切换',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      // 确认切换：退出编辑模式，重置内容，加载目标文章
      isEditing.value = false
      isContentChanged.value = false
      await fetchEssayDetail(targetEssay)
    } catch (err) {
      // 取消切换：不做任何操作
      if (err !== 'cancel' && err.type !== 'cancel') {
        ElMessage.error('操作异常：' + err.message)
      }
      return
    }
  } else {
    // 未编辑/内容未修改：直接加载目标文章
    await fetchEssayDetail(targetEssay)
  }
}

// 5. 切换编辑模式（优化：完善保存/放弃逻辑，包含标题修改）
const toggleEditMode = () => {
  if (isEditing.value) {
    // 退出编辑模式
    const isTitleChanged = currentTitle.value !== originTitle.value
    if (!isContentChanged.value && !isTitleChanged) {
      // 内容和标题都未修改：直接退出
      isEditing.value = false
      ElMessage.info('未修改内容和标题，直接退出编辑模式')
      return
    }

    // 内容或标题已修改：弹出保存确认框
    ElMessageBox.confirm(
      `是否保存对【${originTitle.value}】的修改？`,
      '保存确认',
      {
        confirmButtonText: '保存',
        cancelButtonText: '不保存',
        type: 'info'
      }
    ).then(async () => {
      // 保存修改（调用后端保存接口）
      await saveEssayContent()
      isEditing.value = false
      // 更新原始内容和标题
      originContent.value = essayContent.value
      originTitle.value = currentTitle.value
      // 更新当前文章的标题（前端展示）
      currentEssay.value.title = currentTitle.value
      isContentChanged.value = false // 重置修改标记
      ElMessage.success('修改已保存')
    }).catch(async (err) => {
      if (err === 'cancel' || err.type === 'cancel') {
        // 不保存：直接退出，重置内容和标题为原始版本
        isEditing.value = false
        essayContent.value = originContent.value
        currentTitle.value = originTitle.value
        isContentChanged.value = false
        ElMessage.info('未保存修改，已退出编辑模式')
      } else {
        ElMessage.error('操作异常：' + err.message)
      }
    })
  } else {
    // 进入编辑模式：记录原始内容和标题
    originContent.value = essayContent.value
    originTitle.value = currentEssay.value.title
    currentTitle.value = currentEssay.value.title
    isEditing.value = true
  }
}

// 6. 保存编辑后的文章内容（修复：新增title参数传给后端）
const saveEssayContent = async () => {
  try {
    const res = await axios.post(
      '/saveEssayContent',
      {
        id: currentEssay.value.id,
        storagePath: currentEssay.value.storagePath,
        title: currentTitle.value.trim(), // 新增：传递修改后的标题
        content: editor?.getHtml() || essayContent.value
      },
      { headers: { 'Content-Type': 'application/json' } }
    )
    if (res.data.code !== 0) {
      throw new Error(res.data.msg)
    }
  } catch (err) {
    ElMessage.error('保存失败：' + err.message)
    throw err // 抛出错误，让上层处理
  }
}

// 7. 发布文章（修改文章status状态，对接后台发布接口）
const handlePublish = async () => {
  // 增加防护：如果isShare=1，直接提示不执行发布
  if (currentEssay.value.isShare === 1) {
    ElMessage.warning('已分享的文章不可重复发布')
    return
  }

  try {
    // 模拟调用发布接口，传入文章id和发布状态
    const res = await axios.post(
      '/publishEssay',
      { id: currentEssay.value.id, status: 1 }, // status=1 标记为已发布
      { headers: { 'Content-Type': 'application/json' } }
    )
    if (res.data.code === 0) {
      ElMessage.success('文章发布成功！')
      // 刷新文章列表
      fetchMyEssayList()
    } else {
      ElMessage.error('发布失败：' + res.data.msg)
    }
  } catch (err) {
    ElMessage.error('发布接口异常：' + err.message)
  }
}

// 8. 删除文章（弹窗确认，对接后台删除接口）
const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      '此操作将永久删除该文章，是否继续？',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 调用后台删除接口
    const res = await axios.post(
      '/deleteEssay',
      { id: currentEssay.value.id },
      { headers: { 'Content-Type': 'application/json' } }
    )

    if (res.data.code === 0) {
      ElMessage.success('文章删除成功！')
      // 重置当前选中文章和内容，刷新列表
      currentEssay.value = null
      essayContent.value = ''
      originContent.value = ''
      currentTitle.value = ''
      originTitle.value = ''
      fetchMyEssayList()
    } else {
      ElMessage.error('删除失败：' + res.data.msg)
    }
  } catch (err) {
    // 补充：判断是否是取消操作（ElMessageBox的cancel类型）
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
}

/* 左侧侧边栏 */
.left-sidebar {
  width: 300px;
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  overflow-y: auto;
  /* 修复：设置flex布局，让分页栏固定在底部 */
  display: flex;
  flex-direction: column;
  justify-content: space-between;
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
  /* 修复：给列表留出分页栏的空间 */
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
  padding-right: 60px;
}

.essay-item:hover {
  background-color: #e3f2fd;
}

.essay-item.active {
  background-color: #3498db;
  color: #fff;
}

.no-data {
  text-align: center;
  padding: 20px;
  color: #95a5a6;
  font-size: 1rem;
}

/* 修复：分页栏样式优化 */
.list-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid #eee;
  margin-top: auto;
  /* 固定在左侧底部 */
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

/* 新增：标题输入框样式 */
.title-input {
  width: 400px;
  font-size: 1.6rem;
  font-weight: 600;
  color: #2c3e50;
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
  padding: 2px 3px;
  cursor: pointer;
  border-radius: 2px;
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

/* 富文本编辑器容器 */
.editor-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-radius: 4px;
  overflow: hidden;
  min-height: 300px;
}

#editor-toolbar {
  border-bottom: 1px solid #eee;
  padding: 8px 10px;
  background-color: #fafafa;
  min-height: 40px;
}

#editor-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  min-height: 200px;
}

/* 文章预览区 */
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
  white-space: pre-wrap;
  word-break: break-all;
}

.empty-tip {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #95a5a6;
  font-size: 1.2rem;
}

/* 兼容wangEditor样式 */
:deep(.w-e-toolbar) {
  border: none !important;
  flex-wrap: wrap;
  gap: 5px;
}

:deep(.w-e-text-container) {
  border: none !important;
  height: 100% !important;
}

:deep(.w-e-menu) {
  margin: 0 !important;
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

  /* 整体容器改为上下布局，高度自适应 */
  .create-space-container {
    flex-direction: column;
    height: auto;
    padding: 10px;
    gap: 15px;
  }

  /* 左侧侧边栏占满宽度，高度自适应 */
  .left-sidebar {
    width: 100%;
    height: auto;
    padding: 15px;
    max-height: 40vh;
    /* 限制侧边栏高度，避免占满屏幕 */
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

  /* 右侧内容区适配 */
  .right-content {
    padding: 15px;
    min-height: 50vh;
    /* 保证内容区最小高度 */
  }

  .content-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
    margin-bottom: 15px;
    padding-bottom: 15px;
  }

  /* 标题输入框适配宽度 */
  .title-input {
    width: 100%;
    font-size: 1.2rem;
  }

  .content-header h3 {
    font-size: 1.2rem;
  }

  /* 操作按钮换行，适配移动端 */
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

  /* 编辑器/预览区适配 */
  .editor-container {
    min-height: 200px;
  }

  #editor-toolbar {
    padding: 5px 8px;
    min-height: 35px;
  }

  #editor-content {
    padding: 15px;
    min-height: 150px;
  }

  .content-body {
    padding: 15px;
  }

  .essay-content {
    font-size: 0.9rem;
    line-height: 1.6;
  }

  .empty-tip {
    font-size: 1rem;
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

  /* 分页栏字体缩小 */
  .total {
    font-size: 12px;
  }

  .pagination-btns el-button {
    width: 32px;
    height: 32px;
    padding: 0;
  }

  /* 新建文章弹窗宽度适配 */
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

  :deep(.w-e-toolbar) {
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 5px;
  }
}
</style>