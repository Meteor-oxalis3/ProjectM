import { defineStore } from 'pinia';
import axios from 'axios';

export const useDotStore = defineStore('dotStore', {
  state: () => ({
    data: null as Record<string, any> | null, // 存储 JSON 数据
    loading: false, // 加载状态
    error: null as string | null, // 错误信息
  }),
  actions: {
    async fetchData() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get('/api/dot2json');
        this.data = response.data; // 将数据存储到状态
      } catch (error) {
        this.error = error instanceof Error ? error.message : '请求失败';
      } finally {
        this.loading = false;
      }
    },
  },
});
