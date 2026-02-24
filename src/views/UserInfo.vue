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
          <el-form-item label="空间(MB)">
            <!-- 改为下拉框 -->
            <el-select 
              v-model="userForm.defaultMb" 
              @change="handleSpaceChange"
              placeholder="请选择空间大小"
            >
              <el-option label="100 MB" value="100" />
              <el-option label="500 MB" value="500" />
              <el-option label="1000 MB" value="1000" />
            </el-select>
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

    <!-- 添加黑名单的弹窗 -->
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

    <!-- 空间扩容支付弹窗 -->
    <el-dialog 
      v-model="payDialogVisible" 
      title="空间扩容支付" 
      width="400px" 
      center
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <div class="pay-content">
        <p class="pay-desc">
          您当前空间：<span class="current-space">{{ originalSpace }} MB</span><br>
          选择空间：<span class="target-space">{{ userForm.defaultMb }} MB</span><br>
          扩容大小：<span class="increase-space">{{ increaseSpace }} MB</span><br>
          需支付费用：<span class="pay-amount">¥{{ payAmount }}</span>（按100MB/1元计算）
        </p>
        <div v-if="payQrCode" class="qr-code-container">
          <p class="qr-tip">请扫描下方支付宝二维码完成支付：</p>
          <img :src="payQrCode" alt="支付宝支付二维码" class="qr-code" />
        </div>
        <div v-else class="loading-qr" v-loading="generateQrLoading">正在生成支付二维码...</div>
      </div>
      <template #footer>
        <el-button @click="cancelPay">取消</el-button>
        <el-button 
          type="primary" 
          @click="generatePayQrCode" 
          :loading="generateQrLoading"
          v-if="!payQrCode"
        >
          确认支付
        </el-button>
        <el-button 
          type="success" 
          @click="checkPayResult" 
          :loading="checkPayLoading"
          v-if="payQrCode"
        >
          已完成支付，确认
        </el-button>
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
  defaultMb: "100", // 默认空间100MB
});
// 原始空间大小（用于计算扩容费用）
const originalSpace = ref(100);
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
const activeState = ref("1");
const followList = ref([]);
const followLoading = ref(false);
const actionLoading = ref(false);

// 添加关注弹窗相关
const addFollowDialogVisible = ref(false);
const addBlackDialogVisible = ref(false);
const searchUsername = ref("");
const userList = ref([]);
const userListLoading = ref(false);
const selectedUserIds = ref([]);
const submitFollowLoading = ref(false);
const submitBlackLoading = ref(false);

// 空间扩容支付相关
const payDialogVisible = ref(false);
const increaseSpace = ref(0); // 扩容大小
const payAmount = ref(0); // 支付金额
const payQrCode = ref(""); // 支付二维码
const generateQrLoading = ref(false); // 生成二维码加载状态
const checkPayLoading = ref(false); // 检查支付结果加载状态

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
        defaultMb: data.defaultMb ? data.defaultMb.toString() : "100", // 确保是字符串类型
      };
      // 保存原始空间大小
      originalSpace.value = Number(data.defaultMb) || 100;
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
      getFollowList();
    } else {
      ElMessage.error("部分用户关注失败");
    }
  } catch (err) {
    ElMessage.error("关注操作异常：" + err.message);
  } finally {
    submitFollowLoading.value = false;
    selectedUserIds.value = [];
  }
};

// 8. 提交拉黑操作
const submitBlack = async () => {
  if (selectedUserIds.value.length === 0) {
    ElMessage.warning("请选择要加入黑名单的用户");
    return;
  }
  submitBlackLoading.value = true;
  try {
    const promises = selectedUserIds.value.map(userId =>
      axios.post("/action", {
        toUser: userId,
        action: "block"
      })
    );
    const results = await Promise.all(promises);
    const isSuccess = results.every(res => res.data.code === 0);
    if (isSuccess) {
      ElMessage.success("加入黑名单成功");
      addBlackDialogVisible.value = false;
      getFollowList();
    } else {
      ElMessage.error("部分用户加入黑名单失败");
    }
  } catch (err) {
    ElMessage.error("加入黑名单操作异常：" + err.message);
  } finally {
    submitBlackLoading.value = false;
    selectedUserIds.value = [];
  }
};

