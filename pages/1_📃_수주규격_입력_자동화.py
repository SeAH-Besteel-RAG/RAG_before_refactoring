import streamlit as st
import time

from backend import documentEnsembleRetreiver, cleanup_process

from langchain.chains import RetrievalQA

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.llms import GooglePalm


import settings

from prompt_config import format_instructions, combined_prompt as prompt
from prompt_config import parser

import pandas as pd
import ast
import json

#################### get question sheet
with open('qr_dic.json', 'r') as file:
    loaded_data = json.load(file)
qsheet = loaded_data



st.set_page_config(page_title="수주규격 자동화 입력", page_icon="📃")
st.header("📃수주규격 자동화 입력 서비스")

with st.sidebar:
        # 전달.
        api_key = st.text_input("Enter apikey", value='', placeholder="Enter OpenAI Key", type="password")
        files_pdf = st.file_uploader(
            label="""Upload document here.""", 
            type=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt'], 
            accept_multiple_files=True
            )

        proceed_button = st.button('Proceed',use_container_width=True)

if proceed_button:
    # button Call
    if files_pdf :
        # container = st.container()
        st.caption("filled Document")

        with st.spinner(' Retrieving Information From Document...') :
            # from backend: split and chunked at VectorStore.
            retriever = documentEnsembleRetreiver(api_key, files_pdf)

            # LLM Chain
            llm = GooglePalm(google_api_key=settings.PALM_api_key, temperature=0, max_output_tokens=512)
            # llm = OpenAI(model="gpt-3.5-turbo-instruct", openai_api_key=settings.OpenAI_api_key, temperature=0, max_tokens=512)
            # llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=settings.OpenAI_api_key, temperature=0, max_tokens=512)

            chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
            )

            result_lst = []
            for key, value in qsheet.items():
                message = prompt.format(question=key, description=value, 
                                    format_instructions=format_instructions)
                
                answer_message = chain.run(message)
                try:
                    result_message = parser.parse(answer_message)
                    st.write(result_message)
                except:
                    st.write(answer_message)

        # Cleanup   
        cleanup_process()

    else:
        errorFileOrKeyNotFound = st.error("Dataset or API key not provided. Please check.")
        time.sleep(2.5)
        errorFileOrKeyNotFound.empty()