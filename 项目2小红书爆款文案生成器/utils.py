from langchain import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
import logging
from typing import  List, Optional
import requests  # 新增
from urllib.parse import quote

# 配置日志，���于调试
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Xiaohongshu(BaseModel):
    titles: List[str] = Field(description="5个带emoji的标题")
    content: str = Field(description="带emoji的正文内容，包含tag标签")


def generate_xiaohongshu(
        theme: str,
        openai_api_key: str,
        style: str = "活泼种草",
        num_titles: int = 5  # ��增参数
) -> (Xiaohongshu, str):
    """生成小红书内容（含错误处理和调试日志），返回(Xiaohongshu, 原始响应)"""
    from prompt_template import get_prompt_template, USER_TEMPLATE

    try:
        # 获取风格模板
        style_config = get_prompt_template(style)

        # 构建提示词（动态标题数量）
        system_template = f"""
        {style_config["system_template"]}

        重要：必须按照以下JSON格式输出，不要添加任何额外内容！
        {{
          "titles": ["标题1", ..., "标题{num_titles}"],
          "content": "正文内容（包含emoji和tag）"
        }}
        标题数量：{num_titles}个
        """
        system_message = SystemMessage(content=system_template)
        user_message = HumanMessage(content=USER_TEMPLATE.format(theme=theme))
        prompt = ChatPromptTemplate.from_messages([system_message, user_message])

        # 初始化模型
        model = ChatOpenAI(
            base_url="https://api.deepseek.com",
            model="deepseek-chat",
            openai_api_key=openai_api_key,
            temperature=0.7,  # 降低随机性，提高格式稳定性
        )

        # 配置解析器
        output_parser = PydanticOutputParser(pydantic_object=Xiaohongshu)
        format_instructions = output_parser.get_format_instructions()

        # 打印提示词（调试用）
        logger.info(f"生成提示词: {prompt.format_prompt(parser_instructions=format_instructions, theme=theme)}")

        # 调用模型
        chain = LLMChain(llm=model, prompt=prompt)
        raw_response = chain.run(parser_instructions=format_instructions, theme=theme)
        logger.info(f"原始响应: {raw_response}")

        # 解析响应
        result = output_parser.parse(raw_response)
        # 截断标题数量（防止AI多生成）
        result.titles = result.titles[:num_titles]
        return result, raw_response

    except Exception as e:
        logger.error(f"生成失败: {str(e)}", exc_info=True)
        raise  # 重新抛出异常，便于上层捕获


def get_baidu_image_url(query: str) -> Optional[str]:
    """
    爬取百度图片搜索结果，返回最相关的图片URL。
    """
    try:
        # 关键词优化
        def clean_query(q: str) -> str:
            # 移除常见的干扰词
            noise_words = ['怎么样', '如何', '为什么', '是什么', '可以', '应该', '教程']
            for word in noise_words:
                q = q.replace(word, '')
            return q.strip()

        # 清理搜索词
        query = clean_query(query)

        # 分析主题类型
        product_keywords = ['产品', '物品', '商品', '东西', '神器']
        scene_keywords = ['场景', '地方', '环境', '空间']
        person_keywords = ['人物', '博主', '达人', '美女', '帅哥']

        # 根据主题类型添加特定的搜索限定词
        if any(kw in query for kw in product_keywords):
            search_query = f"{query} 实物图 白底"
        elif any(kw in query for kw in scene_keywords):
            search_query = f"{query} 实景图 高清"
        elif any(kw in query for kw in person_keywords):
            search_query = f"{query} 生活照 清晰"
        else:
            search_query = f"{query} 高清实拍 清晰"

        encoded_query = quote(search_query)
        search_url = f"https://image.baidu.com/search/acjson"
        params = {
            "tn": "resultjson_com",
            "logid": "7882159396532078822",  # 添加logid
            "ipn": "rj",
            "ct": "201326592",
            "is": "",
            "fp": "result",
            "fr": "",
            "word": encoded_query,
            "queryWord": encoded_query,
            "height": "800",    # 提高最小高度要求
            "width": "800",     # 提高最小宽度要求
            "ic": "0",          # 只搜索彩色图片
            "z": "0",           # 普通图片
            "s": "0",           # 全部图片
            "pn": "0",          # 第一页
            "rn": "30",         # 增加返回数量以提高匹配概率
            "gsm": "1e",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/plain, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://image.baidu.com/search/index?tn=baiduimage",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "XMLHttpRequest",
        }

        resp = requests.get(
            search_url,
            params=params,
            headers=headers,
            timeout=10
        )

        logger.info(f"请求URL: {resp.url}")
        logger.info(f"状态码: {resp.status_code}")

        if resp.status_code == 200:
            try:
                data = resp.json()
                if "data" in data and isinstance(data["data"], list):
                    valid_items = []
                    # 图片质量评分函数
                    def score_image(item: dict) -> float:
                        score = 0
                        # 分辨率评分
                        width = int(item.get("width", 0))
                        height = int(item.get("height", 0))
                        score += min(1.0, (width * height) / (1920 * 1080))

                        # 文件类型评分
                        if item.get("type") in ["jpg", "png"]:
                            score += 0.5

                        # 图片来源评分
                        if "小红书" in item.get("fromPageTitle", ""):
                            score += 2.0

                        return score

                    # 过滤并排序图片
                    valid_items = [
                        item for item in data["data"][:30]
                        if isinstance(item, dict) and
                        int(item.get("width", 0)) >= 800 and
                        int(item.get("height", 0)) >= 800
                    ]

                    # 按质量评分排序
                    valid_items.sort(key=score_image, reverse=True)

                    # 尝试获取最佳图片URL
                    for item in valid_items[:5]:  # 只尝试质量最高的5张
                        for url_field in ["objURL", "middleURL", "thumbURL"]:
                            if item.get(url_field):
                                url = item[url_field]
                                try:
                                    test_resp = requests.head(url, timeout=3)
                                    if test_resp.status_code == 200:
                                        logger.info(f"成功获取最佳匹配图片URL: {url}")
                                        return url
                                except:
                                    continue

        logger.warning(f"未找到合适的图片URL, 响应内容: {resp.text[:200]}...")
    except Exception as e:
        logger.error(f"百度图片获取失败: {str(e)}")
    return None
