import os
import json
import pandas as pd

from tika import parser

import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler

from langchain.text_splitter import RecursiveCharacterTextSplitter, NLTKTextSplitter
from langchain.docstore.document import Document
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings

#Retriever
from langchain.vectorstores import Chroma
from langchain.retrievers import BM25Retriever, EnsembleRetriever

from chromadb.errors import InvalidDimensionException

#### pdf preprocessing
from PDFProcess import PDFParser


def device_check() : 
    ''' for check cuda availability '''
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return device


#실행 이후에 collection 정리(일단 임시.)
def cleanup_process() :
    Chroma().delete_collection()
    st.markdown('===========END============')

def document_handler(uploaded_files) : 
    storage = []
    
    for file in uploaded_files : 
        if file.name.endswith(".pdf") :
            parsed_pdf_file = PDFParser(file)
            parsed_page = parsed_pdf_file.parse_pdf()

            # create document object
            for page in parsed_page :
                document = Document(page_content=page['text'], metadata={'source':file.name, 'page':page['page']})
                storage.append(document)

        #나머지 형식 파일들은 받아서 splitter에서 split한 이후에 document로 생성함.
        elif file.name.endswith('.docx') or file.name.endswith('.doc') :
            raw = parser.from_buffer(file,xmlContent=False)
            document = Document(page_content=raw['content'], metadata={'source':file.name})
            storage.append(document)

        elif file.name.endswith('.xlsx') or file.name.endswith('.xls') :
            raw = parser.from_buffer(file,xmlContent=False)
            document = Document(page_content=raw['content'], metadata={'source':file.name})
            storage.append(document)
            
    return storage


def extract_text_from_file(uploaded_files):
    text_splitter = RecursiveCharacterTextSplitter(separators=['\n\n\n','\n\n','\n',' ','.',''], length_function=len, add_start_index=True)
    storage = []

    #priority filter
    #검색될때 나온거 기반으로 우선순위(rank)
    for file in uploaded_files :
        raw = parser.from_buffer(file,xmlContent=False)
        document = text_splitter.create_documents(texts=[raw['content']],metadatas=[{'source':file.name}])
        storage.append(document)

    return storage

def documentEnsembleRetreiver(api_key, files) :
    os.environ["OPENAI_API_KEY"] = api_key

    # documents = extract_text_from_file(files)
    documents = document_handler(files)

    # Embedding and Store
    embedding_function = SentenceTransformerEmbeddings(
        model_name="BAAI/bge-base-en-v1.5", model_kwargs={'device':device_check()}, encode_kwargs={'normalize_embeddings':True}
        )
    
    #DimensionException 뜨면 기존 문서 지울것.
    try:
        vectordb = Chroma.from_documents(documents=documents, embedding=embedding_function)
    except InvalidDimensionException:
        Chroma().delete_collection()
        vectordb = Chroma.from_documents(documents=documents, embedding=embedding_function)

    chroma_retriever = vectordb.as_retriever(search_type='mmr', search_kwargs={"k": 3})

    #BM25 Retriever
    bm25_retriever = BM25Retriever.from_documents(documents=documents)
    bm25_retriever.k = 2

    # embedding_function = OpenAIEmbeddings()
    ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, chroma_retriever], weights=[0.4, 0.6])

    return ensemble_retriever

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container: st.delta_generator.DeltaGenerator, initial_text: str = ''):
        self.container = container
        self.text = initial_text
        self.run_id_ignore_token = None
        self.previous_run_id = None

    def on_llm_start(self, serialized: dict, prompts: list, **kwargs):
        # Workaround to prevent showing the rephrased question as output
        if prompts[0].startswith("Human"):
            self.run_id_ignore_token = kwargs.get("run_id")

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        current_run_id = kwargs.get("run_id", None)

        # Check if the current run_id is different from the previous one.
        # If yes, then a new question has started, so insert a separator.
        if self.previous_run_id and self.previous_run_id != current_run_id:
            self.text += "\n\n"  # Insert a markdown horizontal line as separator

        if self.run_id_ignore_token == current_run_id:
            return

        self.text += token
        self.container.markdown(self.text)
        self.previous_run_id = current_run_id


# ======================= 검토항목 로드 및 저장 함수 ===========================
## For : 검토항목 추가 및 질문지 수정
# 검토항목 파일 로드
def load_data():
    with open("qr_dic.json", "r", encoding = "utf-8") as file:
        data = json.load(file)
    return data

# 검토항목 파일 업데이트
def save_data(data, filename= "qr_dic.json"):
    with open(filename, "w", encoding = "utf-8") as file:
        json.dump(data, file, indent=4)


# =========================== 결과 출력 함수 ===============================

# value 하나에 대한 전처리 함수
def process_value(value):
    # Case when value is a dictionary and has only one key-value pair
    if isinstance(value, dict) and len(value) == 1:
        key, sub_value = list(value.items())[0]
        return f"{key} {sub_value}"
    # Case when value is not a dictionary
    else:
        return value

# 전체 결과 및 별도표 데이터프레임으로 반환
def total_req(message):
    # Process the 'Specification' part of the message
    message["Specification"] = process_value(message["Specification"])
    
    value = message["Specification"]
    
    if isinstance(value, str):
        temp_df = pd.DataFrame([message])
        sub_df = pd.DataFrame()
    elif isinstance(value, dict):
        sub_df = pd.DataFrame([value])
        message["Specification"] = "하단 표 참조"  
        temp_df = pd.DataFrame([message])
    
    return  temp_df, sub_df

