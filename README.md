# AI工具集合 - 基于LangChain的多功能AI应用

本项目是一个基于 Streamlit + LangChain 的多功能 AI 工具集合，集成了视频脚本生成、小红书爆款文案、ChatGPT对话克隆、多文件智能PDF问答等实用AI能力，支持多API接入和多种文档类型。

---

## ✨ 功能模块

### 🎬 一键生成视频脚本

- 基于 OpenAI GPT 智能生成各类视频脚本
- 支持多种风格、类型、结构
- 可选分镜头、BGM、标签、简介等高级功能
- 支持历史记录、收藏、Word/PDF 导出

### 📝 小红书爆款文案生成器

- 支持多风格（幽默调侃、专业干货、亲切治愈、活泼种草）
- 基于 DeepSeek API（需单独API Key）
- 自动生成多个标题、正文、配图
- 支持历史记录、收藏、Markdown 导出

### 💬 ChatGPT克隆

- 多轮对话，支持上下文记忆
- 支持流式/非流式输出
- 可切换模型（gpt-3.5-turbo/gpt-4）及参数
- 聊天历史管理、角色设定

### 📄 PDF多文件智能问答

- 支持 PDF、TXT、CSV、DOCX 多文件上传
- 基于向量检索（FAISS+HuggingFace Embeddings）
- 支持多轮对话、上下文记忆、历史切换
- 自动生成追问建议，答案可溯源

---

## 👥 制作团队

**傅彬彬，董政，聂群松，何星伽**

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- OpenAI API 密钥（必需，支持 twapi/openai-hk 代理）
- DeepSeek API 密钥（用于小红书文案）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行应用

```bash
streamlit run app.py
```

### 4. 访问网站

浏览器打开： [http://localhost:8501](http://localhost:8501)

---

## 🔧 配置说明

### API密钥设置

- **OpenAI API Key**：在侧栏输入，支持官方和 twapi/openai-hk 代理
- **DeepSeek API Key**：用于小红书文案生成，需单独在小红书页面输入

### 功能入口

- 侧栏切换不同功能页面
- 每个功能均有详细参数设置和结果导出/收藏/历史管理

---

## 📁 项目结构

```text
LangChain/
├── app.py                        # 主应用入口
├── requirements.txt              # 依赖包列表
├── README.md                     # 项目说明
├── script_history/               # 视频脚本历史记录
├── 项目1视频脚本一键生成器/
│   └── utils.py                  # 视频脚本生成核心逻辑
├── 项目2小红书爆款文案生成器/
│   ├── main.py
│   ├── utils.py                  # 小红书文案生成与配图
│   ├── prompt_template.py        # 风格提示词模板
│   └── readme.md
├── 项目3克隆ChatGPT/
│   └── utils.py                  # ChatGPT对话核心逻辑
├── 项目4智能PDF问答工具/
│   ├── utils.py                  # 多文件问答与向量检索
│   └── main.py
└── temp.pdf                      # 示例PDF
```

---

## 🛠️ 技术栈

- **前端**：Streamlit
- **AI框架**：LangChain
- **大模型**：OpenAI GPT-3.5/4、DeepSeek Chat
- **向量数据库**：FAISS
- **嵌入模型**：HuggingFace Embeddings
- **文档处理**：PyPDF, python-docx, reportlab
- **数据验证**：Pydantic

---

## 📝 使用说明

1. **首次使用**：在侧栏输入 OpenAI API 密钥（小红书需单独输入 DeepSeek Key）
2. **选择功能**：点击侧栏按钮切换不同工具
3. **输入内容**：根据界面提示输入相关信息
4. **获取结果**：等待AI处理并查看生成结果
5. **历史记录/收藏**：支持查看、恢复、导出、收藏

---

## ⚠️ 注意事项

- 确保 API 密钥有效且有余额
- PDF/文档建议控制在50MB以内
- 网络需能访问 OpenAI/DeepSeek API（如需代理请配置 base_url）
- 推荐使用虚拟环境
- 若遇到 `langchain_huggingface` 报错，请安装 `langchain-huggingface` 包

---

## 📞 技术支持

如遇到问题或需要技术支持，请联系开发团队或在 [GitHub Issues](https://github.com/HeShen-1/LangChain) 留言。

---

**© 2025 AI工具集合 | 制作团队：傅彬彬，董政，聂群松，何星伽**
