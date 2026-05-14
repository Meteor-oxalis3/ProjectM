<template>
  <v-row justify="center" align="center" style="background: #cbfed8; height: 20vh;">
  </v-row>

  <v-row justify="center" align="center" style="background: linear-gradient(to bottom, #cbfed8, #94b9fd); height: 50vh;">
    <v-col cols="1"></v-col>
      <v-img src="/projectm_logo.png" ></v-img>
    <v-col cols="1"></v-col>
    <v-col cols="4">
      <v-card style="margin-top: 5%; margin-bottom: 5%;" height="auto">
        <v-card-title class="text-h4 text-center">登录</v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-row justify="center" align="center">
            <v-col cols="8">
              <v-form ref="form" v-model="valid">
                <v-alert v-if="message" :type="messageType" dismissible>
                  {{ message }}
                </v-alert>
                <v-text-field
                  v-model="username"
                  label="用户名"
                  :rules="[rules.required]"
                  required
                  style="margin-top: 20px;"
                ></v-text-field>
                <v-text-field
                  v-model="password"
                  label="密码"
                  type="password"
                  :rules="[rules.required, rules.minLength(6)]"
                  required
                ></v-text-field>

                <v-row justify="center">
                  <v-col cols="auto">
                    <v-btn color="primary" :disabled="!valid || loading" @click="login">
                      <v-progress-circular v-if="loading" indeterminate size="20" color="white"></v-progress-circular>
                      <span v-else>登录</span>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-form>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-row justify="center" align="center">
            还没有账号? &nbsp;
            <v-btn text="点此注册" @click="navigateToRegister"></v-btn>
          </v-row>
        </v-card-actions>
        <v-divider></v-divider>
        <v-btn text="测试账号: demo" @click="autoFillAndLogin"></v-btn>
      </v-card>
    </v-col>
    <v-col cols="2"></v-col>
  </v-row>

  <v-row justify="center" align="center" style="background: #94b9fd; height: 30vh;">
  </v-row>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'Login',
  setup() {
    const valid = ref(false);
    const username = ref('');
    const password = ref('');
    const message = ref('');
    const messageType = ref<'success' | 'error'>('success');
    const loading = ref(false);
    const router = useRouter();

    const rules = {
      required: (value: string) => !!value || 'This field is required',
      minLength: (length: number) => (value: string) =>
        value.length >= length || `Minimum length is ${length}`,
    };

    const login = async () => {
      loading.value = true;
      message.value = '';

      try {
        const response = await axios.post(
          '/api/login',
          { username: username.value, password: password.value },
          { withCredentials: true } // 确保请求携带 session 信息
        );

        if (response.data.success) {
          message.value = '登录成功!';
          messageType.value = 'success';

          // 存储用户信息到 localStorage
          localStorage.setItem('currentUser', JSON.stringify(response.data.user));
          // 存储user_id
          localStorage.setItem('user_id', response.data.user.id);

          // 延迟 1 秒后跳转，提供更好的用户体验
          setTimeout(() => router.push('/dashboard'), 1000);
        } else {
          message.value = response.data.message || 'Invalid credentials';
          messageType.value = 'error';
        }
      } catch (err: any) {
        message.value = err.response?.data?.message || 'An error occurred.';
        messageType.value = 'error';
      } finally {
        loading.value = false;
      }
    };

    const navigateToRegister = () => {
      router.push('/register');
    };

    const autoFillAndLogin = () => {
      username.value = 'demo'; // 替换为你的账号
      password.value = 'demo123';

      // 短暂延迟后自动提交
      setTimeout(login, 500);
    };

    return {
      valid,
      username,
      password,
      message,
      messageType,
      rules,
      login,
      navigateToRegister,
      loading,
      autoFillAndLogin
    };
  },
});
</script>
