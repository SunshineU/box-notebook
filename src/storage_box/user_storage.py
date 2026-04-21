import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional
from .schemas import User, UserCreate
from .auth import get_password_hash, verify_password


class UserStorage:
    def __init__(self, file_path: str = "data/users.csv"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._init_csv()

    def _init_csv(self):
        """初始化 CSV 文件"""
        df = pd.DataFrame(columns=[
            "id", "username", "email", "password_hash", "created_at"
        ])
        df.to_csv(self.file_path, index=False)

    def _get_next_id(self) -> int:
        """获取下一个 ID"""
        df = pd.read_csv(self.file_path)
        if df.empty:
            return 1
        return int(df["id"].max()) + 1

    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        df = pd.read_csv(self.file_path)
        row = df[df["username"] == username]
        if row.empty:
            return None
        return User(**row.iloc[0].to_dict())

    def get_by_id(self, user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        df = pd.read_csv(self.file_path)
        row = df[df["id"] == user_id]
        if row.empty:
            return None
        return User(**row.iloc[0].to_dict())

    def create(self, user: UserCreate) -> Optional[User]:
        """创建新用户"""
        df = pd.read_csv(self.file_path)

        # 检查用户名是否已存在
        if not df[df["username"] == user.username].empty:
            return None

        # 检查邮箱是否已存在
        if not df[df["email"] == user.email].empty:
            return None

        new_user = {
            "id": self._get_next_id(),
            "username": user.username,
            "email": user.email,
            "password_hash": get_password_hash(user.password),
            "created_at": datetime.now().isoformat()
        }
        df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
        df.to_csv(self.file_path, index=False)
        return User(**new_user)

    def verify_password(self, username: str, password: str) -> Optional[User]:
        """验证用户密码"""
        user = self.get_by_username(username)
        if not user:
            return None
        # 读取密码哈希
        df = pd.read_csv(self.file_path)
        row = df[df["username"] == username]
        if row.empty:
            return None
        password_hash = row.iloc[0]["password_hash"]
        if verify_password(password, password_hash):
            return user
        return None
