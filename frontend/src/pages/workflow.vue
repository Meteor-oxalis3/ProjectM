<template>
  <MenuLogined />
  <br>
  <v-row justify="center">
    <v-col cols="1"></v-col>
    <v-col cols="5">
  <ListWorkflows />
    </v-col>
    <v-col cols="5">
      <ListResults />
    </v-col>
    <v-col cols="1"></v-col>

  </v-row>
</template>

<script lang="ts">
import ListResults from '@/components/ListResults.vue';
import ListWorkflows from '@/components/ListWorkflows.vue';
import { ref } from 'vue';

export default {
  setup() {
    const dialog = ref(false);
    return {
      dialog,
    };
  },
};
</script>
