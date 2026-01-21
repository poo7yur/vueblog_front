<template>
  <div id="app" class="blog-container">
    <!-- 博客头部（新增头像下拉菜单） -->
    <header class="blog-header">
      <div class="header-left">
        <h1>我的个人博客</h1>
        <p class="header-desc">学无止境分享有限</p>
      </div>
      <div class="header-right">
        <!-- Element Plus下拉菜单：头像+动态菜单 -->
        <el-dropdown trigger="hover" placement="bottom">
          <div class="avatar-wrapper">
            <img src="@/assets/head.png" alt="个人头像" class="avatar" />

          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <!-- 未登录状态显示 -->
              <template v-if="!isLoggedIn">
                <el-dropdown-item @click="handleLogin">登录</el-dropdown-item>
                <el-dropdown-item @click="handleRegister">注册</el-dropdown-item>
                <el-dropdown-item divided @click="handleMessages">消息</el-dropdown-item>
              </template>
              <!-- 已登录状态显示 -->
              <template v-else>
                <el-dropdown-item disabled>{{ currentUser }}</el-dropdown-item>
                <el-dropdown-item divided @click="handleMessages">我的消息</el-dropdown-item>
                <el-dropdown-item @click="handleLogout">
                  <span style="color: #f56c6c;">退出登录</span>
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleAvatar">
                  <span style="color: green;">更改头像</span>
                </el-dropdown-item>
              </template>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- 中间模块内容保持不变... -->
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
                <span>更新时间：{{ formatDate(article.updateTime) }}</span>
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
          <span>更新时间：{{ formatDate(currentArticle.updateTime) }}</span>
        </div>
        <hr />
        <p class="dialog-summary">{{ currentArticle.summary }}</p>
      </div>
    </el-dialog>

    <!-- 登录弹窗（保持不变） -->
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
  if (token && user) {
    isLoggedIn.value = true;
    currentUser.value = user;
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

// 原有函数保持不变...
const fetchEssayList = async () => {
  try {
    const res = await axios.post(
      "http://127.0.0.1:8081/queryEssay",
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

const formatDate = (dateStr) => {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
};

// 登录相关函数（保持原有逻辑）
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
      "http://127.0.0.1:8081/sendNotice",
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

    const res = await axios.post("http://127.0.0.1:8081/login", requestData,
      { headers: { "Content-Type": "application/json" } }
    );

    if (res.data.code === 0) {
      // 登录成功：存储token和用户名
      localStorage.setItem("userToken", res.data.data.token);
      localStorage.setItem("currentUser", res.data.data.userName || loginForm.value.account);
      isLoggedIn.value = true;
      currentUser.value = res.data.data.userName || loginForm.value.account;
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

// 新增：注册函数
const handleRegister = () => {
  registerForm.value = { name: "", password: "", phone: "", email: "" };
  registerDialogVisible.value = true;
};

const cancelRegister = () => {
  registerDialogVisible.value = false;
};

const submitRegister = async () => {
  // 表单验证
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
      "http://127.0.0.1:8081/addUser",
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
      // 注册成功后自动打开登录窗口
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

// 头像修改功能
const handleAvatar = () => {


}

// 新增：退出登录
const handleLogout = () => {
  localStorage.removeItem("userToken");
  localStorage.removeItem("currentUser");
  isLoggedIn.value = false;
  currentUser.value = "";
  ElMessage.success("退出登录成功");
  // 刷新页面
  window.location.reload();
};

// 新增：消息处理
const handleMessages = async () => {
  if (!isLoggedIn.value) {
    ElMessage.warning("请登录后查看信息");
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
      "http://127.0.0.1:8081/getMsg",
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
/* 保持你原有的所有样式，仅添加以下新样式 */

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

/* 保持你原有的所有其他样式不变... */
.blog-container { max-width: 1200px; margin: 0 auto; padding: 0 20px; font-family: "Microsoft YaHei", sans-serif; color: #333; }
.blog-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid #eee; }
.header-left { text-align: left; }
.blog-header h1 { font-size: 2.5rem; color: #2c3e50; margin-bottom: 15px; }
.header-desc { font-size: 1.2rem; color: #7f8c8d; }
.header-right { margin-right: 20px; }
.avatar-wrapper { cursor: pointer; display: flex; align-items: center; }
.avatar { width: 40px; height: 40px; border-radius: 50%; border: 2px solid #eee; }
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
</style>