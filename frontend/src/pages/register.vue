<template>
  <v-row justify="center" align="center" style="background: #cbfed8; height: 5vh;">
  </v-row>

  <v-row justify="center" align="center" style="background: linear-gradient(to bottom, #cbfed8, #94b9fd); height: 50vh;">
      <v-img src="/projectm_logo.png"></v-img>
    <v-col cols="5">
      <v-card style="margin-top: 5%;margin-bottom: 5%;">
        <v-card-title class="text-h4" style="text-align: center;">注册</v-card-title>
        <v-divider></v-divider>
        <v-row justify="center" align="center">
          <v-col cols="9">
            <v-card-text>
              <v-alert v-if="message" :type="messageType" dismissible>
                {{ message }}
              </v-alert>
              <v-form ref="form" v-model="valid">
                <v-text-field v-model="username" label="用户名" :rules="[rules.required]" required
                  style="margin-top: 20px;"></v-text-field>
                <v-text-field v-model="email" label="电子邮箱" type="email" :rules="[rules.required, rules.email]"
                  required></v-text-field>
                <v-text-field v-model="password" label="密码" type="password"
                  :rules="[rules.required, rules.minLength(6)]" required></v-text-field>
                <v-text-field v-model="confirmPassword" label="确认密码" type="password"
                  :rules="[rules.required, rules.matchPassword]" required></v-text-field>
                <v-row justify="center" align="center">
                  <v-col cols="5">
                    <v-img :src="captchaSrc" alt="captcha" @click="refreshCaptcha" class="my-4" height="100" width="200"
                      style="border-radius: 25px;"></v-img>
                  </v-col>
                  <v-col cols="5">
                    <v-text-field v-model="captcha" label="验证码" :rules="[rules.required]" required
                      style="margin-top: 20px;"></v-text-field>
                  </v-col>
                </v-row>
                <v-row justify="center" align="center">
                  <v-col cols="3">
                    <v-btn color="primary" class="mt-4" :disabled="!valid || loading" @click="register">
                      提交
                    </v-btn>
                  </v-col>
                </v-row>
              </v-form>
            </v-card-text>
          </v-col>
        </v-row>
        <v-card-actions>
          <v-row justify="center" align="center">
            已经有账号? &nbsp; <v-btn text="点此登录" @click="navigateToLogin"></v-btn>
          </v-row>
        </v-card-actions>
      </v-card>
    </v-col>
  <v-col cols="1"></v-col>

  </v-row>

  <v-row justify="center" align="center" style="background: #94b9fd; height: 45vh;">
  </v-row>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'Register',
  setup() {
    const valid = ref(false);
    const username = ref('');
    const email = ref('');
    const password = ref('');
    const confirmPassword = ref('');
    const captcha = ref('');
    const captchaSrc = ref('/api/captcha'); // Flask 验证码路由
    const message = ref('');
    const messageType: any = ref('success');
    const loading = ref(false); // 防止重复提交
    const router = useRouter();

    const rules = {
      required: (value: string) => !!value || 'This field is required',
      email: (value: string) =>
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || 'Invalid email address',
      minLength: (length: number) => (value: string) =>
        value.length >= length || `Minimum length is ${length}`,
      matchPassword: (value: string) =>
        value === password.value || 'Passwords must match',
    };

    const refreshCaptcha = () => {
      captchaSrc.value = `/api/captcha?t=${new Date().getTime()}`; // 刷新验证码
    };

    const register = async () => {
      if (!valid.value) {
        message.value = 'Please fill out the form correctly.';
        messageType.value = 'error';
        return;
      }
      loading.value = true; // 禁用按钮
      try {
        const response = await axios.post('/api/register', {
          username: username.value,
          email: email.value,
          password: password.value,
          confirmPassword: confirmPassword.value,
          captcha: captcha.value,
        });

        if (response.data.success) {
          message.value = 'Registration successful!';
          messageType.value = 'success';
          setTimeout(() => (router.push('/login')), 2000);
        } else {
          throw new Error(response.data.message || 'Registration failed');
        }
      } catch (err: any) {
        message.value = err.response?.data?.message || 'An error occurred.';
        messageType.value = 'error';
        refreshCaptcha();
      } finally {
        loading.value = false; // 恢复按钮
      }
    };

    // 跳转到登录界面
    const navigateToLogin = () => {
      router.push('/login'); // 跳转到根路径
    };

    return {
      valid,
      username,
      email,
      password,
      confirmPassword,
      captcha,
      captchaSrc,
      message,
      messageType,
      rules,
      refreshCaptcha,
      register,
      loading,
      navigateToLogin
    };
  },
});
</script>