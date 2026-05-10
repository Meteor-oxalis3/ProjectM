<template>
    <v-card flat>
      <v-card-text>
        <v-data-table :headers="headers" :items="files" dense>
          <template v-slot:item.filename="{ item }">
            {{ item.filename }}
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn color="primary" size="small" @click="openPreview(item.url)">
              <v-icon>mdi-eye</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  
    <!-- 预览弹出框 -->
    <v-dialog v-model="previewDialog" fullscreen>
      <v-card>
        <v-toolbar color="primary" dark>
          <v-card-title>在线预览</v-card-title>
          <v-spacer></v-spacer>
          <v-btn icon @click="previewDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-toolbar>
        <v-divider></v-divider>
        <v-card-text style="height: 70vh;">
          <iframe v-if="selectedUrl" :src="selectedUrl" style="width: 100%; height: 100%;" frameborder="0"></iframe>
        </v-card-text>
      </v-card>
    </v-dialog>
  
    <!-- Snackbar 提示 -->
    <v-snackbar v-model="snackbar" timeout="1000" location="top">
      {{ snackbarText }}
    </v-snackbar>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, watch } from 'vue';
  import axios from 'axios';
  
  export default defineComponent({
    name: 'OpenResultPreview',
    props: {
      workflowUuid: {
        type: String,
        required: true
      }
    },
    setup(props) {
      const files = ref<{ filename: string; url: string }[]>([]);
      const lastUpdated = ref<string>('');
      const previewDialog = ref(false);
      const selectedUrl = ref<string | null>(null);
      const snackbar = ref(false);
      const snackbarText = ref('');
  
      const headers = [
        { title: '文件名称', key: 'filename', sortable: false },
        { title: '预览', key: 'actions', sortable: false }
      ];
  
      const fetchPreviewFiles = async () => {
        try {
          const response = await axios.post('/api/preview', {
            workflow_uuid: props.workflowUuid
          });
          if (response.data.success) {
            files.value = response.data.files;
            lastUpdated.value = new Date().toLocaleString();
          } else {
            files.value = [];
          }
        } catch (error) {
          console.error('Error fetching preview files:', error);
          files.value = [];
        }
      };
  
      watch(() => props.workflowUuid, fetchPreviewFiles, { immediate: true });
  
      const openPreview = (url: string) => {
        snackbarText.value = '文件预览加载中，请耐心等待...';
        snackbar.value = true;

        selectedUrl.value = url;
        previewDialog.value = true;

        // 等待 iframe 加载成功后延迟关闭 snackbar
        const iframe = document.querySelector('iframe') as HTMLIFrameElement;
        if (iframe) {
            iframe.onload = () => {
            setTimeout(() => {
                snackbar.value = false;
            }, 5000); // 延迟 2 秒关闭 Snackbar
            };
        }
        };

  
      return {
        headers,
        files,
        lastUpdated,
        previewDialog,
        selectedUrl,
        snackbar,
        snackbarText,
        openPreview
      };
    }
  });
  </script>
  