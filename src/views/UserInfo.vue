<template>
  <div class="user-info-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>个人中心</h2>
    </div>

    <!-- 基本信息模块 -->
    <div class="module basic-info">
      <h3 class="module-title">基本信息</h3>
      <div class="info-form">
        <el-form :model="userForm" label-width="100px" :rules="formRules" ref="userFormRef">
          <el-form-item label="用户名" prop="name">
            <el-input v-model="userForm.name" disabled />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="userForm.password" type="password" placeholder="请输入新密码（6-20位）" show-password />
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="userForm.phone" placeholder="请输入新手机号" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="userForm.email" placeholder="请输入新邮箱" />
          </el-form-item>
          <el-form-item label="注册时间">
            <el-input v-model="formatCreateTime" disabled />
          </el-form-item>
          <el-form-item label="头像">
            <el-avatar :src="userForm.headPicUrl || require('@/assets/head.png')" size="large" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="updateUserInfo" :loading="updateLoading">保存修改</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 关注相关模块 -->
    <div class="module follow-module">
      <h3 class="module-title">
        <el-tabs v-model="activeState" @tab-change="handleTabChange">
          <el-tab-pane label="我的关注者" name="0"></el-tab-pane>
          <el-tab-pane label="我关注的" name="1">
            <template #label>
              <span>我关注的</span>
              <el-button size="small" icon="Plus" type="primary" @click="openAddFollowDialog" class="add-btn">添加</el-button>
            </template>
          </el-tab-pane>
          <el-tab-pane label="黑名单" name="2">
            <template #label>
              <span>黑名单</span>
              <!-- 修复：统一按钮样式为primary，和关注添加按钮一致 -->
              <el-button size="small" icon="Plus" type="primary" @click="openAddBlackDialog" class="block-btn">添加</el-button>
            </template>
          </el-tab-pane>
        </el-tabs>
      </h3>

      <!-- 列表区域 -->
      <div class="follow-list" v-loading="followLoading">
        <div class="follow-item" v-for="item in followList" :key="item.userId">
          <el-avatar :src="item.headPicUrl || require('@/assets/head.png')" />
          <span class="user-name">{{ item.name }}</span>
          <el-button
            size="small"
            type="danger"
            @click="handleAction(item.userId)"
            :loading="actionLoading"
          >
            {{ getActionText() }}
          </el-button>
        </div>
        <div class="no-data" v-if="followList.length === 0 && !followLoading">暂无数据</div>
      </div>
    </div>

    <!-- 添加关注的弹窗 -->
    <el-dialog v-model="addFollowDialogVisible" title="添加关注" width="600px" center>
      <el-input
        v-model="searchUsername"
        placeholder="输入用户名模糊搜索（为空查询全部）"
        clearable
        style="margin-bottom: 20px;"
        @input="debounceSearchUser"
      />
      <el-table :data="userList" v-loading="userListLoading" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="用户名" />
        <el-table-column prop="userId" label="用户ID" />
      </el-table>
      <template #footer>
        <el-button @click="addFollowDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitFollow" :loading="submitFollowLoading">确认关注</el-button>
      </template>
    </el-dialog>

    <!-- 新增：添加黑名单的弹窗（复用关注弹窗结构，仅修改文案） -->
    <el-dialog v-model="addBlackDialogVisible" title="添加黑名单" width="600px" center>
      <el-input
        v-model="searchUsername"
        placeholder="输入用户名模糊搜索（为空查询全部）"
        clearable
        style="margin-bottom: 20px;"
        @input="debounceSearchUser"
      />
      <el-table :data="userList" v-loading="userListLoading" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="用户名" />
        <el-table-column prop="userId" label="用户ID" />
      </el-table>
      <template #footer>
        <el-button @click="addBlackDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitBlack" :loading="submitBlackLoading">确认加入黑名单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import axios from "axios";
import { ElMessage, ElMessageBox } from "element-plus";

// 路由和token
const token = localStorage.getItem("userToken");
axios.defaults.headers.common["token"] = token;

// 基本信息相关
const userFormRef = ref(null);
const userForm = ref({
  userId: "",
  name: "",
  email: "",
  phone: "",
  createTime: "",
  password: "",
  headPicUrl: "",
});
const formatCreateTime = computed(() => {
  if (!userForm.value.createTime) return "";
  return new Date(userForm.value.createTime).toLocaleString();
});
const updateLoading = ref(false);
const formRules = ref({
  password: [
    { required: false, min: 6, max: 20, message: "密码长度需在6-20位之间", trigger: "blur" },
  ],
  phone: [
    { required: false, pattern: /^1[3-9]\d{9}$/, message: "请输入正确的手机号格式", trigger: "blur" },
  ],
  email: [
    { required: false, pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: "请输入正确的邮箱格式", trigger: "blur" },
  ],
});

