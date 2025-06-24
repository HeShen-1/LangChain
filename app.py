import streamlit as st
import os
import tempfile
from datetime import datetime
# 1. 导入各子项目的功能函数
from 项目1视频脚本一键生成器.utils import (
    generate_script as video_generate_script,
    get_style_options, get_type_options, get_structure_options,
    save_script_history, load_script_history, export_to_word, export_to_txt
)
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
    
    # 添加标签页
    tab1, tab2, tab3 = st.tabs(["🎬 生成脚本", "📚 历史记录", "💡 使用指南"])
    
    with tab1:
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("### 📝 基础设置")
            
            # 基础参数
            subject = st.text_input('💡 请输入视频的主题', placeholder="例如：人工智能的发展趋势")
            
            col1_1, col1_2 = st.columns(2)
            with col1_1:
                video_length = st.number_input('⏱️ 视频时长(分钟)', min_value=1, max_value=60, step=1, value=5)
            with col1_2:
                creativity = st.slider("🎨 创造力", min_value=0.0, max_value=1.0, value=0.2, step=0.1)
            
            st.markdown("### 🎭 风格设置")
            
            col2_1, col2_2, col2_3 = st.columns(3)
            with col2_1:
                style = st.selectbox('🎪 视频风格', get_style_options(), index=0)
            with col2_2:
                video_type = st.selectbox('📹 视频类型', get_type_options(), index=0)
            with col2_3:
                script_structure = st.selectbox('📋 脚本结构', get_structure_options(), index=0)
            
            st.markdown("### ⚙️ 高级功能")
            
            col3_1, col3_2 = st.columns(2)
            with col3_1:
                include_shots = st.checkbox('🎥 分镜头脚本', help="生成详细的分镜头建议")
                include_bgm = st.checkbox('🎵 BGM音效建议', help="包含背景音乐和音效推荐")
                include_hotspot = st.checkbox('🔥 热点信息', help="自动补充相关热点或百科信息")
            with col3_2:
                include_tags = st.checkbox('🏷️ 生成标签', help="自动生成适合的视频标签")
                include_description = st.checkbox('📄 生成简介', help="自动生成视频简介")
                save_to_history = st.checkbox('💾 保存到历史', value=True, help="将生成的脚本保存到历史记录")
            
            if st.button("🎯 生成视频脚本", type="primary", use_container_width=True):
                if not subject:
                    st.warning("⚠️ 请输入视频主题")
                    return
                with st.spinner('AI正在思考中,请稍后...'):
                    try:
                        result = video_generate_script(
                            subject=subject,
                            video_length=video_length, 
                            creativity=creativity,
                            api_key=openai_api_key,
                            style=style,
                            video_type=video_type,
                            script_structure=script_structure,
                            include_shots=include_shots,
                            include_bgm=include_bgm,
                            include_hotspot=include_hotspot,
                            include_tags=include_tags,
                            include_description=include_description
                        )
                        if save_to_history:
                            save_script_history(result)
                        st.success('✅ 视频脚本已生成')
                        st.session_state['current_script'] = result
                        st.session_state['show_script_result'] = True
                    except Exception as e:
                        st.error(f"❌ 生成失败：{str(e)}")
        
        with col2:
            st.markdown("### 🎭 风格说明")
            style_info = {
                "轻松幽默": "适合娱乐内容，轻松搞笑",
                "科普教育": "严谨专业，知识性强",
                "情感温馨": "温暖治愈，情感共鸣",
                "励志激昂": "正能量满满，激发斗志",
                "悬疑神秘": "悬念迭起，引人入胜",
                "尖酸刻薄": "吐槽犀利，语言辛辣，适合讽刺和批判类内容"
                
            }
            for style_name, desc in list(style_info.items()):
                st.markdown(f"**{style_name}:** {desc}")
            st.markdown("### 📋 结构说明")
            structure_info = {
                "开头-中间-结尾": "经典三段式结构",
                "引入-冲突-高潮-结局": "戏剧性故事结构",
                "问题-分析-解决": "逻辑分析结构",
                "故事-道理-启发": "寓教于乐结构",
                "现象-原因-对策": "议论文结构",
                "吐槽-分析-解决": "适合吐槽、批判、分析问题并给出解决方案的内容"
            }
            for struct_name, desc in structure_info.items():
                st.markdown(f"**{struct_name}:** {desc}")

    with tab2:
        st.markdown("### 📚 历史记录")
        history_scripts = load_script_history()
        if not history_scripts:
            st.info("暂无历史记录")
        else:
            col_search, col_filter = st.columns([2, 1])
            with col_search:
                search_term = st.text_input("🔍 搜索脚本", placeholder="输入关键词搜索...")
            with col_filter:
                filter_style = st.selectbox("筛选风格", ["全部"] + get_style_options())
            filtered_scripts = history_scripts
            if search_term:
                filtered_scripts = [s for s in filtered_scripts if search_term.lower() in s.get('title', '').lower() or search_term.lower() in s.get('subject', '').lower()]
            if filter_style != "全部":
                filtered_scripts = [s for s in filtered_scripts if s.get('style') == filter_style]
            st.markdown(f"共找到 {len(filtered_scripts)} 条记录")
            for i, script in enumerate(filtered_scripts[:10]):
                with st.expander(f"📝 {script.get('title', '未命名')} - {script.get('timestamp', '')}"):
                    col_info, col_actions = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"**主题:** {script.get('subject', 'N/A')}")
                        st.markdown(f"**风格:** {script.get('style', 'N/A')} | **类型:** {script.get('type', 'N/A')} | **时长:** {script.get('duration', 'N/A')}分钟")
                        if script.get('structure'):
                            st.markdown(f"**结构:** {script.get('structure', 'N/A')}")
                        script_preview = script.get('script', '')[:200]
                        st.markdown(f"**内容预览:** {script_preview}...")
                    with col_actions:
                        if st.button("👀 查看", key=f"view_{i}"):
                            st.session_state['current_script'] = script
                            st.success("已加载到当前显示")
                        if st.button("⭐ 收藏", key=f"fav_{i}"):
                            st.success("已收藏")
                        if st.button("🗑️ 删除", key=f"del_{i}"):
                            st.warning("删除功能开发中")

    with tab3:
        st.markdown("### 💡 使用指南")
        st.markdown("""
        #### 🚀 快速开始
        1. **输入主题**: 在基础设置中输入你想要制作的视频主题
        2. **选择风格**: 根据内容类型选择合适的风格和类型
        3. **自定义结构**: 选择适合的脚本结构模式
        4. **开启功能**: 根据需要开启分镜头、BGM、标签等功能
        5. **生成脚本**: 点击生成按钮，AI将为你创建完整的视频脚本
        
        #### 🎯 功能特色
        - **🎭 多种风格**: 支持10种不同的视频风格
        - **📹 丰富类型**: 涵盖讲解、剧情、Vlog等10种视频类型
        - **📋 结构自定义**: 5种专业的脚本结构模式
        - **🎥 分镜头建议**: 自动生成拍摄指导
        - **🎵 BGM推荐**: 智能推荐背景音乐和音效
        - **🏷️ 标签生成**: 自动生成SEO友好的视频标签
        - **📄 简介生成**: 创建吸引人的视频简介
        - **💾 历史记录**: 保存和管理你的所有脚本
        - **📥 一键导出**: 支持Word、TXT格式导出
        
        #### 📊 最佳实践
        - **主题选择**: 选择具体、有针对性的主题
        - **时长设置**: 根据平台特点设置合适的时长
        - **风格匹配**: 确保风格与目标受众匹配
        - **结构选择**: 根据内容性质选择合适的结构
        - **功能组合**: 合理组合各种功能，避免信息过载
        """)
        st.markdown("#### 🎯 预设模板说明")
        st.markdown("""
        - **📚 知识科普**: 适合教育类内容，逻辑清晰
        - **😄 搞笑娱乐**: 轻松幽默，适合娱乐内容
        - **💪 励志鸡汤**: 正能量内容，激发共鸣
        - **🔍 产品测评**: 专业客观，适合评测内容
        """)

    # 只在tab1显示生成结果
    if st.session_state.get('show_script_result', False) and st.session_state.get('current_script'):
        with tab1:
            st.markdown("---")
            st.markdown("### 📄 当前脚本")
            display_script_result(st.session_state['current_script'])
    else:
        st.session_state['show_script_result'] = False

