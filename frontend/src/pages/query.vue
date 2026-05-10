<template>
    <MenuLogined />

    <!-- Pipeline Type Selector -->
    <v-row justify="center" class="mt-2">
      <v-col cols="8">
        <v-radio-group v-model="pipelineType" inline hide-details density="compact">
          <v-radio label="宏基因组 (DNA)" value="metagenomics" color="primary"></v-radio>
          <v-radio label="宏转录组 (RNA)" value="metatranscriptomics" color="secondary"></v-radio>
        </v-radio-group>
      </v-col>
    </v-row>

    <iframe
    src="https://udify.app/chatbot/yyzIX6mPIpV2Zllf"
    style="width: 100%; height: 90%;"
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
                <span>&nbsp;&nbsp;正在初始化 ProjectM 智能助手... 请选择上方的分析管道后开始对话</span>
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
