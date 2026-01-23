<template>
  <div id="app" class="blog-container">
    <!-- 博客头部 -->
    <header class="blog-header">
      <div class="header-left">
        <h1>我的个人博客</h1>
        <p class="header-desc">学无止境 分享有限</p>
      </div>
      <div class="header-right">
        <!-- 头像下拉菜单 -->
        <el-dropdown trigger="hover" placement="bottom">
          <div class="avatar-wrapper">
            <!-- 动态头像显示 -->
            <img :src="avatarUrl || require('@/assets/head.png')" alt="个人头像" class="avatar" />
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <!-- 未登录状态 -->
              <template v-if="!isLoggedIn">
                <el-dropdown-item @click="handleLogin">登录</el-dropdown-item>
                <el-dropdown-item @click="handleRegister">注册</el-dropdown-item>
                <el-dropdown-item divided @click="handleMessages">消息</el-dropdown-item>
              </template>
              <!-- 已登录状态 -->
              <template v-else>
                <el-dropdown-item disabled>{{ currentUser }}</el-dropdown-item>
                <el-dropdown-item divided @click="handleMessages">我的消息</el-dropdown-item>
                <el-dropdown-item divided @click="triggerAvatarUpload">
                  <span>更改头像</span>
                </el-dropdown-item>
                <el-dropdown-item @click="handleLogout">
                  <span style="color: #f56c6c;">退出登录</span>
                </el-dropdown-item>
              </template>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- 隐藏的文件输入框 -->
    <input
      type="file"
      ref="avatarInput"
      accept="image/*"
      style="display: none"
      @change="handleAvatarChange"
    />
    <main class="blog-main">
      <div class="module-container">
        <div class="module-item create-space">
          <h2 class="module-title">创作空间</h2>
          <el-button class="enter-btn" @click="toCreateSpace">进入</el-button>
          <div class="article-list" v-if="articleList.length > 0">
            <div class="article-item" v-for="article in articleList" :key="article.id"
              @click="openArticleDialog(article)">
              <h3 class="article-title">{{ article.title }}</h3>
              <div class="article-meta">
                <span>分类：{{ article.category }}</span>
                <span>作者：{{ article.createUser }}</span>
              </div>
              <p class="article-summary">{{ article.summary }}</p>
            </div>
          </div>
          <div class="no-data" v-else>暂无文章数据</div>
        </div>
        <div class="module-item subscribe-link">
          <h2 class="module-title">订阅链接</h2>
          <el-button class="enter-btn" @click="toSubscribeLink">进入</el-button>
        </div>
        <div class="module-item library">
          <h2 class="module-title">图书馆</h2>
          <el-button class="enter-btn" @click="toLibrary">进入</el-button>
        </div>
      </div>
    </main>

    <footer class="blog-footer">
      <p>© 2026 我的个人博客 | poo7yur@outlook.com</p>
    </footer>

    <!-- 文章详情弹窗 -->
    <el-dialog v-model="articleDialogVisible" title="文章详情" width="800px" center>
      <div v-if="currentArticle" class="dialog-article">
        <h3>{{ currentArticle.title }}</h3>
        <div class="dialog-meta">
          <span>分类：{{ currentArticle.category }}</span>
          <span>作者：{{ currentArticle.createUser }}</span>
        </div>
        <hr />
        <p class="dialog-summary">{{ currentArticle.summary }}</p>
      </div>
    </el-dialog>

    <!-- 登录弹窗 -->
    <el-dialog v-model="loginDialogVisible" title="用户登录" width="420px" center
      :close-on-click-modal="false" :before-close="cancelLogin" class="login-dialog">
      <div class="login-type-switch">
        <div :class="['type-item', { active: loginType === 'account' }]" @click="loginType = 'account'">
          账号密码登录
        </div>
        <div :class="['type-item', { active: loginType === 'phone' }]" @click="loginType = 'phone'">
          手机号登录
        </div>
      </div>
      <div class="login-form">
        <div class="form-item">
          <div class="input-with-btn" v-if="loginType === 'phone'">
            <el-input v-model="loginForm.account" placeholder="请输入手机号" prefix-icon="Phone"
              clearable maxlength="11" @input="validateAccount" />
            <el-button class="code-btn" type="primary" :disabled="!canGetCode || codeCountdown > 0"
              @click="getSmsCode" size="small">
              {{ codeCountdown > 0 ? `${codeCountdown}s后重新获取` : '获取验证码' }}
            </el-button>
          </div>
          <el-input v-else v-model="loginForm.account" placeholder="账号名/邮箱/手机号"
            prefix-icon="User" clearable maxlength="50" @input="validateAccount" />
          <div class="error-tip" v-if="accountError">{{ accountError }}</div>
        </div>
        <div class="form-item">
          <el-input v-if="loginType === 'account'" v-model="loginForm.password" type="password"
            placeholder="请输入登录密码" prefix-icon="Lock" show-password clearable maxlength="20"
            @input="validatePassword" />
          <el-input v-else v-model="loginForm.smsCode" placeholder="请输入收到的短信验证码"
            prefix-icon="Message" clearable maxlength="6" @input="validateSmsCode" />
          <div class="error-tip" v-if="loginType === 'account' && passwordError">
            {{ passwordError }}
          </div>
          <div class="error-tip" v-if="loginType === 'phone' && smsCodeError">
            {{ smsCodeError }}
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelLogin" size="default">取消</el-button>
          <el-button type="primary" size="default" @click="submitLogin" :loading="loginLoading" class="login-btn">
            登录
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 注册弹窗 -->
    <el-dialog v-model="registerDialogVisible" title="用户注册" width="420px" center
      :close-on-click-modal="false" :before-close="cancelRegister" class="register-dialog">
      <div class="register-form">
        <div class="form-item">
          <el-input v-model="registerForm.name" placeholder="请输入用户名" prefix-icon="User"
            clearable maxlength="20" />
        </div>
        <div class="form-item">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码"
            prefix-icon="Lock" show-password clearable maxlength="20" />
        </div>
        <div class="form-item">
          <el-input v-model="registerForm.phone" placeholder="请输入手机号" prefix-icon="Phone"
            clearable maxlength="11" />
        </div>
        <div class="form-item">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱" prefix-icon="Message"
            clearable maxlength="50" />
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelRegister" size="default">取消</el-button>
          <el-button type="primary" size="default" @click="submitRegister" :loading="registerLoading">
            注册
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 消息列表弹窗 -->
    <el-dialog v-model="messagesDialogVisible" title="消息列表" width="900px" center
      @close="resetMessages">
      <div v-if="messageList.length > 0" v-loading="messagesLoading">
        <el-table :data="messageList" style="width: 100%">
          <el-table-column prop="msgType" label="类型" width="100" />
          <el-table-column prop="msgContent" label="内容" min-width="250" show-overflow-tooltip />
          <el-table-column prop="createBy" label="创建人" width="120" />
          <el-table-column prop="updateTime" label="更新时间" width="180" />
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.state === 0 ? 'info' : 'success'" size="small">
                {{ row.state === 0 ? '未读' : '已读' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页按钮 -->
        <div class="pagination-btns" style="margin-top: 20px; justify-content: center;">
          <el-button :disabled="messagePageNum === 1" circle @click="changeMessagePage(-1)">
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <span style="margin: 0 15px; line-height: 32px;">
            {{ messagePageNum }} / {{ messageTotalPage }}
          </span>
          <el-button :disabled="messagePageNum === messageTotalPage" circle @click="changeMessagePage(1)">
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
      <div v-else class="no-data">暂无消息数据</div>
    </el-dialog>
  </div>
</template>

<script setup>
import axios from "axios";
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue';

// 全局拦截器
axios.interceptors.request.use(config => {
  config.headers = config.headers || {}
  config.headers.token = localStorage.getItem('userToken') || ''
  return config
})
const router = useRouter();

// 原有数据
const articleList = ref([]);
const articleDialogVisible = ref(false);
const currentArticle = ref(null);

// 登录相关数据
const loginDialogVisible = ref(false);
const loginType = ref("account");
const loginForm = ref({ account: "", password: "", smsCode: "" });
const accountError = ref("");
const passwordError = ref("");
const smsCodeError = ref("");
const loginLoading = ref(false);
const codeCountdown = ref(0);
const canGetCode = ref(false);
let countdownTimer = null;

// 新增：头像相关
const avatarUrl = ref("");
const avatarInput = ref(null);

// 新增：登录状态管理
const isLoggedIn = ref(false);
const currentUser = ref("");

// 新增：注册相关
const registerDialogVisible = ref(false);
const registerForm = ref({ name: "", password: "", phone: "", email: "" });
const registerLoading = ref(false);

// 新增：消息相关
const messagesDialogVisible = ref(false);
const messageList = ref([]);
const messagePageNum = ref(1);
const messagePageSize = ref(10);
const messageTotal = ref(0);
const messageTotalPage = computed(() => Math.ceil(messageTotal.value / messagePageSize.value));
const messagesLoading = ref(false);

// 页面加载时检查登录状态
onMounted(() => {
  const token = localStorage.getItem('userToken');
  const user = localStorage.getItem('currentUser');
  const savedAvatarUrl = localStorage.getItem('userAvatarUrl');
  
  if (token && user) {
    isLoggedIn.value = true;
    currentUser.value = user;
    // 如果有保存的头像URL，使用它
    if (savedAvatarUrl) {
      avatarUrl.value = savedAvatarUrl;
    }
  }
  fetchEssayList();
});

// 监听验证码倒计时
watch(codeCountdown, (val) => {
  if (val <= 0 && countdownTimer) {
    clearInterval(countdownTimer);
    countdownTimer = null;
  }
});

onUnmounted(() => {
  if (countdownTimer) clearInterval(countdownTimer);
});

// 原有函数
const fetchEssayList = async () => {
  try {
    const res = await axios.post(
      "/queryEssay",
      { pageNum: 1, pageSize: 3 },
      { headers: { "Content-Type": "application/json" } },
    );
    if (res.data.code === 0) {
      articleList.value = res.data.data.list;
    } else {
      ElMessage.error("获取文章列表失败：" + res.data.msg);
    }
  } catch (err) {
    ElMessage.error("接口请求异常：" + err.message);
  }
};

const openArticleDialog = (article) => {
  currentArticle.value = article;
  articleDialogVisible.value = true;
};

// 登录相关函数
const handleLogin = () => {
  loginForm.value = { account: "", password: "", smsCode: "" };
  accountError.value = "";
  passwordError.value = "";
  smsCodeError.value = "";
  loginType.value = "account";
  codeCountdown.value = 0;
  canGetCode.value = false;
  loginDialogVisible.value = true;
};

const cancelLogin = () => {
  loginDialogVisible.value = false;
  if (countdownTimer) {
    clearInterval(countdownTimer);
    countdownTimer = null;
  }
  codeCountdown.value = 0;
};

const validateAccount = () => {
  const { account } = loginForm.value;
  accountError.value = "";
  if (!account.trim()) {
    accountError.value = loginType.value === "account" ? "请输入账号名/邮箱/手机号" : "请输入手机号";
    return false;
  }
  if (loginType.value === "phone") {
    const phoneReg = /^1[3-9]\d{9}$/;
    if (!phoneReg.test(account.trim())) {
      accountError.value = "请输入正确的手机号格式";
      return false;
    }
  }
  canGetCode.value = loginType.value === "phone" && /^1\d{10}$/.test(account.trim());
  return true;
};

const validatePassword = () => {
  const { password } = loginForm.value;
  passwordError.value = "";
  if (!password.trim()) {
    passwordError.value = "请输入登录密码";
    return false;
  }
  if (password.length < 6 || password.length > 20) {
    passwordError.value = "密码长度需在6-20位之间";
    return false;
  }
  return true;
};

const validateSmsCode = () => {
  const { smsCode } = loginForm.value;
  smsCodeError.value = "";
  if (!smsCode.trim()) {
    smsCodeError.value = "请输入收到的短信验证码";
    return false;
  }
  if (!/^\d{6}$/.test(smsCode.trim())) {
    smsCodeError.value = "验证码为6位数字";
    return false;
  }
  return true;
};

const getSmsCode = async () => {
  if (!validateAccount()) return;
  try {
    const res = await axios.post(
      "/sendNotice",
      { phone: loginForm.value.account.trim() },
      { headers: { "Content-Type": "application/json" } }
    );
    if (res.data.code === 0) {
      ElMessage.success("验证码已发送，请注意查收");
      codeCountdown.value = 60;
      countdownTimer = setInterval(() => codeCountdown.value--, 1000);
    } else {
      ElMessage.error(`发送失败：${res.data.msg || "系统异常"}`);
    }
  } catch (err) {
    ElMessage.error(`发送异常：${err.message || "请检查网络连接"}`);
  }
};

const submitLogin = async () => {
  const isAccountValid = validateAccount();
  let isOtherValid = true;
  if (loginType.value === "account") {
    isOtherValid = validatePassword();
  } else {
    isOtherValid = validateSmsCode();
  }
  if (!isAccountValid || !isOtherValid) return;

  loginLoading.value = true;
  try {
    const requestData = loginType.value === "account" 
      ? { username: loginForm.value.account.trim(), password: loginForm.value.password.trim() }
      : { phone: loginForm.value.account.trim(), smsCode: loginForm.value.smsCode.trim() };

    const res = await axios.post("/login", requestData,
      { headers: { "Content-Type": "application/json" } }
    );

    if (res.data.code === 0) {
      // 登录成功：存储token和用户信息
      localStorage.setItem("userToken", res.data.data.token);
      localStorage.setItem("currentUser", res.data.data.name || loginForm.value.account);
      
      // 保存头像URL（如果有）
      if (res.data.data.headPicUrl) {
        localStorage.setItem("userAvatarUrl", res.data.data.headPicUrl);
        avatarUrl.value = res.data.data.headPicUrl;
      }
      
      isLoggedIn.value = true;
      currentUser.value = res.data.data.name || loginForm.value.account;
      loginDialogVisible.value = false;
      ElMessage.success("登录成功！");
    } else {
      ElMessage.error(`登录失败：${res.data.msg || "验证信息错误"}`);
    }
  } catch (err) {
    ElMessage.error(`登录异常：${err.message || "请检查网络连接"}`);
  } finally {
    loginLoading.value = false;
  }
};

// 注册函数
const handleRegister = () => {
  registerForm.value = { name: "", password: "", phone: "", email: "" };
  registerDialogVisible.value = true;
};

const cancelRegister = () => {
  registerDialogVisible.value = false;
};

const submitRegister = async () => {
  if (!registerForm.value.name || !registerForm.value.password || !registerForm.value.phone || !registerForm.value.email) {
    ElMessage.error("请填写完整信息");
    return;
  }
  
  const phoneReg = /^1[3-9]\d{9}$/;
  if (!phoneReg.test(registerForm.value.phone)) {
    ElMessage.error("请输入正确的手机号");
    return;
  }
  
  const emailReg = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailReg.test(registerForm.value.email)) {
    ElMessage.error("请输入正确的邮箱格式");
    return;
  }
  
  if (registerForm.value.password.length < 6 || registerForm.value.password.length > 20) {
    ElMessage.error("密码长度需在6-20位之间");
    return;
  }

  registerLoading.value = true;
  try {
    const res = await axios.post(
      "/addUser",
      {
        name: registerForm.value.name,
        email: registerForm.value.email,
        password: registerForm.value.password,
        phone: registerForm.value.phone
      },
      { headers: { "Content-Type": "application/json" } }
    );

    if (res.data.code === 0) {
      ElMessage.success(res.data.msg || "注册成功");
      registerDialogVisible.value = false;
      handleLogin();
    } else {
      ElMessage.error(`注册失败：${res.data.msg || "请检查输入信息"}`);
    }
  } catch (err) {
    ElMessage.error(`注册异常：${err.message || "请检查网络连接"}`);
  } finally {
    registerLoading.value = false;
  }
};

// 头像上传相关函数
const triggerAvatarUpload = () => {
  avatarInput.value?.click();
};

const handleAvatarChange = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件');
    return;
  }

  // 验证文件大小 (5MB)
  if (file.size > 600 * 1024 ) {
    ElMessage.error('图片大小不能超过600kb');
    return;
  }

  const token = localStorage.getItem('userToken');
  if (!token) {
    ElMessage.error('请先登录');
    return;
  }

  // 创建FormData上传文件
  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await axios.post(
      "/changeAvatar",
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
          'token': token
        }
      }
    );

    if (res.data.code === 0) {
      // 更新头像URL
      const newAvatarUrl = res.data.data;
      localStorage.setItem('userAvatarUrl', newAvatarUrl);
      avatarUrl.value = newAvatarUrl;
      ElMessage.success('头像更新成功');
      
      // 清空input，允许重复选择同一文件
      event.target.value = '';
    } else {
      ElMessage.error(`头像更新失败：${res.data.msg || '系统异常'}`);
    }
  } catch (err) {
    ElMessage.error(`头像更新异常：${err.message || '请检查网络连接'}`);
  }
};

