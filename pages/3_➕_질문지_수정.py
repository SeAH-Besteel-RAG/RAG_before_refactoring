import streamlit as st
from backend import load_data, save_data
import pandas as pd

st.set_page_config(page_title="edit_script", page_icon="➕")

st.header("➕질문지 수정➕")
    # 사용자 입력을 받습니다.

# 데이터 로드
data = load_data()

# 사용자 입력
selected_key = st.selectbox("검토항목 선택", options=list(data.keys()))

# 선택된 키에 해당하는 값을 파싱
value_str = data[selected_key]

# 각 항목의 시작 위치를 찾기
defination_index = value_str.find("Defination: ")
synonyms_index = value_str.find("Synonyms: ")
unit_index = value_str.find("Unit: ")

# 각 항목의 값을 추출
defination = value_str[defination_index + 12 :synonyms_index].strip()
synonyms = value_str[synonyms_index + 9 :unit_index].strip()
unit = value_str[unit_index + 6 :].strip()


# 각 항목에 대한 별도의 입력 필드 제공
new_Defination = st.text_input("Edit Defination", value=defination)
new_Synonyms = st.text_input("Edit Synonyms", value=synonyms)
new_Unit = st.text_input("Edit Unit", value=unit)


# 데이터 수정 및 저장
if st.button("Save"):
    # 입력 값을 하나의 문자열로 결합
    new_value = f"Defination: {new_Defination},Synonyms: {new_Synonyms}, Unit: {new_Unit}, "
    data[selected_key] = new_value
    save_data(data)
    st.success("Data saved!")
    
    # # 데이터프레임 업데이트
    # st.write(pd.DataFrame(list(data.items()), columns=["Key", "Value"]))
    
    
# 데이터를 데이터프레임으로 변환하여 표시
st.subheader("검토항목 조회")
if st.button("조회하기") :
    st.write(pd.DataFrame(list(data.items()), columns=["Key", "Value"]))