// 关注相关
const activeState = ref("1"); // 默认显示我关注的（state=1）
const followList = ref([]);
const followLoading = ref(false);
const actionLoading = ref(false);

// 添加关注弹窗相关
const addFollowDialogVisible = ref(false);
// 新增：添加黑名单弹窗控制
const addBlackDialogVisible = ref(false);
const searchUsername = ref("");
const userList = ref([]);
const userListLoading = ref(false);
const selectedUserIds = ref([]);
const submitFollowLoading = ref(false);
// 新增：拉黑提交加载状态
const submitBlackLoading = ref(false);

// 防抖搜索
const debounceSearchUser = ref(null);
onMounted(() => {
  debounceSearchUser.value = debounce(getUserList, 500);
  // 初始化加载用户基本信息和关注列表
  getUserDetail();
  getFollowList();
});

// 防抖函数
function debounce(fn, delay) {
  let timer = null;
  return function (...args) {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => {
      fn.apply(this, args);
    }, delay);
  };
}

// 1. 获取用户基本信息
const getUserDetail = async () => {
  try {
    const res = await axios.get("/userDetail");
    if (res.data.code === 0) {
      const data = res.data.data;
      userForm.value = {
        ...data,
        password: "******",
      };
    } else {
      ElMessage.error("获取用户信息失败：" + res.data.msg);
    }
  } catch (err) {
    ElMessage.error("获取用户信息异常：" + err.message);
  }
};

// 2. 修改用户信息
const updateUserInfo = async () => {
  if (!userFormRef.value) return;
  try {
    await userFormRef.value.validate();
    // 过滤空值（只修改有填写的字段）
    const updateData = {};
    if (userForm.value.password && userForm.value.password !== "***") {
      updateData.password = userForm.value.password;
    }
    if (userForm.value.email) updateData.email = userForm.value.email;
    if (userForm.value.phone) updateData.phone = userForm.value.phone;

    if (Object.keys(updateData).length === 0) {
      ElMessage.warning("请填写需要修改的信息");
      return;
    }

    updateLoading.value = true;
    const res = await axios.post("/updateUser", updateData);
    if (res.data.code === 0) {
      ElMessage.success("修改信息成功");
      getUserDetail(); // 重新加载最新信息
    } else {
      ElMessage.error("修改失败：" + res.data.msg);
    }
  } catch (err) {
    ElMessage.error("修改信息异常：" + err.message);
  } finally {
    updateLoading.value = false;
  }
};

// 3. 获取关注列表（根据state）
const getFollowList = async () => {
  followLoading.value = true;
  try {
    const res = await axios.get(`/followInfo?state=${activeState.value}`);
    if (res.data.code === 0) {
      followList.value = res.data.data;
    } else {
      ElMessage.error("获取列表失败：" + res.data.msg);
    }
  } catch (err) {
    ElMessage.error("获取列表异常：" + err.message);
  } finally {
    followLoading.value = false;
  }
};

// 4. 切换标签页加载对应列表
const handleTabChange = () => {
  getFollowList();
};

// 5. 获取可关注的用户列表
const getUserList = async () => {
  userListLoading.value = true;
  try {
    const params = {};
    if (searchUsername.value) params.username = searchUsername.value;
    const res = await axios.get("/listUser", { params });
    if (res.data.code === 0) {
      userList.value = res.data.data;
    } else {
      ElMessage.error("获取用户列表失败：" + res.data.msg);
    }
  } catch (err) {
    ElMessage.error("获取用户列表异常：" + err.message);
  } finally {
    userListLoading.value = false;
  }
};

// 6. 选择要操作的用户（关注/拉黑通用）
const handleSelectionChange = (val) => {
  selectedUserIds.value = val.map(item => item.userId);
};

// 7. 提交关注操作
const submitFollow = async () => {
  if (selectedUserIds.value.length === 0) {
    ElMessage.warning("请选择要关注的用户");
    return;
  }
  submitFollowLoading.value = true;
  try {
    // 批量关注（可根据后端调整，若不支持批量则循环调用）
    const promises = selectedUserIds.value.map(userId =>
      axios.post("/action", {
        toUser: userId,
        action: "follow"
      })
    );
    const results = await Promise.all(promises);
    const isSuccess = results.every(res => res.data.code === 0);
    if (isSuccess) {
      ElMessage.success("关注成功");
      addFollowDialogVisible.value = false;
      getFollowList(); // 刷新关注列表
    } else {
      ElMessage.error("部分用户关注失败");
    }
  } catch (err) {
    ElMessage.error("关注操作异常：" + err.message);
  } finally {
    submitFollowLoading.value = false;
    // 清空选中状态
    selectedUserIds.value = [];
  }
};

