from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader, Docx2txtLoader
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tempfile
import os
from langchain_huggingface import HuggingFaceEmbeddings


def get_embed():
    """获取词嵌入模型"""
    embed_model = HuggingFaceEmbeddings(
        model_name="./paraphrase-multilingual-Mpnet-base-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': False}
    )
    return embed_model


def load_documents(files):
    """根据文件类型加载文档"""
    documents = []

    for file in files:
        file_ext = os.path.splitext(file.name)[1].lower()
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.name)

        # 保存文件到临时位置
        with open(temp_path, "wb") as f:
            f.write(file.getbuffer())

        try:
            # 根据文件类型选择加载器
            if file_ext == '.pdf':
                loader = PyPDFLoader(temp_path)
            elif file_ext == '.txt':
                loader = TextLoader(temp_path, encoding='utf-8')
            elif file_ext == '.csv':
                loader = CSVLoader(temp_path)
            elif file_ext == '.docx':
                loader = Docx2txtLoader(temp_path)
            else:
                print(f"不支持的文件类型: {file.name}")
                continue

            # 加载文档
            docs = loader.load()
            # 添加来源信息
            for doc in docs:
                doc.metadata['source'] = file.name

            documents.extend(docs)
        finally:
            # 清理临时文件
            os.remove(temp_path)
            os.rmdir(temp_dir)

    return documents



def qa_agent(openai_api_key, memory, uploaded_files, question):
    """
    多文件问答助手核心函数
    :param openai_api_key: OpenAI API密钥
    :param memory: 历史对话内存
    :param uploaded_files: 上传的文件列表
    :param question: 用户提出的问题
    :return: 回答及来源文档
    """
    if not uploaded_files:
        return {"answer": "请先上传文件", "source_documents": []}

    model = ChatOpenAI(
        model='gpt-3.5-turbo',
        openai_api_key=openai_api_key,
        openai_api_base='https://twapi.openai-hk.com/v1/'
    )

    # 加载文档
    docs = load_documents(uploaded_files)

    # 文本分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=250,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", ",", "、"]
    )
    texts = text_splitter.split_documents(docs)

    # 词嵌入模型
    embedding_model = get_embed()

    # 创建向量数据库
    db = FAISS.from_documents(texts, embedding_model)
    # 将向量数据库转换为检索器
    retriever = db.as_retriever()
    # 创建问答链
    qa = ConversationalRetrievalChain.from_llm(
        llm=model,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
    )
    # 调用问答链，处理用户问题
    response = qa.invoke({
        'chat_history': memory.buffer,
        'question': question
    })
    return response

def get_custom_prompt():
    """
    创建自定义的问答提示词模板，确保回答基于文档内容
    """
    from langchain.prompts import PromptTemplate
    
    template = """使用以下文档片段来回答问题。如果文档中没有相关信息来回答问题，请明确回复"未在文档中找到相关内容。"

文档内容:
{context}

问题: {question}

回答:"""
    
    return PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )


def gen_followup_questions(uploaded_files, openai_api_key):
    """
    基于上传的文档内容生成建议问题
    :param uploaded_files: 上传的文件列表
    :param openai_api_key: OpenAI API密钥
    :return: 建议问题列表
    """
    if not openai_api_key or not uploaded_files:
        return []
        
    try:
        # 加载文档内容
        docs = load_documents(uploaded_files)
        if not docs:
            return []
        
        # 获取文档的前几段内容作为上下文
        doc_content = ""
        for doc in docs[:3]:  # 只使用前3个文档
            content = doc.page_content[:500]  # 每个文档取前500字符
            doc_content += f"文档内容片段: {content}\n\n"
        
        prompt = (
            "你是一个智能文档分析助手。基于以下文档内容，生成3个用户可能会询问的相关问题。\n\n"
            f"{doc_content}\n"
            "请根据文档的实际内容生成问题，确保问题都能在文档中找到答案。"
            "只返回问题本身，每个问题一行，不要编号。"
        )
        
        # 使用OpenAI接口生成问题
        from langchain_openai import ChatOpenAI
        model = ChatOpenAI(
            model='gpt-3.5-turbo',
            api_key=openai_api_key,
            base_url='https://twapi.openai-hk.com/v1/'
        )
        resp = model.invoke([{"role": "user", "content": prompt}])
        
        # 解析返回的文本为问题列表
        questions = [line.strip() for line in resp.content.split('\n') if line.strip() and not line.strip().startswith(('1.', '2.', '3.', '-', '•'))]
        return questions[:3]
    except Exception as e:
        print(f"生成建议问题失败: {e}")
        return []


def gen_followup_questions_from_qa(question, answer, openai_api_key):
    """
    根据当前问题和答案生成三个后续可能的提问（保留原函数作为备用）
    """
    if not openai_api_key:
        return []
        
    prompt = (
        "你是一个智能问答助手。用户刚刚问了这样一个问题：\n"
        f"问题：{question}\n"
        f"AI的回答：{answer}\n"
        "请基于用户的原始问题和AI的回答，生成三个用户可能会继续追问的相关问题。"
        "只返回问题本身，每个问题一行，不要编号。"
    )
    # 这里用OpenAI接口生成问题（如需更换模型可自行调整）
    from langchain_openai import ChatOpenAI
    try:
        model = ChatOpenAI(
            model='gpt-3.5-turbo',
            api_key=openai_api_key,
            base_url='https://twapi.openai-hk.com/v1/'
        )
        resp = model.invoke([{"role": "user", "content": prompt}])
        # 解析返回的文本为问题列表
        questions = [line.strip() for line in resp.content.split('\n') if line.strip()]
        return questions[:3]
    except Exception as e:
        print(f"生成后续问题失败: {e}")
        return []

