<template>
    <div class="custom-node">
        ✅ &nbsp;
      <div>{{ data.label }}</div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  
  export default defineComponent({
    props: {
      data: {
        type: Object,
        required: true,
      },
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
  