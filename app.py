import streamlit as st
import random
from datetime import datetime
# 1. 导入各子项目的功能函数
from 项目1视频脚本一键生成器.utils import (
    generate_script as video_generate_script,
    get_style_options, get_type_options, get_structure_options,
    save_script_history, load_script_history, export_to_word, export_to_pdf,
    toggle_favorite_script, delete_script_history, get_favorite_scripts
)
from 项目1视频脚本一键生成器.utils import generate_script as video_generate_script
from 项目2小红书爆款文案生成器.utils import generate_xiaohongshu, get_all_baidu_image_urls
from 项目3克隆ChatGPT.utils import get_chat_response, get_chat_response_stream, generate_chat_title
from 项目4智能文档问答工具.utils import load_documents, qa_agent, gen_followup_questions, gen_followup_questions_from_qa
from langchain.memory import ConversationBufferMemory
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.schema import HumanMessage, AIMessage
from typing import List

# 设置页面配置
st.set_page_config(
    page_title="AI工具集合",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 全局CSS美化样式
st.markdown("""
    <style>
    .main-title {
        font-size:2.5rem !important;
        font-weight:900;
        color:#e94f4a;
        letter-spacing:2px;
        margin-bottom:0.5em;
    }
    .subtitle {
        font-size:1.2rem;
        color:#666;
        margin-bottom:1.5em;
    }
    .card {
        background: #fff7f4;
        border-radius: 1.2em;
        padding: 1.5em 1.5em 1em 1.5em;
        margin-bottom: 1.5em;
        box-shadow: 0 2px 8px #f7d7d733;
    }
    .title-card {
        background: linear-gradient(90deg,#ffe0e0 0%,#fff7f4 100%);
        border-radius: 1em;
        padding: 1em 1em 0.5em 1em;
        margin-bottom: 1em;
    }
    .content-card {
        background: #f7fafd;
        border-radius: 1em;
        padding: 1.2em 1em 1em 1em;
        margin-bottom: 1em;
    }
    .style-tip {
        background: #fffbe6;
        border-left: 6px solid #ffe58f;
        border-radius: 0.7em;
        padding: 0.8em 1em;
        margin-bottom: 1em;
        color: #ad6800;
    }
    .stButton>button {
        background: linear-gradient(90deg,#e94f4a 0%,#ffb199 100%);
        color: white;
        font-weight: bold;
        border-radius: 2em;
        border: none;
        padding: 0.5em 2em;
        font-size: 1.1em;
        margin-top: 0.5em;
        margin-bottom: 0.5em;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(233, 79, 74, 0.3);
    }
    .stDownloadButton>button {
        background: #e94f4a;
        color: white;
        border-radius: 2em;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    .stDownloadButton>button:hover {
        background: #d63384;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(233, 79, 74, 0.3);
    }
    /* 美化侧栏 */
    .css-1d391kg {
        background: linear-gradient(180deg, #fff 0%, #f8f9fa 100%);
    }
    /* 美化主内容区域 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* 美化输入框 */
    .stTextInput>div>div>input {
        border-radius: 1em;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    .stTextInput>div>div>input:focus {
        border-color: #e94f4a;
        box-shadow: 0 0 0 0.2rem rgba(233, 79, 74, 0.25);
    }
    /* 美化选择框 */
    .stSelectbox>div>div>div {
        border-radius: 1em;
        border: 2px solid #e0e0e0;
    }
         /* 美化滑块 */
     .stSlider>div>div>div>div {
         background: linear-gradient(90deg,#e94f4a 0%,#ffb199 100%);
     }
     /* 美化标签页 */
     .stTabs [data-baseweb="tab-list"] {
         gap: 8px;
     }
     .stTabs [data-baseweb="tab"] {
         border-radius: 1em;
         padding: 0.5em 1em;
         background: #f8f9fa;
         border: 2px solid #e0e0e0;
         color: #666;
         font-weight: 500;
         transition: all 0.3s ease;
     }
     .stTabs [aria-selected="true"] {
         background: linear-gradient(90deg,#e94f4a 0%,#ffb199 100%);
         color: white;
         border-color: #e94f4a;
     }
     /* 美化警告和信息框 */
     .stWarning {
         border-radius: 1em;
         border-left: 6px solid #ffc107;
     }
     .stSuccess {
         border-radius: 1em;
         border-left: 6px solid #28a745;
     }
     .stInfo {
         border-radius: 1em;
         border-left: 6px solid #17a2b8;
     }
     .stError {
         border-radius: 1em;
         border-left: 6px solid #dc3545;
     }
     /* 美化侧栏按钮 */
     .css-1d391kg .stButton>button {
         width: 100%;
         margin-bottom: 0.5rem;
         background: linear-gradient(90deg,#f8f9fa 0%,#e9ecef 100%);
         color: #495057;
         border: 1px solid #dee2e6;
     }
     .css-1d391kg .stButton>button:hover {
         background: linear-gradient(90deg,#e94f4a 0%,#ffb199 100%);
         color: white;
         border-color: #e94f4a;
     }
     /* 美化首页制作团队卡片 */
     .team-card {
         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
         border-radius: 1.5em;
         padding: 2em;
         color: white;
         text-align: center;
         box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
         margin: 2em 0;
     }
     </style>
 """, unsafe_allow_html=True)

# 小红书模型定义（兼容主页面显示）
class XiaoHongShu(BaseModel):
    titles: List[str] = Field(description='小红书的5个标题', min_items=5, max_items=10)
    content: str = Field(description='小红书的正文内容')

# 初始化session state
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = "首页"

# 新增状态管理
if 'view_history_script' not in st.session_state:
    st.session_state.view_history_script = None
if 'return_to_tab' not in st.session_state:
    st.session_state.return_to_tab = None
if 'history_tab_index' not in st.session_state:
    st.session_state.history_tab_index = 0  # 0=全部记录, 1=收藏记录

# 全局侧栏API密钥输入
with st.sidebar:
    st.title("🤖 AI工具集合")
    st.markdown("---")
    
    # API密钥输入
    openai_api_key = st.text_input('请输入API密钥', type='password', key='global_api_key')
    if openai_api_key:
        st.success("✅ API密钥已设置")
    else:
        st.warning("⚠️ 请输入API密钥以使用AI功能")
    
    st.markdown("[获取OpenAI API密钥](https://openai-hk.com/v3/ai/key)")
    st.markdown("[获取DeepSeek API密钥](https://deepseek.com/key)")
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
    
    if st.button("📄 智能文档问答工具", use_container_width=True):
        st.session_state.selected_page = "智能文档问答"
    
    st.markdown("---")
    st.markdown("### 📞 联系我们")
    st.markdown("如有问题，请联系开发团队")
    st.markdown("或者在[GitHub仓库](https://github.com/HeShen-1/LangChain)留下你的Issues")

# 首页
def show_home():
    st.markdown('<div class="main-title">🎉 欢迎使用AI工具集合</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">集成多种AI工具，一站式解决您的创作需求</div>', unsafe_allow_html=True)
    
    # 居中显示制作团队信息
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="team-card">
            <h2 style="margin-bottom: 0.5em; font-size: 2rem;">👥 制作团队</h2>
            <h3 style="margin: 0; font-size: 1.5rem; font-weight: 300;">傅彬彬，董政，聂群松，何星伽</h3>
            <p style="margin-top: 1em; opacity: 0.9;">致力于打造最优秀的AI工具集合</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 工具介绍
    st.markdown("## 🛠️ 工具介绍")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card" style="background: linear-gradient(135deg, #667eea 0%,rgb(73, 127, 226) 100%);">
            <h3 style="color: #ffffff; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                🎬 一键生成视频脚本---何星伽
            </h3>
            <ul style="color: #e2e8f0; font-size: 1.1rem; font-weight: 500;">
                <li>快速生成各类视频脚本</li>
                <li>支持多种风格和类型</li>
                <li>自动优化内容结构</li>
                <li>基于LangChain和OpenAI GPT</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);">
            <h3 style="color: #7c2d12; font-weight: bold; text-shadow: 1px 1px 2px rgba(255,255,255,0.5);">
                📝 生成小红书爆款文案---董政
            </h3>
            <ul style="color: #7c2d12; font-size: 1.1rem; font-weight: 500;">
                <li>智能生成小红书文案</li>
                <li>优化标题和内容</li>
                <li>智能配图选择</li>
                <li>包含爆款关键词和emoji</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
            <h3 style="color: #1e293b; font-weight: bold; text-shadow: 1px 1px 2px rgba(255,255,255,0.5);">
                💬 克隆ChatGPT---聂群松
            </h3>
            <ul style="color: #1e293b; font-size: 1.1rem; font-weight: 500;">
                <li>智能对话系统</li>
                <li>多轮对话能力</li>
                <li>个性化回复</li>
                <li>支持上下文记忆</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card" style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);">
            <h3 style="color: #7c2d12; font-weight: bold; text-shadow: 1px 1px 2px rgba(255,255,255,0.5);">
                📄 智能文档问答工具---傅彬彬
            </h3>
            <ul style="color: #7c2d12; font-size: 1.1rem; font-weight: 500;">
                <li>上传PDF文档</li>
                <li>智能文档问答</li>
                <li>快速信息提取</li>
                <li>基于向量检索技术</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# 视频脚本
def show_video_script():
    st.markdown('<div class="main-title">🎬 一键生成视频脚本</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">AI智能创作，多种风格和类型，专业分镜头建议</div>', unsafe_allow_html=True)
    
    if not openai_api_key:
        st.warning("⚠️ 请在左侧侧栏输入OpenAI API密钥")
        return
    
    # 检查是否是从历史记录查看
    if st.session_state.view_history_script:
        show_history_script_view()
        return
    
    # 添加标签页
    tab1, tab2, tab3 = st.tabs(["🎬 生成脚本", "📚 历史记录", "💡 使用指南"])
    
    with tab1:
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("### 🧩 基础设置")
            
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
                script_structure = st.selectbox('🔖 脚本结构', get_structure_options(), index=0)
            
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
            st.markdown("### 🌚 风格说明")
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
            st.markdown("### 🪐 结构说明")
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
        
        # 初始化session state
        if 'history_refresh' not in st.session_state:
            st.session_state['history_refresh'] = 0
        
        # 显示返回提示信息
        if st.session_state.get('history_tab_index') == 1:
            st.success("✅ 已从收藏记录查看返回，请切换到【⭐ 收藏记录】标签页")
            st.session_state.history_tab_index = 0  # 重置
        elif st.session_state.get('history_tab_index') == 0 and 'return_to_tab' in st.session_state:
            st.success("✅ 已从全部记录查看返回，请查看【📋 全部记录】标签页") 
            # 清理返回状态
            if 'return_to_tab' in st.session_state:
                del st.session_state['return_to_tab']
        
        hist_tab1, hist_tab2 = st.tabs(["📋 全部记录", "⭐ 收藏记录"])
        
        with hist_tab1:
            history_scripts = load_script_history()
            if not history_scripts:
                st.info("暂无历史记录")
            else:
                # 搜索和筛选
                col_search, col_filter, col_sort = st.columns([2, 1, 1])
                with col_search:
                    search_term = st.text_input("🔍 搜索脚本", placeholder="输入关键词搜索...", key="search_all")
                with col_filter:
                    filter_style = st.selectbox("筛选风格", ["全部"] + get_style_options(), key="filter_all")
                with col_sort:
                    sort_option = st.selectbox("排序方式", ["时间(最新)", "时间(最旧)", "收藏优先"], key="sort_all")
                
                # 应用筛选和搜索
                filtered_scripts = history_scripts
                if search_term:
                    filtered_scripts = [s for s in filtered_scripts if 
                                      search_term.lower() in s.get('title', '').lower() or 
                                      search_term.lower() in s.get('subject', '').lower()]
                if filter_style != "全部":
                    filtered_scripts = [s for s in filtered_scripts if s.get('style') == filter_style]
                
                # 应用排序
                if sort_option == "时间(最旧)":
                    filtered_scripts.sort(key=lambda x: x.get('timestamp', ''))
                elif sort_option == "收藏优先":
                    filtered_scripts.sort(key=lambda x: (not x.get('is_favorite', False), x.get('timestamp', '')), reverse=True)
                
                st.markdown(f"共找到 {len(filtered_scripts)} 条记录")
                
                # 分页显示
                items_per_page = 10
                total_pages = (len(filtered_scripts) + items_per_page - 1) // items_per_page
                
                # 初始化当前页面
                if 'current_page_all' not in st.session_state:
                    st.session_state['current_page_all'] = 0
                
                if total_pages > 1:
                    page = st.session_state['current_page_all']
                    
                    # 分页按钮
                    col_prev, col_info, col_next = st.columns([1, 2, 1])
                    with col_prev:
                        if st.button("⬅️ 上一页", disabled=(page == 0), key="prev_all"):
                            st.session_state['current_page_all'] = max(0, page - 1)
                            st.rerun()
                    with col_info:
                        st.markdown(f"<div style='text-align: center; padding: 8px;'>第 {page + 1} 页 / 共 {total_pages} 页</div>", unsafe_allow_html=True)
                    with col_next:
                        if st.button("➡️ 下一页", disabled=(page >= total_pages - 1), key="next_all"):
                            st.session_state['current_page_all'] = min(total_pages - 1, page + 1)
                            st.rerun()
                else:
                    page = 0
                
                start_idx = page * items_per_page
                end_idx = min(start_idx + items_per_page, len(filtered_scripts))
                page_scripts = filtered_scripts[start_idx:end_idx]
                
                # 显示脚本列表
                for i, script in enumerate(page_scripts):
                    is_favorite = script.get('is_favorite', False)
                    fav_icon = "⭐" if is_favorite else "☆"
                    
                    with st.expander(f"📝 {fav_icon} {script.get('title', '未命名')} - {script.get('timestamp', '')}"):
                        col_info, col_actions = st.columns([3, 1])
                        with col_info:
                            st.markdown(f"**主题:** {script.get('subject', 'N/A')}")
                            st.markdown(f"**风格:** {script.get('style', 'N/A')} | **类型:** {script.get('type', 'N/A')} | **时长:** {script.get('duration', 'N/A')}分钟")
                            if script.get('structure'):
                                st.markdown(f"**结构:** {script.get('structure', 'N/A')}")
                            if is_favorite:
                                st.markdown("⭐ **已收藏**")
                            script_preview = script.get('script', '')[:200]
                            st.markdown(f"**内容预览:** {script_preview}...")
                        
                        with col_actions:
                            # 查看按钮
                            if st.button("👀 查看", key=f"view_all_{start_idx + i}", use_container_width=True):
                                # 设置查看状态，跳转到生成脚本页面
                                st.session_state.view_history_script = script
                                st.session_state.return_to_tab = "all"
                                st.rerun()
                            
                            # 收藏/取消收藏按钮
                            fav_label = "💔 取消收藏" if is_favorite else "⭐ 收藏"
                            if st.button(fav_label, key=f"fav_all_{start_idx + i}", use_container_width=True):
                                success, message = toggle_favorite_script(script['filename'])
                                if success:
                                    st.success(f"✅ {message}")
                                    st.session_state['history_refresh'] += 1
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                            
                            # 删除按钮
                            if st.button("🗑️ 删除", key=f"del_all_{start_idx + i}", use_container_width=True, type="secondary"):
                                # 使用确认对话框
                                if f"confirm_delete_all_{start_idx + i}" not in st.session_state:
                                    st.session_state[f"confirm_delete_all_{start_idx + i}"] = False
                                
                                if not st.session_state[f"confirm_delete_all_{start_idx + i}"]:
                                    st.session_state[f"confirm_delete_all_{start_idx + i}"] = True
                                    st.warning("⚠️ 请再次点击确认删除")
                                else:
                                    success, message = delete_script_history(script['filename'])
                                    if success:
                                        st.success(f"✅ {message}")
                                        # 清理确认状态
                                        del st.session_state[f"confirm_delete_all_{start_idx + i}"]
                                        st.session_state['history_refresh'] += 1
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {message}")
                                        st.session_state[f"confirm_delete_all_{start_idx + i}"] = False
        
        with hist_tab2:
            favorite_scripts = get_favorite_scripts()
            if not favorite_scripts:
                st.info("暂无收藏记录")
                st.markdown("💡 **提示:** 在全部记录中点击 ⭐ 收藏按钮来收藏你喜欢的脚本")
            else:
                # 搜索和筛选收藏
                col_search_fav, col_filter_fav = st.columns([2, 1])
                with col_search_fav:
                    search_term_fav = st.text_input("🔍 搜索收藏脚本", placeholder="输入关键词搜索...", key="search_fav")
                with col_filter_fav:
                    filter_style_fav = st.selectbox("筛选风格", ["全部"] + get_style_options(), key="filter_fav")
                
                # 应用筛选
                filtered_favorites = favorite_scripts
                if search_term_fav:
                    filtered_favorites = [s for s in filtered_favorites if 
                                        search_term_fav.lower() in s.get('title', '').lower() or 
                                        search_term_fav.lower() in s.get('subject', '').lower()]
                if filter_style_fav != "全部":
                    filtered_favorites = [s for s in filtered_favorites if s.get('style') == filter_style_fav]
                
                st.markdown(f"共找到 {len(filtered_favorites)} 条收藏记录")
                
                # 显示收藏脚本
                for i, script in enumerate(filtered_favorites):
                    with st.expander(f"⭐ {script.get('title', '未命名')} - {script.get('timestamp', '')}"):
                        col_info, col_actions = st.columns([3, 1])
                        with col_info:
                            st.markdown(f"**主题:** {script.get('subject', 'N/A')}")
                            st.markdown(f"**风格:** {script.get('style', 'N/A')} | **类型:** {script.get('type', 'N/A')} | **时长:** {script.get('duration', 'N/A')}分钟")
                            if script.get('structure'):
                                st.markdown(f"**结构:** {script.get('structure', 'N/A')}")
                            script_preview = script.get('script', '')[:200]
                            st.markdown(f"**内容预览:** {script_preview}...")
                        
                        with col_actions:
                            # 查看按钮
                            if st.button("👀 查看", key=f"view_fav_{i}", use_container_width=True):
                                # 设置查看状态，跳转到生成脚本页面
                                st.session_state.view_history_script = script
                                st.session_state.return_to_tab = "favorite"
                                st.rerun()
                            
                            # 取消收藏按钮
                            if st.button("💔 取消收藏", key=f"unfav_{i}", use_container_width=True):
                                success, message = toggle_favorite_script(script['filename'])
                                if success:
                                    st.success(f"✅ {message}")
                                    st.session_state['history_refresh'] += 1
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                            
                            # 删除按钮
                            if st.button("🗑️ 删除", key=f"del_fav_{i}", use_container_width=True, type="secondary"):
                                # 使用确认对话框
                                if f"confirm_delete_fav_{i}" not in st.session_state:
                                    st.session_state[f"confirm_delete_fav_{i}"] = False
                                
                                if not st.session_state[f"confirm_delete_fav_{i}"]:
                                    st.session_state[f"confirm_delete_fav_{i}"] = True
                                    st.warning("⚠️ 请再次点击确认删除")
                                else:
                                    success, message = delete_script_history(script['filename'])
                                    if success:
                                        st.success(f"✅ {message}")
                                        # 清理确认状态
                                        del st.session_state[f"confirm_delete_fav_{i}"]
                                        st.session_state['history_refresh'] += 1
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {message}")
                                        st.session_state[f"confirm_delete_fav_{i}"] = False



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
        - **📥 一键导出**: 支持Word、PDF格式导出
        
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

# 历史记录查看脚本
def show_history_script_view():
    """显示从历史记录查看的脚本"""
    script = st.session_state.view_history_script
    return_tab = st.session_state.return_to_tab
    
    # 返回按钮和标题
    col1, col2, col3 = st.columns([2, 4, 2])
    with col1:
        return_text = "← 返回历史记录"
        if st.button(return_text, key="return_to_history", use_container_width=True):
            # 根据来源设置标签页索引
            if return_tab == "all":
                st.session_state.history_tab_index = 0  # 全部记录
            elif return_tab == "favorite":
                st.session_state.history_tab_index = 1  # 收藏记录
            
            # 清理查看状态，返回历史记录页面
            st.session_state.view_history_script = None
            st.session_state.return_to_tab = None
            st.rerun()
    
    with col2:
        st.markdown(f"<h3 style='text-align: center;'>📄 查看历史脚本</h3>", unsafe_allow_html=True)
    
    # 显示来源信息
    source_text = "全部记录" if return_tab == "all" else "收藏记录"
    st.info(f"📂 来源：{source_text} | 生成时间：{script.get('timestamp', 'N/A')}")
    
    st.markdown("---")
    
    # 显示脚本详情
    display_script_result(script, is_history_view=True)

# 显示脚本详情
def display_script_result(result, is_history_view=False):
    """
    按照优先级显示生成的脚本结果
    优先级：视频标题 > 推荐标签 > 视频简介 > 视频脚本 > 分镜头建议 > BGM和音效建议
    """
    unique_key = str(result.get('timestamp', ''))
    
    # 1. 视频标题（始终显示）
    st.subheader('🔥 视频标题')
    st.write(result['title'])
    
    # 基本信息
    info_cols = st.columns(4)
    with info_cols[0]:
        st.info(f"**风格:** {result['style']}")
    with info_cols[1]:
        st.info(f"**类型:** {result['type']}")
    with info_cols[2]:
        st.info(f"**结构:** {result.get('structure', 'N/A')}")
    with info_cols[3]:
        st.info(f"**时长:** {result['duration']}分钟")
    
    # 2. 推荐标签（如果生成）
    if 'tags' in result and result['tags']:
        st.subheader('🏷️ 推荐标签')
        tags_str = ' '.join([f"#{tag}" for tag in result['tags']])
        st.markdown(tags_str)
    
    # 3. 视频简介（如果生成）
    if 'description' in result and result['description']:
        st.subheader('📄 视频简介')
        st.write(result['description'])
    
    # 4. 视频脚本（始终显示）
    st.subheader('📚 视频脚本')
    st.write(result['script'])
    
    # 5. 分镜头建议（如果生成）
    if 'shots' in result and result['shots']:
        st.subheader('🎥 分镜头建议')
        for i, shot in enumerate(result['shots'], 1):
            st.write(f"**{i}.** {shot}")
    
    # 6. BGM和音效建议（如果生成）
    if 'bgm_suggestions' in result and result['bgm_suggestions']:
        st.subheader('🎵 BGM和音效建议')
        for bgm in result['bgm_suggestions']:
            st.write(f"• {bgm}")
    
    # 导出选项
    if not is_history_view:
        st.markdown("### 📥 导出选项")
        export_cols = st.columns(3)
    else:
        st.markdown("### 📥 导出选项")
        export_cols = st.columns(2)
    with export_cols[0]:
        if st.button("📘 导出为Word", use_container_width=True, key=f"word_{unique_key}"):
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
        if st.button("📕 导出为PDF", use_container_width=True, key=f"pdf_{unique_key}"):
            try:
                filename = f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                if export_to_pdf(result, filename):
                    st.success(f"✅ 已导出为 {filename}")
                    with open(filename, 'rb') as f:
                        st.download_button(
                            label="⬇️ 下载PDF文件",
                            data=f,
                            file_name=filename,
                            mime="application/pdf",
                            key=f"download_pdf_{unique_key}"
                        )
                else:
                    st.error("❌ PDF导出失败")
            except Exception as e:
                st.error(f"❌ 导出失败: {str(e)}")
    if not is_history_view:
        with export_cols[2]:
            # 按优先级构建复制内容
            full_content = f"标题: {result['title']}\n"
            full_content += f"风格: {result['style']} | 类型: {result['type']} | 结构: {result.get('structure', 'N/A')}\n"
            full_content += f"时长: {result['duration']}分钟\n\n"
            
            if 'tags' in result and result['tags']:
                full_content += f"推荐标签: {', '.join(result['tags'])}\n\n"
            
            if 'description' in result and result['description']:
                full_content += f"视频简介: {result['description']}\n\n"
            
            full_content += f"视频脚本:\n{result['script']}\n"
            
            if 'shots' in result and result['shots']:
                full_content += f"\n分镜头建议:\n"
                for i, shot in enumerate(result['shots'], 1):
                    full_content += f"{i}. {shot}\n"
            
            if 'bgm_suggestions' in result and result['bgm_suggestions']:
                full_content += f"\nBGM和音效建议:\n"
                for bgm in result['bgm_suggestions']:
                    full_content += f"• {bgm}\n"
            
            if st.button("📋 复制全部内容", use_container_width=True, key=f"copy_{unique_key}"):
                st.text_area("复制以下内容:", value=full_content, height=200, key=f"copy_area_{unique_key}")

# 小红书文案
def show_xiaohongshu():
    STYLES = ["幽默调侃", "专业干货", "亲切治愈", "活泼种草"]
    
    st.markdown('<div class="main-title">小红书爆款文案生成器 <span style="font-size:1.5rem;">🌈</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">一键生成高质量小红书标题与正文，支持多种风格，自动配图，助你轻松打造爆款内容！</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">此功能基于DeepSeek模型实现,请输入DeepSeek API Key!</div>', unsafe_allow_html=True)

    # 初始化session_state用于缓存生成结果
    if "xiaohongshu_result" not in st.session_state:
        st.session_state["xiaohongshu_result"] = None
    if "xiaohongshu_raw_response" not in st.session_state:
        st.session_state["xiaohongshu_raw_response"] = ""
    if "xiaohongshu_style" not in st.session_state:
        st.session_state["xiaohongshu_style"] = ""
    if "xiaohongshu_num_titles" not in st.session_state:
        st.session_state["xiaohongshu_num_titles"] = 5
    if "xiaohongshu_num_images" not in st.session_state:
        st.session_state["xiaohongshu_num_images"] = 3
    if "xiaohongshu_selected_image_idx" not in st.session_state:
        st.session_state["xiaohongshu_selected_image_idx"] = 0
    if "xiaohongshu_image_urls" not in st.session_state:
        st.session_state["xiaohongshu_image_urls"] = []
    if "xiaohongshu_all_image_urls" not in st.session_state:
        st.session_state["xiaohongshu_all_image_urls"] = []
    if "xiaohongshu_final_selected_image" not in st.session_state:
        st.session_state["xiaohongshu_final_selected_image"] = None
    # 新增历史记录与收藏
    if "xiaohongshu_history" not in st.session_state:
        st.session_state["xiaohongshu_history"] = []
    if "xiaohongshu_favorites" not in st.session_state:
        st.session_state["xiaohongshu_favorites"] = []

    # 使用全局API密钥
    api_key = openai_api_key
    if not api_key:
        st.warning("⚠️ 请在左侧侧栏输入API密钥")
        return

    # 参数设置区域
    with st.container():
        col1, col2 = st.columns([2, 1])
        with col1:
            theme = st.text_input('请输入创作主题', placeholder="如：夏日防晒好物推荐")
        with col2:
            style = st.selectbox(
                '选择文案风格',
                STYLES,
                help="不同风格将影响标题和正文的语气与表达方式"
            )
        
        col3, col4 = st.columns(2)
        with col3:
            num_titles = st.slider("生成标题数量", min_value=2, max_value=10, value=st.session_state.get("xiaohongshu_num_titles", 5), step=1)
        with col4:
            num_images = st.slider("配图数量", min_value=1, max_value=8, value=st.session_state.get("xiaohongshu_num_images", 3), step=1)

    submit = st.button('🚀 开始生成', type="primary", use_container_width=True)

    # 输入验证
    if submit and not theme:
        st.warning('请输入创作主题', icon="⚠️")
        st.stop()

    if submit:
        with st.spinner('AI正在创作中，请稍候... 🧠✨'):
            try:
                result, raw_response = generate_xiaohongshu(theme, api_key, style, num_titles=num_titles)
                st.session_state["xiaohongshu_result"] = result
                st.session_state["xiaohongshu_raw_response"] = raw_response
                st.session_state["xiaohongshu_style"] = style
                st.session_state["xiaohongshu_num_titles"] = num_titles
                # 获取全部图片用于最终选择
                all_image_urls = get_all_baidu_image_urls(theme, max_images=30)
                st.session_state["xiaohongshu_all_image_urls"] = all_image_urls
                # 随机选取N张用于本轮展示
                image_urls = []
                if all_image_urls:
                    image_urls = random.sample(all_image_urls, min(num_images, len(all_image_urls)))
                st.session_state["xiaohongshu_image_urls"] = image_urls
                st.session_state["xiaohongshu_selected_image_idx"] = 0
                st.session_state["xiaohongshu_final_selected_image"] = None
                # 保存到历史记录
                st.session_state["xiaohongshu_history"].insert(0, {
                    "theme": theme,
                    "style": style,
                    "num_titles": num_titles,
                    "num_images": num_images,
                    "titles": result.titles,
                    "content": result.content,
                    "image_urls": image_urls if image_urls else [],
                    "all_image_urls": all_image_urls,
                    "final_selected_image": None,
                    "raw_response": raw_response
                })
                st.session_state["xiaohongshu_history"] = st.session_state["xiaohongshu_history"][:30]
            except Exception as e:
                st.error(f"生成失败: {str(e)}", icon="🚨")
                st.code(str(e))
                st.stop()

    result = st.session_state.get("xiaohongshu_result", None)
    raw_response = st.session_state.get("xiaohongshu_raw_response", "")
    style = st.session_state.get("xiaohongshu_style", style)
    num_titles = st.session_state.get("xiaohongshu_num_titles", num_titles)
    image_urls = st.session_state.get("xiaohongshu_image_urls", [])
    all_image_urls = st.session_state.get("xiaohongshu_all_image_urls", [])
    selected_image_idx = st.session_state.get("xiaohongshu_selected_image_idx", 0)
    final_selected_image = st.session_state.get("xiaohongshu_final_selected_image", None)
    num_images = st.session_state.get("xiaohongshu_num_images", 3)

    if result:
        st.markdown('<hr style="margin:2em 0 1em 0; border:0; border-top:2px dashed #e94f4a;">', unsafe_allow_html=True)
        st.subheader(f"生成结果 - 风格: {style} 🌟")

        # 仅随机展示N张图片，用户从中选定一张作为最终配图
        if image_urls:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"<span style='font-size:1.1rem;font-weight:bold;'>主题配图（随机展示{len(image_urls)}张，请选择一张作为最终配图）</span>", unsafe_allow_html=True)
            img_cols = st.columns(len(image_urls))
            for i, url in enumerate(image_urls):
                with img_cols[i]:
                    try:
                        st.image(url,use_container_width=True)
                    except:
                        st.image(url, width=200)
                    if st.button("设为最终配图", key=f"final_sel_{i}"):
                        st.session_state["xiaohongshu_final_selected_image"] = url
            if final_selected_image:
                st.success("已选择最终配图！")
                try:
                    st.image(final_selected_image,use_container_width=True, caption="最终配图")
                except:
                    st.image(final_selected_image, width=400, caption="最终配图")
            st.markdown('</div>', unsafe_allow_html=True)

        # 标题区域美化
        st.markdown('<div class="title-card">', unsafe_allow_html=True)
        st.markdown(f"<span style='font-size:1.3rem;font-weight:bold;'>🎯 推荐标题（共 {num_titles} 个）</span>", unsafe_allow_html=True)
        cols = st.columns(num_titles)
        for i in range(num_titles):
            with cols[i]:
                st.markdown(f"<div style='font-size:1.1rem; margin-bottom:0.5em;'><span style='color:#e94f4a;font-weight:bold;'>{i+1}.</span> {result.titles[i]}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 正文区域美化
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("<span style='font-size:1.15rem;font-weight:bold;'>📝 正文内容</span>", unsafe_allow_html=True)
        st.info(result.content, icon="📝")
        st.markdown('</div>', unsafe_allow_html=True)

        # 风格说明区域美化
        style_tips = {
            "幽默调侃": "✅ 特点：含网络热梗和搞笑比喻，适合生活类和吐槽类主题",
            "专业干货": "✅ 特点：含数据支撑和原理分析，适合知识分享、技能教学",
            "亲切治愈": "✅ 特点：第一人称故事分享，语气温柔暖心",
            "活泼种草": "✅ 特点：强安利语气，适合产品推荐、好物分享"
        }
        st.markdown(f'<div class="style-tip">{style_tips.get(style, "")}</div>', unsafe_allow_html=True)

        st.markdown('<hr style="margin:2em 0 1em 0; border:0; border-top:2px dashed #e94f4a;">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            md = f"# 小红书爆款文案\n\n"
            # 多图配图写入markdown
            if final_selected_image:
                url = final_selected_image
                if not url.startswith(('http://', 'https://')):
                    url = f"https:{url}"
                md += f"![最终主题配图]({url})\n\n"
                md += f"*最终配图来源: 百度图片*\n\n"
            elif image_urls:
                for idx, url in enumerate(image_urls):
                    if not url.startswith(('http://', 'https://')):
                        url = f"https:{url}"
                    md += f"![主题配图{idx+1}]({url})\n\n"
                md += f"*图片来源: 百度图片*\n\n"
            md += f"## 标题\n" + \
                  "\n".join([f"- {title}" for title in result.titles]) + \
                  f"\n\n## 正文\n{result.content}\n"
            st.download_button("点击下载Markdown", md, file_name="xiaohongshu.md", use_container_width=True)
            if image_urls or final_selected_image:
                with st.expander("查看图片URL列表（调试用）"):
                    st.code(all_image_urls if all_image_urls else image_urls)
        with col2:
            with st.expander("查看AI原始响应（调试用）"):
                st.code(raw_response)

        # 收藏按钮
        if st.button("⭐ 收藏本次文案", key="fav_this"):
            fav_item = {
                "theme": theme,
                "style": style,
                "num_titles": num_titles,
                "num_images": num_images,
                "titles": result.titles,
                "content": result.content,
                "image_urls": image_urls,
                "all_image_urls": all_image_urls,
                "final_selected_image": final_selected_image,
                "raw_response": raw_response
            }
            if fav_item not in st.session_state["xiaohongshu_favorites"]:
                st.session_state["xiaohongshu_favorites"].insert(0, fav_item)
                st.success("已收藏到收藏夹！")
            else:
                st.info("该文案已在收藏夹中。")

    # 历史记录与收藏管理区 - 移动到tab中
    tab1, tab2 = st.tabs(["📜 历史记录", "⭐ 我的收藏"])
    
    with tab1:
        st.markdown("### 📜 历史记录")
        if st.session_state["xiaohongshu_history"]:
            # 显示更多历史记录，每行3个
            items_per_row = 3
            history_items = st.session_state["xiaohongshu_history"]
            
            for i in range(0, len(history_items), items_per_row):
                cols = st.columns(items_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(history_items):
                        item = history_items[i + j]
                        idx = i + j
                        
                        with col:
                            with st.container():
                                st.markdown(f"**主题：** {item['theme']}")
                                st.markdown(f"**风格：** {item['style']}")
                                st.markdown(f"**标题：** {item['titles'][0][:20]}...")
                                st.markdown(f"**正文：** {item['content'][:30]}...")
                                
                                col_btn1, col_btn2 = st.columns(2)
                                with col_btn1:
                                    if st.button("🔄 恢复", key=f"restore_{idx}", use_container_width=True):
                                        # 使用type创建result对象
                                        result_type = type('Result', (), {})()
                                        result_type.titles = item["titles"]
                                        result_type.content = item["content"]
                                        st.session_state["xiaohongshu_result"] = result_type
                                        st.session_state["xiaohongshu_raw_response"] = item["raw_response"]
                                        st.session_state["xiaohongshu_style"] = item["style"]
                                        st.session_state["xiaohongshu_num_titles"] = item["num_titles"]
                                        st.session_state["xiaohongshu_num_images"] = item.get("num_images", 3)
                                        st.session_state["xiaohongshu_image_urls"] = item.get("image_urls", [])
                                        st.session_state["xiaohongshu_all_image_urls"] = item.get("all_image_urls", [])
                                        st.session_state["xiaohongshu_final_selected_image"] = item.get("final_selected_image", None)
                                        st.session_state["xiaohongshu_selected_image_idx"] = 0
                                        st.rerun()
                                
                                with col_btn2:
                                    if st.button("⭐ 收藏", key=f"fav_hist_{idx}", use_container_width=True):
                                        if item not in st.session_state["xiaohongshu_favorites"]:
                                            st.session_state["xiaohongshu_favorites"].insert(0, item)
                                            st.success("已收藏！")
                                        else:
                                            st.info("已在收藏夹中")
                                
                                st.divider()
        else:
            st.info("🔍 暂无历史记录，快去生成一些小红书文案吧！")

    with tab2:
        st.markdown("### ⭐ 我的收藏")
        if st.session_state["xiaohongshu_favorites"]:
            # 显示收藏，每行3个
            items_per_row = 3
            favorite_items = st.session_state["xiaohongshu_favorites"]
            
            for i in range(0, len(favorite_items), items_per_row):
                cols = st.columns(items_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(favorite_items):
                        item = favorite_items[i + j]
                        idx = i + j
                        
                        with col:
                            with st.container():
                                st.markdown(f"**主题：** {item['theme']}")
                                st.markdown(f"**风格：** {item['style']}")
                                st.markdown(f"**标题：** {item['titles'][0][:20]}...")
                                st.markdown(f"**正文：** {item['content'][:30]}...")
                                
                                col_btn1, col_btn2 = st.columns(2)
                                with col_btn1:
                                    if st.button("🔄 恢复", key=f"restore_fav_{idx}", use_container_width=True):
                                        # 使用type创建result对象
                                        result_type = type('Result', (), {})()
                                        result_type.titles = item["titles"]
                                        result_type.content = item["content"]
                                        st.session_state["xiaohongshu_result"] = result_type
                                        st.session_state["xiaohongshu_raw_response"] = item["raw_response"]
                                        st.session_state["xiaohongshu_style"] = item["style"]
                                        st.session_state["xiaohongshu_num_titles"] = item["num_titles"]
                                        st.session_state["xiaohongshu_num_images"] = item.get("num_images", 3)
                                        st.session_state["xiaohongshu_image_urls"] = item.get("image_urls", [])
                                        st.session_state["xiaohongshu_all_image_urls"] = item.get("all_image_urls", [])
                                        st.session_state["xiaohongshu_final_selected_image"] = item.get("final_selected_image", None)
                                        st.session_state["xiaohongshu_selected_image_idx"] = 0
                                        st.rerun()
                                
                                with col_btn2:
                                    if st.button("🗑️ 移除", key=f"remove_fav_{idx}", use_container_width=True):
                                        st.session_state["xiaohongshu_favorites"].pop(idx)
                                        st.rerun()
                                
                                st.divider()
        else:
            st.info("💫 暂无收藏内容，快去收藏一些优质文案吧！")


# ChatGPT克隆
def show_chatgpt_clone():
    st.title("💬 ClonGPT")
    st.divider()

    # 检查 API key
    if not openai_api_key:
        st.warning("⚠️ 请在左侧侧栏输入 OpenAI API 密钥")
        return

    # ------------------------ 初始化会话状态 ------------------------
    if 'memory' not in st.session_state:
        st.session_state['memory'] = ConversationBufferMemory(return_messages=True)
    if 'messages' not in st.session_state:
        st.session_state['messages'] = [{'role': 'ai', 'content': '你好，我是你的AI助手，有什么可以帮你的吗？'}]
    if 'history_list' not in st.session_state:
        st.session_state['history_list'] = []  # 每条为 {'name': timestamp, 'messages': [...]}
    if 'active_history' not in st.session_state:
        st.session_state['active_history'] = None
    if 'first_question_in_session' not in st.session_state:
        st.session_state['first_question_in_session'] = None
    
    # 初始化默认参数
    if "chat_model" not in st.session_state:
        st.session_state["chat_model"] = "gpt-3.5-turbo"
    if "temperature" not in st.session_state:
        st.session_state["temperature"] = 0.7
    if "top_p" not in st.session_state:
        st.session_state["top_p"] = 1.0
    if "presence_penalty" not in st.session_state:
        st.session_state["presence_penalty"] = 0.0
    if "max_tokens" not in st.session_state:
        st.session_state["max_tokens"] = 1000
    if "system_prompt" not in st.session_state:
        st.session_state["system_prompt"] = "你是ChatGPT，一个由OpenAI训练的大语言模型，请简洁而专业地回答用户问题。"

    # ------------------------ 标签页 ------------------------
    tab1, tab2, tab3 = st.tabs(["当前聊天", "历史消息", "角色设定"])

    # ======================== 当前聊天 Tab ========================
    with tab1:
        # 新建对话按钮和当前角色显示
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if st.button("🗨️ 新建对话", use_container_width=True):
                # 如果当前有对话且不是默认状态，保存到历史
                if len(st.session_state['messages']) > 1 and st.session_state['first_question_in_session']:
                    # 生成聊天标题
                    try:
                        chat_title = generate_chat_title(st.session_state['first_question_in_session'], openai_api_key)
                    except:
                        chat_title = st.session_state['first_question_in_session'][:20] + "..."
                    
                    st.session_state['history_list'].append({
                        'name': chat_title,
                        'messages': st.session_state['messages'].copy()
                    })
                
                # 重置当前对话
                st.session_state['memory'] = ConversationBufferMemory(return_messages=True)
                st.session_state['messages'] = [{'role': 'ai', 'content': '你好，我是你的AI助手，有什么可以帮你的吗？'}]
                st.session_state['first_question_in_session'] = None
                st.session_state['active_history'] = None
                st.rerun()
        
        with col2:
            # 显示当前角色信息
            current_role = "默认助手"
            role_options = {
                "你是ChatGPT，一个由OpenAI训练的大语言模型，请简洁而专业地回答用户问题。": "默认助手",
                "你是一个专业的编程助手，擅长多种编程语言，能够提供代码示例、调试建议和最佳实践。请用简洁明了的方式回答编程相关问题。": "编程助手",
                "你是一个耐心的学习导师，擅长用通俗易懂的方式解释复杂概念，能够根据学习者的水平调整讲解深度。请用循序渐进的方式回答问题。": "学习导师",
                "你是一个富有创造力的写手，擅长创作故事、写作建议和文案策划。请用生动有趣的语言风格回答问题，并提供有创意的建议。": "创意写手"
            }
            
            # 确定当前角色
            current_system_prompt = st.session_state.get("system_prompt", "你是ChatGPT，一个由OpenAI训练的大语言模型，请简洁而专业地回答用户问题。")
            if current_system_prompt in role_options:
                current_role = role_options[current_system_prompt]
            elif current_system_prompt != "你是ChatGPT，一个由OpenAI训练的大语言模型，请简洁而专业地回答用户问题。":
                current_role = st.session_state.get("current_custom_role_name", "自定义角色")
            
            st.info(f"🎭 当前角色：**{current_role}**  |  💡 在【角色设定】标签页中可以更换角色")
        
        # 聊天历史 container
        chat_container = st.container()
        with chat_container:
            for message in st.session_state['messages']:
                st.chat_message(message['role']).write(message['content'])

        # 底部输入区域 container
        bottom_container = st.container()
        with bottom_container:
            cols = st.columns([0.95, 0.05])
            with cols[0]:
                prompt = st.chat_input("请输入您的问题...")
            with cols[1]:
                with st.popover("⚙️", use_container_width=True):
                    st.markdown("### 🤖 模型参数设置")
                    model_list = ["gpt-3.5-turbo", "gpt-4"]
                    st.session_state["chat_model"] = st.selectbox("选择模型", model_list, 
                                                                 index=model_list.index(st.session_state["chat_model"]) if st.session_state["chat_model"] in model_list else 0)
                    st.session_state["temperature"] = st.slider("temperature (创造力)", 0.0, 1.5, st.session_state["temperature"], 0.1)
                    st.session_state["top_p"] = st.slider("top_p (采样范围)", 0.0, 1.0, st.session_state["top_p"], 0.1)
                    st.session_state["presence_penalty"] = st.slider("presence_penalty (重复惩罚)", -2.0, 2.0, st.session_state["presence_penalty"], 0.1)
                    st.session_state["max_tokens"] = st.slider("max_tokens (最大回复长度)", 100, 4000, st.session_state["max_tokens"], 100)

                    if st.button("🗑️ 清空对话", key="clear_chat_button"):
                        st.session_state['memory'] = ConversationBufferMemory(return_messages=True)
                        st.session_state['messages'] = [{'role': 'ai', 'content': '你好，我是你的AI助手，有什么可以帮你的吗？'}]
                        st.session_state['first_question_in_session'] = None
                        st.rerun()

        # 聊天响应逻辑 - 默认使用流式输出
        if prompt:
            # 记录第一个问题
            if st.session_state['first_question_in_session'] is None:
                st.session_state['first_question_in_session'] = prompt
            
            st.session_state['messages'].append({'role': 'human', 'content': prompt})
            chat_container.chat_message('human').write(prompt)

            # 使用流式输出
            message_placeholder = chat_container.chat_message("ai").empty()
            full_response = ""
            try:
                for chunk in get_chat_response_stream(
                    prompt=prompt,
                    memory=st.session_state["memory"],
                    openai_api_key=openai_api_key,
                    model_name=st.session_state["chat_model"],
                    temperature=st.session_state["temperature"],
                    top_p=st.session_state["top_p"],
                    presence_penalty=st.session_state["presence_penalty"],
                    max_tokens=st.session_state["max_tokens"],
                    system_prompt=st.session_state["system_prompt"]
                ):
                    if "response" in chunk:
                        full_response += chunk['response']
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                st.session_state['messages'].append({'role': 'ai', 'content': full_response})
            except Exception as e:
                st.error(f"❌ 回复失败：{e}")

    # ======================== 角色设定 Tab ========================
    with tab3:
        st.markdown("### 🎭 角色设定")
        
        # 角色设定选择器
        role_options = {
            "默认助手": "你是ChatGPT，一个由OpenAI训练的大语言模型，请简洁而专业地回答用户问题。",
            "编程助手": "你是一个专业的编程助手，擅长多种编程语言，能够提供代码示例、调试建议和最佳实践。请用简洁明了的方式回答编程相关问题。",
            "学习导师": "你是一个耐心的学习导师，擅长用通俗易懂的方式解释复杂概念，能够根据学习者的水平调整讲解深度。请用循序渐进的方式回答问题。",
            "创意写手": "你是一个富有创造力的写手，擅长创作故事、写作建议和文案策划。请用生动有趣的语言风格回答问题，并提供有创意的建议。",
            "自定义角色": "custom"
        }
        
        # 初始化自定义角色提示词和保存的角色列表
        if "custom_system_prompt" not in st.session_state:
            st.session_state["custom_system_prompt"] = "请输入你的自定义角色设定..."
        if "saved_custom_roles" not in st.session_state:
            st.session_state["saved_custom_roles"] = {}
        if "show_custom_role_modal" not in st.session_state:
            st.session_state["show_custom_role_modal"] = False
        if "current_custom_role_name" not in st.session_state:
            st.session_state["current_custom_role_name"] = "自定义角色"
        
        # 动态更新角色选项显示
        display_role_options = role_options.copy()
        if st.session_state.get("current_custom_role_name") and st.session_state.get("current_custom_role_name") != "自定义角色":
            display_role_options["自定义角色"] = f"自定义角色 ({st.session_state['current_custom_role_name']})"
        
        selected_role = st.selectbox(
            "🎭 选择角色设定",
            list(display_role_options.keys()),
            key="role_selector",
            format_func=lambda x: display_role_options.get(x, x) if x == "自定义角色" else x
        )
        
        # 如果选择自定义角色，显示设置界面
        if selected_role == "自定义角色":
            st.markdown("---")
            st.markdown("### 🎭 自定义角色设置")
            
            # 角色名称设置
            role_display_name = st.text_input(
                "🏷️ 角色名称",
                value=st.session_state["current_custom_role_name"],
                placeholder="给你的自定义角色起个名字",
                help="这个名称将显示在角色选择器中"
            )
            
            # 角色设定输入
            custom_prompt = st.text_area(
                "✍️ 角色设定",
                value=st.session_state["custom_system_prompt"],
                height=120,
                placeholder="例如：你是一个专业的心理咨询师，擅长倾听和提供情感支持。请用温和、理解的语气回答问题，并提供建设性的建议。",
                help="请详细描述你希望AI扮演的角色特征、专业领域和回答风格"
            )
            
            # 快速示例选择
            st.markdown("#### 💡 快速选择示例角色")
            example_roles = {
                "心理咨询师": "你是一个专业的心理咨询师，擅长倾听和提供情感支持。请用温和、理解的语气回答问题，并提供建设性的建议。",
                "旅行规划师": "你是一个经验丰富的旅行规划师，熟悉世界各地的旅游景点、交通、住宿和美食。请为用户提供详细的旅行建议和规划。",
                "健身教练": "你是一个专业的健身教练，了解各种运动形式、营养搭配和健康生活方式。请用激励性的语言提供健身建议。",
                "美食评论家": "你是一个资深的美食评论家，对各地美食文化有深入了解。请用生动的语言描述美食，并提供烹饪技巧和餐厅推荐。"
            }
            
            cols = st.columns(2)
            for i, (example_name, example_prompt) in enumerate(example_roles.items()):
                col = cols[i % 2]
                with col:
                    if st.button(f"📝 {example_name}", key=f"example_role_{i}", use_container_width=True):
                        st.session_state["custom_system_prompt"] = example_prompt
                        st.session_state["current_custom_role_name"] = example_name
                        st.rerun()
            
            # 已保存角色管理
            if st.session_state["saved_custom_roles"]:
                st.markdown("#### 📁 已保存的角色")
                saved_role_names = list(st.session_state["saved_custom_roles"].keys())
                
                col_select, col_load, col_delete = st.columns([2, 1, 1])
                with col_select:
                    selected_saved_role = st.selectbox(
                        "选择已保存的角色",
                        [""] + saved_role_names,
                        key="select_saved_role"
                    )
                with col_load:
                    if st.button("📂 加载", key="load_saved_role", use_container_width=True):
                        if selected_saved_role:
                            st.session_state["custom_system_prompt"] = st.session_state["saved_custom_roles"][selected_saved_role]
                            st.session_state["current_custom_role_name"] = selected_saved_role
                            st.success(f"✅ 已加载角色 '{selected_saved_role}'")
                            st.rerun()
                with col_delete:
                    if st.button("🗑️ 删除", key="delete_saved_role", use_container_width=True):
                        if selected_saved_role:
                            del st.session_state["saved_custom_roles"][selected_saved_role]
                            st.success(f"✅ 已删除角色 '{selected_saved_role}'")
                            st.rerun()
            
            # 操作按钮
            st.markdown("---")
            col_save, col_apply = st.columns(2)
            
            with col_save:
                save_name = st.text_input("💾 保存为", placeholder="输入保存名称", key="save_role_name")
                if st.button("💾 保存角色", key="save_custom_role", use_container_width=True):
                    if save_name and custom_prompt and custom_prompt != "请输入你的自定义角色设定...":
                        st.session_state["saved_custom_roles"][save_name] = custom_prompt
                        st.success(f"✅ 角色 '{save_name}' 已保存")
                    else:
                        st.warning("⚠️ 请输入保存名称和有效的角色设定")
            
            with col_apply:
                if st.button("✅ 应用设置", key="apply_custom_role", use_container_width=True, type="primary"):
                    if custom_prompt and custom_prompt != "请输入你的自定义角色设定...":
                        st.session_state["custom_system_prompt"] = custom_prompt
                        st.session_state["system_prompt"] = custom_prompt
                        if role_display_name:
                            st.session_state["current_custom_role_name"] = role_display_name
                        st.success("✅ 自定义角色设置已应用")
                        st.rerun()
                    else:
                        st.warning("⚠️ 请输入有效的角色设定")
            
            # 应用自定义角色设定
            st.session_state["system_prompt"] = st.session_state["custom_system_prompt"]
        else:
            # 使用预设角色
            if st.session_state["system_prompt"] != role_options[selected_role]:
                st.session_state["system_prompt"] = role_options[selected_role]
                st.rerun()
            
            # 显示当前角色的设定信息
            st.markdown("---")
            st.markdown("### 📋 当前角色信息")
            st.info(f"**角色：** {selected_role}")
            st.text_area("角色设定内容", value=role_options[selected_role], height=100, disabled=True)

    # ======================== 历史消息 Tab ========================
    with tab2:
        if not st.session_state['history_list']:
            st.info("暂无历史对话记录")
            st.markdown("💡 **提示**: 在当前聊天中点击「新建对话」可以保存当前对话到历史记录")
        else:
            for idx, record in enumerate(st.session_state['history_list']):
                with st.container():
                    col1, col2 = st.columns([0.9, 0.1])
                    with col1:
                        if st.button(record['name'], key=f"load_{idx}", use_container_width=True):
                            st.session_state['messages'] = record['messages']
                            st.session_state['memory'] = ConversationBufferMemory(return_messages=True)
                            st.session_state['active_history'] = idx
                            # 重建memory
                            for msg in record['messages']:
                                if msg['role'] == 'human':
                                    st.session_state['memory'].save_context(
                                        {"input": msg['content']}, 
                                        {"output": ""}
                                    )
                                elif msg['role'] == 'ai' and msg['content'] != '你好，我是你的AI助手，有什么可以帮你的吗？':
                                    # 获取对应的human消息
                                    human_msgs = [m for m in record['messages'] if m['role'] == 'human']
                                    if human_msgs:
                                        last_human = human_msgs[-1]['content']
                                        st.session_state['memory'].save_context(
                                            {"input": last_human}, 
                                            {"output": msg['content']}
                                        )
                            st.rerun()
                    with col2:
                        with st.expander("..."):
                            if st.button("删除", key=f"delete_{idx}"):
                                st.session_state['history_list'].pop(idx)
                                if st.session_state['active_history'] == idx:
                                    st.session_state['messages'] = [{'role': 'ai', 'content': '你好，我是你的AI助手，有什么可以帮你的吗？'}]
                                    st.session_state['memory'] = ConversationBufferMemory(return_messages=True)
                                    st.session_state['active_history'] = None
                                    st.session_state['first_question_in_session'] = None
                                st.rerun()

# 智能文档问答
def show_pdf_qa():
    st.markdown('<div class="main-title">📄 智能文档问答工具</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">上传文档，智能问答，快速获取信息</div>', unsafe_allow_html=True)
    
    # 使用全局API密钥
    openai_key = openai_api_key
    
    # 显示API密钥状态
    if not openai_key:
        st.warning("⚠️ 请在左侧侧栏输入OpenAI API密钥以使用智能问答功能")
        return
    
    # 使用一个列表缓存历史记录
    if 'history_cache' not in st.session_state:
        st.session_state['history_cache'] = []

    # ====== 文件上传和操作区域 ======
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 📁 上传文档")
        upload_files = st.file_uploader(
            "支持: PDF, TXT, CSV, DOCX",
            type=["pdf", "txt", "csv", "docx"],
            accept_multiple_files=True,
            help="可以同时上传多个文档进行问答"
        )
        
        # 当文档上传后，自动生成基于文档内容的建议问题
        if upload_files and 'document_suggestions_generated' not in st.session_state:
            with st.spinner("📄 正在分析文档内容，生成建议问题..."):
                document_suggestions = gen_followup_questions(upload_files, openai_key)
                st.session_state['document_suggestions'] = document_suggestions
                st.session_state['document_suggestions_generated'] = True
        elif not upload_files and 'document_suggestions_generated' in st.session_state:
            # 清理文档相关的建议问题
            if 'document_suggestions' in st.session_state:
                del st.session_state['document_suggestions']
            del st.session_state['document_suggestions_generated']
    
    with col2:
        st.markdown("### 🗨️ 对话管理")
        # 新建对话按钮
        if st.button("🗨️ 新建对话", use_container_width=True):
            # 保存当前对话到历史记录（如果有对话内容）
            if 'memory' in st.session_state and st.session_state['memory'].buffer:
                session_data = {
                    'memory': st.session_state['memory'],
                    'chat_history': st.session_state.get('chat_history', []),
                    'followup_questions': st.session_state.get('followup_questions', []),
                    'last_question': st.session_state.get('last_question', "")
                }
                st.session_state['history_cache'].append(session_data)
            
            # 创建新对话
            st.session_state['memory'] = ConversationBufferMemory(
                return_messages=True,
                memory_key='chat_history',
                output_key='answer'
            )
            st.session_state['chat_history'] = []
            st.session_state['followup_questions'] = []
            st.session_state['last_question'] = ""
            st.session_state['user_input'] = ""
            st.success("新对话已开始！")

    with col3:
        st.markdown("### 📚 历史对话")
        if st.session_state['history_cache']:
            # 使用下拉框选择历史记录（更节省空间）
            history_idx = st.selectbox(
                "选择历史对话",
                list(range(1, len(st.session_state['history_cache']) + 1)),
                key="history_select"
            )
            if st.button(f"📂 加载对话 {history_idx}", use_container_width=True):
                history = st.session_state['history_cache'][history_idx - 1]
                st.session_state['memory'] = history['memory']
                st.session_state['chat_history'] = history['chat_history']
                st.session_state['followup_questions'] = history['followup_questions']
                st.session_state['last_question'] = history['last_question']
                st.session_state['user_input'] = ""
                st.success(f"已加载对话 {history_idx}")
        else:
            st.info("暂无历史对话")
    
    # 分隔线
    st.markdown("---")

    # ====== 会话状态初始化 ======
    if 'memory' not in st.session_state:
        st.session_state['memory'] = ConversationBufferMemory(
            return_messages=True,
            memory_key='chat_history',
            output_key='answer'
        )
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []
    if 'followup_questions' not in st.session_state:
        st.session_state['followup_questions'] = []
    if 'last_question' not in st.session_state:
        st.session_state['last_question'] = ""
    if 'user_input' not in st.session_state:
        st.session_state['user_input'] = ""

    # ====== 主区域样式 ======
    st.markdown(
        """
        <style>
        .fixed-bottom-bar {
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            background: #fff;
            padding: 1rem 0.5rem 0.5rem 1rem;
            box-shadow: 0 -2px 8px rgba(0,0,0,0.04);
            z-index: 100;
        }
        .followup-btn {
            margin-right: 8px;
            margin-bottom: 8px;
            display: inline-block;
            font-size: 14px;
            color: #007bff;
            background-color: #fff;
            border: 1px solid #007bff;
            border-radius: 4px;
            padding: 5px 10px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .followup-btn:hover {
            background-color: #007bff;
            color: white;
        }
        .chat-container {
            padding-bottom: 200px; /* 为底部固定区域留出空间 */
            padding-top: 20px; /* 增加顶部间距 */
        }
        .message-box {
            margin-top: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("学而不思则罔，思而不学则殆")

    # ====== 聊天历史展示 ======
    chat_container = st.container()
    chat_container.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # 使用 st.chat_message 重构聊天界面
    chat_history = st.session_state['memory'].load_memory_variables({}).get('chat_history', [])
    for message in chat_history:
        if isinstance(message, HumanMessage):
            with chat_container:
                st.chat_message("user").markdown(message.content)
        elif isinstance(message, AIMessage):
            with chat_container:
                ai = message.content
                st.chat_message("assistant").markdown(ai)

                # 展示来源 (整合到AI消息中)
                if hasattr(message, 'source_documents') and message.source_documents:
                    with st.expander('回答来源'):
                        sources = {}
                        for doc in message.source_documents:
                            source = doc.metadata.get('source', '未知来源')
                            if source not in sources:
                                sources[source] = []
                            sources[source].append(doc.page_content)
                        for source, contents in sources.items():
                            if "不知道" in ai:
                                st.markdown(f"找不到来源")
                                continue
                            st.markdown(f"**来源: {source}**")
                            st.markdown(f"片段 : {contents[0]}")

    chat_container.markdown('</div>', unsafe_allow_html=True)

    # ====== 固定底部输入区 ======
    st.markdown('<div class="fixed-bottom-bar">', unsafe_allow_html=True)

    # 建议问题按钮区
    selected_question = None
    
    # 优先显示基于文档的建议问题
    document_suggestions = st.session_state.get('document_suggestions', [])
    followup_suggestions = st.session_state.get('followup_questions', [])
    
    if document_suggestions and not followup_suggestions:
        st.markdown("**📋 基于文档内容的建议问题：**")
        cols = st.columns(3)
        for idx, q in enumerate(document_suggestions[:3]):
            if cols[idx].button(q, key=f"doc_suggest_{idx}", help="点击直接提问", use_container_width=True):
                selected_question = q
                break
    elif followup_suggestions:
        st.markdown("**💡 后续问题建议：**")
        cols = st.columns(3)
        for idx, q in enumerate(followup_suggestions[:3]):
            if cols[idx].button(q, key=f"followup_{idx}", help="点击直接提问", use_container_width=True):
                selected_question = q
                break
    elif document_suggestions:
        # 如果已经有对话，但还想显示文档建议问题
        with st.expander("📋 查看基于文档内容的建议问题"):
            doc_cols = st.columns(3)
            for idx, q in enumerate(document_suggestions[:3]):
                if doc_cols[idx].button(q, key=f"doc_suggest_exp_{idx}", help="点击直接提问", use_container_width=True):
                    selected_question = q
                    break

    # 用st.chat_input美化输入框
    input_placeholder = "请输入您的问题..." if upload_files else "请先上传文档，然后输入问题"
    user_input = st.chat_input(
        input_placeholder,
        key="user_input_box",
        disabled=not upload_files
    )
    
    # 如果用户点击了后续问题按钮，直接使用该问题
    if selected_question:
        user_input = selected_question

    st.markdown('</div>', unsafe_allow_html=True)

    # ====== 处理提问 ======
    if upload_files and user_input:
        if not openai_key:
            st.error('❌ API密钥未设置，请在左侧侧栏输入OpenAI API密钥')
            st.stop()
        
        question = user_input
        with st.spinner("AI正在思考中..."):
            # 显示处理状态
            status_placeholder = st.empty()
            try:
                status_placeholder.info("🔄 正在加载嵌入模型...")
                response = qa_agent(
                    openai_api_key=openai_key,
                    memory=st.session_state['memory'],
                    uploaded_files=upload_files,
                    question=question
                )
                status_placeholder.empty()
            except Exception as e:
                status_placeholder.error(f"❌ 处理失败: {str(e)}")
                st.stop()
        # 更新状态
        st.session_state['last_question'] = question

        # 生成基于当前问答的后续问题建议
        st.session_state['followup_questions'] = gen_followup_questions_from_qa(
            question=question,
            answer=response['answer'],
            openai_api_key=openai_key
        )

        st.session_state["user_input"] = ""

        # 将来源信息添加到AI消息中
        if response.get('source_documents'):
            # 找到最新的AI消息并添加来源信息
            messages = st.session_state['memory'].load_memory_variables({}).get('chat_history', [])
            if messages and isinstance(messages[-1], AIMessage):
                messages[-1].source_documents = response['source_documents']

        st.rerun()

# 检查PDF智能问答

# 根据选择的页面显示相应内容
if st.session_state.selected_page == "首页":
    show_home()
elif st.session_state.selected_page == "视频脚本":
    show_video_script()
elif st.session_state.selected_page == "小红书文案":
    show_xiaohongshu()
elif st.session_state.selected_page == "ChatGPT克隆":
    show_chatgpt_clone()
elif st.session_state.selected_page == "智能文档问答":
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