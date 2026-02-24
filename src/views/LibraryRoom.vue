<template>
  <div class="library-room" :class="['theme-' + currentTheme]">
  <nav class="icon-bar">
    <div class="icon-group">
      <button 
        class="icon-btn" 
        :class="{ active: activePanel === 'toc' }"
        @click="togglePanel('toc')"
        title="目录"
      >
        <svg viewBox="0 0 24 24" width="20" height="20">
          <path fill="currentColor" d="M3 3h18v2H3V3m0 4h18v2H3V7m0 4h18v2H3v-2m0 4h18v2H3v-2m0 4h18v2H3v-2z"/>
        </svg>
      </button>
      
      <button 
        class="icon-btn" 
        :class="{ active: activePanel === 'settings' }"
        @click="togglePanel('settings')"
        title="排版"
      >
        <svg viewBox="0 0 24 24" width="20" height="20">
          <path fill="currentColor" d="M12 15.5A3.5 3.5 0 0 1 8.5 12 3.5 3.5 0 0 1 12 8.5a3.5 3.5 0 0 1 3.5 3.5 3.5 3.5 0 0 1-3.5 3.5m7.43-2.53c.04-.32.07-.64.07-.97 0-.33-.03-.66-.07-1l2.11-1.63c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.3-.61-.22l-2.49 1c-.52-.4-1.08-.73-1.69-.98l-.38-2.65A.488.488 0 0 0 14 2h-4c-.25 0-.46.18-.5.42l-.38 2.65c-.61.25-1.17.59-1.69.98l-2.49-1c-.23-.09-.49 0-.61.22l-2 3.46c-.13.22-.07.49.12.64l2.11 1.63c-.04.34-.07.67-.07 1 0 .33.03.66.07.97l-2.11 1.63c-.19.15-.24.42-.12.64l2 3.46c.12.22.39.3.61.22l2.49-1.01c.52.4 1.08.73 1.69.98l.38 2.65c.04.24.25.42.5.42h4c.25 0 .46-.18.5-.42l.38-2.65c.61-.25 1.17-.59 1.69-.98l2.49 1.01c.22.08.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64l-2.11-1.63z"/>
        </svg>
      </button>
      
      <button 
        class="icon-btn" 
        :class="{ active: activePanel === 'theme' }"
        @click="togglePanel('theme')"
        title="主题"
      >
        <svg viewBox="0 0 24 24" width="20" height="20">
          <path fill="currentColor" d="M12 2a10 10 0 0 0 0 20 1 1 0 0 0 1-1v-3a1 1 0 0 0-1-1 4 4 0 0 1 0-8 1 1 0 0 0 1-1V3a1 1 0 0 0-1-1z"/>
        </svg>
      </button>

      <!-- 新增：曲库按钮 -->
      <button 
        class="icon-btn" 
        :class="{ active: activePanel === 'music' }"
        @click="togglePanel('music')"
        title="曲库"
      >
        <svg viewBox="0 0 24 24" width="20" height="20">
          <path fill="currentColor" d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6zm-2 16c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z"/>
        </svg>
      </button>
    </div>
    
    <div class="icon-group bottom">
      <button class="icon-btn" @click="toggleFullscreen" title="全屏">
        <svg viewBox="0 0 24 24" width="20" height="20">
          <path fill="currentColor" d="M5 5h5v2H7v3H5V5m9 0h5v5h-2V7h-3V5m3 9h2v5h-5v-2h3v-3m-7 3v2H5v-5h2v3h3z"/>
        </svg>
      </button>
    </div>
  </nav>

    <!-- 中间栏：可展开的目录/设置/主题/曲库 -->
    <aside class="drawer-panel" :class="{ 
      'is-open': activePanel !== null,
      'mobile-open': isMobile && activePanel !== null 
    }">
      <!-- 目录面板 -->
      <div v-if="activePanel === 'toc'" class="panel-content">
        <div class="panel-header">
          <h3>目录</h3>
          <el-button type="primary" circle size="small" @click="showUploadDialog = true">+</el-button>
        </div>
        <div class="toc-list" ref="tocRef">
          <div 
            v-for="(item, index) in tocItems" 
            :key="index"
            class="toc-item"
            :class="{ active: currentChapter === item.chapter }"
            :style="{ paddingLeft: item.level * 1 + 'rem' }"
            @click="jumpToChapter(item)"
          >
            <span class="toc-title">{{ item.title }}</span>
            <!-- 非Public路径显示删除按钮 -->
            <button 
              v-if="!isPublicPath(item.path)" 
              class="toc-delete-btn"
              @click.stop="confirmDeleteBook(item)"
              title="删除书籍"
            >
              ×
            </button>
          </div>
        </div>
      </div>

      <!-- 排版设置面板 -->
      <div v-if="activePanel === 'settings'" class="panel-content">
        <div class="panel-header">
          <h3>排版</h3>
          <button class="close-btn" @click="closePanel">×</button>
        </div>
        
        <div class="settings-body">
          <div class="setting-block">
            <label>字体</label>
            <div class="font-options">
              <button 
                v-for="font in fontOptions" 
                :key="font.value"
                class="font-btn"
                :class="{ active: settings.fontFamily === font.value }"
                :style="{ fontFamily: font.value }"
                @click="setFont(font.value)"
              >
                {{ font.label }}
              </button>
            </div>
          </div>

          <div class="setting-block">
            <label>字号</label>
            <div class="size-slider">
              <span class="size-small">A</span>
              <input 
                type="range" 
                v-model.number="settings.fontSize" 
                min="12" 
                max="24" 
                step="1"
                @input="saveSettings"
              />
              <span class="size-large">A</span>
            </div>
            <div class="size-value">{{ settings.fontSize }}px</div>
          </div>

          <div class="setting-block">
            <label>行高</label>
            <div class="line-height-options">
              <button 
                v-for="lh in lineHeightOptions" 
                :key="lh"
                class="lh-btn"
                :class="{ active: settings.lineHeight === lh }"
                @click="setLineHeight(lh)"
              >
                <div class="lh-preview" :style="{ lineHeight: lh }">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </button>
            </div>
          </div>

          <div class="setting-block">
            <label>边距</label>
            <div class="margin-options">
              <button 
                v-for="margin in marginOptions" 
                :key="margin.value"
                class="margin-btn"
                :class="{ active: settings.margin === margin.value }"
                @click="setMargin(margin.value)"
              >
                <div class="margin-preview" :style="{ padding: margin.preview }">
                  <div></div>
                </div>
                <span>{{ margin.label }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 主题面板 -->
      <div v-if="activePanel === 'theme'" class="panel-content">
        <div class="panel-header">
          <h3>主题</h3>
          <button class="close-btn" @click="closePanel">×</button>
        </div>
        
        <div class="theme-grid">
          <div 
            v-for="theme in themes" 
            :key="theme.name"
            class="theme-card"
            :class="{ active: currentTheme === theme.name }"
            @click="setTheme(theme)"
          >
            <div class="theme-preview" :style="{ background: theme.colors.bg, color: theme.colors.text }">
              <span>Aa</span>
            </div>
            <span class="theme-name">{{ theme.label }}</span>
          </div>
        </div>
      </div>

      <!-- 新增：曲库面板 -->
      <div v-if="activePanel === 'music'" class="panel-content">
        <div class="panel-header">
          <h3>曲库</h3>
          <button class="close-btn" @click="closePanel">×</button>
        </div>
        
        <div class="music-list" ref="musicRef">
          <!-- 加载状态 -->
          <div v-if="musicLoading" class="music-loading">加载中...</div>
          
          <!-- 空状态 -->
          <div v-if="!musicLoading && songList.length === 0" class="music-empty">
            <span>暂无音乐文件</span>
          </div>
          
          <!-- 音乐列表 -->
          <div 
            v-for="(song, index) in songList" 
            :key="index"
            class="music-item"
            :class="{ active: currentPlaySong?.path === song.path }"
          >
            <span class="music-title">{{ song.name }}</span>
            <!-- 播放/暂停按钮 -->
            <button 
              class="music-play-btn"
              @click.stop="toggleMusicPlay(song)"
              title="播放/暂停"
            >
              <svg v-if="currentPlaySong?.path !== song.path || !isMusicPlaying" viewBox="0 0 24 24" width="16" height="16">
                <path fill="currentColor" d="M8 5v14l11-7z"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" width="16" height="16">
                <path fill="currentColor" d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- 音乐播放控制条（底部固定） -->
        <div class="music-player-bar" v-if="currentPlaySong">
          <div class="player-info">
            <span class="now-playing">正在播放：</span>
            <span class="playing-name">{{ currentPlaySong.name }}</span>
          </div>
          <div class="player-controls">
            <button class="player-btn" @click="stopMusicPlay" title="停止播放">
              <svg viewBox="0 0 24 24" width="16" height="16">
                <path fill="currentColor" d="M6 6h12v12H6z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </aside>

    <!-- 右侧主阅读区 -->
    <main class="reader-main">
      <!-- 顶部工具栏 -->
      <header class="reader-toolbar" v-if="currentBook">
        <div class="toolbar-left">
          <button class="tool-btn" @click="prevChapter" :disabled="currentChapter <= 1">
            <svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>
          </button>
          <div class="chapter-indicator">
            <input 
              type="number" 
              v-model.number="currentChapterInput" 
              :min="1" 
              :max="totalChapters"
              class="chapter-input"
              @blur="handleChapterInput"
              @keyup.enter="handleChapterInput"
            />
            / {{ totalChapters }}
          </div>
          <button class="tool-btn" @click="nextChapter" :disabled="currentChapter >= totalChapters">
            <svg viewBox="0 0 24 24" width="18" height="18"><path fill="currentColor" d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>
          </button>
        </div>
        
        <div class="toolbar-center">
          <h1 class="book-title">{{ formatBookName(currentBook) }}</h1>
        </div>

        <div class="toolbar-right">
          <span class="progress-text">{{ readingProgress }}%</span>
        </div>
      </header>

      <!-- 书籍内容区 -->
      <div class="reader-content-wrapper" ref="readerWrapper">
        <div v-if="!currentBook" class="empty-state">
          <div class="empty-icon">📚</div>
          <h2>选择一本书开始阅读</h2>
          <p>点击左侧目录图标浏览书库</p>
        </div>

        <div v-else class="reader-scroll-area" ref="scrollArea" @scroll="handleScroll">
          <article class="reading-article" :style="articleStyles">
              <!-- 章节加载中提示 -->
            <div v-if="chapterLoading" class="chapter-loading">
              章节加载中...
            </div>
            <div class="chapter-body" v-html="currentContent" ref="chapterBody"></div>

            <div class="chapter-footer">
              <div class="page-divider">
                <span>第 {{ currentChapter }} 页结束</span>
              </div>
              <div class="next-chapter-prompt" v-if="currentChapter < totalChapters">
                <button @click="nextChapter" class="next-btn">
                  下一章：{{ nextChapterTitle }}
                  <svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/></svg>
                </button>
              </div>
            </div>
          </article>
        </div>
      </div>

      <!-- 底部进度条 -->
      <div class="reading-progress-bar" v-if="currentBook">
        <div class="progress-fill" :style="{ width: readingProgress + '%' }"></div>
      </div>
    </main>

    <!-- 移动端遮罩 -->
    <div 
      class="mobile-overlay" 
      v-if="isMobile && activePanel !== null"
      @click="closePanel"
    ></div>

    <!-- 快速导航（右下角） -->
    <div class="quick-nav" v-if="currentBook">
      <button class="quick-btn" @click="scrollToTop" title="回到顶部">
        <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M7.41 15.41L12 10.83l4.59 4.58L18 14l-6-6-6 6z"/></svg>
      </button>
    </div>

    <!-- 上传本地书籍弹窗 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传本地书籍"
      width="400px"
      destroy-on-close
    >
      <div class="upload-container">
        <el-upload
          class="upload-demo"
          drag
          action="#"
          :auto-upload="false"
          :file-list="uploadFileList"
          accept=".epub"
          :on-change="handleFileChange"
        >
          <i class="el-icon-upload"></i>
          <div class="el-upload__text">将EPUB文件拖到此处，或<em>点击选择</em></div>
        </el-upload>
        <el-button
          type="primary"
          class="upload-btn"
          @click="uploadBook"
          :disabled="!uploadFileList.length"
        >
          上传书籍
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox, ElDialog, ElUpload, ElButton } from 'element-plus'
import axios from 'axios'

