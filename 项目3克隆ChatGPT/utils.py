# utils.py
# -*- coding: utf-8 -*-
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate

def get_chat_response_stream(
        prompt: str,
        memory: ConversationBufferMemory,
        openai_api_key: str,
        model_name: str='gpt-3.5-turbo',
        temperature: float=0.7,
        top_p: float=1.0,
        presence_penalty: float=0.0,
        max_tokens: int=1000,
        system_prompt=None
    ):
    '''
    获取AI聊天响应的核心函数
    该函数使用 LangChain 封装的 ChatOpenAI 接口，根据用户提供的 prompt 与对话记忆，生成 AI 回复文本。
    支持流式输出和多种模型参数配置，适合构建基于聊天记忆的对话系统。
    :param prompt: 用户输入的问题或者提示
    :param memory: 对话内存对象，存储历史对话
    :param openai_api_key: OpenAI API密钥
    :param stream: 是否启用流式输出，默认 True。
    :param model_name: 使用的模型名称（如 'gpt-3.5-turbo'），默认 'gpt-3.5-turbo'。
    :param temperature: 控制输出的创造力，值越高回答越发散，默认 0.7。
    :param top_p: 控制核采样的多样性，默认 1.0。
    :param presence_penalty: 重复惩罚系数，越高越不容易重复，默认 0.0。
    :param max_tokens: 最大生成的 token 数量，默认 1000。
    :param system_prompt: 系统级提示词，用于设定角色或风格，默认 None。
    :return: AI生成的回答文本
    '''
    # 创建模型
    model = ChatOpenAI(
        base_url='https://twapi.openai-hk.com/v1/',
        openai_api_key=openai_api_key,
        model=model_name,
        streaming=True,
        temperature=temperature,
        top_p=top_p,
        presence_penalty=presence_penalty,
        max_tokens=max_tokens
    )

    if system_prompt:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("ai", "{history}"),
            ("human", "{input}")
        ])
        chain = ConversationChain(llm=model, memory=memory, prompt=prompt_template)
    else:
        chain = ConversationChain(llm=model, memory=memory)

    for chunk in chain.stream({'input': prompt}):
        print('[DEBUG]收到的chunk: ', chunk)
        yield chunk

# 非流式输出
def get_chat_response(
        prompt: str,
        memory: ConversationBufferMemory,
        openai_api_key: str,
        model_name: str='gpt-3.5-turbo',
        temperature: float=0.7,
        top_p: float=1.0,
        presence_penalty: float=0.0,
        max_tokens: int=1000,
        system_prompt=None
    ):
    model = ChatOpenAI(
        base_url='https://twapi.openai-hk.com/v1/',
        openai_api_key=openai_api_key,
        model=model_name,
        streaming=False,
        temperature=temperature,
        top_p=top_p,
        presence_penalty=presence_penalty,
        max_tokens=max_tokens
    )
    if system_prompt:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("ai", "{history}"),
            ("human", "{input}")
        ])
        chain = ConversationChain(llm=model, memory=memory, prompt=prompt_template)
    else:
        chain = ConversationChain(llm=model, memory=memory)

    print("没有启用流式")
    result = chain.invoke({'input': prompt})
    if isinstance(result, dict) and "response" in result:
        return result["response"]
    else:
        return str(result)

def generate_chat_title(first_question: str, openai_api_key: str) -> str:
    """
    基于用户的第一个问题生成聊天标题
    :param first_question: 用户的第一个问题
    :param openai_api_key: OpenAI API密钥
    :return: 生成的聊天标题
    """
    try:
        model = ChatOpenAI(
            base_url='https://twapi.openai-hk.com/v1/',
            openai_api_key=openai_api_key,
            model='gpt-3.5-turbo',
            streaming=False,
            temperature=0.3,
            max_tokens=30
        )
        
        title_prompt = f"""请为以下用户问题生成一个简洁的标题(不超过15个字)，仅返回标题内容：
用户问题：{first_question}

要求：
1. 标题要简洁明了，能概括问题核心
2. 不要包含"关于"、"问题"等词汇
3. 直接返回标题，不要其他内容"""
        
        result = model.invoke(title_prompt)
        title = result.content.strip()
        
        # 如果标题太长，截断处理
        if len(title) > 15:
            title = title[:12] + "..."
            
        return title
    except Exception as e:
        print(f"生成标题失败: {e}")
        # 如果生成失败，使用前20个字符作为标题
        return first_question[:20] + "..." if len(first_question) > 20 else first_question
    

    