<template>
  <v-app-bar color="primary" density="compact">
    <v-btn @click="redirectToDashboard">监控中心</v-btn>
    <v-btn @click="redirectToUpload">上传与运行</v-btn>
    <v-btn @click="redirectToWorkflow">流程与结果</v-btn>
    <v-btn @click="redirectToQuery">智能问答</v-btn>
    <v-spacer></v-spacer>
    <span v-if="user">
      {{ user.username }} &nbsp;&nbsp;&nbsp;&nbsp;
    </span>
    <Logout @logged-out="handleLogout" />
  </v-app-bar>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import Logout from './Logout.vue'; // 确保正确导入 Logout 组件

export default defineComponent({
  name: 'IndexButton',
  components: {
    Logout, // 注册 Logout 组件
  },
  setup() {
    const router = useRouter();
    const user = ref<{ username: string } | null>(null);

    const redirectToDashboard = () => router.push('/dashboard');
    const redirectToUpload = () => router.push('/upload');
    const redirectToWorkflow = () => router.push('/workflow');
    // const redirectToResult = () => router.push('/result');
    const redirectToQuery = () => router.push('/query');

    const fetchCurrentUser = async () => {
      // 先检查 localStorage
      const localUser = localStorage.getItem('currentUser');
      if (localUser) {
        user.value = JSON.parse(localUser);
      } else {
        // 如果没有，则返回登录页
        router.push('/login');
      }
    };

    const handleLogout = () => {
      user.value = null;
      localStorage.removeItem('currentUser');
      router.push('/login'); // 退出后跳转到登录页
    };

    onMounted(fetchCurrentUser);

    return {
      redirectToUpload,
      redirectToWorkflow,
      redirectToQuery,
      redirectToDashboard,
      user,
      handleLogout,
    };
  },
});
</script>