// 9. 取消关注/取消拉黑操作
const handleAction = async (userId) => {
  let action = "";
  let tip = "";
  if (activeState.value === "1") {
    action = "cancelFollow";
    tip = "确定取消关注该用户吗？";
  } else if (activeState.value === "2") {
    action = "unblock";
    tip = "确定取消拉黑该用户吗？";
  } else {
    return;
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
      getFollowList();
    } else {
      ElMessage.error("操作失败：" + res.data.msg);
    }
  } catch (err) {
    if (err !== "cancel") {
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

// 11. 打开关注弹窗方法
const openAddFollowDialog = () => {
  searchUsername.value = "";
  selectedUserIds.value = [];
  addFollowDialogVisible.value = true;
  getUserList();
};

// 12. 打开黑名单弹窗方法
const openAddBlackDialog = () => {
  searchUsername.value = "";
  selectedUserIds.value = [];
  addBlackDialogVisible.value = true;
  getUserList();
};

// 13. 处理空间大小变更
const handleSpaceChange = () => {
  const targetSpace = Number(userForm.value.defaultMb);
  // 只有选中值大于当前值时才弹出支付窗口
  if (targetSpace > originalSpace.value) {
    // 计算扩容大小和费用（100MB/1元）
    increaseSpace.value = targetSpace - originalSpace.value;
    payAmount.value = increaseSpace.value / 100;
    // 打开支付弹窗
    payDialogVisible.value = true;
  }
};

// 14. 生成支付二维码
const generatePayQrCode = async () => {
  try {
    generateQrLoading.value = true;
    // 调用后台接口生成支付宝支付二维码
    const res = await axios.post("/generatePayQrCode", {
      userId: userForm.value.userId,
      targetSpace: userForm.value.defaultMb,
      amount: payAmount.value
    });
    if (res.data.code === 0) {
      payQrCode.value = res.data.data.qrCodeUrl; // 假设接口返回二维码URL
      ElMessage.info("请扫描二维码完成支付");
    } else {
      ElMessage.error("生成支付二维码失败：" + res.data.msg);
    }
  } catch (err) {
    ElMessage.error("生成二维码异常：" + err.message);
  } finally {
    generateQrLoading.value = false;
  }
};

// 15. 检查支付结果并更新空间
const checkPayResult = async () => {
  try {
    checkPayLoading.value = true;
    // 调用后台接口检查支付状态
    const res = await axios.post("/checkPayResult", {
      userId: userForm.value.userId,
      targetSpace: userForm.value.defaultMb
    });
    if (res.data.code === 0) {
      if (res.data.msg.contains("更新完成")) {
        // 支付成功，更新用户空间
        ElMessage.success("支付成功，空间已扩容！");
        // 重新加载用户信息（获取最新空间大小）
        getUserDetail();
        // 关闭支付弹窗
        payDialogVisible.value = false;
        // 重置二维码和支付状态
        payQrCode.value = "";
      } else {
        ElMessage.warning("请完成支付后再试");
      }
    } else {
      ElMessage.error("检查支付结果失败：" + res.data.msg);
    }
  } catch (err) {
    ElMessage.error("检查支付结果异常：" + err.message);
  } finally {
    checkPayLoading.value = false;
  }
};

// 16. 取消支付
const cancelPay = () => {
  // 取消支付时恢复原始空间选择
  userForm.value.defaultMb = originalSpace.value.toString();
  payDialogVisible.value = false;
  // 重置支付相关状态
  payQrCode.value = "";
  increaseSpace.value = 0;
  payAmount.value = 0;
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

.add-btn, .block-btn {
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

/* 支付弹窗样式 */
.pay-content {
  text-align: center;
  padding: 10px 0;
}

.pay-desc {
  font-size: 14px;
  line-height: 1.8;
  margin-bottom: 20px;
  text-align: left;
}

.current-space {
  color: #666;
}

.target-space {
  color: #3498db;
  font-weight: bold;
}

.increase-space {
  color: #e67e22;
  font-weight: bold;
}

.pay-amount {
  color: #e74c3c;
  font-weight: bold;
  font-size: 16px;
}

.qr-code-container {
  margin: 20px 0;
}

.qr-tip {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.qr-code {
  width: 200px;
  height: 200px;
  border: 1px solid #eee;
  padding: 5px;
}

.loading-qr {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
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

  .qr-code {
    width: 150px;
    height: 150px;
  }
}
</style>