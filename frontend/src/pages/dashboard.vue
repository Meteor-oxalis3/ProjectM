<template>
    <MenuLogined />
    <v-row justify="center" style="height: 99%;">

    <v-col cols="8">
    <iframe 
    src="https://ward.meteor-oxalis3.com"
    width="100%"
    height="99%"
    frameborder="false"
    @load="onIframeLoad"
    />
    </v-col>
    <v-col cols="4" align-self="center" >
            <ListWorkflowsDashboard />
            <ListResultsDashboard />
        </v-col>
    </v-row>

    <!-- 加载 -->
        <v-snackbar v-model="loading" color="primary" location="top">
            <v-progress-circular
                indeterminate
                :size="20"
                color="white"/>
                <span>&nbsp;&nbsp;正在初始化ProjectM监控面板... 请稍候...</span>
        </v-snackbar>
</template>

<script lang="ts" setup>
import ListResults from '@/components/ListResults.vue';
import ListResultsDashboard from '@/components/ListResultsDashboard.vue';
import ListWorkflows from '@/components/ListWorkflows.vue';
import ListWorkflowsDashboard from '@/components/ListWorkflowsDashboard.vue';
import { ref } from 'vue'
const loading = ref(true)
// iframe 加载完成后的回调函数
const onIframeLoad = () => {
    setTimeout(() => {
        loading.value = false;
    }, 1000);
};
</script>