// 响应式状态
const isMobile = ref(false)
const activePanel = ref(null) // 'toc', 'settings', 'theme', 'music'

// 书籍数据
const books = ref([])
const currentBook = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)
const totalBooks = ref(0)
const loading = ref(false)

// 阅读状态
const currentContent = ref('')
const currentChapter = ref(1)
const totalChapters = ref(1)
const currentChapterTitle = ref('')
const nextChapterTitle = ref('') 
const readingProgress = ref(0)
const tocItems = ref([])
const chapterLoading = ref(false)

// 阅读设置
const settings = ref({
  fontFamily: "'Noto Serif SC', serif",
  fontSize: 18,
  lineHeight: 1.8,
  margin: 'normal' // narrow, normal, wide
})

// 上传相关
const showUploadDialog = ref(false)
const uploadFileList = ref([])
const currentUploadFile = ref(null)

// 新增：音乐相关状态
const songList = ref([]) // 音乐列表
const musicLoading = ref(false) // 音乐加载状态
const currentPlaySong = ref(null) // 当前播放的音乐
const isMusicPlaying = ref(false) // 音乐播放状态
const audioPlayer = ref(null) // 音频播放器实例

const fontOptions = [
  { label: '宋体', value: "'Noto Serif SC', serif" },
  { label: '黑体', value: "'Noto Sans SC', sans-serif" },
  { label: '楷体', value: "'LXGW WenKai', serif" },
  { label: '系统', value: "system-ui, -apple-system, sans-serif" }
]

