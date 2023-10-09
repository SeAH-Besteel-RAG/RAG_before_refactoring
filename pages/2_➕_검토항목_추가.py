import streamlit as st
import pandas as pd
from backend import load_data, save_data


st.set_page_config(page_title="st_add_item", page_icon="➕")


data = load_data()

st.header("➕검토항목 추가➕")
# 새로운 항목 추가
st.subheader("새로운 항목 추가")
new_key = st.text_input("새로운 검토항목")
new_Defination = st.text_input("새로운 Defination")
new_Synonyms = st.text_input("새로운 Synonyms")
new_Unit = st.text_input("새로운 Unit")

if st.button("Add"):
    new_value = f"Defination: {new_Defination},Synonyms: {new_Synonyms}, Unit: {new_Unit}, "
    data[new_key] = new_value
    save_data(data)
    st.success("New item added!")

# 데이터를 데이터프레임으로 변환하여 표시
st.subheader("검토항목 조회")
if st.button("조회하기") :
    st.write(pd.DataFrame(list(data.items()), columns=["Key", "Value"]))