<template>
  <v-app>
    <Menu />
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script lang="ts" setup>
import Menu from './components/Menu.vue';

  //
</script>

<style>
body {
    background-color: #607D8B; /* Gray-blue color */
}
</style>