const lineHeightOptions = [1.4, 1.6, 1.8, 2.0, 2.2]

const marginOptions = [
  { label: '窄', value: 'narrow', preview: '1rem' },
  { label: '中', value: 'normal', preview: '2rem' },
  { label: '宽', value: 'wide', preview: '4rem' }
]

// 主题配置
const themes = [
  {
    name: 'light',
    label: '白昼',
    colors: { bg: '#ffffff', text: '#2c3e50', sidebar: '#f5f5f5' }
  },
  {
    name: 'sepia',
    label: ' sepia',
    colors: { bg: '#f4ecd8', text: '#433422', sidebar: '#e9dfc8' }
  },
  {
    name: 'dark',
    label: '暗夜',
    colors: { bg: '#1a1a1a', text: '#d1d5db', sidebar: '#2d2d2d' }
  },
  {
    name: 'green',
    label: '护眼',
    colors: { bg: '#c7edcc', text: '#2c3e50', sidebar: '#b8e0bd' }
  },
  {
    name: 'blue',
    label: '海蓝',
    colors: { bg: '#e3f2fd', text: '#1565c0', sidebar: '#bbdefb' }
  }
]

const currentTheme = ref('light')

// 计算样式
const articleStyles = computed(() => {
  const theme = themes.find(t => t.name === currentTheme.value)
  const marginMap = { narrow: '4%', normal: '8%', wide: '15%' }
  
  return {
    fontFamily: settings.value.fontFamily,
    fontSize: settings.value.fontSize + 'px',
    lineHeight: settings.value.lineHeight,
    paddingLeft: marginMap[settings.value.margin] || '8%',
    paddingRight: marginMap[settings.value.margin] || '8%',
    backgroundColor: 'transparent',
    color: theme?.colors.text || '#2c3e50',
    maxWidth: settings.value.margin === 'wide' ? '720px' : 'none'
  }
})