// 退出登录
const handleLogout = () => {
  localStorage.removeItem("userToken");
  localStorage.removeItem("currentUser");
  localStorage.removeItem("userAvatarUrl"); // 清除头像URL
  isLoggedIn.value = false;
  currentUser.value = "";
  avatarUrl.value = ""; // 恢复默认头像
  ElMessage.success("退出登录成功");
  window.location.reload();
};

// 消息处理
const handleMessages = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning("请登录后查看消息");
    return;
  }
  messagesDialogVisible.value = true;
  await fetchMessages();
};

const fetchMessages = async () => {
  messagesLoading.value = true;
  try {
    const token = localStorage.getItem("userToken");
    const res = await axios.post(
      "/getMsg",
      {
        keyword: "",
        pageNum: messagePageNum.value,
        pageSize: messagePageSize.value
      },
      {
        headers: {
          "Content-Type": "application/json",
          "token": token
        }
      }
    );

    if (res.data.code === 0) {
      messageList.value = res.data.data.list;
      messageTotal.value = res.data.data.total;
    } else {
      ElMessage.error(`获取消息失败：${res.data.msg}`);
    }
  } catch (err) {
    ElMessage.error(`获取消息异常：${err.message}`);
  } finally {
    messagesLoading.value = false;
  }
};

