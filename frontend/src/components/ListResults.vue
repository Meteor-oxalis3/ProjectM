<template>
  <v-container>
    <v-row justify="center" align="center">
      <v-col cols="12">
        <v-card>
          <v-toolbar color="primary" dark>
            <v-card-title>结果文件</v-card-title>
            <v-spacer />
            <v-btn icon @click="refreshFolders" color="white" class="ml-2" :loading="isLoading" :disabled="isLoading">
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </v-toolbar>

          <v-data-table
            v-model="selectedFolders" 
            :headers="headers" 
            :items="folders" 
            :loading="isLoading"
            item-value="name"
            :sort-by="sortBy"
            show-select
            dense 
            class="elevation-1" 
            no-data-text="No workflows available.">
            
            <template v-slot:item.time="{ item }">
              {{ formatTime(item.time) }}
            </template>
            
            <template v-slot:item.actions="{ item }">
              <v-btn color="primary" size="small" @click="downloadFile(item.name)">
                <v-icon>mdi-download</v-icon>
              </v-btn>
            </template>

            <template v-slot:item.preview="{ item }">
              <v-btn 
                color="secondary" 
                size="small" 
                @click="openPreview(item.name)"
                class="ml-2"
              >
                <v-icon>mdi-eye</v-icon>
              </v-btn>
            </template>

          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- 下载进度对话框 -->
    <v-dialog v-model="downloadDialog" persistent max-width="400px">
      <v-card>
        <v-card-title class="text-h6">下载中，请稍候...</v-card-title>
        <v-card-text>
          <v-progress-linear v-model="downloadProgress" height="20" color="blue" striped rounded>
            {{ downloadProgress.toFixed(2) }}%
          </v-progress-linear>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="red" @click="cancelDownload" :disabled="!isDownloading">取消</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="PreviewDialog" width="40%">
        <v-card>
          <v-toolbar color="primary" dark>
            <v-toolbar-title>结果预览</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-btn icon @click="PreviewDialog = false">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-toolbar>
          <div class="workflow" style="width: 100%; height: 100%;">
            <OpenResultPreview :workflowUuid="selectedWorkflowUuid" />
          </div>
        </v-card>
      </v-dialog>

  </v-container>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import axios from 'axios';
import OpenResultPreview from './OpenResultPreview.vue';

interface FolderItem {
  id: number;
  name: string;
  time: string;
  alias: string;
}

export default defineComponent({
  name: 'FolderListComponent',
  setup() {
    const sortBy: any = [{ key: 'time', order: 'desc' }];
    const headers: any = ref([
    // { title: '流程编号', key: 'name', sortable: true },
    { title: '流程名称', key: 'alias', sortable: true },
    { title: '最后更新', key: 'time', sortable: true },
    { title: '在线预览', key: 'preview', sortable: false, align: 'center'}, // 新增预览列
    { title: '下载', key: 'actions', sortable: false, align: 'center' },
  ]);

    const folders = ref<FolderItem[]>([]);
    const selectedFolders = ref<FolderItem[]>([]);
    const isLoading = ref(false);

    const downloadDialog = ref(false);
    const downloadProgress = ref(0);
    const isDownloading = ref(false);

    const PreviewDialog = ref(false);

    const selectedWorkflowUuid = ref<string | null>(null);
    const openPreview = (workflowName: string) => {
      selectedWorkflowUuid.value = workflowName;
      PreviewDialog.value = true;
    };

    let xhrRequest: XMLHttpRequest | null = null;

    const fetchFolders = async () => {
      try {
        const response = await axios.get('/api/user_results');
        if (response.data.success) {
          folders.value = response.data.folders.map((folder: FolderItem) => ({
            id: folder.id,
            name: folder.name,
            time: folder.time,
            alias: folder.alias,
          }));
        } else {
          folders.value = [];
        }
      } catch (error) {
        console.error('Error fetching folders:', error);
        alert('Failed to fetch folders');
      }
    };

    const refreshFolders = async () => {
      isLoading.value = true;
      try {
        await fetchFolders();
      } catch (error) {
        console.error('Error refreshing folders:', error);
        alert('Failed to refresh folders');
      } finally {
        isLoading.value = false;
      }
    };

    const formatTime = (time: string) => {
      return new Date(time).toLocaleString();
    };

    const downloadFile = async (filename: string) => {
      const url = "/api/results_download";
      xhrRequest = new XMLHttpRequest();
      xhrRequest.open("POST", url, true);
      xhrRequest.responseType = "blob";

      xhrRequest.setRequestHeader("Content-Type", "application/json");

      // 显示对话框
      downloadDialog.value = true;
      downloadProgress.value = 0;
      isDownloading.value = true;

      // 监听下载进度
      xhrRequest.onprogress = (event) => {
        if (event.lengthComputable) {
          downloadProgress.value = (event.loaded / event.total) * 100;
        }
      };

      xhrRequest.onload = () => {
        if (xhrRequest?.status === 200) {
          // 创建 Blob 并下载
          const blob = new Blob([xhrRequest.response]);
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.download = filename + "_results.zip";
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        } else {
          console.error("Download failed:", xhrRequest?.statusText);
        }

        // 关闭对话框
        downloadDialog.value = false;
        isDownloading.value = false;
      };

      xhrRequest.onerror = () => {
        console.error("Network error during download");
        downloadDialog.value = false;
        isDownloading.value = false;
      };

      // 发送请求
      xhrRequest.send(JSON.stringify({ filename }));
    };

    const cancelDownload = () => {
      if (xhrRequest) {
        xhrRequest.abort();
        console.log("Download canceled");
      }
      downloadDialog.value = false;
      isDownloading.value = false;
    };

    onMounted(() => {
      refreshFolders();
    });

    return {
      headers,
      folders,
      selectedFolders,
      isLoading,
      refreshFolders,
      formatTime,
      sortBy,
      downloadFile,
      downloadDialog,
      downloadProgress,
      isDownloading,
      cancelDownload,
      PreviewDialog,
      openPreview,
      selectedWorkflowUuid,
    };
  },
});
</script>