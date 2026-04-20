from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import ItemCreate, ItemUpdate
from .storage import CSVStorage

app = FastAPI(title="收纳记录管理系统", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage = CSVStorage()


@app.get("/")
def root():
    return {"message": "欢迎使用收纳记录管理系统", "version": "1.0.0"}


@app.get("/items", tags=["物品管理"])
def get_all_items(keyword: str | None = None):
    """获取所有物品，支持关键词搜索"""
    if keyword:
        return storage.search(keyword)
    return storage.get_all()


@app.get("/items/{item_id}", tags=["物品管理"])
def get_item(item_id: int):
    """根据 ID 获取物品详情"""
    item = storage.get_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="物品不存在")
    return item


@app.post("/items", tags=["物品管理"])
def create_item(item: ItemCreate):
    """创建新物品"""
    return storage.create(item)


@app.put("/items/{item_id}", tags=["物品管理"])
def update_item(item_id: int, item: ItemUpdate):
    """更新物品信息"""
    updated = storage.update(item_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="物品不存在")
    return updated


@app.delete("/items/{item_id}", tags=["物品管理"])
def delete_item(item_id: int):
    """删除物品"""
    if not storage.delete(item_id):
        raise HTTPException(status_code=404, detail="物品不存在")
    return {"message": "删除成功"}
