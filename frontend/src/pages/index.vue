<template>
  <v-row justify="center" align="center" style="background: linear-gradient(to bottom, #cbfed8, #94b9fd); height: 50vh;">
      <v-img src="/projectm_logo.png" ></v-img>
  </v-row>

  <v-row justify="center" align="center" style="background-color: #94b9fd; height: 5vh;">
    <h1 style="text-align: center; color: white;">ProjectM：基因测序分析流程智能云</h1>
  </v-row>

  <v-row justify="center" align="center" style="background-color: #94b9fd; height: 15vh;">
    <ToLogin />
  </v-row>
  <v-row justify="center" align="center" style="background-color: #94b9fd; height: 5vh;">
    <ToRegister />
  </v-row>

  <v-row justify="center" align="center" style="background-color: #94b9fd; height: 25vh;">
  </v-row>
  
</template>
<script lang="ts" setup>
import ToLogin from '@/components/ToLogin.vue';
import ToRegister from '@/components/ToRegister.vue';

  //
</script>
