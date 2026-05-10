<template>
    <v-container>
      <v-row justify="center" align="center">
        <v-col cols="12">
          <v-card>
            <v-toolbar color="primary" dark>
              <v-card-title>流程</v-card-title>
              <v-spacer />
              <v-btn 
                icon
                @click="confirmDialog = true" 
                color="white" 
                class="ml-2"
                :disabled="selectedFolders.length === 0 || isLoading || isDeleting" 
                :loading="isDeleting">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
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
                <v-btn color="primary" size="small" @click="openWorkflow(item.name)">
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card>
        </v-col>
      </v-row>
  
      <!-- 删除确认对话框 -->
      <v-dialog v-model="confirmDialog" max-width="400px">
        <v-card>
          <v-card-title class="text-h5">确认删除</v-card-title>
          <v-card-text>确定要删除选中的文件吗？此操作无法撤销。</v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="gray" @click="confirmDialog = false">取消</v-btn>
            <v-btn color="error" @click="confirmDelete" :loading="isDeleting">确认删除</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>


      <!-- 打开工作流对话框 -->
      <v-dialog v-model="dialog" width="90%" height="90%">
        <v-card>
          <v-toolbar color="primary" dark>
            <v-toolbar-title>流程监控</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-btn icon @click="dialog = false">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-toolbar>
          <div class="workflow" style="width: 100%; height: 100%;">
            <OpenWorkflow :workflowUuid="selectedWorkflowUuid" />
          </div>
        </v-card>
      </v-dialog>
    </v-container>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, onMounted } from 'vue';
  import axios from 'axios';
  
  const dialog = ref(false);

  interface FolderItem {
    id: number;
    name: string;
    time: string;
    alias: string;
  }

  // 按钮点击事件
  const handleAction = (item: FolderItem) => {
  console.log('Clicked item:', item);
  alert(`You clicked on ${item.name}`);
  };
  const selectedWorkflowUuid = ref<string | null>(null);

  const openWorkflow = (workflowName: string) => {
    selectedWorkflowUuid.value = workflowName;
    dialog.value = true;
  };
  
  export default defineComponent({
    name: 'FolderListComponent',
    setup() {
      const sortBy: any = [{ key: 'time', order: 'desc' }];
      const headers: any = ref([
        // { title: '流程编号', key: 'name', sortable: true },
        { title: '流程名称', key: 'alias', sortable: true },
        { title: '最后更新', key: 'time', sortable: true },
        { title: '监控', key: 'actions', sortable: false, align: 'center' },
      ]);
  
      const folders = ref<FolderItem[]>([]);
      const selectedFolders = ref<FolderItem[]>([]);
      const confirmDialog = ref(false);
      const isLoading = ref(false);
      const isDeleting = ref(false);
  
      const confirmDelete = async () => {
        confirmDialog.value = false;
        if (selectedFolders.value.length === 0) return;
  
        isDeleting.value = true;
        console.log(selectedFolders.value);
        try {
          const response = await axios.post('/api/delete_workflows', {
            folders: selectedFolders.value,
          });
  
          if (response.data.success) {
            // alert('Folders deleted successfully');
            selectedFolders.value = [];
            await refreshFolders();
          } else {
            alert('Failed to delete folders');
          }
        } catch (error) {
          console.error('Error deleting folders:', error);
          alert('Failed to delete folders');
        } finally {
          isDeleting.value = false;
        }
      };
  
      const fetchFolders = async () => {
        try {
          const response = await axios.get('/api/user_workflows');
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
  
      onMounted(() => {
        refreshFolders();
      });
  
      return {
        headers,
        folders,
        selectedFolders,
        confirmDialog,
        isLoading,
        refreshFolders,
        formatTime,
        confirmDelete,
        isDeleting,
        sortBy,
        handleAction,
        dialog,
        openWorkflow,
        selectedWorkflowUuid,
      };
    },
  });
  </script>
  