// 检测移动端
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
  if (isMobile.value) {
    activePanel.value = null
  }
}

// 面板控制
const togglePanel = (panel) => {
  if (activePanel.value === panel) {
    activePanel.value = null
  } else {
    activePanel.value = panel
    if (panel === 'toc' && tocItems.value.length === 0) {
      loadToc()
    }
    // 新增：打开曲库面板时加载音乐列表
    if (panel === 'music' && songList.value.length === 0) {
      fetchSongList()
    }
  }
}

// 新增响应式变量
const currentChapterInput = ref(1)

// 监听 currentChapter 变化，同步到输入框
watch(currentChapter, (newVal) => {
  currentChapterInput.value = newVal
}, { immediate: true })

// 输入框处理函数
const handleChapterInput = async () => {
  const inputValue = currentChapterInput.value
  
  // 边界校验
  if (!inputValue || isNaN(inputValue)) {
    ElMessage.warning('请输入有效的章节号')
    currentChapterInput.value = currentChapter.value // 恢复为当前值
    return
  }
  
  if (inputValue < 1) {
    ElMessage.warning('章节号不能小于1')
    currentChapterInput.value = currentChapter.value
    return
  }
  
  if (inputValue > totalChapters.value) {
    ElMessage.warning(`章节号不能大于 ${totalChapters.value}`)
    currentChapterInput.value = currentChapter.value
    return
  }
  
  // 相同值不重复加载
  if (inputValue === currentChapter.value) return
  
  // 加载章节
  try {
    await loadChapter(inputValue)
  } catch (e) {
    // 加载失败，恢复输入框值
    currentChapterInput.value = currentChapter.value
  }
}

const closePanel = () => {
  activePanel.value = null
}

// 判断是否为Public路径
const isPublicPath = (path) => {
  if (!path) return false
  // 检测路径是否包含public目录（不区分大小写）
  return path.toLowerCase().includes('public')
}

// 处理上传文件选择
const handleFileChange = (file) => {
  // 只保留最新选择的一个文件
  uploadFileList.value = [file]
  currentUploadFile.value = file.raw
}

