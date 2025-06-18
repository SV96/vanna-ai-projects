import os

from vanna.openai import OpenAI_Chat
from constants import DDL_STR, DOCUMENT_STR, QUERIES_ARR
from dotenv import load_dotenv
from vanna.chromadb import ChromaDB_VectorStore
from utils import pretty_print
from sentence_former import get_answer_statement

load_dotenv()

OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')
OPENAI_MODEL_NAME=os.getenv('OPENAI_MODEL_NAME')
POSTGRES_HOST=os.getenv('POSTGRES_HOST')
POSTGRES_DB_NAME=os.getenv('POSTGRES_DB_NAME')
POSTGRES_USER=os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD')
POSTGRES_PORT=os.getenv('POSTGRES_PORT')
        
class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):    
       ChromaDB_VectorStore.__init__(self, config=config)
       OpenAI_Chat.__init__(self, config=config)

vn = MyVanna(config={'api_key': OPENAI_API_KEY,
                     'model': OPENAI_MODEL_NAME})
vn.connect_to_postgres(
        host=POSTGRES_HOST, 
        dbname=POSTGRES_DB_NAME, 
        user=POSTGRES_USER, 
        password=POSTGRES_PASSWORD, 
        port=POSTGRES_PORT)

try:
    ddl_training_data = vn.get_training_data(ddl=DDL_STR)
    if not ddl_training_data:
        vn.train(ddl=DDL_STR)
    else:
       print("DDL already exists. Skipping...")

    documentation_training_data = vn.get_training_data(documentation=DOCUMENT_STR)
    if not documentation_training_data:
       print("Adding SQL queries...")
       vn.train(documentation=DOCUMENT_STR)
       print("Training completed successfully!")
    else:
       print("Documentation already exists. Skipping...")   
except Exception as e:
    print(f"Error during training: {str(e)}")
  

try:
    for query in QUERIES_ARR:
       sql_training_data = vn.get_training_data(sql=query)
       if not sql_training_data:
           print("Adding SQL queries...")
           vn.train(sql=query)
           print("Training completed successfully!")
       else:
           print(f"SQL query '{query}' already exists. Skipping...")

except Exception as e:
    print(f"Error during training: {str(e)}")  


# remove training data if there's obsolete/incorrect information. 
# vn.remove_training_data(id='1-ddl')

def get_clean_answer(vn, question):
    response = vn.ask(question=question, allow_llm_to_see_data=True)
    if isinstance(response, tuple) and len(response) >= 2:
        df = response[1]
        if hasattr(df, 'iloc'):
            return df.iloc[0, 0]
    return "Could not extract answer"

def ask_question(question):
    try:
        answer = get_clean_answer(vn, question)
        print(f"Answer: {answer}")
        full_answer = get_answer_statement(question, answer)
        print(f"Full Answer: {full_answer}")
        return full_answer
    except Exception as e:
        print(f"Error: {str(e)}")
        return "Unable to find related answer. Please try again later."

# que1= vn.ask(question="Can you give me total movies count?",allow_llm_to_see_data=True)
# pretty_print('Answer', que1)
