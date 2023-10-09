import streamlit as st
from backend import device_check
# from pages import 1_st_retriever as page_1, 2_st_add_item as page_2, 3_st_add_synonym as page_3

def launch() :
    st.set_page_config(page_title='Seah Besteel 수주규격 자동화 서비스', page_icon="🦜", layout='centered', initial_sidebar_state='collapsed')
    st.title("🦜 Seah Besteel : 수주규격 자동화 서비스")

    st.markdown("""
    <style>
            border: 2px solid #f63366;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="table-box">
    
    | 항목                   | 설명                                          |
    |------------------------|--------------------------------------------------|
    | **자동화 서비스 이용** | 수주규격 자동화 페이지로 이동하여 사이드바에 API KEYS와 파일을 업로드하고 실행 버튼을 누르세요.  |
    | **검토항목 추가**      | 검토항목 추가 페이지로 이동하여 검토항목명과 내용을 입력하세요.  |
    | **동의어 추가**        | 동의어 추가 페이지로 이동하여 검토항목명과 추가할 동의어를 입력하세요.  |

    </div>
    """, unsafe_allow_html=True)


# launch
if __name__  == "__main__" :
    device_check()
    launch()


