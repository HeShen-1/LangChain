import streamlit as st
from langchain.memory import ConversationBufferMemory
from utils import get_chat_response

st.title('🗨 克隆ChatGPT')

with st.sidebar:
    openai_api_key = st.text_input('请输入OpenAI API密钥',type='password')
    st.markdown('[获取OpenAI API密钥](https://openai-hk.com/v3/ai/key)')

#管理会话状态{Session State},这是Streamlit保持页面刷新时数据不丢失的机制
if 'memory' not in st.session_state:
    st.session_state['memory'] = ConversationBufferMemory(return_messages=True)
    #初始化对话历史，添加一条AI的欢迎消息
    st.session_state['messages'] = [{'role':'ai','content':'你好，我是你的AI助手，有什么可以你帮你的吗？'}]

for message in st.session_state['messages']:
    st.chat_message(message['role']).write(message['content'])

#获取用户输入
prompt = st.chat_input()

if prompt:
    if not openai_api_key:
        st.info('请输入你的OpenAI API Key')
        st.stop()

    #添加用户消息到对话历史
    st.session_state['messages'].append({'role':'human','content':prompt})
    st.chat_message(message['role']).write(prompt)

    with st.spinner('AI正在思考中，请稍等.....'):
        response = get_chat_response(prompt,st.session_state['memory'],openai_api_key)

        #处理AI响应并添加到对话历史
        msg = {'role':'ai','content':response}
        st.session_state['messages'].append(msg)
        st.chat_message('ai').write(response)