import streamlit as st
import time
import json
import asyncio

from backend import documentEnsembleRetreiver, cleanup_process, device_check
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from prompt_config import format_instructions, combined_prompt as prompt

import datetime

async def async_chain_invoke(chain, message):
    return await chain.ainvoke(message)

async def process_half_queries(qsheet, chain, start, end):
    tasks = []
    for key, value in list(qsheet.items())[start:end]:
        message = prompt.format(question=key, description=value, 
                                format_instructions=format_instructions)
        task = asyncio.create_task(async_chain_invoke(chain, message))
        tasks.append(task)

    return await asyncio.gather(*tasks)

async def main(files_pdf, qsheet, chain):
    parts = 3
    part_length = len(qsheet) // parts
    results = []

    for part in range(parts):
        start_index = part * part_length
        end_index = (part + 1) * part_length if part < parts - 1 else len(qsheet)

        # 비동기 호출 실행
        current_part_results = await process_half_queries(qsheet, chain, start_index, end_index)
        results.extend(current_part_results)

        if part < parts - 1:
            time.sleep(3)

    with open("log.txt", 'a', encoding="utf-8") as file:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write("Log started at: " + current_time + "\n")  # 로그 시작 시간 기록
        for pdf_file in files_pdf:
            file.write("Filename:" + pdf_file.name + "\n")

        for result in results:
            file.write(result['result'])
            st.write(result['result'])

        file.write("="*80+'\n')

def launch():
    st.set_page_config(page_title='Seah Besteel : 수주규격 자동화 서비스', page_icon="⚙️", layout='wide', initial_sidebar_state='collapsed')
    st.title("⚙️ Seah Besteel : 수주규격 자동화 서비스")
    st.write("----"*20)
    
    with open('qr_dic.json', 'r') as file:
        loaded_data = json.load(file)
    qsheet = loaded_data

    with st.sidebar:
        # api_key = st.text_input("Enter apikey", value='', placeholder="Enter OpenAI Key", type="password")
        files_pdf = st.file_uploader(label="Upload document here.", type=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt'], accept_multiple_files=True)
        proceed_button = st.button('Proceed',use_container_width=True)

    if proceed_button and files_pdf:
        with st.spinner('Retrieving Information From Document...'):
            retriever = documentEnsembleRetreiver(files_pdf)
            llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, max_tokens=1024)
            chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
            asyncio.run(main(files_pdf, qsheet, chain))
        cleanup_process()
    # elif not files_pdf:
    #     st.error("Dataset or API key not provided. Please check.")

if __name__  == "__main__":
    device_check()
    launch()
