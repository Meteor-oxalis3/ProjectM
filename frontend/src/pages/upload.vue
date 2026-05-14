<template>
<MenuLogined />
<br>

<v-row>
  <!-- 左侧：管道选择 + 文件上传 -->
  <v-col cols="1"></v-col>
  <v-col cols="4">
    <v-card class="mb-4">
      <v-card-title>选择分析管道</v-card-title>
      <v-card-text>
        <v-radio-group v-model="pipelineType" inline>
          <v-radio label="宏基因组 (Metagenome)" value="metagenomics" color="primary"></v-radio>
          <v-radio label="宏转录组 (Metatranscriptome)" value="metatranscriptomics" color="secondary"></v-radio>
        </v-radio-group>
        <v-alert v-if="pipelineType === 'metagenomics'" type="info" variant="tonal" density="compact">
          宏基因组管道：FastQC → fastp → 去宿主/去PhiX → Kraken2 → LEfSe → MEGAHIT → Prodigal → Prokka → 多样性分析
        </v-alert>
        <v-alert v-if="pipelineType === 'metatranscriptomics'" type="info" variant="tonal" density="compact">
          宏转录组管道：FastQC → fastp → 去宿主/去PhiX → SortMeRNA → Kraken2 → LEfSe → MEGAHIT → Prodigal → CD-HIT → eggNOG-mapper → DESeq2 KO分析
        </v-alert>
      </v-card-text>
    </v-card>

    <v-card>
      <v-card-title>上传原始数据</v-card-title>
      <v-card-text>
        <UploadFiles />
      </v-card-text>
    </v-card>
  </v-col>

  <!-- 右侧：文件列表 -->
  <v-col cols="6">
    <UserFiles />
  </v-col>
  <v-col cols="1"></v-col>

</v-row>

</template>

<script lang="ts" setup>
import { ref, provide, watch } from 'vue'
const pipelineType = ref(localStorage.getItem('pipelineType') || 'metagenomics')
provide('pipelineType', pipelineType)
watch(pipelineType, (val) => localStorage.setItem('pipelineType', val))
</script>
