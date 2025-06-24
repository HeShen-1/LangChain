from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List


class XiaoHongShu(BaseModel):
    titles: List[str] = Field(description='小红书的5个标题', min_items=5, max_items=10)
    content: str = Field(description='小红书的正文内容')
    