const changeMessagePage = (step) => {
  const newPage = messagePageNum.value + step;
  if (newPage >= 1 && newPage <= messageTotalPage.value) {
    messagePageNum.value = newPage;
    fetchMessages();
  }
};

const resetMessages = () => {
  messagePageNum.value = 1;
  messageList.value = [];
};

// 其他跳转函数
const toCreateSpace = () => router.push("/CreateSpace");
const toSubscribeLink = () => ElMessage.info("订阅链接功能开发中");
const toLibrary = () => ElMessage.info("图书馆功能开发中");
</script>

<style scoped>
/* 保持原有样式不变 */
.username {
  margin-left: 8px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* 注册弹窗样式 */
.register-dialog {
  --el-color-primary: #ff4400;
  --el-button-primary-bg-color: #ff4400;
  --el-button-primary-border-color: #ff4400;
  --el-button-primary-hover-bg-color: #e63d00;
}

.register-form {
  padding: 10px 0;
}

/* 消息列表样式 */
.el-table {
  margin-top: 10px;
}

/* 分页按钮样式 */
.pagination-btns {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

/* 保持原有所有样式 */
.blog-container { max-width: 1200px; margin: 0 auto; padding: 0 20px; font-family: "Microsoft YaHei", sans-serif; color: #333; }
.blog-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid #eee; }
.header-left { text-align: left; }
.blog-header h1 { font-size: 2.5rem; color: #2c3e50; margin-bottom: 15px; }
.header-desc { font-size: 1.2rem; color: #7f8c8d; }
.header-right { margin-right: 20px; }
.avatar-wrapper { cursor: pointer; display: flex; align-items: center; }
.avatar { width: 40px; height: 40px; border-radius: 50%; border: 2px solid #eee; object-fit: cover; }
.module-container { display: flex; justify-content: space-between; flex-wrap: wrap; padding: 40px 0; gap: 20px; }
.module-item { flex: 1; min-width: 300px; padding: 30px; background-color: #f9f9f9; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); position: relative; }
.create-space .enter-btn { position: absolute; top: 33px; right: 20px; background-color: #3498db; border: none; }
.subscribe-link .enter-btn { position: absolute; top: 33px; right: 20px; background-color: #0bd43e; border: none; }
.library .enter-btn { position: absolute; top: 33px; right: 20px; background-color: #a8a8a4; border: none; }
.module-title { font-size: 1.8rem; color: #3498db; margin-bottom: 20px; }
.article-list { margin-top: 40px; }
.article-item { margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px dashed #eee; cursor: pointer; transition: all 0.3s; }
.article-item:hover { transform: translateY(-5px); box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08); }
.article-title { font-size: 1.4rem; color: #2c3e50; margin-bottom: 10px; }
.article-meta { font-size: 0.9rem; color: #95a5a6; margin-bottom: 15px; display: flex; gap: 20px; }
.article-summary { font-size: 1rem; line-height: 1.6; color: #555; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.no-data { text-align: center; padding: 20px; color: #95a5a6; font-size: 1rem; }
.dialog-article { text-align: left; }
.dialog-meta { font-size: 0.9rem; color: #95a5a6; margin: 10px 0; display: flex; gap: 20px; }
.dialog-summary { font-size: 1rem; line-height: 1.8; color: #555; margin-top: 20px; }
.blog-footer { text-align: center; padding: 30px 0; border-top: 1px solid #eee; color: #7f8c8d; font-size: 0.9rem; }
.login-dialog { --el-color-primary: #ff4400; --el-button-primary-bg-color: #ff4400; --el-button-primary-border-color: #ff4400; --el-button-primary-hover-bg-color: #e63d00; }
.login-type-switch { display: flex; margin-bottom: 20px; border-bottom: 1px solid #eee; }
.type-item { flex: 1; text-align: center; padding: 8px 0; cursor: pointer; color: #666; font-size: 14px; position: relative; }
.type-item.active { color: #ff4400; font-weight: 500; }
.type-item.active::after { content: ""; position: absolute; bottom: -1px; left: 0; width: 100%; height: 2px; background-color: #ff4400; }
.login-form { padding: 10px 0; }
.form-item { margin-bottom: 16px; }
.form-item .el-input { --el-input-border-color: #ddd; --el-input-hover-border-color: #ff4400; border-radius: 4px; }
.input-with-btn { display: flex; align-items: center; gap: 10px; }
.input-with-btn .el-input { flex: 1; }
.code-btn { white-space: nowrap; width: 120px; height: 32px; font-size: 12px; }
.error-tip { height: 20px; line-height: 20px; font-size: 12px; color: #f56c6c; margin-top: 4px; padding-left: 2px; }
.login-btn { width: 100%; height: 44px; font-size: 16px; border-radius: 4px; }
.dialog-footer { display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 0; }
.dialog-footer .el-button { flex: 1; margin: 0 5px; height: 44px; }
/* 移动端适配 - 平板/大屏手机 (max-width: 768px) */
@media (max-width: 768px) {
  .blog-container {
    max-width: 100%;
    padding: 0 10px;
  }

  /* 头部适配 */
  .blog-header {
    padding: 15px 0;
  }
  .blog-header h1 {
    font-size: 1.8rem;
    margin-bottom: 10px;
  }
  .header-desc {
    font-size: 1rem;
  }
  .header-right {
    margin-right: 0;
  }
  .avatar {
    width: 36px;
    height: 36px;
  }

  /* 模块容器适配 */
  .module-container {
    flex-direction: column;
    padding: 20px 0;
    gap: 15px;
  }
  .module-item {
    min-width: 100%;
    padding: 20px 15px;
  }
  .module-title {
    font-size: 1.5rem;
    margin-bottom: 15px;
  }
  .create-space .enter-btn,
  .subscribe-link .enter-btn,
  .library .enter-btn {
    top: 20px;
    right: 15px;
    padding: 6px 12px;
    font-size: 12px;
  }

  /* 文章列表适配 */
  .article-list {
    margin-top: 25px;
  }
  .article-item {
    margin-bottom: 20px;
    padding-bottom: 15px;
  }
  .article-title {
    font-size: 1.2rem;
  }
  .article-meta {
    font-size: 0.8rem;
    gap: 15px;
  }
  .article-summary {
    font-size: 0.9rem;
  }

  /* 弹窗适配 */
  .el-dialog {
    width: 90% !important;
    margin: 0 auto;
  }
  .dialog-summary {
    font-size: 0.9rem;
    line-height: 1.6;
  }

  /* 登录/注册弹窗适配 */
  .login-dialog, .register-dialog {
    width: 90% !important;
  }
  .form-item {
    margin-bottom: 12px;
  }
  .code-btn {
    width: 100px;
    font-size: 11px;
  }
  .dialog-footer .el-button {
    height: 40px;
    font-size: 14px;
  }

  /* 消息列表适配 */
  .el-table {
    font-size: 12px;
  }
  .el-table-column {
    padding: 0 5px;
  }
  .el-table-column--label {
    padding: 8px 5px;
  }
}

/* 移动端适配 - 小屏手机 (max-width: 480px) */
@media (max-width: 480px) {
  /* 头部进一步适配 */
  .blog-header {
    flex-wrap: wrap;
    gap: 10px;
  }
  .header-left {
    width: 100%;
    text-align: center;
    margin-bottom: 10px;
  }
  .blog-header h1 {
    font-size: 1.5rem;
  }
  .header-desc {
    font-size: 0.9rem;
  }
  .header-right {
    margin: 0 auto;
  }

  /* 模块按钮适配 */
  .create-space .enter-btn,
  .subscribe-link .enter-btn,
  .library .enter-btn {
    position: static;
    display: block;
    width: 100%;
    margin-top: 15px;
    text-align: center;
  }

  /* 登录/注册表单适配 */
  .input-with-btn {
    flex-direction: column;
    gap: 8px;
  }
  .code-btn {
    width: 100%;
    height: 36px;
  }
  .login-btn {
    height: 40px;
    font-size: 14px;
  }

  /* 消息列表表格适配（横向滚动） */
  .el-table {
    overflow-x: auto;
    display: block;
  }
  .el-table__body-wrapper {
    overflow-x: auto;
  }
  .pagination-btns {
    gap: 5px;
  }
  .pagination-btns span {
    margin: 0 8px;
    font-size: 12px;
  }

  /* 页脚适配 */
  .blog-footer {
    padding: 20px 0;
    font-size: 0.8rem;
  }
}

/* 解决Element Plus弹窗在移动端的滚动问题 */
.el-dialog__body {
  max-height: 70vh;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* 移动端点击元素去除高亮 */
* {
  -webkit-tap-highlight-color: transparent;
  tap-highlight-color: transparent;
}

</style>