<template>
<v-app-bar color="primary" density="compact">
      <img src="/favicon.ico" height="50px"></img>
      <v-btn @click="redirectToIndex">ProjectM</v-btn>
      <!-- 隔断 -->
      <v-spacer></v-spacer>
      <v-btn @click="redirectToHost">
      <v-icon icon="mdi-server"></v-icon>&nbsp;&nbsp;本地部署
      </v-btn>
      <v-btn @click="redirectToDocs">
      <v-icon icon="mdi-book"></v-icon>&nbsp;&nbsp;文档
      </v-btn>
      <about></about>
</v-app-bar>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useRouter } from 'vue-router';
  
  export default defineComponent({
    name: 'IndexButton',
    setup() {
      const router = useRouter();
  
      const redirectToIndex = () => {
        router.push('/'); // 跳转到 / 路径
      };

      // 超链接到doc.projectm.org
      const redirectToDocs = () => {
        window.open('https://doc.projectm.org/ProjectM/', '_blank');
      };

      // 超链接到本地部署
      const redirectToHost = () => {
        window.open('https://doc.projectm.org/ProjectM/ykcla083/', '_blank');
      };

      return {
        redirectToIndex,
        redirectToDocs,
        redirectToHost,
      };
    },
  });
</script>