<template>
  <div class="container">
    <h1>📦 收纳记录管理</h1>

    <div class="toolbar">
      <input
        v-model="searchKeyword"
        @input="searchItems"
        placeholder="搜索物品名称、分类、位置..."
        class="search-input"
      />
      <button @click="showForm = true" class="btn-primary">+ 新增物品</button>
    </div>

    <div class="stats" v-if="items.length > 0">
      <span>共 {{ items.length }} 件物品</span>
      <span>总数量：{{ totalQuantity }} 件</span>
    </div>

    <div class="table-container">
      <table v-if="items.length > 0">
        <thead>
          <tr>
            <th>ID</th>
            <th>名称</th>
            <th>分类</th>
            <th>位置</th>
            <th>数量</th>
            <th>备注</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>{{ item.id }}</td>
            <td>{{ item.name }}</td>
            <td><span class="tag">{{ item.category }}</span></td>
            <td>{{ item.location }}</td>
            <td>{{ item.quantity }}</td>
            <td class="notes">{{ item.notes }}</td>
            <td>
              <button @click="editItem(item)" class="btn-edit">编辑</button>
              <button @click="deleteItem(item.id)" class="btn-delete">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">
        <p>暂无物品记录，点击上方按钮添加</p>
      </div>
    </div>

    <!-- 弹窗表单 -->
    <div v-if="showForm" class="modal-overlay" @click.self="closeForm">
      <div class="modal">
        <h2>{{ editingItem ? '编辑物品' : '新增物品' }}</h2>
        <form @submit.prevent="submitForm">
          <div class="form-group">
            <label>名称 *</label>
            <input v-model="form.name" required />
          </div>
          <div class="form-group">
            <label>分类 *</label>
            <input v-model="form.category" required placeholder="如：文具、工具、衣物..." />
          </div>
          <div class="form-group">
            <label>位置 *</label>
            <input v-model="form.location" required placeholder="如：A 区 -1 层 -2 号" />
          </div>
          <div class="form-group">
            <label>数量</label>
            <input v-model.number="form.quantity" type="number" min="1" />
          </div>
          <div class="form-group">
            <label>备注</label>
            <textarea v-model="form.notes" rows="3"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeForm" class="btn-cancel">取消</button>
            <button type="submit" class="btn-primary">确定</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_BASE = '/api'

export default {
  name: 'App',
  data() {
    return {
      items: [],
      searchKeyword: '',
      showForm: false,
      editingItem: null,
      form: {
        name: '',
        category: '',
        location: '',
        quantity: 1,
        notes: ''
      }
    }
  },
  computed: {
    totalQuantity() {
      return this.items.reduce((sum, item) => sum + item.quantity, 0)
    }
  },
  mounted() {
    this.loadItems()
  },
  methods: {
    async loadItems() {
      try {
        const res = await axios.get(`${API_BASE}/items`)
        this.items = res.data
      } catch (err) {
        console.error('加载失败:', err)
      }
    },
    async searchItems() {
      if (!this.searchKeyword.trim()) {
        this.loadItems()
        return
      }
      try {
        const res = await axios.get(`${API_BASE}/items`, {
          params: { keyword: this.searchKeyword }
        })
        this.items = res.data
      } catch (err) {
        console.error('搜索失败:', err)
      }
    },
    editItem(item) {
      this.editingItem = item
      this.form = {
        name: item.name,
        category: item.category,
        location: item.location,
        quantity: item.quantity,
        notes: item.notes || ''
      }
      this.showForm = true
    },
    closeForm() {
      this.showForm = false
      this.editingItem = null
      this.form = { name: '', category: '', location: '', quantity: 1, notes: '' }
    },
    async submitForm() {
      try {
        if (this.editingItem) {
          await axios.put(`${API_BASE}/items/${this.editingItem.id}`, this.form)
        } else {
          await axios.post(`${API_BASE}/items`, this.form)
        }
        this.closeForm()
        this.loadItems()
      } catch (err) {
        console.error('保存失败:', err)
      }
    },
    async deleteItem(id) {
      if (!confirm('确定要删除这个物品吗？')) return
      try {
        await axios.delete(`${API_BASE}/items/${id}`)
        this.loadItems()
      } catch (err) {
        console.error('删除失败:', err)
      }
    }
  }
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f5f5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.btn-primary {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary:hover {
  background: #45a049;
}

.stats {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  color: #666;
  font-size: 14px;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 13px;
}

.notes {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #999;
}

.btn-edit, .btn-delete {
  padding: 4px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 5px;
}

.btn-edit {
  background: #2196F3;
  color: white;
}

.btn-delete {
  background: #f44336;
  color: white;
}

.empty-state {
  padding: 60px;
  text-align: center;
  color: #999;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 24px;
  width: 100%;
  max-width: 450px;
}

.modal h2 {
  margin-bottom: 20px;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn-cancel {
  background: #eee;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
}
</style>
