<template>
<MenuLogined />
<br>

<!-- Pipeline Selection -->
<v-row align="center" justify="center">
  <v-col cols="10">
    <v-card>
      <v-card-title>选择分析管道</v-card-title>
      <v-card-text>
        <v-radio-group v-model="pipelineType" inline>
          <v-radio label="宏基因组 (DNA)" value="metagenomics" color="primary"></v-radio>
          <v-radio label="宏转录组 (RNA)" value="metatranscriptomics" color="secondary"></v-radio>
        </v-radio-group>
        <v-alert v-if="pipelineType === 'metagenomics'" type="info" variant="tonal" density="compact">
          宏基因组管道：FastQC → fastp → 去宿主/去PhiX → Kraken2 → LEfSe → MEGAHIT → Prodigal → Prokka → 多样性分析
        </v-alert>
        <v-alert v-if="pipelineType === 'metatranscriptomics'" type="success" variant="tonal" density="compact">
          宏转录组管道：FastQC → fastp → 去宿主/去PhiX → SortMeRNA → Kraken2 → LEfSe → MEGAHIT → Prodigal → CD-HIT → eggNOG-mapper → DESeq2 KO分析
        </v-alert>
      </v-card-text>
    </v-card>
  </v-col>
</v-row>

<br>

<!-- Sample Table Upload -->
<v-row align="center" justify="center">
  <v-col cols="10">
    <v-card>
      <v-card-title>上传样本信息表 (CSV)</v-card-title>
      <v-card-subtitle>
        格式：ID,fastq1,fastq2,group（group 为分组名如 UC / nonIBD）
      </v-card-subtitle>
      <v-card-text>
        <UploadFiles />
      </v-card-text>
    </v-card>
  </v-col>
</v-row>

<br>

<v-row align="center">
    <v-col cols="1"></v-col>
    <v-col cols="10">
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
