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
    num_titles = st.slider("生成标题数量", min_value=2, max_value=10, value=st.session_state.get("num_titles", 5), step=1)
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
            st.markdown(f"**{i+1}. {result.titles[i]}**")

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

    # 新增：显示原始AI��应
    with col2:
        with st.expander("查看AI原始响应（调试用）"):
            st.code(raw_response)
