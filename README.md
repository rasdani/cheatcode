# Ch(e)atCode 🤞🗣️
ChatGPT for your codebase. Your cheatcode for productivity 🚀.




Fleshed out version of my [proof of concept](https://github.com/rasdani/chat-your-code).

<!-- ![Demo Pic](./demo.png) -->
<div style="text-align: center;">
    <img src="./demo.png" alt="demo pic" width="368" height="472" />
</div>

Embeds all `.py` files in a given repo and stores them in a VectorDB.
Finds cosine similiar source files to your question and stuffs them into ChatGPT's prompt using LangChain's ConversationalRetrievalChain.
Uncomment GPT4 for more accurate answers.

## setup
Install dependencies with `pip install -r requirements.txt`.
Set `OPENAI_API_KEY` in your environment variables.

## run CLI app
`python cheatcode.py init` searches recursively for `.py` files in your current directory and creates a `.cheatcode` folder, which stores your embedded source code.
(Or specify a path with `python cheatcode.py init <path>`)


`python cheatcode.py chat` starts the chat on your terminal.
(You can point this to a directory, too: `python cheatcode.py chat <path>`)

## run web app
`python app.py` starts the web UI on localhost:8000.
(Or `python app.py <path>`)

You need to init your codebase first.


## TODO
 - [ ] add more file support (other languages, docs, PDFs)
 - [ ] optimtize use of context window
 - [ ] estimate API cost
 - [ ] add Agents
 - [ ] LangChain memory instead of chat history