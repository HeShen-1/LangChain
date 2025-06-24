from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import messages_to_dict, messages_from_dict


def qa_agent(openai_api_key, memory, uploaded_file, question):
    '''
    PDF智能问答代理核心函数

    :param openai_api_key: OpenAI API密钥
    :param memory: 对话内存，存储历史对话
    :param uploaded_file: 上传的PDF文件对象
    :param question: 用户提出的问题
    :return: AI基于PDF内容生成的回答
    '''
    model = ChatOpenAI(
        model='gpt-3.5-turbo',
        openai_api_key=openai_api_key,
        base_url='https://api.chatanywhere.tech'
    )

    # 读取上传的PDF内容
    file_content = uploaded_file.read()

    # 临时保存PDF到本地
    temp_file_path = 'temp.pdf'
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_content)

    loder = PyPDFLoader(temp_file_path)
    docs = loder.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
        separators=['\n', '。', '，', '!', '?', ',', '、', '']
    )

    texts = text_splitter.split_documents(docs)

    # 初始化文本嵌入模型
    embedding_model = OpenAIEmbeddings(
        openai_api_key=openai_api_key,
        base_url='https://api.chatanywhere.tech',
        model='text-embedding-3-large'
    )

    # 创建向量数据
    db = FAISS.from_documents(texts, embedding_model)

    # 将向量存储转换为检索器
    retriever = db.as_retriever()

    # 从内存中提取对话历史消息
    chat_messages = memory.chat_memory.messages

    # 创建新的对话内存，不传递原来的memory参数
    new_memory = ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history"
    )

    # 将历史消息添加到新内存中
    for message in chat_messages:
        new_memory.chat_memory.add_message(message)

    # 创建对话链，注意这里使用新的内存对象
    qa = ConversationalRetrievalChain.from_llm(
        llm=model,
        retriever=retriever,
        memory=new_memory
    )

    # 调用对话链处理用户问题，这里传递问题，对话链会自动使用内存中的历史
    response = qa.invoke({'question': question})

    # 更新原始内存中的对话历史
    for message in response["chat_history"]:
        memory.chat_memory.add_message(message)

    return response