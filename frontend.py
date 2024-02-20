import streamlit as st
import time

from backend import documentEnsembleRetreiver, cleanup_process, total_req, device_check

from langchain.chains import RetrievalQA

from langchain_openai import OpenAI, ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI
import settings

from prompt_config import format_instructions, combined_prompt as prompt


import json

from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers.json import parse_json_markdown
import re
import os

import asyncio

async def async_chain_invoke(chain, message):
    return await chain.ainvoke(message)

async def process_queries(api_key, files_pdf, qsheet, chain):
    tasks = []
    for key, value in qsheet.items():
        message = prompt.format(question=key, description=value, 
                                format_instructions=format_instructions)
        task = asyncio.create_task(async_chain_invoke(chain, message))
        tasks.append(task)

    return await asyncio.gather(*tasks)

async def process_half_queries(files_pdf, qsheet, chain, start, end):
    tasks = []
    for key, value in list(qsheet.items())[start:end]:
        message = prompt.format(question=key, description=value, 
                                format_instructions=format_instructions)
        task = asyncio.create_task(async_chain_invoke(chain, message))
        tasks.append(task)

    return await asyncio.gather(*tasks)

def launch():
    ## os 환경 변수 설정
    # os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY

    st.set_page_config(page_title='Seah Besteel : 수주규격 자동화 서비스', page_icon="⚙️", layout='wide', initial_sidebar_state='collapsed')
    st.title("⚙️ Seah Besteel : 수주규격 자동화 서비스")
    st.write("----"*20)
    
    with open('qr_dic.json', 'r') as file:
        loaded_data = json.load(file)
    qsheet = loaded_data

    with st.sidebar:
            # 전달.
            api_key = st.text_input("Enter apikey", value='', placeholder="Enter OpenAI Key", type="password")
            files_pdf = st.file_uploader(
                label="Upload document here.", 
                type=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt'], 
                accept_multiple_files=True
                )

            proceed_button = st.button('Proceed',use_container_width=True)

    if proceed_button:
        if files_pdf:
            with st.spinner('Retrieving Information From Document...'):
                retriever = documentEnsembleRetreiver(files_pdf)

                # 체인 설정
                llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, max_tokens=1024)
                chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=retriever,
                )

                # 비동기 호출 실행
                first_half_results = asyncio.run(process_half_queries(files_pdf, qsheet, chain, 0, len(qsheet) // 2))

                # 결과 처리
                for result in first_half_results:
                    st.write(result["result"])

                # 두 번째 절반의 쿼리 처리
                second_half_results = asyncio.run(process_half_queries(files_pdf, qsheet, chain, len(qsheet) // 2, len(qsheet)))

                # 결과 처리
                for result in second_half_results:
                    st.write(result["result"])

            # Cleanup   
            cleanup_process()

        else:
            st.error("Dataset or API key not provided. Please check.")

# launch
if __name__  == "__main__" :
    device_check()
    launch()


