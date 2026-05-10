/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Plugins
import { registerPlugins } from '@/plugins'

// Components
import App from './App.vue'

// Composables
import { createApp } from 'vue'

// import vue-flow
/* these are necessary styles for vue flow */
import '@vue-flow/core/dist/style.css';

/* this contains the default theme, these are optional styles */
import '@vue-flow/core/dist/theme-default.css';

// import axios
import axios from 'axios'
axios.defaults.withCredentials = true

// import socket.io
import { io } from 'socket.io-client';

// import pinia
import { createPinia } from 'pinia'
const pinia = createPinia()
const app = createApp(App)
registerPlugins(app)
app.use(pinia)

app.mount('#app')
