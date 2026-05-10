<template>
  <v-container>
    <v-row justify="center" align="center">
      <v-card width="80%" class="d-flex flex-column">
  <v-toolbar color="primary" dark>
    <v-card-title>已上传的文件</v-card-title>
    <v-spacer />
    <v-btn 
      icon
      @click="confirmDialog = true" 
      color="white" 
      class="ml-2"
      :disabled="selectedFiles.length === 0 || isLoading || isDeleting" 
      :loading="isDeleting">
      <v-icon>mdi-delete</v-icon>
    </v-btn>
    <v-btn icon @click="refreshFiles" color="white" class="ml-2" :loading="isLoading" :disabled="isLoading">
      <v-icon>mdi-refresh</v-icon>
    </v-btn>
  </v-toolbar>

  <v-data-table 
    v-model="selectedFiles" 
    :headers="headers" 
    :items="files" 
    :loading="isLoading" 
    item-value="name"
    :sort-by="sortBy"
    show-select 
    dense 
    class="elevation-1 flex-grow-1" 
    no-data-text="No files available">
    <template v-slot:item.time="{ item }">
      {{ formatTime(item.time) }}
    </template>
  </v-data-table>

  <!-- 右下角 Next 按钮 -->
  <v-card-actions class="justify-end">
    <span>
      <v-icon icon="mdi-tooltip-check-outline"/>
      选中所需文件后，点击下一步
    </span>
    <v-spacer />
    <v-btn
      @click="openDialog" 
      color="#ffffff"
      style="background-color: #1866bf;"
      :disabled="selectedFiles.length === 0">
      下一步
    </v-btn>
  </v-card-actions>
</v-card>
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

    <!-- AI编排对话框 -->
    <v-dialog v-model="dialog" max-width="800px">
      <v-card>
        <v-toolbar color="primary" dark title="AI 编排">
          <v-spacer />
          <v-btn @click="copyToClipboard">
            <v-icon icon='mdi-tooltip-question-outline'></v-icon>
            &nbsp;示例
            <v-tooltip activator="parent" location="top">
              (点击按钮可复制：)<br>
              我有几个ATAC-seq测序样本，<br>
              实验组1有SRR13849307_1和SRR13849307_2，<br>
              实验组2有SRR13849313_1和SRR13849313_2，<br>
              对照组1有SRR13849295_1和SRR13849295_2，<br>
              对照组2有SRR13849301_1和SRR13849301_2
            </v-tooltip>
          </v-btn>
        </v-toolbar>

        <v-container>
          <!-- 新增流程命名和物种选择 -->
          <v-row>
            <v-col cols="6">
              <v-text-field
                v-model="processName"
                label="流程命名"
                variant="filled"
                :rules="[v => !!v || '流程名称不能为空']"
                required
              ></v-text-field>
            </v-col>
            <v-col cols="6">
              <v-select
                v-model="selectedSpecies"
                :items="speciesOptions"
                default-item="人类"
                label="选择物种"
                variant="filled"
                :rules="[v => !!v || '必须选择物种']"
                required
              ></v-select>
            </v-col>
          </v-row>

          <v-textarea
            v-model="inputText"
            label="输入样本描述信息"
            row-height="30"
            rows="4"
            variant="filled"
            auto-grow
            :rules="[v => !!v || '样本描述不能为空']"
          ></v-textarea>
        </v-container>

        <v-card-actions>
          <v-spacer />
          <v-btn color="error" @click="dialog = false">取消</v-btn>
          <v-btn 
            color="primary" 
            @click="sendData" 
            :disabled="!formValid" 
            :loading="isSubmitLoading"
          >
            提交
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 流程提交失败的对话框 -->
    <v-dialog v-model="ErrDialog" max-width="400">
    <v-card>
      <v-card-title class="headline">错误</v-card-title>
      <v-card-text>流程 '{{processName}}' 未能正常运行，请检查输入文件及提示词。</v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn 
        color="primary"
        @click="ErrDialog = false;
        ">确定</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

      <!-- 流程提交成功的对话框 -->
      <v-dialog v-model="OKDialog" max-width="400">
    <v-card>
      <v-card-title class="headline">成功</v-card-title>
      <v-card-text>流程 '{{processName}}' 提交成功，将导航至 '流程与结果' 面板。</v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn 
        color="primary"
        @click="OKWorkflow">确定</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue';
import axios from 'axios';
import type Workflow from '@/pages/workflow.vue';
import { useRouter } from 'vue-router';


