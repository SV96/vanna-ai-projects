import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')
OPENAI_MODEL_NAME=os.getenv('OPENAI_MODEL_NAME')

llm = ChatOpenAI(model=OPENAI_MODEL_NAME)

prompt = PromptTemplate.from_template(
    "Rewrite the question '{question}' as a declarative sentence with a answer '{answer}'."
)

def get_answer_statement(question, answer):
    formatted_prompt = prompt.format(question=question,answer=answer)
    response = llm.invoke(formatted_prompt)
    print(f"Formatted Answer: {response.content}")
    return response.content