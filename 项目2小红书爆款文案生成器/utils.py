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
import random  # 新增
from .prompt_template import get_prompt_template, USER_TEMPLATE

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Xiaohongshu(BaseModel):
    titles: List[str] = Field(description="5个带emoji的标题")
    content: str = Field(description="带emoji的正文内容，包含tag标签")


def generate_xiaohongshu(
        theme: str,
        openai_api_key: str,
        style: str = "活泼种草",
        num_titles: int = 5  # 标题数量
) -> (Xiaohongshu, str):
    """生成小红书内容（含错误处理和调试日志），返回(Xiaohongshu, 原始响应)"""


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
            base_url="https://api.deepseek.com/v1",
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
        # 截断标题数量防止AI多生成）
        result.titles = result.titles[:num_titles]
        return result, raw_response

    except Exception as e:
        logger.error(f"生成失败: {str(e)}", exc_info=True)
        raise  # 重新抛出异常，便上层捕获


def get_baidu_image_urls(query: str, num_images: int = 3) -> Optional[list]:
    """
    使用百度图片搜索，返回num_images张相关图片URL列表（随机选取）。
    """
    import re

    if not query or not isinstance(query, str):
        logger.error("无效的搜索关键词")
        return None

    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    }
    url = 'https://image.baidu.com/search/acjson?'

    param = {
        'tn': 'resultjson_com',
        'logid': '7603311155072595725',
        'ipn': 'rj',
        'ct': 201326592,
        'is': '',
        'fp': 'result',
        'queryWord': query,
        'cl': 2,
        'lm': -1,
        'ie': 'utf-8',
        'oe': 'utf-8',
        'adpicid': '',
        'st': -1,
        'z': '',
        'ic': '',
        'hd': '',
        'latest': '',
        'copyright': '',
        'word': query,
        's': '',
        'se': '',
        'tab': '',
        'width': '',
        'height': '',
        'face': 0,
        'istype': 2,
        'qc': '',
        'nc': '1',
        'fr': '',
        'expermode': '',
        'force': '',
        'cg': '',
        'pn': 0,
        'rn': '30',  # 一次多取一些，便于随机
        'gsm': '1e',
        '1618827096642': ''
    }

    try:
        logger.info(f"正在搜索关键词: '{query}'...")
        response = requests.get(url=url, headers=header, params=param, timeout=15)
        response.raise_for_status()

        try:
            response.encoding = 'utf-8'
            html = response.text
        except UnicodeDecodeError:
            html = response.content.decode('utf-8', 'ignore')

        image_url_list = re.findall('"thumbURL":"(.*?)",', html, re.S)
        if not image_url_list:
            image_url_list = re.findall('"thumbUrl":"(.*?)",', html, re.S)
            if not image_url_list:
                logger.info("未找到thumbURL，尝试objURL匹配...")
                image_url_list = re.findall('"objURL":"(.*?)"', html, re.S)

        if image_url_list:
            # 去重并清理URL
            image_url_list = [u.replace('\\/', '/') for u in image_url_list]
            image_url_list = list(dict.fromkeys(image_url_list))
            # 随机选取N张
            if len(image_url_list) <= num_images:
                selected = image_url_list
            else:
                selected = random.sample(image_url_list, num_images)
            logger.info(f"随机选取图片URL: {selected}")
            return selected
        else:
            logger.warning("❌ 未在响应中找到图片URL")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {e}")
        return None
    except Exception as e:
        logger.error(f"发生意外错误: {e}")
        return None


# 保留原有单图接口以兼容
def get_baidu_image_url(query: str) -> Optional[str]:
    urls = get_baidu_image_urls(query, num_images=1)
    if urls:
        return urls[0]
    return None


# 新增：获取全部图片（用于最终选择区分度）
def get_all_baidu_image_urls(query: str, max_images: int = 50) -> list:
    """
    获取百度图片搜索的全部图片URL（最多max_images张），用于最终选择。
    """
    import re
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    }
    url = 'https://image.baidu.com/search/acjson?'
    param = {
        'tn': 'resultjson_com',
        'logid': '7603311155072595725',
        'ipn': 'rj',
        'ct': 201326592,
        'is': '',
        'fp': 'result',
        'queryWord': query,
        'cl': 2,
        'lm': -1,
        'ie': 'utf-8',
        'oe': 'utf-8',
        'adpicid': '',
        'st': -1,
        'z': '',
        'ic': '',
        'hd': '',
        'latest': '',
        'copyright': '',
        'word': query,
        's': '',
        'se': '',
        'tab': '',
        'width': '',
        'height': '',
        'face': 0,
        'istype': 2,
        'qc': '',
        'nc': '1',
        'fr': '',
        'expermode': '',
        'force': '',
        'cg': '',
        'pn': 0,
        'rn': str(max_images),
        'gsm': '1e',
        '1618827096642': ''
    }
    try:
        response = requests.get(url=url, headers=header, params=param, timeout=15)
        response.raise_for_status()
        try:
            response.encoding = 'utf-8'
            html = response.text
        except UnicodeDecodeError:
            html = response.content.decode('utf-8', 'ignore')
        image_url_list = re.findall('"thumbURL":"(.*?)",', html, re.S)
        if not image_url_list:
            image_url_list = re.findall('"thumbUrl":"(.*?)",', html, re.S)
            if not image_url_list:
                image_url_list = re.findall('"objURL":"(.*?)"', html, re.S)
        image_url_list = [u.replace('\\/', '/') for u in image_url_list]
        image_url_list = list(dict.fromkeys(image_url_list))
        return image_url_list[:max_images]
    except Exception:
        return []
