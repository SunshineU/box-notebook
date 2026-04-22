# Render 部署指南

## 准备工作

1. **GitHub 账号** - 用于连接 Render
2. **Render 账号** - 访问 https://render.com 注册

## 部署步骤

### 1. 推送代码到 GitHub

```bash
git add render.yaml requirements.txt src/storage_box/main.py
git commit -m "chore: add render deployment config"
git push origin main
```

### 2. 在 Render 创建服务

1. 登录 Render Dashboard
2. 点击 **"New +"** → **"Blueprint"**
3. 连接你的 GitHub 仓库
4. 选择 `storage-box` 仓库
5. Render 会自动读取 `render.yaml` 配置

### 3. 配置环境变量

在 Render 服务设置中确认以下变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `PYTHON_VERSION` | `3.11.0` | Python 版本 |
| `SECRET_KEY` | (自动生成) | JWT 密钥，点击"Generate" |
| `FRONTEND_URL` | `https://your-app.onrender.com` | 部署后填写实际域名 |

### 4. 等待部署完成

- 首次部署约 3-5 分钟
- 可在 Logs 标签查看进度
- 部署成功后访问分配的域名即可

## 免费层限制

- **服务休眠**：15 分钟无请求后进入休眠
- **唤醒时间**：首次访问约需 30-50 秒
- **存储**：1GB 磁盘空间
- **带宽**：每月 100GB

## 本地测试构建

```bash
# 构建前端
cd frontend
npm run build

# 回到项目根目录启动后端
cd ..
uv run uvicorn src.storage_box.main:app --host 0.0.0.0 --port 8000

# 访问 http://localhost:8000
```

## 故障排查

### 前端 404
检查 `frontend/dist` 是否存在，确保构建成功

### CSV 数据丢失
确认磁盘已挂载到 `/opt/render/project/src/data`

### CORS 错误
设置 `FRONTEND_URL` 环境变量为你的实际域名

## 升级建议

如需移除休眠限制，升级到付费计划：
- **Standard** - $7/月，无休眠
- **Pro** - 更高性能