// 上传书籍接口调用
const uploadBook = async () => {
  if (!currentUploadFile.value) {
    ElMessage.warning('请选择要上传的EPUB文件')
    return
  }

  const formData = new FormData()
  formData.append('file', currentUploadFile.value)

  try {
    const response = await axios.post('/uploadBook', formData, {
      headers: {

        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.code === 0) {
      ElMessage.success('书籍上传成功！')
      showUploadDialog.value = false
      uploadFileList.value = []
      // 刷新书籍列表
      fetchBooks(1)
    } else {
      ElMessage.error(`上传失败：${response.data.msg}`)
    }
  } catch (error) {
    console.error('上传书籍失败:', error)
    ElMessage.error(`上传失败：${error.message}`)
  }
}

// 确认删除书籍
const confirmDeleteBook = async (item) => {
  try {
    await ElMessageBox.confirm(
      `是否确认删除《${item.title}》？`,
      '删除确认',
      {
        confirmButtonText: '是',
        cancelButtonText: '否',
        type: 'warning'
      }
    )
    await deleteBook(item.title)
  } catch (err) {
    ElMessage.info('已取消删除')
  }
}

// 删除书籍接口调用
const deleteBook = async (bookName) => {
  try {
    // 编码书名（处理中文/特殊字符）
    const encodedName = encodeURIComponent(bookName)
    const response = await axios.get(`/delBook?name=${encodedName}`, {
      headers: {
     
      }
    })

    if (response.data.code === 0) {
      ElMessage.success('书籍删除成功！')
      // 刷新书籍列表
      fetchBooks(1)
      // 如果删除的是当前阅读的书籍，清空状态
      if (currentBook.value && formatBookName(currentBook.value) === bookName) {
        currentBook.value = null
        currentContent.value = ''
        currentChapter.value = 1
        totalChapters.value = 1
        readingProgress.value = 0
      }
    } else {
      ElMessage.error(`删除失败：${response.data.msg}`)
    }
  } catch (error) {
    console.error('删除书籍失败:', error)
    ElMessage.error(`删除失败：${error.message}`)
  }
}

// 获取书籍列表
const fetchBooks = async (page = 1) => {
  if (loading.value) return
  loading.value = true
  
  try {
    const response = await axios.post('/listBooks', {
      pageNo: page,
      pageSize: pageSize.value
    })
    
    if (response.data.code === 0) {
      const processedImages = response.data.data.urls.map(path => 
        path.replace(/\\/g, '/')
      )
      
      if (page === 1) {
        books.value = processedImages
      } else {
        books.value.push(...processedImages)
      }
      totalBooks.value = response.data.data.total
      currentPage.value = response.data.data.pageNo
      
      tocItems.value = processedImages.map((book, index) => ({
        title: formatBookName(book),
        chapter: index + 1,
        level: 0,
        path: book
      }))
    }
  } catch (error) {
    console.error('获取书籍列表失败:', error)
    const mockBooks = [
      'C:/Users/Admin/Documents/books/有毒的逻辑：为何有说服力的话反而不可信.epub'
    ]
    books.value = mockBooks
    totalBooks.value = mockBooks.length
    tocItems.value = mockBooks.map((book, index) => ({
      title: formatBookName(book),
      chapter: index + 1,
      level: 0,
      path: book
    }))
  } finally {
    loading.value = false
  }
}

// 选择书籍
const selectBook = async (bookPath) => {
  currentBook.value = bookPath
  currentChapter.value = 1
  await loadChapter(1) 
  if (isMobile.value) {
    closePanel()
  }
}

// 加载章节
const loadChapter = async (chapterNum) => {
  // 无书籍路径时直接返回，避免无效请求
  if (!currentBook.value) return
  try {
    chapterLoading.value = true // 开启章节加载状态
    // 调用Java加载章节接口，入参：书籍路径+章节号
    const res = await axios.post('/loadChapter', {
      bookPath: currentBook.value, // 选中的书籍完整路径（兼容Windows/Linux）
      chapterNum: chapterNum       // 要加载的章节号
    })

    if (res.data.code === 0) {
      // 解构接口返回的章节数据
       const {  chapterTitle, content, totalChapters: total, nextChapterTitle: nextTitle  // 重命名，避免与 nextChapterTitle ref 冲突
      } = res.data.data

      currentContent.value = content        
      currentChapter.value = chapterNum     
      currentChapterTitle.value = chapterTitle
      nextChapterTitle.value = nextTitle || '已是最后一章' // 使用重命名后的变量
      totalChapters.value = total

      // 原有逻辑：章节加载后滚动到顶部
      nextTick(() => {
        const scrollArea = document.querySelector('.reader-scroll-area')
        if (scrollArea) scrollArea.scrollTop = 0
      })
    } else {
      // 接口返回失败（如章节不存在），给出错误提示
      ElMessage.error(`加载章节失败：${res.data.msg}`)
   
    }
  } catch (e) {
    // 网络异常/接口报错，统一捕获
    ElMessage.error(`章节接口请求失败：${e.message}`)
  } finally {
    chapterLoading.value = false // 关闭章节加载状态
  }
}

// 目录跳转
const jumpToChapter = (item) => {
  if (item.path && item.path !== currentBook.value) {
    selectBook(item.path)
  } else {
    loadChapter(item.chapter)
  }
  closePanel()
}

const loadToc = () => {
  // 实际应用中这里应该解析EPUB的目录
  if (tocItems.value.length === 0) {
    fetchBooks(1)
  }
}

// 阅读导航
const prevChapter = () => {
  if (currentChapter.value > 1) {
    loadChapter(currentChapter.value - 1)
  }
}

const nextChapter = () => {
  if (currentChapter.value < totalChapters.value) {
    loadChapter(currentChapter.value + 1)
  }
}

// 滚动处理
const handleScroll = (e) => {
  const { scrollTop, scrollHeight, clientHeight } = e.target
  readingProgress.value = Math.round((scrollTop / (scrollHeight - clientHeight)) * 100) || 0
  
  // 接近底部自动加载下一章
  if (scrollHeight - scrollTop - clientHeight < 100 && !loading.value) {
    // 可以实现连续滚动加载
  }
}

const scrollToTop = () => {
  const scrollArea = document.querySelector('.reader-scroll-area')
  if (scrollArea) {
    scrollArea.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// 设置调整
const setFont = (font) => {
  settings.value.fontFamily = font
  saveSettings()
}

const setLineHeight = (lh) => {
  settings.value.lineHeight = lh
  saveSettings()
}

const setMargin = (margin) => {
  settings.value.margin = margin
  saveSettings()
}

const setTheme = (theme) => {
  currentTheme.value = theme.name
  // 应用CSS变量
  const root = document.documentElement
  root.style.setProperty('--reader-bg', theme.colors.bg)
  root.style.setProperty('--reader-text', theme.colors.text)
  root.style.setProperty('--sidebar-bg', theme.colors.sidebar)
  saveSettings()
}

const saveSettings = () => {
  localStorage.setItem('flowReaderSettings', JSON.stringify({
    ...settings.value,
    theme: currentTheme.value
  }))
}

const loadSettings = () => {
  const saved = localStorage.getItem('flowReaderSettings')
  if (saved) {
    const parsed = JSON.parse(saved)
    Object.assign(settings.value, parsed)
    currentTheme.value = parsed.theme || 'light'
    setTheme(themes.find(t => t.name === currentTheme.value) || themes[0])
  }
}

// 全屏
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

// 工具函数
const formatBookName = (path) => {
  if (!path) return ''
  const normalizedPath = path.replace(/\\/g, '/')
  const filename = normalizedPath.split('/').pop()
  return filename.replace(/\.epub$/i, '').replace(/\s*\([^)]*Library\)\s*$/i, '')
}

// 新增：获取音乐列表
const fetchSongList = async () => {
  if (musicLoading.value) return
  musicLoading.value = true
  
  try {
    const response = await axios.get('/listSongs', {

    })
    
    if (response.data.code === 0) {
      songList.value = response.data.data || []
    } else {
      ElMessage.error(`获取曲库失败：${response.data.msg}`)
    }
  } catch (error) {
    ElMessage.error(`获取曲库失败：${error.message}`)
  } finally {
    musicLoading.value = false
  }
}

// 新增：播放/暂停音乐
const toggleMusicPlay = async (song) => {
  try {
    // 【关键1】空值校验：当前播放的是目标歌曲，但实例未创建 → 直接返回（避免调用null的方法）
    if (currentPlaySong.value?.path === song.path && !audioPlayer.value) {
      ElMessage.warning('音频加载中，请稍候');
      return;
    }

    // 点击当前正在播放/暂停的歌曲 → 切换状态
    if (currentPlaySong.value?.path === song.path) {
      if (isMusicPlaying.value) {
        audioPlayer.value.pause(); // 实例已存在，可安全调用
        isMusicPlaying.value = false;
      } else {
        audioPlayer.value.play();
        isMusicPlaying.value = true;
      }
      return;
    }

    // 播放新歌曲：先停止原有音频（若有实例），避免多音频同时播放
    if (audioPlayer.value) {
      audioPlayer.value.pause();
      isMusicPlaying.value = false; // 【关键2】状态同步，避免残留播放状态
    }

    // 标记当前播放歌曲，提前置为加载状态
    currentPlaySong.value = song;
    ElMessage.info('正在加载音频...');

    // 获取音乐文件（二进制Blob）
    const encodedPath = encodeURIComponent(song.path);
    const response = await axios.get(`/getSong?path=${encodedPath}`, {

      responseType: 'blob' // 必须指定，否则会解析为乱码
    });

    // 【关键3】销毁旧的音频URL，避免内存泄漏
    if (audioPlayer.value) {
      URL.revokeObjectURL(audioPlayer.value.src);
    }

    // 创建新的音频实例并赋值（确保实例初始化后再使用）
    const audioUrl = URL.createObjectURL(response.data);
    audioPlayer.value = new Audio(audioUrl); // 此时实例才被创建，非null

    // 播放音频（实例已存在，安全调用）
    await audioPlayer.value.play();
    isMusicPlaying.value = true;

    // 监听音乐结束 → 重置状态
    audioPlayer.value.onended = () => {
      isMusicPlaying.value = false;
    };

    // 监听音频加载错误 → 清空状态并提示
    audioPlayer.value.onerror = (e) => {
      ElMessage.error(`音频加载失败：${e.message || '未知错误'}`);
      isMusicPlaying.value = false;
      currentPlaySong.value = null;
      audioPlayer.value = null; // 销毁错误实例
    };

  } catch (error) {
    console.error('播放音乐失败:', error);
    ElMessage.error(`播放失败：${error.message || '网络/接口异常'}`);
    // 【关键4】异常兜底：重置所有状态，避免残留null实例
    isMusicPlaying.value = false;
    currentPlaySong.value = null;
    audioPlayer.value = null;
  }
};

// 新增：停止播放音乐
const stopMusicPlay = () => {
  if (audioPlayer.value) { // 仅当实例存在时执行
    audioPlayer.value.pause();
    audioPlayer.value.currentTime = 0; // 重置播放进度
    URL.revokeObjectURL(audioPlayer.value.src); // 释放URL资源
  }
  // 强制重置状态，与实例同步
  isMusicPlaying.value = false;
};

// 生命周期
onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  loadSettings()
  fetchBooks(1)
  
  // 键盘快捷键
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') prevChapter()
    if (e.key === 'ArrowRight') nextChapter()
    if (e.key === 'Escape') closePanel()
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile);
  // 【关键】彻底销毁音频实例和资源
  if (audioPlayer.value) {
    audioPlayer.value.pause();
    URL.revokeObjectURL(audioPlayer.value.src); // 释放创建的Blob URL
    audioPlayer.value = null; // 置空实例
  }
  // 重置所有音乐状态
  isMusicPlaying.value = false;
  currentPlaySong.value = null;
});
</script>

