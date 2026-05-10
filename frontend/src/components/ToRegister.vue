<template>
    <v-btn
      size="large"
      class="text-none font-weight-regular"
      :style="{ color: 'white' }"
      prepend-icon="mdi-account"
      text="注册"
      variant="tonal"
      @click="redirectToRegister"
    ></v-btn>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  import { useRouter } from 'vue-router';
  
  export default defineComponent({
    name: 'LoginRegisterButton',
    setup() {
      const router = useRouter();
  
      const redirectToRegister = () => {
        router.push('/register'); // 跳转到 /register 路径
      };
  
      return {
        redirectToRegister,
      };
    },
  });
  </script>
  