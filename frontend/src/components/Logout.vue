<template>
  <v-btn
    class="text-none font-weight-regular"
    prepend-icon="mdi-logout"
    text="Logout"
    variant="tonal"
    @click="confirmLogout"
  ></v-btn>

  <!-- 确认登出对话框 -->
  <v-dialog v-model="dialog" max-width="400px">
    <v-card>
      <v-card-title class="text-h5">Confirm Logout</v-card-title>
      <v-card-text>Are you sure you want to logout?</v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="grey" text="Cancel" @click="dialog = false"></v-btn>
        <v-btn color="red" text="Logout" @click="logout"></v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'LogoutButton',
  setup() {
    const router = useRouter();
    const dialog = ref(false); // 控制登出确认对话框

    const confirmLogout = () => {
      dialog.value = true;
    };

    const logout = async () => {
      dialog.value = false; // 关闭对话框
      try {
        const response = await axios.post('/api/logout', {}, { withCredentials: true });

        if (response.data.success) {
          // 清除本地存储的用户信息
          localStorage.removeItem('currentUser');
          localStorage.removeItem('user_id');
          sessionStorage.clear();

          // 跳转到登录页
          router.push('/login');
        }
      } catch (err: any) {
        console.error('Logout failed:', err.response?.data?.message || 'An error occurred.');
      }
    };

    return {
      dialog,
      confirmLogout,
      logout,
    };
  },
});
</script>
