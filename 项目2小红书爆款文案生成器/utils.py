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

# 配置日志，���试
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
    直接使用用户输入的主题作为搜索关键词，确保相关性。
    """
    if not query or not isinstance(query, str):
        logger.error("无效的搜索关键词")
        return None

    try:
        # 关键词优化：保持原始主题，只去除干扰词
        def clean_query(q: str) -> str:
            noise_words = ['怎么样', '如何', '为什么', '是什么', '可以', '应该', '教程']
            # 只移除独立的干扰词，保持短语的完整性
            words = q.split()
            cleaned_words = [w for w in words if w not in noise_words]
            return ' '.join(cleaned_words).strip()

        # 清理并验证搜索词
        cleaned_query = clean_query(query)
        if not cleaned_query:
            logger.error("清理后的搜索关键词为空")
            return None

        # 使用原始主题作为基础搜索词
        search_query = cleaned_query

        # 根据主题内容添加搜索限定词
        if any(kw in cleaned_query for kw in ['产品', '物品', '商品', '神器', '好物']):
            search_query = f"{cleaned_query} 实拍图"
        elif any(kw in cleaned_query for kw in ['场景', '地点', '环境', '空间']):
            search_query = f"{cleaned_query} 场景图"
        elif any(kw in cleaned_query for kw in ['人物', '博主', '达人']):
            search_query = f"{cleaned_query} 人物图"
        else:
            # 保持原始搜索词，只添加高清限定
            search_query = f"{cleaned_query} 高清"

        logger.info(f"原始主题: {query}")
        logger.info(f"清理后的搜索词: {cleaned_query}")
        logger.info(f"最终搜索词: {search_query}")

        encoded_query = quote(search_query)
        search_url = "https://image.baidu.com/search/acjson"

        params = {
            "tn": "resultjson_com",
            "logid": "7882159396532078822",
            "ipn": "rj",
            "ct": "201326592",
            "fp": "result",
            "word": encoded_query,
            "queryWord": encoded_query,
            "height": "800",
            "width": "800",
            "ic": "0",
            "z": "0",
            "s": "0",
            "pn": "0",
            "rn": "30"
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/plain, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://image.baidu.com/search/index?tn=baiduimage",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120"',
            "Sec-Fetch-Dest": "empty",
            "X-Requested-With": "XMLHttpRequest"
        }

        logger.info(f"正在搜索图片: {search_query}")
        resp = requests.get(search_url, params=params, headers=headers, timeout=10)

        if resp.status_code != 200:
            logger.error(f"搜索请求失败: HTTP {resp.status_code}")
            return None

        try:
            data = resp.json()
        except ValueError as e:
            logger.error(f"JSON解析失败: {e}")
            return None

        if not isinstance(data, dict) or "data" not in data:
            logger.error("返回数据格式错误")
            return None

        # 更新评分函数以提高主题相关性
        def score_image(item: dict) -> float:
            try:
                score = 0.0

                # 主题相关性评分（最高3分）
                title = item.get("fromPageTitle", "").lower()
                desc = item.get("fromPageTitleEnc", "").lower()

                # 检查原始主题关键词的出现
                main_keywords = cleaned_query.lower().split()
                for keyword in main_keywords:
                    if keyword in title or keyword in desc:
                        score += 1.5

                # 分辨率评分（最高2分）
                width = int(item.get("width", 0))
                height = int(item.get("height", 0))
                score += min(2.0, (width * height) / (1920 * 1080))

                # 图片来源评分（最高1分）
                if "小红书" in title:
                    score += 1.0
                elif any(kw in title for kw in ["官方", "原创"]):
                    score += 0.5

                return score
            except Exception as e:
                logger.warning(f"图片评分失败: {e}")
                return 0.0

        # 过滤和排序图片时添加更严格的相关性检查
        valid_items = []
        for item in data["data"][:30]:
            try:
                if not isinstance(item, dict):
                    continue

                # 基本尺寸检查
                width = int(item.get("width", 0))
                height = int(item.get("height", 0))

                # 确保图片符合尺寸要求且至少包含一个主题关键词
                title = item.get("fromPageTitle", "").lower()
                desc = item.get("fromPageTitleEnc", "").lower()
                has_keyword = any(kw.lower() in title or kw.lower() in desc
                                for kw in cleaned_query.split())

                if width >= 800 and height >= 800 and has_keyword:
                    valid_items.append(item)
            except (ValueError, TypeError) as e:
                logger.warning(f"图片数据处理错误: {e}")
                continue

        if not valid_items:
            logger.warning("未找到符合尺寸要求的图片")
            return None

        # 按质量评分排序
        valid_items.sort(key=score_image, reverse=True)

        # 尝试获取可用的图片URL
        for item in valid_items[:5]:
            for url_field in ["objURL", "middleURL", "thumbURL"]:
                if url := item.get(url_field):
                    try:
                        test_resp = requests.head(url, timeout=3, allow_redirects=True)
                        if test_resp.status_code == 200:
                            logger.info(f"成功获取图片: {url[:100]}...")
                            return url
                    except requests.RequestException as e:
                        logger.warning(f"图片URL测试失败: {url[:100]}... ({e})")
                        continue

        logger.warning("所有候选图片均无法访问")
        return None

    except requests.Timeout:
        logger.error("请求超时")
    except requests.ConnectionError:
        logger.error("网络连接错误")
    except Exception as e:
        logger.error(f"图片搜索过程出错: {e}", exc_info=True)

    return None
