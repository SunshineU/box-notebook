import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional
from .schemas import Item, ItemCreate, ItemUpdate


class ItemStorage:
    def __init__(self, file_path: str = "data/items.csv"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._init_csv()

    def _init_csv(self):
        """初始化 CSV 文件"""
        df = pd.DataFrame(columns=[
            "id", "user_id", "name", "category", "location",
            "quantity", "notes", "created_at", "updated_at"
        ])
        df.to_csv(self.file_path, index=False)

    def _get_next_id(self) -> int:
        """获取下一个 ID"""
        df = pd.read_csv(self.file_path)
        if df.empty:
            return 1
        return int(df["id"].max()) + 1

    def get_by_user(self, user_id: int) -> list[Item]:
        """获取用户的所有物品"""
        df = pd.read_csv(self.file_path)
        df = df[df["user_id"] == user_id]
        if df.empty:
            return []
        # 处理 NaN 值
        df = df.fillna({'notes': ''})
        return [Item(**row.to_dict()) for _, row in df.iterrows()]

    def get_by_id(self, item_id: int, user_id: Optional[int] = None) -> Optional[Item]:
        """根据 ID 获取物品"""
        df = pd.read_csv(self.file_path)
        row = df[df["id"] == item_id]
        if row.empty:
            return None
        # 如果指定了 user_id，验证所有权
        if user_id is not None and row.iloc[0]["user_id"] != user_id:
            return None
        # 处理 NaN 值
        data = row.iloc[0].to_dict()
        if pd.isna(data.get('notes')):
            data['notes'] = ''
        return Item(**data)

    def create(self, item: ItemCreate, user_id: int) -> Item:
        """创建新物品"""
        now = datetime.now().isoformat()
        new_item = {
            "id": self._get_next_id(),
            "user_id": user_id,
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

    def update(self, item_id: int, item: ItemUpdate, user_id: int) -> Optional[Item]:
        """更新物品"""
        df = pd.read_csv(self.file_path)
        mask = (df["id"] == item_id) & (df["user_id"] == user_id)
        if not mask.any():
            return None

        update_data = item.model_dump(exclude_unset=True)
        if update_data:
            df.loc[mask, "updated_at"] = datetime.now().isoformat()
            for key, value in update_data.items():
                if value is not None:
                    df.loc[mask, key] = value
            df.to_csv(self.file_path, index=False)
        return self.get_by_id(item_id, user_id)

    def delete(self, item_id: int, user_id: int) -> bool:
        """删除物品"""
        df = pd.read_csv(self.file_path)
        mask = ~((df["id"] == item_id) & (df["user_id"] == user_id))
        if mask.sum() == len(df):
            return False
        df = df[mask]
        df.to_csv(self.file_path, index=False)
        return True

    def search(self, keyword: str, user_id: int) -> list[Item]:
        """搜索物品"""
        df = pd.read_csv(self.file_path)
        df = df[df["user_id"] == user_id]
        if df.empty:
            return []
        # 处理 NaN 值
        df = df.fillna({'notes': ''})
        mask = (
            df["name"].str.contains(keyword, case=False, na=False) |
            df["category"].str.contains(keyword, case=False, na=False) |
            df["location"].str.contains(keyword, case=False, na=False)
        )
        return [Item(**row.to_dict()) for _, row in df[mask].iterrows()]

    def export_to_csv(self, user_id: int) -> str:
        """导出用户数据为 CSV 格式字符串"""
        df = pd.read_csv(self.file_path)
        df = df[df["user_id"] == user_id]
        if df.empty:
            return ""
        # 处理 NaN 值
        df = df.fillna({'notes': ''})
        # 移除 user_id 列，不导出
        df = df.drop(columns=['user_id'])
        return df.to_csv(index=False)

    def import_from_csv(self, csv_content: str, user_id: int) -> dict:
        """从 CSV 导入数据"""
        import io
        df = pd.read_csv(io.StringIO(csv_content))

        # 验证必要列
        required_columns = ['name', 'category', 'location']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"缺少必要列：{', '.join(missing)}")

        # 补充默认值
        if 'quantity' not in df.columns:
            df['quantity'] = 1
        if 'notes' not in df.columns:
            df['notes'] = ''

        now = datetime.now().isoformat()
        count = 0
        for _, row in df.iterrows():
            new_item = {
                "id": self._get_next_id(),
                "user_id": user_id,
                "name": str(row['name']),
                "category": str(row['category']),
                "location": str(row['location']),
                "quantity": int(row.get('quantity', 1)),
                "notes": str(row.get('notes', '')) or '',
                "created_at": now,
                "updated_at": now
            }
            data_df = pd.read_csv(self.file_path)
            data_df = pd.concat([data_df, pd.DataFrame([new_item])], ignore_index=True)
            data_df.to_csv(self.file_path, index=False)
            count += 1

        return {"imported": count}