const ErrDialog = ref(false)
const OKDialog = ref(false)

interface FileItem {
  id: number;
  name: string;
  time: string;
}

export default defineComponent({
  name: 'FileListComponent',
  setup() {
    const sortBy: any = [{ key: 'time', order: 'desc' }];
    const headers = ref([
      { title: '文件名称', key: 'name', sortable: true },
      // 按照时间新旧排序
      { title: '最后更新', key: 'time', sortable: true },
    ]);

    const files = ref<FileItem[]>([]);
    const selectedFiles = ref<FileItem[]>([]);
    const dialog = ref(false);
    const confirmDialog = ref(false);
    const inputText = ref('');
    const isLoading = ref(false);
    const isSubmitLoading = ref(false);
    const isDeleting = ref(false);
    const textToCopy = ref("我有几个ATAC-seq测序样本，实验组1有SRR13849307_1和SRR13849307_2，实验组2有SRR13849313_1和SRR13849313_2，对照组1有SRR13849295_1和SRR13849295_2，对照组2有SRR13849301_1和SRR13849301_2");

    const processName = ref('');
    const router = useRouter();

    const selectedSpecies = ref('');
    const speciesOptions = ref(['人类', '小鼠']);

    const formValid = computed(() => {
      return (
        processName.value.trim() !== '' &&
        selectedSpecies.value !== '' &&
        inputText.value.trim() !== ''
      );
    });


    const copyToClipboard = async () => {
      try {
        await navigator.clipboard.writeText(textToCopy.value);
      } catch (err) {
        console.error("复制失败:", err);
      }
    };
    
    const confirmDelete = async () => {
      confirmDialog.value = false;
      if (selectedFiles.value.length === 0) return;

      isDeleting.value = true;
      try {
        const response = await axios.post('/api/delete_files', {
          files: selectedFiles.value,
        });

        if (response.data.success) {
          alert('Files deleted successfully');
          selectedFiles.value = [];
          await refreshFiles();
        } else {
          alert('Failed to delete files');
        }
      } catch (error) {
        console.error('Error deleting files:', error);
        alert('Failed to delete files');
      } finally {
        isDeleting.value = false;
      }
    };

    const fetchFiles = async () => {
      try {
        const response = await axios.get('/api/user_upload_files');
        if (response.data.success) {
          files.value = response.data.files.map((file: FileItem) => ({
            id: file.id,
            name: file.name,
            time: file.time,
          }));
        } else {
          files.value = [];
        }
      } catch (error) {
        console.error('Error fetching files:', error);
        alert('Failed to fetch files');
      }
    };

    const refreshFiles = async () => {
      isLoading.value = true;
      try {
        await fetchFiles();
      } catch (error) {
        console.error('Error refreshing files:', error);
        alert('Failed to refresh files');
      } finally {
        isLoading.value = false;
      }
    };

    const openDialog = () => {
      if (selectedFiles.value.length > 0) {
        dialog.value = true;
      }
    };

    const sendData = async () => {
      isSubmitLoading.value = true;
      try {
        const response = await axios.post('/api/receive', {
          workflow_alias: processName.value,
          pipeline_type: localStorage.getItem('pipelineType') || 'metagenomics',
          files: selectedFiles.value,
          input_text: inputText.value,
          user_id: localStorage.getItem('user_id')
        });

        if (response.data.success) {
          // alert('Data sent successfully');
          OKDialog.value = true;
          dialog.value = false;
          inputText.value = '';
          selectedFiles.value = [];
        } else {
          // alert('流程提交失败，请检查输入文件是否完整');
          ErrDialog.value = true;
        }
      } catch (error) {
        console.error('Error sending data:', error);
        alert('Submission failed');
      } finally {
        isSubmitLoading.value = false;
      }
    };

    const formatTime = (time: string) => {
      return new Date(time).toLocaleString();
    };

    const OKWorkflow = () => {
        OKDialog.value = false;
        router.push('/workflow'); // 跳转到 / 路径
      };

    onMounted(() => {
      refreshFiles();
    });

    return {
      OKWorkflow,
      headers,
      files,
      selectedFiles,
      dialog,
      confirmDialog,
      inputText,
      isLoading,
      refreshFiles,
      openDialog,
      sendData,
      formatTime,
      isSubmitLoading,
      confirmDelete,
      isDeleting,
      sortBy,
      copyToClipboard,
      processName,
      selectedSpecies,
      speciesOptions,
      formValid,
      ErrDialog,
      OKDialog
    };
  },
});
</script>