def display_script_result(result):
    unique_key = str(result.get('timestamp', ''))
    st.subheader('🔥 视频标题')
    st.write(result['title'])
    info_cols = st.columns(4)
    with info_cols[0]:
        st.info(f"**风格:** {result['style']}")
    with info_cols[1]:
        st.info(f"**类型:** {result['type']}")
    with info_cols[2]:
        st.info(f"**结构:** {result.get('structure', 'N/A')}")
    with info_cols[3]:
        st.info(f"**时长:** {result['duration']}分钟")
    if 'tags' in result and result['tags']:
        st.subheader('🏷️ 推荐标签')
        tags_str = ' '.join([f"#{tag}" for tag in result['tags']])
        st.markdown(tags_str)
    if 'description' in result and result['description']:
        st.subheader('📄 视频简介')
        st.write(result['description'])
    st.subheader('📚 视频脚本')
    st.write(result['script'])
    if 'shots' in result:
        st.subheader('🎥 分镜头建议')
        for i, shot in enumerate(result['shots'], 1):
            st.write(f"**{i}.** {shot}")
    if 'bgm_suggestions' in result:
        st.subheader('🎵 BGM和音效建议')
        for bgm in result['bgm_suggestions']:
            st.write(f"• {bgm}")
    st.markdown("### 📥 导出选项")
    export_cols = st.columns(3)
    with export_cols[0]:
        if st.button("📄 导出为Word", use_container_width=True, key=f"word_{unique_key}"):
            try:
                filename = f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                if export_to_word(result, filename):
                    st.success(f"✅ 已导出为 {filename}")
                    with open(filename, 'rb') as f:
                        st.download_button(
                            label="⬇️ 下载Word文件",
                            data=f,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"download_word_{unique_key}"
                        )
                else:
                    st.error("❌ Word导出失败")
            except Exception as e:
                st.error(f"❌ 导出失败: {str(e)}")
    with export_cols[1]:
        if st.button("📝 导出为TXT", use_container_width=True, key=f"txt_{unique_key}"):
            try:
                filename = f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                if export_to_txt(result, filename):
                    st.success(f"✅ 已导出为 {filename}")
                    with open(filename, 'r', encoding='utf-8') as f:
                        st.download_button(
                            label="⬇️ 下载TXT文件",
                            data=f,
                            file_name=filename,
                            mime="text/plain",
                            key=f"download_txt_{unique_key}"
                        )
                else:
                    st.error("❌ TXT导出失败")
            except Exception as e:
                st.error(f"❌ 导出失败: {str(e)}")
    with export_cols[2]:
        full_content = f"""标题: {result['title']}\n风格: {result['style']} | 类型: {result['type']} | 结构: {result.get('structure', 'N/A')}\n时长: {result['duration']}分钟\n\n{result.get('description', '')}\n\n{result['script']}\n\n标签: {', '.join(result.get('tags', []))}"""
        if st.button("📋 复制全部内容", use_container_width=True, key=f"copy_{unique_key}"):
            st.text_area("复制以下内容:", value=full_content, height=200, key=f"copy_area_{unique_key}")

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
