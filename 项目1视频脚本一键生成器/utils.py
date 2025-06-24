from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.utilities import WikipediaAPIWrapper
import json
import os
from datetime import datetime
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


def generate_script(subject, video_length, creativity, api_key, 
                   style="轻松幽默", video_type="讲解类", 
                   include_shots=False, include_bgm=False, 
                   include_hotspot=False, script_structure="开头-中间-结尾",
                   include_tags=False, include_description=False):
    """
    生成视频标题和脚本的函数
    参数:
        subject: 视频主题
        video_length: 视频时长（分钟）
        creativity: 创造力参数（控制模型输出的随机性）
        api_key: OpenAI API密钥
        style: 视频风格（搞笑、科普、情感、励志、悬疑等）
        video_type: 视频类型（讲解类、剧情类、Vlog类、测评类等）
        include_shots: 是否生成分镜头脚本
        include_bgm: 是否包含BGM/音效建议
        include_hotspot: 是否补充热点/百科信息
        script_structure: 脚本结构（开头-中间-结尾、引入-冲突-高潮-结局等）
        include_tags: 是否生成标签
        include_description: 是否生成简介
    返回：
        包含视频标题、脚本、分镜头、BGM建议的字典
    """
    
    # 脚本结构映射
    structure_prompts = {
        "开头-中间-结尾": "按照【开头、中间、结尾】分隔",
        "引入-冲突-高潮-结局": "按照【引入、冲突、高潮、结局】分隔",
        "问题-分析-解决": "按照【问题提出、深入分析、解决方案】分隔",
        "故事-道理-启发": "按照【故事叙述、道理阐述、启发总结】分隔",
        "现象-原因-对策": "按照【现象描述、原因分析、对策建议】分隔",
        "吐槽-分析-解决": "按照【吐槽、分析、解决】分隔"
    }
    
    # 语言映射
    lang_prompts = {
        "title_prompt": "请为{subject}这个主题的视频想一个吸引人的标题",
        "script_base": "你是一位短视频频道的博主。",
        "style_desc": f"请用{style}风格",
        "type_desc": f"生成一份{video_type}类型的视频脚本",
        "requirements": [
            "1. 开头抓住眼球，中间提供干货内容，结尾有惊喜",
            f"2. 脚本格式{structure_prompts.get(script_structure, '按照【开头、中间、结尾】分隔')}",
            f"3. 体现{style}风格特点",
            f"4. 符合{video_type}类型特征",
            f"5. 内容要适合{video_length}分钟的时长",
            "6. 表达方式要吸引目标受众"
        ],
        "shots": "请同时提供分镜头建议：\n- 镜头1：[场景描述]\n- 镜头2：[场景描述]\n- 镜头3：[场景描述]",
        "bgm": "请提供BGM和音效建议：\n- 开头BGM：[音乐类型和情绪]\n- 中间音效：[适合的音效]\n- 结尾BGM：[音乐类型和情绪]\n- 画面切换：[转场建议]",
        "tags": "请为该视频生成5-8个适合的标签，用逗号分隔，标签要简短、准确、容易搜索",
        "description": "请为该视频写一段50-100字的简介，要吸引观众点击观看"
    }
    
    # 1. 获取热点/百科信息
    background_info = ""
    if include_hotspot:
        try:
            search = WikipediaAPIWrapper(lang='zh')
            background_info = search.run(subject)
            background_info = f"\n背景信息参考：{background_info[:500]}..."
        except:
            background_info = ""

    # 2. 生成标题
    title_template = ChatPromptTemplate.from_messages([
        ('human', lang_prompts["title_prompt"])
    ])
    
    # 3. 构建脚本生成模板
    requirements = "\n".join(lang_prompts["requirements"])
    script_prompt = f"""
        {lang_prompts["script_base"]} {lang_prompts["style_desc"]}，{lang_prompts["type_desc"]}。
        
        视频标题：{{title}}
        视频时长：{{duration}}分钟
        视频风格：{style}
        视频类型：{video_type}
        脚本结构：{script_structure}
        {background_info}
        
        要求：
        {requirements}
    """
    
    if include_shots:
        script_prompt += f"\n\n{lang_prompts['shots']}"
    
    if include_bgm:
        script_prompt += f"\n\n{lang_prompts['bgm']}"
        
    if include_tags:
        script_prompt += f"\n\n{lang_prompts['tags']}"
        
    if include_description:
        script_prompt += f"\n\n{lang_prompts['description']}"

    script_template = ChatPromptTemplate.from_messages([
        ('human', script_prompt)
    ])

    # 4. 初始化模型
    model = ChatOpenAI(
        base_url='https://twapi.openai-hk.com/v1/',
        openai_api_key=api_key,
        temperature=creativity
    )
    
    # 5. 生成内容
    title_chain = title_template | model
    script_chain = script_template | model

    title = title_chain.invoke({'subject': subject}).content
    script_content = script_chain.invoke({
        'title': title, 
        'duration': video_length
    }).content

    # 6. 解析和组织输出
    result = {
        'title': title,
        'script': script_content,
        'style': style,
        'type': video_type,
        'structure': script_structure,
        'duration': video_length,
        'subject': subject,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 如果包含分镜头，尝试解析
    if include_shots:
        result['shots'] = extract_shots_from_script(script_content)
    
    # 如果包含BGM建议，尝试解析
    if include_bgm:
        result['bgm_suggestions'] = extract_bgm_from_script(script_content)
        
    # 如果包含标签，尝试解析
    if include_tags:
        result['tags'] = extract_tags_from_script(script_content)
        
    # 如果包含简介，尝试解析
    if include_description:
        result['description'] = extract_description_from_script(script_content)
    
    return result


def extract_shots_from_script(script_content):
    shots = []
    lines = script_content.split('\n')
    for line in lines:
        if '镜头' in line or 'Shot' in line or '场景' in line:
            shots.append(line.strip())
    return shots if shots else ["未检测到具体分镜头信息"]


def extract_bgm_from_script(script_content):
    bgm_info = []
    lines = script_content.split('\n')
    for line in lines:
        if any(keyword in line for keyword in ['BGM', '音效', '背景音乐', '音乐', '转场']):
            bgm_info.append(line.strip())
    return bgm_info if bgm_info else ["未检测到具体BGM建议"]


def extract_tags_from_script(script_content):
    """从脚本中提取标签"""
    tags = []
    lines = script_content.split('\n')
    for line in lines:
        if '标签' in line or 'tags' in line.lower() or '#' in line:
            # 提取标签内容
            tag_content = line.replace('标签：', '').replace('标签:', '').replace('#', '').strip()
            if tag_content:
                tags.extend([tag.strip() for tag in tag_content.split(',') if tag.strip()])
    return tags if tags else ["AI", "科技", "教程", "分享", "干货"]


def extract_description_from_script(script_content):
    """从脚本中提取简介，优先找简介/描述行，否则找50-200字段落，否则取开头100字"""
    lines = script_content.split('\n')
    # 1. 优先找包含"简介"或"描述"的行
    for line in lines:
        if '简介' in line or '描述' in line or 'description' in line.lower():
            desc = line.replace('简介：', '').replace('简介:', '').replace('描述：', '').replace('描述:', '').strip()
            if 20 < len(desc) < 200:
                return desc
    # 2. 找50-200字的段落
    for line in lines:
        l = line.strip()
        if 50 < len(l) < 200:
            return l
    # 3. 取脚本开头100字
    script_lines = [line.strip() for line in lines if line.strip()]
    if script_lines:
        return script_lines[0][:100] + "..." if len(script_lines[0]) > 100 else script_lines[0]
    return "精彩视频内容，值得观看！"


def get_style_options():
    return ["轻松幽默", "科普教育", "情感温馨", "励志激昂", "悬疑神秘", "搞笑娱乐", "专业严谨", "文艺清新", "热血激情", "治愈温暖", "尖酸刻薄"]


def get_type_options():
    return ["讲解类", "剧情类", "Vlog类", "测评类", "教程类", "访谈类", "纪录类", "娱乐类", "开箱类", "体验类", "吐槽类"]


def get_structure_options():
    """获取可选的脚本结构"""
    return ["开头-中间-结尾", "引入-冲突-高潮-结局", "问题-分析-解决", "故事-道理-启发", "现象-原因-对策", "吐槽-分析-解决"]


def save_script_history(result):
    """保存脚本到历史记录"""
    history_dir = "script_history"
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)
    
    filename = f"{history_dir}/script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return filename


