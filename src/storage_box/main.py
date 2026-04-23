from fastapi import FastAPI, HTTPException, Depends, status, Response, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Annotated
from datetime import timedelta
from fastapi.responses import JSONResponse, Response as FastAPIResponse
import os

from .schemas import UserCreate, UserLogin, Token, Item, ItemCreate, ItemUpdate
from .user_storage import UserStorage
from .storage import ItemStorage
from .auth import create_access_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI(title="收纳记录管理系统", version="2.0.0")

# CORS 配置 - 生产环境限制具体域名
origins = ["*"]
if os.getenv("FRONTEND_URL"):
    origins = [os.getenv("FRONTEND_URL")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化存储
user_storage = UserStorage()
item_storage = ItemStorage()

# JWT Bearer Token
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
) -> dict:
    """获取当前登录用户"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_storage.get_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"user_id": user.id, "username": user.username}


# ============== 用户认证接口 ==============
@app.post("/auth/register", tags=["用户认证"])
async def register(user: UserCreate):
    """用户注册"""
    if len(user.username) < 3:
        raise HTTPException(status_code=400, detail="用户名至少 3 个字符")
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="密码至少 6 个字符")

    existing_user = user_storage.get_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    created_user = user_storage.create(user)
    if not created_user:
        raise HTTPException(status_code=400, detail="注册失败")

    # 自动登录
    access_token = create_access_token(
        data={"sub": created_user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": created_user.username
    }


@app.post("/auth/login", tags=["用户认证"])
async def login(user: UserLogin):
    """用户登录"""
    verified_user = user_storage.verify_password(user.username, user.password)
    if not verified_user:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": verified_user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": verified_user.username
    }


@app.get("/auth/me", tags=["用户认证"])
async def get_me(current_user: Annotated[dict, Depends(get_current_user)]):
    """获取当前用户信息"""
    user = user_storage.get_by_id(current_user["user_id"])
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at
    }


# ============== 物品管理接口 ==============
@app.get("/items", tags=["物品管理"])
def get_all_items(
    current_user: Annotated[dict, Depends(get_current_user)],
    keyword: str | None = None
):
    """获取所有物品，支持关键词搜索"""
    user_id = current_user["user_id"]
    if keyword:
        return item_storage.search(keyword, user_id)
    return item_storage.get_by_user(user_id)


@app.get("/items/{item_id}", tags=["物品管理"])
def get_item(
    item_id: int,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """根据 ID 获取物品详情"""
    user_id = current_user["user_id"]
    item = item_storage.get_by_id(item_id, user_id)
    if not item:
        raise HTTPException(status_code=404, detail="物品不存在")
    return item


@app.post("/items", tags=["物品管理"])
def create_item(
    item: ItemCreate,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """创建新物品"""
    return item_storage.create(item, current_user["user_id"])


@app.put("/items/{item_id}", tags=["物品管理"])
def update_item(
    item_id: int,
    item: ItemUpdate,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """更新物品信息"""
    user_id = current_user["user_id"]
    updated = item_storage.update(item_id, item, user_id)
    if not updated:
        raise HTTPException(status_code=404, detail="物品不存在")
    return updated


@app.delete("/items/{item_id}", tags=["物品管理"])
def delete_item(
    item_id: int,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """删除物品"""
    user_id = current_user["user_id"]
    if not item_storage.delete(item_id, user_id):
        raise HTTPException(status_code=404, detail="物品不存在")
    return {"message": "删除成功"}


# ============== 导入/导出接口 ==============
@app.get("/items/export/csv", tags=["导入/导出"])
def export_items_csv(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """导出物品数据为 CSV 文件"""
    user_id = current_user["user_id"]
    csv_content = item_storage.export_to_csv(user_id)
    if not csv_content:
        raise HTTPException(status_code=404, detail="没有可导出的数据")

    response = FastAPIResponse(content=csv_content, media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=items.csv"
    return response


@app.post("/items/import", tags=["导入/导出"])
async def import_items(
    file: UploadFile = File(...),
    current_user: Annotated[dict, Depends(get_current_user)] = None
):
    """从 CSV 文件导入物品数据"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="请上传 CSV 文件")

    try:
        content = await file.read()
        csv_content = content.decode('utf-8')
        result = item_storage.import_from_csv(csv_content, current_user["user_id"])
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败：{str(e)}")


# ============== 前端静态文件 ==============
# 挂载前端构建产物
# Render 路径：/opt/render/project/src/frontend/dist
# 本地路径：./frontend/dist
import sys
from starlette.exceptions import HTTPException as StarletteHTTPException

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
frontend_dir = os.path.join(base_dir, "frontend", "dist")

if os.path.exists(frontend_dir):
    # 处理 SPA 路由：所有 404 且非 API 路径，返回 index.html
    @app.exception_handler(StarletteHTTPException)
    async def spa_exception_handler(request, exc):
        if exc.status_code == 404:
            # 如果是 API 路径，返回原始 404
            if request.url.path.startswith('/api') or request.url.path.startswith('/docs') or request.url.path.startswith('/openapi'):
                raise exc
            # 否则返回 index.html 让前端路由处理
            from fastapi.responses import FileResponse
            return FileResponse(os.path.join(frontend_dir, 'index.html'))
        raise exc
else:
    @app.get("/")
    async def root():
        return {"message": "Storage Box API", "docs": "/docs"}


@app.get("/healthz")
async def health_check():
    """健康检查端点（用于 Render 等部署平台）"""
    return {"status": "healthy"}
