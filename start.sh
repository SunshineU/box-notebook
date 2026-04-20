#!/bin/bash

echo "🚀 启动收纳记录管理系统..."

# 启动后端
echo "启动后端服务 (http://localhost:8000)..."
uv run uvicorn src.storage_box.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 等待后端启动
sleep 2

# 启动前端
echo "启动前端服务 (http://localhost:3000)..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ 服务启动完成!"
echo "   后端 API: http://localhost:8000"
echo "   前端界面：http://localhost:3000"
echo "   API 文档：http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待中断信号
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait
