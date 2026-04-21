<template>
  <div class="container">
    <h1>📦 收纳记录管理</h1>

    <!-- 视图切换 -->
    <div class="view-tabs">
      <button :class="['tab', { active: currentView === 'list' }]" @click="currentView = 'list'">
        📋 列表视图
      </button>
      <button :class="['tab', { active: currentView === 'dashboard' }]" @click="currentView = 'dashboard'">
        📊 数据看板
      </button>
    </div>

    <div class="toolbar">
      <input
        v-model="searchKeyword"
        @input="searchItems"
        placeholder="搜索物品名称、分类、位置..."
        class="search-input"
      />
      <button @click="showForm = true" class="btn-primary">+ 新增物品</button>
    </div>

    <!-- 数据看板视图 -->
    <div v-if="currentView === 'dashboard'" class="dashboard">
      <!-- 统计卡片 -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon">📦</div>
          <div class="stat-info">
            <div class="stat-value">{{ items.length }}</div>
            <div class="stat-label">物品种类</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🔢</div>
          <div class="stat-info">
            <div class="stat-value">{{ totalQuantity }}</div>
            <div class="stat-label">物品总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🏷️</div>
          <div class="stat-info">
            <div class="stat-value">{{ categories.length }}</div>
            <div class="stat-label">分类数量</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📍</div>
          <div class="stat-info">
            <div class="stat-value">{{ locations.length }}</div>
            <div class="stat-label">存放位置</div>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-grid">
        <div class="chart-card">
          <h3>📌 分类分布</h3>
          <Pie :data="categoryChartData" :options="chartOptions" />
        </div>
        <div class="chart-card">
          <h3>📍 位置分布</h3>
          <Bar :data="locationChartData" :options="chartOptions" />
        </div>
        <div class="chart-card">
          <h3>📊 分类数量排行</h3>
          <Bar :data="categoryQuantityChartData" :options="chartOptions" />
        </div>
        <div class="chart-card">
          <h3>🏷️ 位置容量分布</h3>
          <Pie :data="locationQuantityChartData" :options="chartOptions" />
        </div>
      </div>
    </div>

    <!-- 列表视图 -->
    <div v-if="currentView === 'list'" class="table-container">
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
import { Pie, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale
)

const API_BASE = '/api'

// 颜色 palette
const colors = [
  '#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0',
  '#00BCD4', '#FF5722', '#795548', '#607D8B', '#3F51B5'
]

export default {
  name: 'App',
  components: {
    Pie,
    Bar
  },
  data() {
    return {
      items: [],
      searchKeyword: '',
      currentView: 'list',
      showForm: false,
      editingItem: null,
      form: {
        name: '',
        category: '',
        location: '',
        quantity: 1,
        notes: ''
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    }
  },
  computed: {
    totalQuantity() {
      return this.items.reduce((sum, item) => sum + item.quantity, 0)
    },
    categories() {
      return [...new Set(this.items.map(i => i.category))]
    },
    locations() {
      return [...new Set(this.items.map(i => i.location))]
    },
    categoryChartData() {
      const categoryCount = {}
      this.items.forEach(item => {
        categoryCount[item.category] = (categoryCount[item.category] || 0) + 1
      })
      return {
        labels: Object.keys(categoryCount),
        datasets: [{
          data: Object.values(categoryCount),
          backgroundColor: colors.slice(0, Object.keys(categoryCount).length)
        }]
      }
    },
    locationChartData() {
      const locationCount = {}
      this.items.forEach(item => {
        locationCount[item.location] = (locationCount[item.location] || 0) + 1
      })
      return {
        labels: Object.keys(locationCount),
        datasets: [{
          label: '物品数',
          data: Object.values(locationCount),
          backgroundColor: colors.slice(0, Object.keys(locationCount).length)
        }]
      }
    },
    categoryQuantityChartData() {
      const categoryQty = {}
      this.items.forEach(item => {
        categoryQty[item.category] = (categoryQty[item.category] || 0) + item.quantity
      })
      const entries = Object.entries(categoryQty).sort((a, b) => b[1] - a[1])
      return {
        labels: entries.map(e => e[0]),
        datasets: [{
          label: '总数量',
          data: entries.map(e => e[1]),
          backgroundColor: colors.slice(0, entries.length)
        }]
      }
    },
    locationQuantityChartData() {
      const locationQty = {}
      this.items.forEach(item => {
        locationQty[item.location] = (locationQty[item.location] || 0) + item.quantity
      })
      return {
        labels: Object.keys(locationQty),
        datasets: [{
          data: Object.values(locationQty),
          backgroundColor: colors.slice(0, Object.keys(locationQty).length)
        }]
      }
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

/* 视图切换标签 */
.view-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  justify-content: center;
}

.tab {
  padding: 10px 20px;
  border: 2px solid #ddd;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.tab:hover {
  border-color: #4CAF50;
}

.tab.active {
  background: #4CAF50;
  color: white;
  border-color: #4CAF50;
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

/* 数据看板样式 */
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stat-icon {
  font-size: 36px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 13px;
  color: #666;
  margin-top: 2px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.chart-card h3 {
  margin-bottom: 15px;
  color: #333;
  font-size: 16px;
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
  max-height: 90vh;
  overflow-y: auto;
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
