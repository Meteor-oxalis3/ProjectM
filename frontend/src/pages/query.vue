<template>
    <MenuLogined />

    <iframe
    src="https://udify.app/chatbot/gPKR9FNDedYBKcjy"
    style="width: 100%; height: 100%;"
    frameborder="0"
    @load="onIframeLoad"
    allow="microphone">
    </iframe>

    <!-- 全屏加载对话框 -->
    <v-snackbar v-model="loading" color="primary" location="top">
            <v-progress-circular
                indeterminate
                :size="20"
                color="white"/>
                <span>&nbsp;&nbsp;正在初始化 ProjectM 智能助手...</span>
    </v-snackbar>
</template>

<script lang="ts" setup>
import { ref, provide, watch } from 'vue'
const loading = ref(true)
const pipelineType = ref(localStorage.getItem('pipelineType') || 'metagenomics')
provide('pipelineType', pipelineType)
watch(pipelineType, (val) => localStorage.setItem('pipelineType', val))

const onIframeLoad = () => {
    setTimeout(() => {
        loading.value = false;
    }, 1000);
};
</script>
