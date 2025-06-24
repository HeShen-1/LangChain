import streamlit as st
import os
import tempfile
# 1. 导入各子项目的功能函数
from 项目1视频脚本一键生成器.utils import generate_script as video_generate_script
from 项目2小红书爆款文案生成器.utils import generte_xiaohongshu
from 项目3克隆ChatGPT.utils import get_chat_response
from 项目4智能PDF问答工具.utils import qa_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

# 设置页面配置
st.set_page_config(
    page_title="AI工具集合",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 小红书模型定义（兼容主页面显示）
class XiaoHongShu(BaseModel):
    titles: List[str] = Field(description='小红书的5个标题', min_items=5, max_items=10)
    content: str = Field(description='小红书的正文内容')

# 初始化session state
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = "首页"

# 全局侧栏API密钥输入
with st.sidebar:
    st.title("🤖 AI工具集合")
    st.markdown("---")
    
    # API密钥输入
    openai_api_key = st.text_input('请输入OpenAI API密钥', type='password', key='global_api_key')
    if openai_api_key:
        st.success("✅ API密钥已设置")
    else:
        st.warning("⚠️ 请输入API密钥以使用AI功能")
    
    st.markdown("[获取OpenAI API密钥](https://openai-hk.com/v3/ai/key)")
    st.markdown("---")
    
    # 侧栏按钮
    if st.button("🏠 首页", use_container_width=True):
        st.session_state.selected_page = "首页"
    
    if st.button("🎬 一键生成视频脚本", use_container_width=True):
        st.session_state.selected_page = "视频脚本"
    
    if st.button("📝 生成小红书爆款文案", use_container_width=True):
        st.session_state.selected_page = "小红书文案"
    
    if st.button("💬 克隆ChatGPT", use_container_width=True):
        st.session_state.selected_page = "ChatGPT克隆"
    
    if st.button("📄 PDF文档问答工具", use_container_width=True):
        st.session_state.selected_page = "PDF问答"
    
    st.markdown("---")
    st.markdown("### 📞 联系我们")
    st.markdown("如有问题，请联系开发团队")

# 首页
def show_home():
    st.title("🎉 欢迎使用AI工具集合")
    
    # 居中显示制作团队信息
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 50px; background-color: #f0f2f6; border-radius: 10px; margin: 50px 0;">
            <h2 style="color: #1f77b4;">制作团队</h2>
            <h3 style="color: #333;">傅彬彬，董政，聂群松，何星伽</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 工具介绍
    st.markdown("## 🛠️ 工具介绍")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎬 一键生成视频脚本
        - 快速生成各类视频脚本
        - 支持多种风格和类型
        - 自动优化内容结构
        - 基于LangChain和OpenAI GPT
        """)
        
        st.markdown("""
        ### 📝 生成小红书爆款文案
        - 智能生成小红书文案
        - 优化标题和内容
        - 提高文案吸引力
        - 包含爆款关键词和emoji
        """)
    
    with col2:
        st.markdown("""
        ### 💬 克隆ChatGPT
        - 智能对话系统
        - 多轮对话能力
        - 个性化回复
        - 支持上下文记忆
        """)
        
        st.markdown("""
        ### 📄 PDF文档问答工具
        - 上传PDF文档
        - 智能文档问答
        - 快速信息提取
        - 基于向量检索技术
        """)

# 视频脚本
def show_video_script():
    st.title("🎬 一键生成视频脚本")
    
    if not openai_api_key:
        st.warning("⚠️ 请在左侧侧栏输入OpenAI API密钥")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 脚本设置")
        
        subject = st.text_input('💡 请输入视频的主题')
        video_length = st.number_input('请输入视频的大致时长(单位: 分钟)', min_value=1, max_value=60, step=1, value=5)
        creativity = st.slider("⭐ 请输入视频脚本的创造力(数字小说明越严谨,数字大说明更多样)", min_value=0.0, max_value=1.0, value=0.2, step=0.1)
        
        # 生成按钮
        if st.button("🎯 生成视频脚本", type="primary", use_container_width=True):
            if not subject:
                st.warning("⚠️ 请输入视频主题")
                return
                
            with st.spinner('AI正在思考中,请稍后...'):
                try:
                    title, script = video_generate_script(subject, video_length, creativity, openai_api_key)
                    
                    st.success('✅ 视频脚本已生成')
                    
                    st.subheader('🔥 标题:')
                    st.write(title)

                    st.subheader('📚 视频脚本: ')
                    st.write(script)
                    
                except Exception as e:
                    st.error(f"❌ 生成失败：{str(e)}")
    
    with col2:
        st.markdown("### 💡 使用提示")
        st.info("""
        1. 选择合适的视频主题
        2. 设定视频时长
        3. 调整创造力参数
        4. 点击生成按钮
        5. 等待AI生成结果
        """)
        
        st.markdown("### 📊 脚本特点")
        st.markdown("""
        - 🎯 开头抓住眼球
        - 📖 中间提供干货
        - 🎉 结尾有惊喜
        - 😊 轻松有趣风格
        """)

# 小红书文案
def show_xiaohongshu():
    st.title("📝 生成小红书爆款文案")
    
    if not openai_api_key:
        st.warning("⚠️ 请在左侧侧栏输入OpenAI API密钥")
        return
    
    theme = st.text_input('主题')
    
    if st.button('✨ 开始写作', type="primary", use_container_width=True):
        if not theme:
            st.warning("⚠️ 请输入主题")
            return
            
        with st.spinner('AI正在努力创作中,请稍后...'):
            try:
                result = generte_xiaohongshu(theme, openai_api_key)
                
                st.success("✅ 小红书文案生成成功！")
                st.divider()

                left, right = st.columns(2)

                with left:
                    st.markdown('#### 🔥 爆款标题')
                    for i, title in enumerate(result.titles[:5], 1):
                        st.markdown(f'**标题{i}：** {title}')

                with right:
                    st.markdown('#### 📝 小红书正文')
                    st.write(result.content)
                    
            except Exception as e:
                st.error(f"❌ 生成失败：{str(e)}")

# ChatGPT克隆
def show_chatgpt_clone():
    st.title("💬 克隆ChatGPT")
    
    if not openai_api_key:
        st.warning("⚠️ 请在左侧侧栏输入OpenAI API密钥")
        return
    
    # 管理会话状态
    if 'memory' not in st.session_state:
        st.session_state['memory'] = ConversationBufferMemory(return_messages=True)
        st.session_state['messages'] = [{'role': 'ai', 'content': '你好，我是你的AI助手，有什么可以帮你的吗？'}]

    # 聊天设置
    with st.sidebar:
        st.markdown("### ⚙️ 聊天设置")
        if st.button("🗑️ 清空对话"):
            st.session_state['memory'] = ConversationBufferMemory(return_messages=True)
            st.session_state['messages'] = [{'role': 'ai', 'content': '你好，我是你的AI助手，有什么可以帮你的吗？'}]
            st.rerun()

    # 显示聊天历史
    for message in st.session_state['messages']:
        st.chat_message(message['role']).write(message['content'])

    # 获取用户输入
    if prompt := st.chat_input("请输入您的问题..."):
        # 添加用户消息到对话历史
        st.session_state['messages'].append({'role': 'human', 'content': prompt})
        st.chat_message('human').write(prompt)

        with st.spinner('AI正在思考中，请稍等.....'):
            try:
                response = get_chat_response(prompt, st.session_state['memory'], openai_api_key)
                
                # 处理AI响应并添加到对话历史
                msg = {'role': 'ai', 'content': response}
                st.session_state['messages'].append(msg)
                st.chat_message('ai').write(response)
                
            except Exception as e:
                st.error(f"❌ 回复失败：{str(e)}")

# PDF问答
def show_pdf_qa():
    st.title("📄 PDF文档问答工具")
    
    if not openai_api_key:
        st.warning("⚠️ 请在左侧侧栏输入OpenAI API密钥")
        return
    
    # 初始化PDF问答的内存
    if "pdf_memory" not in st.session_state:
        st.session_state["pdf_memory"] = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
            output_key="answer"
        )

    uploaded_file = st.file_uploader("📁 上传你的PDF文件：", type="pdf")
    question = st.text_input("💭 对PDF的内容进行提问", disabled=not uploaded_file)

    if uploaded_file and question:
        with st.spinner("AI正在思考中，请稍等..."):
            try:
                response = qa_agent(openai_api_key, st.session_state["pdf_memory"], uploaded_file, question)
                
                st.success("✅ 问答完成")
                st.markdown("### 💡 答案")
                st.write(response["answer"])
                
                # 保存聊天历史到session state
                st.session_state["chat_history"] = response["chat_history"]
                
            except Exception as e:
                st.error(f"❌ 问答失败：{str(e)}")

    # 显示历史消息
    if "chat_history" in st.session_state:
        with st.expander("📝 历史消息"):
            for i in range(0, len(st.session_state["chat_history"]), 2):
                if i + 1 < len(st.session_state["chat_history"]):
                    human_message = st.session_state["chat_history"][i]
                    ai_message = st.session_state["chat_history"][i + 1]
                    
                    st.markdown(f"**🙋 问题：** {human_message.content}")
                    st.markdown(f"**🤖 回答：** {ai_message.content}")
                    
                    if i < len(st.session_state["chat_history"]) - 2:
                        st.divider()

# 根据选择的页面显示相应内容
if st.session_state.selected_page == "首页":
    show_home()
elif st.session_state.selected_page == "视频脚本":
    show_video_script()
elif st.session_state.selected_page == "小红书文案":
    show_xiaohongshu()
elif st.session_state.selected_page == "ChatGPT克隆":
    show_chatgpt_clone()
elif st.session_state.selected_page == "PDF问答":
    show_pdf_qa()

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 20px;">
        © 2025 AI工具集合 | 制作团队：傅彬彬，董政，聂群松，何星伽
    </div>
    """, 
    unsafe_allow_html=True
)
