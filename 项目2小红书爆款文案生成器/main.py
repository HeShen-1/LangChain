import streamlit as st
from utils import generte_xiaohongshu

st.header('爆款小红书AI写作助手✍:')

with st.sidebar:
    openai_api_key = st.text_input('请输入Open AI API密钥', type='password')
    st.markdown('[获取OpenAI](https://openai-hk.com/v3/ai/key)')

theme = st.text_input('主题')

submit = st.button('开始写作')

if submit and not openai_api_key:
    st.info('请输入你的OpenAI API密钥!')
    st.stop()
if submit and not theme:
    st.info('请输入你的主题')
    st.stop()

if submit:
    with st.spinner('AI正在努力创作中,请稍后...'):
        result = generte_xiaohongshu(theme, openai_api_key)

    st.divider()

    left, right = st.columns(2)

    with left:
        # 在左列中展示生成的5个小红书标题
        st.markdown('#### 小红书标题1')
        st.write(result.titles[0])

        st.markdown('#### 小红书标题2')
        st.write(result.titles[1])

        st.markdown('#### 小红书标题3')
        st.write(result.titles[2])

        st.markdown('#### 小红书标题4')
        st.write(result.titles[3])

        st.markdown('#### 小红书标题5')
        st.write(result.titles[3])
    with right:
        st.markdown('#### 小红书正文')
        st.write(result.content)
