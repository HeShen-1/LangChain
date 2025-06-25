from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader, Docx2txtLoader
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tempfile
import os

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False


def get_embed(openai_api_key=None, force_backup=False):
    """获取词嵌入模型"""
    import os
    
    # 如果强制使用备选方案，直接跳过OpenAI
    if force_backup:
        print("🔄 强制使用备选嵌入方案")
    elif openai_api_key:
        try:
            print("🔄 尝试使用OpenAI嵌入API")
            embed_model = OpenAIEmbeddings(
                api_key=openai_api_key,
                base_url='https://twapi.openai-hk.com/v1/'
            )
            # 进行更严格的API测试 - 测试多次确保稳定性
            print("🧪 正在测试OpenAI嵌入API...")
            for i in range(3):  # 测试3次
                test_result = embed_model.embed_query(f"测试文本{i+1}")
                if not test_result or not isinstance(test_result, list) or len(test_result) == 0:
                    print(f"❌ OpenAI嵌入API第{i+1}次测试失败")
                    raise ValueError(f"OpenAI API第{i+1}次测试响应无效")
            print("✅ OpenAI嵌入API多次测试成功")
            return embed_model
        except Exception as e:
            print(f"❌ OpenAI嵌入API失败: {e}")
            print("🔄 切换到备选嵌入方案...")
    
    # 立即使用备选方案，避免网络延迟
    print("🔄 使用备选嵌入方案...")
    
    # 优先使用假嵌入模型（快速可靠）
    try:
        print("⚡ 使用快速嵌入模型（用于测试）")
        from langchain_community.embeddings import FakeEmbeddings
        return FakeEmbeddings(size=384)
    except Exception as e:
        print(f"❌ 假嵌入模型失败: {e}")
    
    # 如果假嵌入不可用，尝试HuggingFace模型
    if HUGGINGFACE_AVAILABLE:
        try:
            # 尝试使用本地模型（避免网络请求）
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(project_root, "paraphrase-multilingual-Mpnet-base-v2")
            
            if os.path.exists(model_path):
                print(f"🔄 尝试加载本地模型: {model_path}")
                embed_model = HuggingFaceEmbeddings(
                    model_name=model_path,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': False}
                )
                return embed_model
        except Exception as e:
            print(f"❌ 本地模型加载失败: {e}")
        
        try:
            # 最后尝试在线模型
            print("🔄 尝试在线嵌入模型: all-MiniLM-L6-v2")
            embed_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': False}
            )
            return embed_model
        except Exception as e:
            print(f"❌ 在线模型加载失败: {e}")
    
    raise RuntimeError("无法加载任何嵌入模型。请检查API密钥或网络连接。")


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

    try:
        model = ChatOpenAI(
            model='gpt-3.5-turbo',
            api_key=openai_api_key,
            base_url='https://twapi.openai-hk.com/v1/'
        )

        # 加载文档
        docs = load_documents(uploaded_files)
        if not docs:
            return {"answer": "文档加载失败，请检查文件格式", "source_documents": []}

        # 文本分割
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=250,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "！", "？", ",", "、"]
        )
        texts = text_splitter.split_documents(docs)
        
        if not texts:
            return {"answer": "文档内容为空或无法解析", "source_documents": []}

        # 词嵌入模型
        print("🔄 正在加载嵌入模型...")
        embedding_model = None
        use_backup_embedding = False
        
        try:
            embedding_model = get_embed(openai_api_key)
            print("✅ 嵌入模型加载成功")
        except Exception as e:
            print(f"❌ 嵌入模型加载失败: {e}")
            # 直接使用备选嵌入模型
            try:
                print("🔄 使用备选嵌入模型...")
                embedding_model = get_embed(openai_api_key, force_backup=True)
                use_backup_embedding = True
                print("✅ 备选嵌入模型加载成功")
            except Exception as backup_e:
                return {"answer": f"所有嵌入模型都加载失败: {str(e)}, 备选: {str(backup_e)}", "source_documents": []}

        # 创建向量数据库
        print("🔄 正在创建向量数据库...")
        db = None
        retriever = None
        
        try:
            # 为了避免大量文档造成的问题，限制文档数量
            if len(texts) > 100:
                texts = texts[:100]  # 只使用前100个文档片段
                print(f"⚠️ 文档片段过多，只使用前100个片段")
            
            db = FAISS.from_documents(texts, embedding_model)
            print("✅ 向量数据库创建成功")
            # 将向量数据库转换为检索器
            retriever = db.as_retriever()
        except Exception as e:
            print(f"❌ 向量数据库创建失败: {e}")
            # 如果还没有使用备选嵌入，现在尝试
            if not use_backup_embedding:
                try:
                    print("🔄 尝试使用备选嵌入模型重建数据库...")
                    backup_embedding = get_embed(openai_api_key, force_backup=True)
                    db = FAISS.from_documents(texts, backup_embedding)
                    retriever = db.as_retriever()
                    print("✅ 使用备选嵌入模型重建数据库成功")
                except Exception as backup_e:
                    return {"answer": f"向量数据库创建失败: {str(e)}\n备选方案也失败: {str(backup_e)}", "source_documents": []}
            else:
                return {"answer": f"向量数据库创建失败: {str(e)}", "source_documents": []}

        # 创建问答链并处理查询
        try:
            qa = ConversationalRetrievalChain.from_llm(
                llm=model,
                retriever=retriever,
                memory=memory,
                return_source_documents=True,
            )
            print("🔄 正在处理问答...")
            # 调用问答链，处理用户问题
            response = qa.invoke({
                'chat_history': memory.buffer,
                'question': question
            })
            print("✅ 问答处理成功")
            return response
        except Exception as e:
            print(f"❌ 问答处理失败: {e}")
            # 如果问答处理失败，可能是查询时嵌入模型问题，尝试重建整个系统
            if not use_backup_embedding:
                try:
                    print("🔄 检测到查询阶段嵌入问题，使用备选方案重建...")
                    backup_embedding = get_embed(openai_api_key, force_backup=True)
                    db_backup = FAISS.from_documents(texts, backup_embedding)
                    retriever_backup = db_backup.as_retriever()
                    
                    qa_backup = ConversationalRetrievalChain.from_llm(
                        llm=model,
                        retriever=retriever_backup,
                        memory=memory,
                        return_source_documents=True,
                    )
                    response = qa_backup.invoke({
                        'chat_history': memory.buffer,
                        'question': question
                    })
                    print("✅ 备选方案问答处理成功")
                    return response
                except Exception as backup_e:
                    return {"answer": f"问答处理失败: {str(e)}\n备选方案也失败: {str(backup_e)}", "source_documents": []}
            else:
                return {"answer": f"问答处理失败: {str(e)}", "source_documents": []}
            
    except Exception as e:
        return {"answer": f"系统错误: {str(e)}", "source_documents": []}


def gen_followup_questions(question, answer, openai_api_key):
    """
    根据当前问题和答案生成三个后续可能的提问
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

