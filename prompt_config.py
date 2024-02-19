from langchain_core.messages.system import SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

import json


#################### pydantic output prompt

response_schemas = [
    ResponseSchema(name="Name", description="{question}."),
    ResponseSchema(name="Reference", description="Source file name. If no reference is available, Use '-'."),
    # 답변에 입력한 검사항목명 외에도 다른 내용을 가져와서 정확하게 명시해주기 위해서 {question} 넣어줌
    ResponseSchema(name="Specification" , description="Answer to {question} only in dict or string. If answer or key is None, '-'. ", type="string")
]

parser = StructuredOutputParser.from_response_schemas(response_schemas)
format_instructions = parser.get_format_instructions()

#################### basic prompt

#System Prompt
system_template = """You are an expert in the Steel industry. Use only given information.
Kindly examine the Given Steel Order document and address the following questions.\n:"""

#Human Prompt
human_template = """
Q : Based on the provided document, What is requested about ```{question}``` in this document?
Further description about the {question} are as follows:

description : ```{description}```

{format_instructions}

"""

system_message = SystemMessage(
  content= (system_template)
)
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

combined_prompt = ChatPromptTemplate.from_messages([
    system_message,
    human_message_prompt
    ])
