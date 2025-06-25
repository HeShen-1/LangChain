import streamlit as st
from 项目3克隆ChatGPT.utils import generate_xiaohongshu, get_baidu_image_urls, get_all_baidu_image_urls  # 新增导入

STYLES = ["幽默调侃", "专业干货", "亲切治愈", "活泼种草"]
st.set_page_config(page_title="小红书爆款文案生成器", layout="wide")

# 自定义CSS美化
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
    }
    .stDownloadButton>button {
        background: #e94f4a;
        color: white;
        border-radius: 2em;
        font-weight: bold;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">小红书爆款文案生成器 <span style="font-size:1.5rem;">🌈</span></div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">一键生成高质量小红书标题与正文，支持多种风格，自动配图，助你轻松打造爆款内容！</div>', unsafe_allow_html=True)

# 初始化session_state用于缓存生成结果
if "result" not in st.session_state:
    st.session_state["result"] = None
if "raw_response" not in st.session_state:
    st.session_state["raw_response"] = ""
if "style" not in st.session_state:
    st.session_state["style"] = ""
if "num_titles" not in st.session_state:
    st.session_state["num_titles"] = 5
if "num_images" not in st.session_state:
    st.session_state["num_images"] = 3
if "selected_image_idx" not in st.session_state:
    st.session_state["selected_image_idx"] = 0
if "image_urls" not in st.session_state:
    st.session_state["image_urls"] = []
if "all_image_urls" not in st.session_state:
    st.session_state["all_image_urls"] = []
if "final_selected_image" not in st.session_state:
    st.session_state["final_selected_image"] = None
# 新增历史记录与收藏
if "history" not in st.session_state:
    st.session_state["history"] = []
if "favorites" not in st.session_state:
    st.session_state["favorites"] = []

with st.sidebar:
    st.subheader("参数设置")
    api_key = st.text_input('请输入你的DeepSeek API Key', type='password', placeholder="sk-...")
    theme = st.text_input('请输入创作主题', placeholder="如：夏日防晒好物推荐")
    style = st.selectbox(
        '选择文案风格',
        STYLES,
        help="不同风格将影响标题和正文的语气与表达方式"
    )
    num_titles = st.slider("生成标题数量", min_value=2, max_value=10, value=st.session_state.get("num_titles", 5), step=1)
    num_images = st.slider("配图数量", min_value=1, max_value=8, value=st.session_state.get("num_images", 3), step=1)

submit = st.button('🚀 开始生成', type="primary", use_container_width=True)

# 输入验证
if submit and not api_key:
    st.warning('请输入DeepSeek API密钥', icon="⚠️")
    st.stop()
if submit and not theme:
    st.warning('请输入创作主题', icon="⚠️")
    st.stop()

if submit:
    with st.spinner('AI正在创作中，请稍候... 🧠✨'):
        try:
            result, raw_response = generate_xiaohongshu(theme, api_key, style, num_titles=num_titles)
            st.session_state["result"] = result
            st.session_state["raw_response"] = raw_response
            st.session_state["style"] = style
            st.session_state["num_titles"] = num_titles
            # 获取全部图片用于最终选择
            all_image_urls = get_all_baidu_image_urls(theme, max_images=30)
            st.session_state["all_image_urls"] = all_image_urls
            # 随机选取N张用于本轮展示
            image_urls = []
            if all_image_urls:
                import random
                image_urls = random.sample(all_image_urls, min(num_images, len(all_image_urls)))
            st.session_state["image_urls"] = image_urls
            st.session_state["selected_image_idx"] = 0
            st.session_state["final_selected_image"] = None
            # 保存到历史记录
            st.session_state["history"].insert(0, {
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
            st.session_state["history"] = st.session_state["history"][:30]
        except Exception as e:
            st.error(f"生成失败: {str(e)}", icon="🚨")
            st.code(str(e))
            st.stop()

result = st.session_state.get("result", None)
raw_response = st.session_state.get("raw_response", "")
style = st.session_state.get("style", style)
num_titles = st.session_state.get("num_titles", num_titles)
image_urls = st.session_state.get("image_urls", [])
all_image_urls = st.session_state.get("all_image_urls", [])
selected_image_idx = st.session_state.get("selected_image_idx", 0)
final_selected_image = st.session_state.get("final_selected_image", None)
num_images = st.session_state.get("num_images", 3)

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
                st.image(url, use_container_width=True)
                if st.button("设为最终配图", key=f"final_sel_{i}"):
                    st.session_state["final_selected_image"] = url
        if final_selected_image:
            st.success("已选择最终配图！")
            st.image(final_selected_image, use_container_width=True, caption="最终配图")
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
        if fav_item not in st.session_state["favorites"]:
            st.session_state["favorites"].insert(0, fav_item)
            st.success("已收藏到收藏夹！")
        else:
            st.info("该文案已在收藏夹中。")

# 历史记录与收藏管理区
with st.sidebar:
    st.markdown("### 📜 历史记录")
    if st.session_state["history"]:
        for idx, item in enumerate(st.session_state["history"][:5]):
            with st.expander(f"{item['theme']} | {item['style']} | {item['titles'][0][:12]}..."):
                st.markdown(f"**标题示例：** {item['titles'][0]}")
                st.markdown(f"**正文预览：** {item['content'][:40]}...")
                if st.button("恢复到主界面", key=f"restore_{idx}"):
                    st.session_state["result"] = type(result)(titles=item["titles"], content=item["content"])
                    st.session_state["raw_response"] = item["raw_response"]
                    st.session_state["style"] = item["style"]
                    st.session_state["num_titles"] = item["num_titles"]
                    st.session_state["num_images"] = item.get("num_images", 3)
                    st.session_state["image_urls"] = item.get("image_urls", [])
                    st.session_state["all_image_urls"] = item.get("all_image_urls", [])
                    st.session_state["final_selected_image"] = item.get("final_selected_image", None)
                    st.session_state["selected_image_idx"] = 0
                if st.button("收藏此条", key=f"fav_hist_{idx}"):
                    if item not in st.session_state["favorites"]:
                        st.session_state["favorites"].insert(0, item)
                        st.success("已收藏到收藏夹！")
    else:
        st.info("暂无历史记录")

    st.markdown("### ⭐ 我的收藏")
    if st.session_state["favorites"]:
        for idx, item in enumerate(st.session_state["favorites"][:5]):
            with st.expander(f"{item['theme']} | {item['style']} | {item['titles'][0][:12]}..."):
                st.markdown(f"**标题示例：** {item['titles'][0]}")
                st.markdown(f"**正文预览：** {item['content'][:40]}...")
                if st.button("恢复到主界面 ", key=f"restore_fav_{idx}"):
                    st.session_state["result"] = type(result)(titles=item["titles"], content=item["content"])
                    st.session_state["raw_response"] = item["raw_response"]
                    st.session_state["style"] = item["style"]
                    st.session_state["num_titles"] = item["num_titles"]
                    st.session_state["num_images"] = item.get("num_images", 3)
                    st.session_state["image_urls"] = item.get("image_urls", [])
                    st.session_state["all_image_urls"] = item.get("all_image_urls", [])
                    st.session_state["final_selected_image"] = item.get("final_selected_image", None)
                    st.session_state["selected_image_idx"] = 0
                if st.button("移除收藏", key=f"remove_fav_{idx}"):
                    st.session_state["favorites"].pop(idx)
                    st.experimental_rerun()
    else:
        st.info("暂无收藏内容")
