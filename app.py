import argparse
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from pydantic import BaseModel
import webbrowser
import uvicorn

from cheatcode import setup_qa


app = FastAPI()
app.mount("/static", StaticFiles(directory="static/static"), name="static")

chat_history = []

class ChatInput(BaseModel):
    question: str


@app.get("/")
async def serve_index(request: Request):
    return FileResponse("static/index.html")

@app.post("/chat")
async def chat(chat_input: ChatInput):
    global chat_history # works so don't complain
    question = chat_input.question
    # print("QUESTION", question)
    print("SENDING REQUEST...")
    result = qa({"question": question, "chat_history": chat_history})
    chat_history.append((question, result["answer"]))
    # chat_history.append((question, result["answer"], result["source_documents"]))
    print(result["chat_history"])
    # print(result["source_documents"])
    return {"answer": result["answer"], "source_documents": result["source_documents"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to chat with (default: current directory)",
    )
    root_dir = parser.parse_args().directory
    qa = setup_qa(root_dir)
    print("Serving on http://localhost:8000")
    webbrowser.open("http://localhost:8000")
    uvicorn.run(app, host="localhost", port=8000)
