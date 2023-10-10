from langchain.llms import OpenAI
import settings
import os

import pypdf
import io
import json

import pytesseract

from unstructured.partition.pdf import partition_pdf
from unstructured.staging.base import elements_to_json


###### from windows get local tesseract.


class PDFParser :
    def __init__ (self, file, strategy = "hi_res", model_name = "yolox") :
        self.pdf = pypdf.PdfReader(file)
        self.strategy = strategy
        self.model_name = model_name # can use another model like "yolox_quantized" "detectron2_onnx"

    @staticmethod
    def element_json_parsing(json_result) -> list :
        ''' get parsed json from page and find table. dump text into extracted elements and return.'''
    
        data = json.loads(json_result)
        extracted_elements = []

        for entry in data:
            if entry["type"] == "Table":
                extracted_elements.append(entry["metadata"]["text_as_html"])

        return extracted_elements

    @staticmethod
    def compare_table_and_origin_text(parsed_table_list, text):
        for table in parsed_table_list:
            
            table_string = "\n".join([f"{key}: {value}" for key, value in table.items()])

            start_pos = len(text)
            end_pos = -1

            for key, value in table.items():
                # Check position for keys
                key_pos = text.rfind(key)
                if key_pos != -1:
                    start_pos = min(start_pos, key_pos)
                    end_pos = max(end_pos, key_pos + len(key))

                # Check position for values
                # If the value is a list, check each item in the list
                if isinstance(value, list):
                    for item in value:
                        item_pos = text.rfind(str(item))
                        if item_pos != -1:
                            start_pos = min(start_pos, item_pos)
                            end_pos = max(end_pos, item_pos + len(str(item)))
                
                # If not, check each value's position
                else:
                    value_pos = text.rfind(str(value))
                    if value_pos != -1:
                        start_pos = min(start_pos, value_pos)
                        end_pos = max(end_pos, value_pos + len(str(value)))

            ####### key, value로 문서 상 최소 위치, 최대 위치 찾아서 그 사이 구간 전부 table로 바꾸는 것.

            ### Grid Box 생성했으면 문서에서 위치 교체.
            if start_pos != len(text) and end_pos != -1:
                # Replace the text range with the new table string
                text = text[:start_pos] + table_string + text[end_pos:]

            else : text += table_string

        return text

    @staticmethod
    def page_object_to_pdf(page) -> None :
        ''' convert pypdf page object to temporary file 'result.pdf'. '''

        #byte 단위로 page 처리.
        pdf_writer = pypdf.PdfWriter()
        pdf_writer.add_page(page=page)

                                                                                                                                                                                                                                                                                
        pdf_bytes = io.BytesIO()
        pdf_writer.write(pdf_bytes)
        pdf_bytes.seek(0)

        with open('result.pdf','wb') as result_pdf:
            pdf_writer.write(result_pdf)

        return None

    def getDictTableFromGPT(self, table_list) -> list : 
        ''' get HTML table list and query to gpt-3.5-turbo-instruct and get str'''

        #storage
        converted_dictionary_table_list = []

        for table in table_list :
        ##### html 형식으로 바꿔달라고 질문 던져 넣기.
            prompt = f"{table} \n\n Convert given table to formatted python dictionary. careful with structure and grammar."

            table_completion = OpenAI(model=f'gpt-3.5-turbo-instruct', openai_api_key=settings.OpenAI_api_key)
            table_completion_result = table_completion.predict(prompt)

            ##### json값으로 바꿀 수 있어야만 추가. 아니면 pass
            try : 
                res = json.loads(table_completion_result)
                converted_dictionary_table_list.append(res)
                
            except ValueError : 
                pass

        return converted_dictionary_table_list

    def parse_pdf(self): 
        ''' return langchain document '''
        num_pages = len(self.pdf.pages)

        result_storage = []

        for page_num in range(num_pages):
            page = self.pdf.pages[page_num]

            #page object to temporary file named 'result.pdf'
            self.page_object_to_pdf(page)

            # element config
            elements = partition_pdf(
                filename = './result.pdf',
                strategy= self.strategy, 
                infer_table_structure=True, 
                model_name= self.model_name,
            )

            # unstructured-io function으로 table 내에 elements들 찾아서 json으로 변경
            result = elements_to_json(elements, indent=4, encoding='utf-8')
            # json으로 변경 된 list중에서 table 요소만 찾기.
            table_list = self.element_json_parsing(result)

            # table 요소 html_text로 입력된 것 gpt로 json 변경.
            converted_dictionary_table_list = self.getDictTableFromGPT(table_list)
            # 원본 텍스트
            page_text = page.extract_text()

            ##### 원본 텍스트랑 json file로 받았던 html 파일 비교해서 삭제하는 알고리즘.
            new_text = self.compare_table_and_origin_text(converted_dictionary_table_list, page_text)

            ##### new_text 받아서 처리

            result_storage.append({"text":new_text, 'page':page_num+1})

        ##### loop 돌았으면 파일 처리
        os.remove('./result.pdf')
        return result_storage

        
### 사용법

# if __name__ == "__main__" :
#         parser = PDFParser('06-M-5010.005.pdf')
#         print(parser.parse_pdf())

