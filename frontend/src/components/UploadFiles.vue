<template>
    <v-row align="center" justify="center">
    <v-col cols="8">
    <v-file-input
      label="点击上传文件"
      show-size
      v-model="selectedFile"
      accept="*"
    ></v-file-input>
    </v-col>

    <v-col cols="4">
    <v-btn
      color="primary"
      @click="uploadFile"
      :disabled="!selectedFile"
      :loading="uploading"
    >
      <v-icon left>mdi-cloud-upload</v-icon>
      开始上传
    </v-btn>
    </v-col>
  </v-row>

    <v-dialog v-model="dialog" persistent max-width="500">
      <v-card>
        <v-card-title class="headline">文件上传中...</v-card-title>
        <v-card-text>
          <v-progress-linear
            v-model="uploadProgress"
            color="light-blue"
            height="25"
            striped
            reactive
          >
            <strong>{{ uploadProgress }}%</strong>
          </v-progress-linear>
          <div class="text-caption mt-2">已上传 {{ uploadedSize }} MB</div>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn 
            color="red darken-1" 
            text 
            @click="cancelUpload"
            :disabled="uploadComplete"
          >
            取消
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      selectedFile: null,
      dialog: false,
      uploadProgress: 0,
      uploadComplete: false,
      uploading: false,
      totalSize: 0,
      uploadedSize: 0,
      cancelToken: null,
    };
  },

  methods: {
    handleFileSelect(files) {
      this.selectedFile = files && files.length > 0 ? files[0] : null;
      if (this.selectedFile) {
        this.totalSize = (this.selectedFile.size / 1024 / 1024).toFixed(2);
      }
    },

    async uploadFile() {
      if (!this.selectedFile) return;

      this.dialog = true;
      this.uploading = true;
      this.uploadComplete = false;
      this.uploadProgress = 0;
      this.uploadedSize = 0;
      
      const CancelToken = axios.CancelToken;
      const source = CancelToken.source();
      this.cancelToken = source;

      const formData = new FormData();
      formData.append("file", this.selectedFile);

      try {
        const response = await axios.post("/api/upload_raw_files", formData, {
          headers: { "Content-Type": "multipart/form-data" },
          cancelToken: source.token,
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              this.uploadProgress = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              this.uploadedSize = (progressEvent.loaded / 1024 / 1024).toFixed(2);
            }
          },
        });

        console.log("上传成功:", response.data);
        this.uploadComplete = true;
        setTimeout(() => {
          this.dialog = false;
          this.resetState();
        }, 100);
      } catch (error) {
        if (!axios.isCancel(error)) {
          console.error("上传失败:", error);
          this.$emit("upload-error", error);
        }
      } finally {
        this.uploading = false;
      }
    },

    cancelUpload() {
      if (this.cancelToken) {
        this.cancelToken.cancel("用户取消上传");
      }
      this.dialog = false;
      this.resetState();
    },

    resetState() {
      this.selectedFile = null;
      this.uploadProgress = 0;
      this.uploadComplete = false;
      this.totalSize = 0;
      this.uploadedSize = 0;
      this.cancelToken = null;
    }
  }
};
</script>

<style scoped>
.v-btn {
  transition: all 0.3s ease;
}
</style>