import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from utils import  qa_agent, gen_followup_questions

# 使用一个列表缓存历史记录
if 'history_cache' not in st.session_state:
    st.session_state['history_cache'] = []

st.set_page_config(page_title="多文件智能问答助手", layout="wide")

# ====== 顶部配置区域 ======
st.markdown("### 🤖 智能问答助手配置区")
col1, col2 = st.columns([2, 1])  # 左侧2份宽度，右侧1份宽度

with col1:
    openai_key = st.text_input('请输入OpenAI API密钥', type='password')
    st.markdown('[获取OpenAI API秘钥](https://openai-hk.com/v3/ai/key)')

with col2:
    st.markdown("### 支持的文件类型")
    st.info("PDF, TXT, CSV, DOCX")
    upload_files = st.file_uploader(
        "上传文件",
        type=["pdf", "txt", "csv", "docx"],
        accept_multiple_files=True
    )

# ====== 操作按钮区域 ======
st.markdown("---")  # 分隔线
col1, col2 = st.columns([1, 1])

with col1:
    # 新建对话按钮
    if st.button("新建对话"):
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

        # 新会话开始后保存到历史记录
        session_data = {
            'memory': st.session_state['memory'],
            'chat_history': st.session_state['chat_history'],
            'followup_questions': st.session_state['followup_questions'],
            'last_question': st.session_state['last_question']
        }
        st.session_state['history_cache'].append(session_data)

with col2:
    # 历史记录区域
    st.markdown("### 历史记录")
    if st.session_state['history_cache']:
        # 使用下拉框选择历史记录（更节省空间）
        history_idx = st.selectbox(
            "选择历史对话",
            list(range(1, len(st.session_state['history_cache']) + 1))
        )
        if st.button(f"加载 历史对话 {history_idx}"):
            history = st.session_state['history_cache'][history_idx - 1]
            st.session_state['memory'] = history['memory']
            st.session_state['chat_history'] = history['chat_history']
            st.session_state['followup_questions'] = history['followup_questions']
            st.session_state['last_question'] = history['last_question']
            st.session_state['user_input'] = ""
            st.success(f"已加载 历史对话 {history_idx}")
    else:
        st.info("没有历史记录。")

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

# 预测问题按钮区
cols = st.columns(3)
for idx, q in enumerate(st.session_state['followup_questions']):
    if cols[idx].button(q, key=f"followup_{idx}", help="点击填入输入框"):
        st.session_state['user_input'] = q

# 用st.chat_input美化输入框
user_input = st.chat_input(
    "请输入您的问题",
    key="user_input_box",
    disabled=not upload_files
)

st.markdown('</div>', unsafe_allow_html=True)

# ====== 处理提问 ======
if upload_files and user_input:
    if not openai_key:
        st.info('请输入你的OpenAI API密钥')
        st.stop()
    question = user_input
    with st.spinner("AI正在思考中..."):
        response = qa_agent(
            openai_api_key=openai_key,
            memory=st.session_state['memory'],
            uploaded_files=upload_files,
            question=question
        )
    # 不再手动追加chat_history，交由memory维护
    st.session_state['last_question'] = question

    st.session_state['followup_questions'] = gen_followup_questions(
        question=question,
        answer=response['answer'],
        openai_api_key=openai_key
    )

    st.session_state["user_input"] = ""

    # 将来源信息添加到AI消息中
    if response['source_documents']:
        # 找到最新的AI消息并添加来源信息
        messages = st.session_state['memory'].load_memory_variables({}).get('chat_history', [])
        if messages and isinstance(messages[-1], AIMessage):
            messages[-1].source_documents = response['source_documents']

    st.rerun()