// 新增：8. 提交拉黑操作
const submitBlack = async () => {
  if (selectedUserIds.value.length === 0) {
    ElMessage.warning("请选择要加入黑名单的用户");
    return;
  }
  submitBlackLoading.value = true;
  try {
    // 批量拉黑（根据后端接口调整action字段）
    const promises = selectedUserIds.value.map(userId =>
      axios.post("/action", {
        toUser: userId,
        action: "block" // 假设后端拉黑的action值为block，需和后端确认
      })
    );
    const results = await Promise.all(promises);
    const isSuccess = results.every(res => res.data.code === 0);
    if (isSuccess) {
      ElMessage.success("加入黑名单成功");
      addBlackDialogVisible.value = false;
      getFollowList(); // 刷新黑名单列表
    } else {
      ElMessage.error("部分用户加入黑名单失败");
    }
  } catch (err) {
    ElMessage.error("加入黑名单操作异常：" + err.message);
  } finally {
    submitBlackLoading.value = false;
    // 清空选中状态
    selectedUserIds.value = [];
  }
};

// 9. 取消关注/取消拉黑操作
const handleAction = async (userId) => {
  let action = "";
  let tip = "";
  if (activeState.value === "1") { // 我关注的：取消关注
    action = "cancelFollow";
    tip = "确定取消关注该用户吗？";
  } else if (activeState.value === "2") { // 黑名单：取消拉黑
    action = "unblock";
    tip = "确定取消拉黑该用户吗？";
  } else {
    return; // 我的关注者无操作
  }

  try {
    await ElMessageBox.confirm(tip, "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    actionLoading.value = true;
    const res = await axios.post("/action", {
      toUser: userId,
      action
    });
    if (res.data.code === 0) {
      ElMessage.success(activeState.value === "1" ? "取消关注成功" : "取消拉黑成功");
      getFollowList(); // 刷新列表
    } else {
      ElMessage.error("操作失败：" + res.data.msg);
    }
  } catch (err) {
    if (err !== "cancel") { // 排除取消弹窗的情况
      ElMessage.error("操作异常：" + err.message);
    }
  } finally {
    actionLoading.value = false;
  }
};

// 10. 获取操作按钮文本
const getActionText = () => {
  if (activeState.value === "1") {
    return "取消关注";
  } else if (activeState.value === "2") {
    return "取消拉黑";
  }
  return "";
};

// 新增：11. 打开关注弹窗方法（修复点击不弹窗问题）
const openAddFollowDialog = () => {
  // 每次打开弹窗重置搜索和列表
  searchUsername.value = "";
  selectedUserIds.value = [];
  addFollowDialogVisible.value = true;
  // 主动加载用户列表
  getUserList();
};

// 新增：12. 打开黑名单弹窗方法
const openAddBlackDialog = () => {
  // 每次打开弹窗重置搜索和列表
  searchUsername.value = "";
  selectedUserIds.value = [];
  addBlackDialogVisible.value = true;
  // 主动加载用户列表
  getUserList();
};
</script>

<style scoped>
.user-info-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: "Microsoft YaHei", sans-serif;
}

.page-header {
  padding: 10px 0 20px;
  border-bottom: 1px solid #eee;
  margin-bottom: 30px;
}

.page-header h2 {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0;
}

.module {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.module-title {
  font-size: 1.5rem;
  color: #3498db;
  margin: 0 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

/* 基本信息样式 */
.info-form {
  max-width: 600px;
}

/* 关注模块样式 */
.follow-module .module-title {
  border: none;
}

.add-btn, .block-btn { /* 统一添加按钮样式 */
  margin-left: 10px;
}

.follow-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 20px;
}

.follow-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  background: #fff;
  border-radius: 6px;
  min-width: 200px;
  justify-content: space-between;
}

.user-name {
  font-size: 14px;
  color: #333;
}

.no-data {
  width: 100%;
  text-align: center;
  padding: 20px;
  color: #95a5a6;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .module {
    padding: 20px 15px;
  }

  .follow-list {
    flex-direction: column;
    gap: 15px;
  }

  .follow-item {
    min-width: 100%;
  }
}
</style>