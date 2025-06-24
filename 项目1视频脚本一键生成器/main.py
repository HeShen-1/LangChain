import streamlit as st
from utils import generate_script

# 设置应用标题
st.title('🎬 视频脚本生成器')

with st.sidebar:
    openai_api_key = st.text_input('请输入OpenAI API密钥', type='password')
    st.markdown('[获取OpenAI](https://openai-hk.com/v3/ai/key)')


# 创建主界面的输入组件
subject = st.text_input('💡 请输入视频的主题')
video_length = st.number_input('请输入视频的大致时长(单位: 分钟)', min_value=1, max_value=60, step=1)

cretivity = st.slider("⭐ 请输入视频脚本的创造力(数字小说明越严谨,数字大说明更多样)", min_value=0.0, max_value=1.0, value=0.2, step=0.1)

submit = st.button('生成脚本')

# 创建按钮组件,用户点击后触发脚本生成
if submit and not openai_api_key:
    st.info('请输入你的OpenAI API密钥!')
    st.stop()
if submit and not subject:
    st.info('请输入你的主题')
    st.stop()

if subject and not video_length >= 0.1:
    st.info('视频时长需要大等于0.1分钟')
    st.stop()


if submit:
    with st.spinner('AI正在思考中,请稍后...'):
        title, script = generate_script(subject, video_length, 0.7)

    st.success('视频脚本已生成')
    st.subheader('🔥 标题:')
    st.write(title)

    st.subheader('📚 视频脚本: ')
    st.write(script)























