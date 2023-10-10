from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.prompts.chat import SystemMessage

from langchain.output_parsers import ResponseSchema, StructuredOutputParser

import json


#################### pydantic output prompt

response_schemas = [
    ResponseSchema(name="Name", description="{question},"),
    ResponseSchema(name="Reference", description="Source file name. If no reference is available, Write '-',"),
    ResponseSchema(name="Specification" , description="Answer with correct data structure. If answer is None, Write '-'", type="string")
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

description : ```{description}```.

Answer strictly obey following instructions.

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

if __name__ == "__main__" :
    print(combined_prompt)