from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.utilities import WikipediaAPIWrapper


'''
生成视频标题和脚本的函数
参数:
    subject:视频主题
    video_length:视频时长（分钟）
    creativity: 创造力参数（控制模型输出的随机性）
    api_key:OpenAI API密钥
返回：
    包含视频标题和脚本的元组    
'''

def generate_script(subject, video_length, creativity, api_key):
    title_template = ChatPromptTemplate.from_messages(
        [
            ('human', '请为{subject}这个主题的视频像一个吸引人的标题')
        ]
    )

    # 告诉模型根据主题生成标题,使用固定的用户消息格式
    script_template = ChatPromptTemplate.from_messages([
        ('human', 
            """
                你是一位短视频频道的博主。根据以下标题和相关信息，为短视频频道写一个视频脚本。
                视频标题：{title}，视频时长：{duration}分钟，生成的脚本的长度尽量遵循视频时长的要求。
                要求开头抓住眼球，中间提供干货内容，结尾有惊喜，脚本格式也请按照【开头、中间，结尾】分隔。
                整体内容的表达方式要尽量轻松有趣，吸引年轻人。
            """)
    ])

    # 定义脚本生成的详细要求,包括标题,时长,结构和风格要求
    model = ChatOpenAI(
        base_url = 'https://twapi.openai-hk.com/v1/',
        openai_api_key = api_key,
        temperature=creativity
    )
    
    title_chain = title_template | model
    script_chain = script_template | model

    title = title_chain.invoke({'subject':subject}).content

    script = script_chain.invoke({'title':title, 'duration':video_length}).content

    # search = WikipediaAPIWrapper(lang='zh')

    # search_result = search.run(subject)

    return title, script


