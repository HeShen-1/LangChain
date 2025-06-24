from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory

def get_chat_response(prompt,memory,openai_api_key):
    '''
    获取AI聊天响应的核心函数

    :param prompt: 用户输入的问题或者提示
    :param memory: 对话内存对象，存储历史对话
    :param openai_api_key: OpenAI API密钥
    :return: AI生成的回答文本
    '''
    model = ChatOpenAI(
        base_url='https://twapi.openai-hk.com/v1/',
        openai_api_key=openai_api_key,
        model = 'gpt-3.5-turbo'
    )
    chain = ConversationChain(llm=model,memory=memory)
    response = chain.invoke({'input':prompt})

    return response['response']