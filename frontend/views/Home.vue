<template>
  <div class="container">
    <div class="header">
      <h1>📦 收纳记录管理</h1>
      <div class="user-info">
        <span class="username">👤 {{ username }}</span>
        <button @click="logout" class="btn-logout">退出</button>
      </div>
    </div>

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
        @keydown.enter="quickAdd"
        placeholder="搜索物品名称、分类、位置... (回车快速新增)"
        class="search-input"
      />
      <button @click="exportCSV" class="btn-secondary">📥 导出</button>
      <button @click="showImportModal = true" class="btn-secondary">📤 导入</button>
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
          <tr v-for="item in items" :key="item.id" @dblclick="editItem(item)" class="clickable-row">
            <td>{{ item.id }}</td>
            <td>{{ item.name }}</td>
            <td><span class="tag">{{ item.category }}</span></td>
            <td>{{ item.location }}</td>
            <td>{{ item.quantity }}</td>
            <td class="notes">{{ item.notes }}</td>
            <td>
              <button @click="editItem(item)" class="btn-edit" title="双击也可编辑">编辑</button>
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
            <input v-model="form.name" ref="nameInput" required placeholder="输入名称后回车可快速保存" />
          </div>
          <div class="form-group">
            <label>分类 *</label>
            <div class="input-with-quick">
              <input v-model="form.category" required placeholder="如：文具、工具、衣物..." />
              <div class="quick-select">
                <span v-for="cat in commonCategories" :key="cat" @click="form.category = cat" class="quick-tag">
                  {{ cat }}
                </span>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>位置 *</label>
            <div class="input-with-quick">
              <input v-model="form.location" required placeholder="如：A 区 -1 层 -2 号" />
              <div class="quick-select">
                <span v-for="loc in commonLocations" :key="loc" @click="form.location = loc" class="quick-tag">
                  {{ loc }}
                </span>
              </div>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>数量</label>
              <input v-model.number="form.quantity" type="number" min="1" />
            </div>
          </div>
          <div class="form-group">
            <label>备注</label>
            <textarea v-model="form.notes" rows="2" placeholder="可选"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeForm" class="btn-cancel">取消 (Esc)</button>
            <button type="submit" class="btn-primary">💾 保存 (Enter)</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 导入弹窗 -->
    <div v-if="showImportModal" class="modal-overlay" @click.self="closeImportModal">
      <div class="modal">
        <h2>📤 导入物品数据</h2>
        <div class="import-content">
          <p class="import-hint">请上传 CSV 文件，文件需包含以下列：name, category, location</p>
          <p class="import-hint-small">可选列：quantity (默认 1), notes (默认空)</p>
          <input
            type="file"
            ref="fileInput"
            accept=".csv"
            @change="onFileSelect"
            class="file-input"
          />
          <div v-if="importError" class="error-message">{{ importError }}</div>
          <div v-if="importSuccess" class="success-message">✅ 成功导入 {{ importSuccess }} 条记录</div>
        </div>
        <div class="form-actions">
          <button type="button" @click="closeImportModal" class="btn-cancel">取消</button>
          <button type="button" @click="uploadFile" class="btn-primary" :disabled="!selectedFile">上传</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { itemAPI } from '../services.js'
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

// 颜色 palette
const colors = [
  '#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0',
  '#00BCD4', '#FF5722', '#795548', '#607D8B', '#3F51B5'
]

