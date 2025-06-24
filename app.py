import streamlit as st
import os
import tempfile
# 1. 导入各子项目的功能函数
from 项目1视频脚本一键生成器.utils import generate_script as video_generate_script
from 项目2小红书爆款文案生成器.utils import generate_xiaohongshu, get_baidu_image_url
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
    import streamlit as st
    from utils import generate_xiaohongshu, get_baidu_image_url

    # 定义支持的风格列表，需与utils中的风格名称一致
    STYLES = ["幽默调侃", "专业干货", "亲切治愈", "活泼种草"]
    st.set_page_config(page_title="小红书爆款文案生成器", layout="wide")
    st.header("小红书爆款文案生成器 🌈")

    # 初始化session_state用于缓存生成结果
    if "result" not in st.session_state:
        st.session_state["result"] = None
    if "raw_response" not in st.session_state:
        st.session_state["raw_response"] = ""
    if "style" not in st.session_state:
        st.session_state["style"] = ""
    if "num_titles" not in st.session_state:
        st.session_state["num_titles"] = 5

    with st.sidebar:
        st.subheader("参数设置")
        api_key = st.text_input('请输入你的OpenAI API Key', type='password')
        theme = st.text_input('请输入创作主题')
        style = st.selectbox(
            '选择文案风格',
            STYLES,
            help="不同风格将影响标题和正文的语气与表达方式"
        )
        num_titles = st.slider("生成标题数量", min_value=2, max_value=10, value=st.session_state.get("num_titles", 5),
                               step=1)
        st.markdown("---")
        st.info("💡 提示：风格选择会影响文案的语气和用词哦~")

    submit = st.button('开始生成', type="primary", use_container_width=True)

    # 输入验证
    if submit and not api_key:
        st.warning('请输入OpenAI API密钥', icon="⚠️")
        st.stop()
    if submit and not theme:
        st.warning('请输入创作主题', icon="⚠️")
        st.stop()

    if submit:
        with st.spinner('AI正在创作中，请稍候... 🧠✨'):
            try:
                result, raw_response = generate_xiaohongshu(theme, api_key, style, num_titles=num_titles)
                # 缓存到session_state
                st.session_state["result"] = result
                st.session_state["raw_response"] = raw_response
                st.session_state["style"] = style
                st.session_state["num_titles"] = num_titles
            except Exception as e:
                st.error(f"生成失败: {str(e)}", icon="🚨")
                st.code(str(e))
                st.stop()

    # 优先从session_state读取内容
    result = st.session_state.get("result", None)
    raw_response = st.session_state.get("raw_response", "")
    style = st.session_state.get("style", style)
    num_titles = st.session_state.get("num_titles", num_titles)

    if result:
        st.divider()
        st.subheader(f"生成结果 - 风格: {style} 🌟")

        # 自动配图（百度图片），直接用输入主题作为关键词，确保相关性
        image_query = theme
        image_url = get_baidu_image_url(image_query)
        if image_url:
            st.image(image_url, use_column_width=True, caption="主题配图（来自百度图片）")

        # 优化布局：标题区域使用网格展示
        st.markdown(f"### 推荐标题 ({num_titles}�����1)")
        cols = st.columns(num_titles)
        for i in range(num_titles):
            with cols[i]:
                st.markdown(f"**{i + 1}. {result.titles[i]}**")

        st.divider()

        # 正文区域使用卡片式展示
        with st.container():
            st.markdown("### 正文内容")
            st.info(result.content, icon="📝")

        # 新增风格说明区域
        style_tips = {
            "幽默调侃": "✅ 特点：含网络热梗和搞笑比喻，适合生活类和吐槽类主题",
            "专业干货": "✅ 特点：含数据支撑和原理分析，适合知识分享、技能教学",
            "亲切治愈": "✅ 特点：第一人称故事分享，语气温柔暖心",
            "活泼种草": "✅ 特点：强安利语气，适合产品推荐、好物分享"
        }
        st.info(style_tips.get(style, ""), icon="💡")

        # 只保留Markdown下载和原始响应
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            # 在Markdown中添加图片链接
            md = f"# 小红书爆款文案\n\n"
            if image_url:  # 如果成功获取到图片，将其添加到Markdown中
                # 确保图片URL是完整的
                if not image_url.startswith(('http://', 'https://')):
                    image_url = f"https:{image_url}"
                md += f"![主题配图]({image_url})\n\n"
                # 添加图片源信息
                md += f"*图片来源: 百度图片*\n\n"

            md += f"## 标题\n" + \
                  "\n".join([f"- {title}" for title in result.titles]) + \
                  f"\n\n## 正文\n{result.content}\n"

            # 添加下载按钮，并显示当前图片URL（用于调试）
            st.download_button("点击下载Markdown", md, file_name="xiaohongshu.md", use_container_width=True)
            if image_url:
                with st.expander("查看图片URL（调试用）"):
                    st.code(image_url)

        # 新增：显示原始AI应
        with col2:
            with st.expander("查看AI原始响应（调试用）"):
                st.code(raw_response)


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
