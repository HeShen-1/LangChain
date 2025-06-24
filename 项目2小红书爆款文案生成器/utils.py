from .prompt_template import system_template_text, user_template_text
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from .xiaohongshumodel import XiaoHongShu


def generte_xiaohongshu(theme, openai_api_key):
    '''
        生成小红书内容的核心函数
        :param theme: 小红书内容的主题
        :param openai_api_key: OpenAI API密钥
        :return: 解析后的小红书模型实例
    '''

    prompt = ChatPromptTemplate.from_messages([
        ('system', system_template_text),
        ('user', user_template_text)
    ])


    model = ChatOpenAI(
        base_url="https://api.openai-hk.com/v1",
        openai_api_key=openai_api_key,
        model='gpt-3.5-turbo'
    )
    
    # 创建Pydantic输出解析器,指定解析目标为小红书模型
    output_parser = PydanticOutputParser(pydantic_object=XiaoHongShu)

    chain = prompt | model | output_parser

    result = chain.invoke({'parser_instructions':output_parser.get_format_instructions(), 'theme':theme})

    return result


