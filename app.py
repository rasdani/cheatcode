from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse
from pydantic import BaseModel
import webbrowser
import uvicorn

from cheatcode import setup_qa


root_dir = '/home/rasdani/git/mp-transformer'
qa = setup_qa(root_dir)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static/static"), name="static")
# templates = Jinja2Templates(directory="templates")


class ChatInput(BaseModel):
    question: str

@app.get("/")
async def serve_index(request: Request):
    # return templates.TemplateResponse("index.html", {"request": request})
    return FileResponse("static/index.html")

@app.post("/chat")
async def chat(chat_input: ChatInput):
    question = chat_input.question
    print("QUESTION", question)
    result = qa({"question": question, "chat_history": []})
    print(result["chat_history"])
    print(result["source_documents"])
    return {"answer": result['answer'], "source_documents": result['source_documents']}

if __name__ == '__main__':
    print("Serving on http://localhost:8000")
    webbrowser.open("http://localhost:8000")
    uvicorn.run(app, host="localhost", port=8000)