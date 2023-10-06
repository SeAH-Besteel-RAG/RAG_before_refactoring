import streamlit as st
import time

from backend import StreamHandler, documentEnsembleRetreiver, cleanup_process, verif_df, table_trans, device_check

from langchain.chains import RetrievalQA

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.llms import GooglePalm

import settings

from prompt_config import format_instructions, combined_prompt as prompt, qr_dic as qsheet

import pandas as pd
import ast


def launch() :
    st.set_page_config(page_title='File Q&A DEMO', page_icon="🦜", layout='wide', initial_sidebar_state='collapsed')
    st.title("🦜 LangChain : SEAH File :red[Q&A] DEMO")

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
            container = st.container()
            container.caption("filled Document")

            with st.spinner(' Retrieving Information From Document...') :
                # from backend: split and chunked at VectorStore.
                retriever = documentEnsembleRetreiver(api_key, files_pdf)

                # LLM Chain
                llm = GooglePalm(google_api_key=settings.PALM_api_key, temperature=0, max_output_tokens=512)
                # llm = OpenAI(model="gpt-3.5-turbo-instruct", api_key=settings.OpenAI_api_key, temperature=0, max_tokens=512)
                # llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=settings.OpenAI_api_key, temperature=0, max_tokens=512)

                chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=retriever,
                )

                for key, value in qsheet.items():
                    message = prompt.format(question=key, description=value, 
                                        format_instructions=format_instructions)
                
                    result_message = ast.literal_eval(chain.run(message))

                    title = result_message['Name']
                    ref = result_message['Reference']
                    spec = result_message['Specification']
                    
                    
                    #### dictionary일 경우 -> run 한 object 따로 빼서 쓸 생각.
                    if isinstance(spec, dict):
                    
                        if verif_df(spec):
                            table_df = table_trans(spec)
                            st.write(title)
                            st.write(table_df)

                        else:
                            table_df = pd.DataFrame(spec)
                            st.write(title)
                            st.write(table_df)
                    
                    else :
                        st.write(result_message)


            # Cleanup   
            cleanup_process()

        else:
            errorFileOrKeyNotFound = st.error("Dataset or API key not provided. Please check.")
            time.sleep(2.5)
            errorFileOrKeyNotFound.empty()

# launch
if __name__  == "__main__" :
    device_check()
    launch()