<style>
/* CSS变量 */
:root {
  --icon-bar-width: 48px;
  --drawer-width: 280px;
  --reader-bg: #ffffff;
  --reader-text: #2c3e50;
  --sidebar-bg: #f5f5f5;
  --border-color: #e0e0e0;
  --accent-color: #4f46e5;
  --hover-bg: rgba(0, 0, 0, 0.05);
}

/* 基础布局 */
.library-room {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--reader-bg);
  color: var(--reader-text);
}

/* 极左图标栏 */
.icon-bar {
  width: var(--icon-bar-width);
  min-width: var(--icon-bar-width);
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem 0;
  z-index: 30;
}

.icon-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  width: 100%;
  align-items: center;
}

.icon-group.bottom {
  margin-top: auto;
}

.icon-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: var(--hover-bg);
  color: var(--accent-color);
}

.icon-btn.active {
  background: var(--accent-color);
  color: white;
}

/* 中间抽屉面板 */
.drawer-panel {
  width: 0;
  min-width: 0;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border-color);
  overflow: hidden;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
}

.drawer-panel.is-open {
  width: var(--drawer-width);
  min-width: var(--drawer-width);
}

.panel-content {
  width: var(--drawer-width);
  height: 100%;
  display: flex;
  flex-direction: column;
  opacity: 0;
  transition: opacity 0.2s;
}

.drawer-panel.is-open .panel-content {
  opacity: 1;
  transition-delay: 0.1s;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.panel-header h3 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.25rem;
  line-height: 1;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: var(--hover-bg);
}

/* 目录列表 */
.toc-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

