// stores/dataStore.js
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useDataStore = defineStore('dataStore', () => {
  const jsonData = ref({});  // 存储 JSON 数据

  // 更新 jsonData 的方法
  const updateData = (newData) => {
    jsonData.value = newData;
  };

  return { jsonData, updateData };
});
