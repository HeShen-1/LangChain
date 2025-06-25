# AI工具集合 - 基于LangChain的多功能AI应用

本项目是一个基于 Streamlit + LangChain 的多功能 AI 工具集合，集成了视频脚本生成、小红书爆款文案、ChatGPT对话克隆、多文件智能PDF问答等实用AI能力，支持多API接入和多种文档类型。

[项目访问地址](https://xiweibing-bot.streamlit.app/):目前存在无法多人同时使用的问题😋

项目4使用了本地模型进行词向量嵌入,使用时注意模型路径问题.

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

- **全新UI设计**：分栏布局，操作更直观
- **多文件支持**：同时上传 PDF、TXT、CSV、DOCX 多个文档
- **智能问答**：基于向量检索（FAISS+HuggingFace Embeddings）
- **对话管理**：支持新建对话、历史对话切换、多轮记忆
- **智能建议**：自动生成追问建议，一键提问
- **来源溯源**：答案可追溯到具体文档片段
- **状态提示**：实时显示处理状态和错误信息
- **优化体验**：固定底部输入栏，聊天界面更友好

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
├── paraphrase-multilingual-Mpnet-base-v2/  # 本地嵌入模型
│   ├── 1_Pooling/
│   ├── config.json
│   ├── model.safetensors
│   └── modules.json
├── 项目1视频脚本一键生成器/
│   └── utils.py                  # 视频脚本生成核心逻辑
├── 项目2小红书爆款文案生成器/
│   ├── main.py
│   ├── utils.py                  # 小红书文案生成与配图
│   ├── prompt_template.py        # 风格提示词模板
│   └── readme.md
├── 项目3克隆ChatGPT/
│   └── utils.py                  # ChatGPT对话核心逻辑
└── 项目4智能PDF问答工具/
    └── utils.py                  # 多文件问答与向量检索
```

---

## 🛠️ 技术栈

- **前端**：Streamlit
- **AI框架**：LangChain
- **大模型**：OpenAI GPT-3.5/4、DeepSeek Chat
- **向量数据库**：FAISS
- **嵌入模型**：HuggingFace Embeddings (paraphrase-multilingual-Mpnet-base-v2)
- **文档处理**：PyPDF, python-docx, reportlab
- **数据验证**：Pydantic

---

## 🆕 最新更新 (v2.0)

### PDF智能问答工具重大升级

- **全新界面设计**：采用三栏布局，操作更直观
- **改进的对话管理**：
  - 🗨️ 一键新建对话，快速重置会话状态
  - 📚 历史对话列表，支持对话切换和恢复
  - 💡 智能问题建议，一键快速提问
- **优化的用户体验**：
  - 固定底部输入栏，输入更便捷
  - 实时状态提示，处理过程透明化
  - 更友好的错误处理和状态反馈
- **增强的功能**：
  - 支持多文档同时上传和问答
  - 改进的答案来源溯源显示
  - 更稳定的向量检索和嵌入处理

---

## 📝 使用说明

1. **首次使用**：在侧栏输入 OpenAI API 密钥（小红书需单独输入 DeepSeek Key）
2. **选择功能**：点击侧栏按钮切换不同工具
3. **PDF问答使用**：
   - 上传文档 → 输入问题 → 获取智能答案
   - 使用建议问题快速提问
   - 通过历史对话管理多个会话
4. **其他功能**：根据界面提示输入相关信息
5. **历史记录/收藏**：支持查看、恢复、导出、收藏

---

## ⚠️ 注意事项

- 确保 API 密钥有效且有余额
- PDF/文档建议控制在50MB以内
- 网络需能访问 OpenAI/DeepSeek API（如需代理请配置 base_url）
- 推荐使用虚拟环境
- 若遇到 `langchain_huggingface` 报错，请安装 `langchain-huggingface` 包
- 首次使用PDF问答功能会自动下载嵌入模型，请耐心等待

---

## 🌐 在线演示

项目已部署到 GitHub Pages，您可以直接访问：
[https://heshen-1.github.io/LangChain/](https://heshen-1.github.io/LangChain/)

---

## 📞 技术支持

如遇到问题或需要技术支持，请联系开发团队或在 [GitHub Issues](https://github.com/HeShen-1/LangChain/issues) 留言。

**© 2025 AI工具集合 | 制作团队：傅彬彬，董政，聂群松，何星伽**