/* 目录列表项 - 新增相对定位，为删除按钮层级做铺垫 */
.toc-item {
  padding: 0.625rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9375rem;
  line-height: 1.5;
  color: var(--reader-text);
  transition: all 0.15s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative; /* 新增：作为删除按钮的定位参考 */
  gap: 0.5rem; /* 新增：标题和按钮之间留固定间距，避免挤在一起 */
}

.toc-item:hover {
  background: var(--hover-bg);
}

.toc-item.active {
  background: var(--accent-color);
  color: #fff; /* 建议改回白色，深色背景配白色文字更醒目，原黑色和主色冲突 */
}

/* 目录项标题 - 单独抽离，确保文字溢出省略生效 */
.toc-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 目录项删除按钮 - 核心调整：提高层级、优化定位、修复遮盖 */
.toc-delete-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  color: #ff4d4f;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.2s ease; /* 优化过渡流畅度 */
  flex-shrink: 0; /* 新增：禁止按钮被挤压变形 */
  z-index: 20; /* 核心：提高层级，避免被背景层遮盖 */
}

/* 鼠标悬浮/选中项 都显示删除按钮，保持交互一致性 */
.toc-item:hover .toc-delete-btn,
.toc-item.active .toc-delete-btn {
  opacity: 1;
}

/* 按钮悬浮样式 - 优化背景，适配active状态的主色背景 */
.toc-delete-btn:hover {
  background: rgba(255, 77, 79, 0.2); /* 提高透明度，适配各种背景 */
  color: #fff; /* 按钮悬浮时文字变白，更醒目 */
}

/* 适配深色主题/active状态的按钮颜色，避免视觉冲突 */
.theme-dark .toc-delete-btn,
.toc-item.active .toc-delete-btn {
  color: #ff6b6b; /* 浅一点的红色，适配深色/主色背景 */
}
.theme-dark .toc-delete-btn:hover,
.toc-item.active .toc-delete-btn:hover {
  background: rgba(255, 107, 107, 0.3);
  color: #fff;
}

.settings-body {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.setting-block {
  margin-bottom: 1.5rem;
}

.setting-block label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.75rem;
  color: #666;
}

/* 字体选项 */
.font-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.font-btn {
  padding: 0.625rem;
  border: 1px solid var(--border-color);
  background: var(--reader-bg);
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9375rem;
  transition: all 0.2s;
}

.font-btn.active {
  border-color: var(--accent-color);
  background: rgba(79, 70, 229, 0.1);
  color: var(--accent-color);
}

/* 字号滑块 */
.size-slider {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.size-small { font-size: 0.875rem; }
.size-large { font-size: 1.125rem; }

.size-slider input[type="range"] {
  flex: 1;
  height: 4px;
  -webkit-appearance: none;
  background: var(--border-color);
  border-radius: 2px;
  outline: none;
}

.size-slider input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: var(--accent-color);
  border-radius: 50%;
  cursor: pointer;
}

.size-value {
  text-align: center;
  font-size: 0.875rem;
  color: #666;
}

/* 行高选项 */
.line-height-options {
  display: flex;
  gap: 0.5rem;
}

.lh-btn {
  flex: 1;
  height: 48px;
  border: 1px solid var(--border-color);
  background: var(--reader-bg);
  border-radius: 6px;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lh-btn.active {
  border-color: var(--accent-color);
}

.lh-preview {
  display: flex;
  flex-direction: column;
  gap: 3px;
  width: 24px;
}

.lh-preview span {
  height: 2px;
  background: currentColor;
  border-radius: 1px;
}

/* 边距选项 */
.margin-options {
  display: flex;
  gap: 0.5rem;
}

.margin-btn {
  flex: 1;
  border: 1px solid var(--border-color);
  background: var(--reader-bg);
  border-radius: 6px;
  cursor: pointer;
  padding: 0.75rem 0.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: #666;
}

.margin-btn.active {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.margin-preview {
  width: 32px;
  height: 24px;
  border: 1px solid currentColor;
  display: flex;
  align-items: center;
  justify-content: center;
}

.margin-preview div {
  width: 60%;
  height: 4px;
  background: currentColor;
  border-radius: 2px;
}

/* 主题网格 */
.theme-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  padding: 1rem;
}

.theme-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.theme-preview {
  width: 100%;
  aspect-ratio: 4/3;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 600;
  border: 2px solid transparent;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.theme-card.active .theme-preview {
  border-color: var(--accent-color);
  transform: scale(1.05);
}

.theme-name {
  font-size: 0.875rem;
  color: #666;
}

/* 主阅读区 */
.reader-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--reader-bg);
  position: relative;
  overflow: hidden;
}

/* 顶部工具栏 */
.reader-toolbar {
  height: 56px;
  min-height: 56px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  background: var(--reader-bg);
}

.toolbar-left, .toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 100px;
}

.tool-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.tool-btn:hover:not(:disabled) {
  background: var(--hover-bg);
  color: var(--reader-text);
}

.tool-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.chapter-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #666;
}

.chapter-input {
  width: 50px;
  height: 28px;
  text-align: center;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: var(--reader-bg);
  color: var(--reader-text);
  font-size: 0.875rem;
  font-variant-numeric: tabular-nums;
  outline: none;
  transition: all 0.2s;
}

.chapter-input:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
}

/* 移除输入框的上下箭头（可选） */
.chapter-input::-webkit-outer-spin-button,
.chapter-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.toolbar-center {
  flex: 1;
  text-align: center;
  overflow: hidden;
}

