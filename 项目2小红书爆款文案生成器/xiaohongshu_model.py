from pydantic import BaseModel, Field
from typing import List
# 定义小红书内容的Pydantic模型
class Xiaohongshu(BaseModel):
    titles: List[str] = Field(description="5个带emoji的标题")
    content: str = Field(description="带emoji的正文内容，包含tag标签")
