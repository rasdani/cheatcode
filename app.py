import os
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from cheatcode import setup_chain, setup_retriever, OpenAIEmbeddings, ChatOpenAI
from langchain.vectorstores import FAISS
from pydantic import BaseModel
import uvicorn

# Set OpenAI API keys as constants here, reading from OS env variables.
FREE_OPENAI_API_KEY = os.getenv("FREE_OPENAI_API_KEY")
GPT4_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_GPT4")


app = FastAPI()
templates = Jinja2Templates(directory="templates")


class ChatInput(BaseModel):
    question: str

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# @app.post("/chat", response_class=HTMLResponse)
# async def chat(request: Request, question: str):
#     print("REQUEST", request)
#     question = request.question
#     print("QUESTION", question)
#     qa = setup_qa()
#     result = qa({"question": question, "chat_history": []})
#     return {"answer": result['answer']}

@app.post("/chat")
async def chat(chat_input: ChatInput):
    question = chat_input.question
    print("QUESTION", question)
    qa = setup_qa()
    result = qa({"question": question, "chat_history": []})
    return {"answer": result['answer']}

def setup_qa():
    # root_dir = '.'
    root_dir = '/home/rasdani/git/mp-transformer'
    embeddings = OpenAIEmbeddings(disallowed_special=())

    db_path = os.path.join(root_dir, ".cheatcode/db")
    db = FAISS.load_local(db_path, embeddings=embeddings)
    # model = ChatOpenAI(openai_api_key=FREE_OPENAI_API_KEY, model='gpt-3.5-turbo')
    model = ChatOpenAI(openai_api_key=GPT4_OPENAI_API_KEY, model='gpt-4')
    retriever = setup_retriever(db)
    qa = setup_chain(model, retriever)
    return qa

# if __name__ == '__main__':
#     uvicorn.run(app, host="localhost", port=8000)