.book-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--reader-text);
}

.progress-text {
  font-size: 0.875rem;
  color: #666;
  font-variant-numeric: tabular-nums;
}

/* 阅读内容区 */
.reader-content-wrapper {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.reader-scroll-area {
  height: 100%;
  overflow-y: auto;
  padding: 2rem 0;
}

.reading-article {
  max-width: 720px;
  margin: 0 auto;
  padding-bottom: 4rem;
}

.chapter-body {
  line-height: 1.8;
}

.chapter-body p {
  margin-bottom: 1.5em;
  text-align: justify;
  text-indent: 2em;
}

/* 章节底部 */
.chapter-footer {
  margin-top: 4rem;
  padding-top: 2rem;
}

.page-divider {
  text-align: center;
  position: relative;
  margin-bottom: 2rem;
}

.page-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--border-color);
}

.page-divider span {
  position: relative;
  background: var(--reader-bg);
  padding: 0 1rem;
  font-size: 0.875rem;
  color: #999;
}

.next-chapter-prompt {
  text-align: center;
}

.next-btn {
  padding: 0.875rem 1.5rem;
  border: 1px solid var(--border-color);
  background: var(--sidebar-bg);
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9375rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--reader-text);
  transition: all 0.2s;
}

.next-btn:hover {
  border-color: var(--accent-color);
  background: rgba(79, 70, 229, 0.05);
}

/* 进度条 */
.reading-progress-bar {
  height: 2px;
  background: var(--border-color);
  position: relative;
}

.progress-fill {
  height: 100%;
  background: var(--accent-color);
  transition: width 0.1s;
}

/* 快速导航 */
.quick-nav {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 20;
}

.quick-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  background: var(--reader-bg);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  transition: all 0.2s;
}

.quick-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
}

/* 空状态 */
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  text-align: center;
  padding: 2rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h2 {
  font-size: 1.25rem;
  color: var(--reader-text);
  margin-bottom: 0.5rem;
}

/* 上传相关样式 */
.upload-container {
  padding: 1rem 0;
}

.upload-btn {
  width: 100%;
  margin-top: 1rem;
}

/* 新增：音乐列表样式 */
.music-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.music-loading {
  padding: 2rem;
  text-align: center;
  color: #666;
  font-size: 0.9375rem;
}

.music-empty {
  padding: 2rem;
  text-align: center;
  color: #999;
  font-size: 0.9375rem;
}

.music-item {
  padding: 0.625rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9375rem;
  line-height: 1.5;
  color: var(--reader-text);
  transition: all 0.15s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.music-item:hover {
  background: var(--hover-bg);
}

.music-item.active {
  background: var(--accent-color);
  color: #fff;
}

.music-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.music-play-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  flex-shrink: 0;
  transition: all 0.2s;
}

.music-item:hover .music-play-btn,
.music-item.active .music-play-btn {
  color: var(--accent-color);
}

.music-item.active .music-play-btn {
  color: #fff;
}

.music-play-btn:hover {
  background: rgba(79, 70, 229, 0.1);
}

.music-item.active .music-play-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 新增：音乐播放控制条 */
.music-player-bar {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--sidebar-bg);
}

.player-info {
  flex: 1;
  overflow: hidden;
}

.now-playing {
  font-size: 0.75rem;
  color: #666;
  margin-right: 0.25rem;
}

.playing-name {
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.player-controls {
  display: flex;
  gap: 0.5rem;
}

.player-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  transition: all 0.2s;
}

.player-btn:hover {
  background: var(--hover-bg);
  color: var(--accent-color);
}

/* 移动端适配 */
@media (max-width: 768px) {
  :root {
    --drawer-width: 80vw;
  }
  
  .icon-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    height: 56px;
    flex-direction: row;
    justify-content: space-around;
    border-right: none;
    border-top: 1px solid var(--border-color);
    padding: 0.5rem;
    background: var(--reader-bg);
  }
  
  .icon-group {
    flex-direction: row;
  }
  
  .icon-group.bottom {
    display: none;
  }
  
  .drawer-panel {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 56px;
    z-index: 40;
    transform: translateX(-100%);
    width: var(--drawer-width);
    transition: transform 0.3s ease;
  }
  
  .drawer-panel.mobile-open {
    transform: translateX(0);
  }
  
  .panel-content {
    opacity: 1;
  }
  
  .reader-main {
    padding-bottom: 56px;
  }
  
  .mobile-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    z-index: 35;
  }
  
  .reading-article {
    padding: 0 1rem;
  }
  
  .quick-nav {
    bottom: 5rem;
    right: 1rem;
  }
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* 主题特定样式 */
.theme-dark .icon-btn,
.theme-dark .tool-btn,
.theme-dark .close-btn {
  color: #9ca3af;
}

.theme-dark .toc-item,
.theme-dark .book-title {
  color: #d1d5db;
}

.theme-sepia {
  --reader-bg: #f4ecd8;
  --reader-text: #433422;
  --sidebar-bg: #e9dfc8;
  --border-color: #d3c6a8;
}

.theme-green {
  --reader-bg: #c7edcc;
  --reader-text: #2c3e50;
  --sidebar-bg: #b8e0bd;
  --border-color: #a8d5ae;
}
</style>