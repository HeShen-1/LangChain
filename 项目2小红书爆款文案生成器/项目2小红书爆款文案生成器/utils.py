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

# 配置日志，便于调试
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Xiaohongshu(BaseModel):
    titles: List[str] = Field(description="5个带emoji的标题")
    content: str = Field(description="带emoji的正文内容，包含tag标签")


def generate_xiaohongshu(
        theme: str,
        openai_api_key: str,
        style: str = "活泼种草",
        num_titles: int = 5  # 新增参数
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
    爬取百度图片搜索结果，返回最相关的一张图片URL。
    """
    try:
        # 构建搜索URL
        encoded_query = quote(query)
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
            "cl": "2",
            "lm": "-1",
            "ie": "utf-8",
            "oe": "utf-8",
            "adpicid": "",
            "st": "-1",
            "z": "",
            "ic": "0",
            "hd": "",
            "latest": "",
            "copyright": "",
            "s": "",
            "se": "",
            "tab": "",
            "width": "",
            "height": "",
            "face": "0",
            "istype": "2",
            "qc": "",
            "nc": "1",
            "expermode": "",
            "nojc": "",
            "isAsync": "",
            "pn": "0",
            "rn": "30",
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
                    for item in data["data"]:
                        # 按优先级尝试不同的图片URL字段
                        for url_field in ["thumbURL", "middleURL", "hoverURL", "objURL"]:
                            if item.get(url_field):
                                url = item[url_field]
                                # 验证URL可访问性
                                try:
                                    test_resp = requests.head(url, timeout=5)
                                    if test_resp.status_code == 200:
                                        logger.info(f"成功获取图片URL: {url}")
                                        return url
                                except:
                                    continue
            except Exception as e:
                logger.error(f"解析JSON失败: {str(e)}")

        logger.warning(f"未找到合适的图片URL, 响应内容: {resp.text[:200]}...")
    except Exception as e:
        logger.error(f"百度图片获取失败: {str(e)}")
    return None