export default {
  name: 'Home',
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
      showImportModal: false,
      editingItem: null,
      form: {
        name: '',
        category: '',
        location: '',
        quantity: 1,
        notes: ''
      },
      selectedFile: null,
      importError: '',
      importSuccess: '',
      username: localStorage.getItem('username') || '用户',
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
    // 常用分类（出现次数最多的前 5 个）
    commonCategories() {
      const count = {}
      this.items.forEach(item => {
        count[item.category] = (count[item.category] || 0) + 1
      })
      return Object.entries(count)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(e => e[0])
    },
    // 常用位置（出现次数最多的前 5 个）
    commonLocations() {
      const count = {}
      this.items.forEach(item => {
        count[item.location] = (count[item.location] || 0) + 1
      })
      return Object.entries(count)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(e => e[0])
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
    // 监听 Esc 键关闭表单
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.showForm) {
        this.closeForm()
      }
    })
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      this.$router.push('/login')
    },
    async loadItems() {
      try {
        const res = await itemAPI.getAll()
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
        const res = await itemAPI.getAll(this.searchKeyword)
        this.items = res.data
      } catch (err) {
        console.error('搜索失败:', err)
      }
    },
    // 快速新增：使用搜索词作为名称
    quickAdd() {
      const keyword = this.searchKeyword.trim()
      if (!keyword) return
      this.form = {
        name: keyword,
        category: this.commonCategories[0] || '',
        location: this.commonLocations[0] || '',
        quantity: 1,
        notes: ''
      }
      this.showForm = true
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
      this.$nextTick(() => {
        this.$refs.nameInput?.focus()
      })
    },
    closeForm() {
      this.showForm = false
      this.editingItem = null
      this.form = { name: '', category: '', location: '', quantity: 1, notes: '' }
    },
    async submitForm() {
      try {
        if (this.editingItem) {
          await itemAPI.update(this.editingItem.id, this.form)
        } else {
          await itemAPI.create(this.form)
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
        await itemAPI.delete(id)
        this.loadItems()
      } catch (err) {
        console.error('删除失败:', err)
      }
    },
    // 导出 CSV
    async exportCSV() {
      try {
        const res = await itemAPI.exportCSV()
        // 创建下载链接
        const blob = new Blob([res.data], { type: 'text/csv;charset=utf-8;' })
        const link = document.createElement('a')
        const url = URL.createObjectURL(blob)
        link.setAttribute('href', url)
        link.setAttribute('download', `items_${new Date().toISOString().split('T')[0]}.csv`)
        link.style.visibility = 'hidden'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (err) {
        console.error('导出失败:', err)
        if (err.response?.status === 404) {
          alert('没有可导出的数据')
        } else {
          alert('导出失败，请重试')
        }
      }
    },
    // 导入相关方法
    closeImportModal() {
      this.showImportModal = false
      this.selectedFile = null
      this.importError = ''
      this.importSuccess = ''
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
    },
    onFileSelect(event) {
      const file = event.target.files[0]
      if (file && file.name.endsWith('.csv')) {
        this.selectedFile = file
        this.importError = ''
        this.importSuccess = ''
      } else {
        this.importError = '请选择 CSV 文件'
        this.selectedFile = null
      }
    },
    async uploadFile() {
      if (!this.selectedFile) return
      try {
        const res = await itemAPI.importCSV(this.selectedFile)
        this.importSuccess = res.data.imported
        this.importError = ''
        // 成功后关闭弹窗并刷新列表
        setTimeout(() => {
          this.closeImportModal()
          this.loadItems()
        }, 1500)
      } catch (err) {
        console.error('导入失败:', err)
        this.importError = err.response?.data?.detail || '导入失败，请重试'
        this.importSuccess = ''
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

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.header h1 {
  text-align: center;
  color: #333;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  color: #666;
  font-size: 14px;
}

.btn-logout {
  background: #f44336;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.btn-logout:hover {
  background: #d32f2f;
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

.btn-secondary {
  background: #2196F3;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary:hover {
  background: #1976d2;
}

.btn-secondary:disabled {
  background: #bdbdbd;
  cursor: not-allowed;
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

/* 导入弹窗样式 */
.import-content {
  padding: 10px 0;
}

.import-hint {
  color: #333;
  font-size: 14px;
  margin-bottom: 8px;
}

.import-hint-small {
  color: #666;
  font-size: 12px;
  margin-bottom: 15px;
}

.file-input {
  width: 100%;
  padding: 10px;
  border: 2px dashed #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.file-input:hover {
  border-color: #2196F3;
}

.error-message {
  color: #f44336;
  font-size: 14px;
  margin-top: 10px;
  padding: 8px;
  background: #ffebee;
  border-radius: 4px;
}

.success-message {
  color: #4CAF50;
  font-size: 14px;
  margin-top: 10px;
  padding: 8px;
  background: #e8f5e9;
  border-radius: 4px;
}

/* 可点击的行 */
.clickable-row {
  cursor: pointer;
}

.clickable-row:hover {
  background: #f5f5f5;
}

/* 快速选择标签 */
.input-with-quick {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-select {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.quick-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-tag:hover {
  background: #1976d2;
  color: white;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-row .form-group {
  flex: 1;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .container {
    padding: 10px;
  }

  h1 {
    font-size: 20px;
    margin-bottom: 15px;
  }

  .toolbar {
    flex-direction: column;
    gap: 10px;
  }

  .search-input {
    width: 100%;
  }

  .btn-primary {
    width: 100%;
  }

  .view-tabs {
    flex-wrap: wrap;
  }

  .tab {
    flex: 1;
    min-width: 120px;
    padding: 8px 16px;
    font-size: 13px;
  }

  /* 表格横向滚动 */
  .table-container {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  table {
    min-width: 700px;
    font-size: 13px;
  }

  th, td {
    padding: 8px 10px;
  }

  .btn-edit, .btn-delete {
    padding: 3px 8px;
    font-size: 11px;
  }

  /* 统计卡片 */
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .stat-card {
    padding: 12px;
  }

  .stat-icon {
    font-size: 28px;
  }

  .stat-value {
    font-size: 22px;
  }

  .stat-label {
    font-size: 12px;
  }

  /* 图表 */
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .chart-card {
    padding: 15px;
  }

  .chart-card h3 {
    font-size: 14px;
  }

  /* 表单 */
  .modal {
    max-width: 95%;
    padding: 16px;
    margin: 10px;
  }

  .modal h2 {
    font-size: 18px;
  }

  .form-group label {
    font-size: 13px;
  }

  .form-group input,
  .form-group textarea {
    font-size: 14px; /* 防止 iOS 自动缩放 */
  }

  .quick-tag {
    padding: 3px 8px;
    font-size: 11px;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions button {
    width: 100%;
    padding: 12px;
  }
}

/* 小屏幕手机 */
@media (max-width: 375px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }

  .tab {
    min-width: 100%;
  }

  table {
    min-width: 650px;
    font-size: 12px;
  }
}
</style>
