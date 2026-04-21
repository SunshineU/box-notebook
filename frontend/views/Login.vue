<template>
  <div class="login-container">
    <div class="login-box">
      <h1>📦 收纳记录管理</h1>

      <div class="tabs">
        <button :class="['tab', { active: isLogin }]" @click="isLogin = true">登录</button>
        <button :class="['tab', { active: !isLogin }]" @click="isLogin = false">注册</button>
      </div>

      <form @submit.prevent="handleSubmit" class="form">
        <div class="form-group" v-if="!isLogin">
          <label>邮箱</label>
          <input v-model="form.email" type="email" required placeholder="your@email.com" />
        </div>

        <div class="form-group">
          <label>用户名</label>
          <input v-model="form.username" type="text" required
                 :placeholder="isLogin ? '输入用户名' : '至少 3 个字符'"
                 :minlength="isLogin ? 1 : 3" />
        </div>

        <div class="form-group">
          <label>密码</label>
          <input v-model="form.password" type="password" required
                 :placeholder="isLogin ? '输入密码' : '至少 6 个字符'"
                 :minlength="isLogin ? 1 : 6" />
        </div>

        <div v-if="error" class="error">{{ error }}</div>

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? '加载中...' : (isLogin ? '登录' : '注册') }}
        </button>
      </form>

      <p class="tip">💡 首次使用请注册账号，数据存储在本地</p>
    </div>
  </div>
</template>

<script>
import { authAPI } from '../api.js'

export default {
  name: 'Login',
  data() {
    return {
      isLogin: true,
      form: {
        username: '',
        email: '',
        password: ''
      },
      error: '',
      loading: false
    }
  },
  methods: {
    async handleSubmit() {
      this.error = ''
      this.loading = true

      try {
        if (this.isLogin) {
          const res = await authAPI.login(this.form.username, this.form.password)
          this.onSuccess(res.data)
        } else {
          const res = await authAPI.register(this.form.username, this.form.email, this.form.password)
          this.onSuccess(res.data)
        }
      } catch (err) {
        this.error = err.response?.data?.detail || '操作失败，请重试'
      } finally {
        this.loading = false
      }
    },
    onSuccess(data) {
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('username', data.username)
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-box {
  background: white;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.login-box h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 24px;
}

.tabs {
  display: flex;
  margin-bottom: 25px;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #eee;
}

.tab {
  flex: 1;
  padding: 12px;
  border: none;
  background: #f9f9f9;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s;
}

.tab.active {
  background: #667eea;
  color: white;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.form-group input {
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.error {
  background: #fee;
  color: #c33;
  padding: 10px 15px;
  border-radius: 8px;
  font-size: 14px;
}

.btn-submit {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, opacity 0.2s;
}

.btn-submit:hover {
  transform: translateY(-2px);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.tip {
  text-align: center;
  color: #999;
  font-size: 13px;
  margin-top: 20px;
}

@media (max-width: 420px) {
  .login-box {
    padding: 30px 20px;
  }
}
</style>