def load_script_history():
    """加载历史脚本记录"""
    history_dir = "script_history"
    if not os.path.exists(history_dir):
        return []
    
    history_files = []
    for filename in os.listdir(history_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(history_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['filename'] = filename
                    history_files.append(data)
            except:
                continue
    
    # 按时间排序，最新的在前
    history_files.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return history_files


def export_to_word(result, filepath):
    """导出脚本为Word文档"""
    try:
        doc = Document()
        
        # 标题
        title = doc.add_heading(result['title'], 0)
        
        # 基本信息
        info_table = doc.add_table(rows=4, cols=2)
        info_table.style = 'Table Grid'
        
        info_data = [
            ['视频风格', result['style']],
            ['视频类型', result['type']],
            ['脚本结构', result['structure']],
            ['视频时长', f"{result['duration']}分钟"]
        ]
        
        for i, (key, value) in enumerate(info_data):
            info_table.cell(i, 0).text = key
            info_table.cell(i, 1).text = value
        
        # 脚本内容
        doc.add_heading('脚本内容', level=1)
        doc.add_paragraph(result['script'])
        
        # 其他内容
        if 'shots' in result:
            doc.add_heading('分镜头建议', level=1)
            for i, shot in enumerate(result['shots'], 1):
                doc.add_paragraph(f"{i}. {shot}")
        
        if 'bgm_suggestions' in result:
            doc.add_heading('BGM音效建议', level=1)
            for bgm in result['bgm_suggestions']:
                doc.add_paragraph(f"• {bgm}")
                
        if 'tags' in result:
            doc.add_heading('标签', level=1)
            doc.add_paragraph(', '.join(result['tags']))
            
        if 'description' in result:
            doc.add_heading('简介', level=1)
            doc.add_paragraph(result['description'])
        
        doc.save(filepath)
        return True
    except Exception as e:
        print(f"导出Word失败: {e}")
        return False


def export_to_txt(result, filepath):
    """导出脚本为TXT文件"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"标题: {result['title']}\n")
            f.write(f"风格: {result['style']}\n")
            f.write(f"类型: {result['type']}\n")
            f.write(f"结构: {result['structure']}\n")
            f.write(f"时长: {result['duration']}分钟\n")
            f.write(f"生成时间: {result['timestamp']}\n")
            f.write("\n" + "="*50 + "\n")
            f.write("脚本内容:\n")
            f.write(result['script'])
            
            if 'shots' in result:
                f.write("\n\n分镜头建议:\n")
                for i, shot in enumerate(result['shots'], 1):
                    f.write(f"{i}. {shot}\n")
            
            if 'bgm_suggestions' in result:
                f.write("\nBGM音效建议:\n")
                for bgm in result['bgm_suggestions']:
                    f.write(f"• {bgm}\n")
                    
            if 'tags' in result:
                f.write(f"\n标签: {', '.join(result['tags'])}\n")
                
            if 'description' in result:
                f.write(f"\n简介: {result['description']}\n")
        
        return True
    except Exception as e:
        print(f"导出TXT失败: {e}")
        return False


# 兼容原有接口的包装函数
def generate_script_simple(subject, video_length, creativity, api_key):
    result = generate_script(subject, video_length, creativity, api_key)
    return result['title'], result['script']


def test_generate_script():
    pass


