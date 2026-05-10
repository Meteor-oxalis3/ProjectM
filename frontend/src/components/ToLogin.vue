<template>
    <v-btn
      size="large"
      class="text-none font-weight-regular"
      :style="{ color: 'white' }"
      prepend-icon="mdi-account"
      text="登录"
      variant="tonal"
      @click="redirectToLogin"
    ></v-btn>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  import { useRouter } from 'vue-router';
  
  export default defineComponent({
    name: 'LoginButton',
    setup() {
      const router = useRouter();
  
      const redirectToLogin = () => {
        router.push('/login'); // 跳转到 /register 路径
      };
  
      return {
        redirectToLogin,
      };
    },
  });
  </script>
  