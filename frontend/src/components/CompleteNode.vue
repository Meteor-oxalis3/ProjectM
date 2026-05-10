<template>
  <div class="custom-node" style="border-color: green;border-width: 3px; background-color: rgba(0,255,0,0.3);">
    <Handle type="target" :position="Position.Left" />
    <!-- <img src="/loadGif.gif" alt="GIF" class="gif-icon" /> -->
    ✅ &nbsp;
    <div>{{ data.label }}</div>
    <!-- 右侧连接点 -->
    <Handle type="source" :position="Position.Right" />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { Handle, Position } from '@vue-flow/core';

export default defineComponent({
  components: {
    Handle,
  },
  props: {
    data: {
      type: Object,
      required: true,
    },
  },
  setup() {
    return {
      Position, // 将 Position 暴露给模板
    };
  },
});
</script>


<style scoped>
.custom-node {
  padding: 10px;
  /* background-color: #f9f9f9; */
  border: 1px solid #ccc;
  border-radius: 4px;
  display: flex;
  align-items: center;
}
.gif-icon {
  width: 15px;
  height: 15px;
  margin-right: 5px;
}
</style>
