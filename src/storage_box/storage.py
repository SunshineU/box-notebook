import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional
from .models import Item, ItemCreate, ItemUpdate


class CSVStorage:
    def __init__(self, file_path: str = "data/items.csv"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._init_csv()

    def _init_csv(self):
        """初始化 CSV 文件"""
        df = pd.DataFrame(columns=[
            "id", "name", "category", "location",
            "quantity", "notes", "created_at", "updated_at"
        ])
        df.to_csv(self.file_path, index=False)

    def _get_next_id(self) -> int:
        """获取下一个 ID"""
        df = pd.read_csv(self.file_path)
        if df.empty:
            return 1
        return int(df["id"].max()) + 1

    def get_all(self) -> list[Item]:
        """获取所有物品"""
        df = pd.read_csv(self.file_path)
        if df.empty:
            return []
        return [Item(**row.to_dict()) for _, row in df.iterrows()]

    def get_by_id(self, item_id: int) -> Optional[Item]:
        """根据 ID 获取物品"""
        df = pd.read_csv(self.file_path)
        row = df[df["id"] == item_id]
        if row.empty:
            return None
        return Item(**row.iloc[0].to_dict())

    def create(self, item: ItemCreate) -> Item:
        """创建新物品"""
        now = datetime.now().isoformat()
        new_item = {
            "id": self._get_next_id(),
            "name": item.name,
            "category": item.category,
            "location": item.location,
            "quantity": item.quantity,
            "notes": item.notes,
            "created_at": now,
            "updated_at": now
        }
        df = pd.read_csv(self.file_path)
        df = pd.concat([df, pd.DataFrame([new_item])], ignore_index=True)
        df.to_csv(self.file_path, index=False)
        return Item(**new_item)

    def update(self, item_id: int, item: ItemUpdate) -> Optional[Item]:
        """更新物品"""
        df = pd.read_csv(self.file_path)
        mask = df["id"] == item_id
        if not mask.any():
            return None

        update_data = item.model_dump(exclude_unset=True)
        if update_data:
            df.loc[mask, "updated_at"] = datetime.now().isoformat()
            for key, value in update_data.items():
                if value is not None:
                    df.loc[mask, key] = value
            df.to_csv(self.file_path, index=False)
        return self.get_by_id(item_id)

    def delete(self, item_id: int) -> bool:
        """删除物品"""
        df = pd.read_csv(self.file_path)
        mask = df["id"] != item_id
        if mask.sum() == len(df):
            return False
        df = df[mask]
        df.to_csv(self.file_path, index=False)
        return True

    def search(self, keyword: str) -> list[Item]:
        """搜索物品"""
        df = pd.read_csv(self.file_path)
        if df.empty:
            return []
        mask = (
            df["name"].str.contains(keyword, case=False, na=False) |
            df["category"].str.contains(keyword, case=False, na=False) |
            df["location"].str.contains(keyword, case=False, na=False)
        )
        return [Item(**row.to_dict()) for _, row in df[mask].iterrows()]
