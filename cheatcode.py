#! /usr/bin/env python3
import os
import argparse
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

FREE_OPENAI_API_KEY=os.environ['OPENAI_API_KEY']
GPT4_OPENAI_API_KEY=os.environ['OPENAI_API_KEY_GPT4']

def load_docs(root_dir):
    print("Loading source files.")
    docs = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith('.py') and '/.venv/' not in dirpath:
                try: 
                    loader = TextLoader(os.path.join(dirpath, file), encoding='utf-8')
                    docs.extend(loader.load_and_split())
                except Exception as e: 
                    pass
    return docs


def create_faiss_db(docs, text_splitter, embeddings):
    print("Creating FAISS database.")
    texts = text_splitter.split_documents(docs)
    db = FAISS.from_documents(texts, embeddings)
    return db


def setup_retriever(db):
    print("Setting up retriever.")
    retriever = db.as_retriever()
    retriever.search_kwargs['distance_metric'] = 'cos'
    retriever.search_kwargs['fetch_k'] = 20
    retriever.search_kwargs['maximal_marginal_relevance'] = True
    retriever.search_kwargs['k'] = 20
    return retriever


def setup_chain(model, retriever):
    print("Setting up chain.")
    return ConversationalRetrievalChain.from_llm(model, retriever=retriever)


def ask_questions(questions, qa):
    chat_history = []
    for question in questions:  
        result = qa({"question": question, "chat_history": chat_history})
        chat_history.append((question, result['answer']))
        print(f"-> **Question**: {question} \n")
        print(f"**Answer**: {result['answer']} \n")

def init_cheatcode_directory():
    os.makedirs(".cheatcode", exist_ok=True)
    os.makedirs(".cheatcode/db", exist_ok=True)

def interactive_chat(qa):
    print("Starting interactive chat. Type 'exit' to end the chat.")
    chat_history = []

    while True:
        question = input("-> **Question**: ")
        if question.lower() == "exit":
            break

        result = qa({"question": question, "chat_history": chat_history})
        chat_history.append((question, result['answer']))
        print(f"**Answer**: {result['answer']} \n")


def main():
    parser = argparse.ArgumentParser(description="CheatCode CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Initialize CheatCode
    parser_init = subparsers.add_parser("init", help="Initialize CheatCode")
    parser_init.add_argument("directory", nargs="?", default=".", help="Directory to initialize CheatCode in (default: current directory)")

    # Start interactive chat
    parser_chat = subparsers.add_parser("chat", help="Start interactive chat")
    parser_chat.add_argument("directory", nargs="?", default=".", help="Directory to chat in (default: current directory)")

    args = parser.parse_args()

    if args.command == "init":
        root_dir = args.directory
        db_path = os.path.join(root_dir, ".cheatcode/db")
        if os.path.exists(db_path):
            print("CheatCode already initialized.")
            return
        init_cheatcode_directory()
        docs = load_docs(root_dir)
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        embeddings = OpenAIEmbeddings(openai_api_key=FREE_OPENAI_API_KEY ,disallowed_special=())

        db = create_faiss_db(docs, text_splitter, embeddings)
        print(f"Saving database to {db_path}")
        db.save_local(db_path)

        print("CheatCode initialized and database stored in .cheatcode/db.")

    elif args.command == "chat":
        # root_dir = args.directory
        root_dir = "/home/rasdani/git/mp-transformer"
        embeddings = OpenAIEmbeddings(disallowed_special=())

        db_path = os.path.join(root_dir, ".cheatcode/db")
        db = FAISS.load_local(db_path, embeddings=embeddings)
        retriever = setup_retriever(db)
        # model = ChatOpenAI(openai_api_key=FREE_OPENAI_API_KEY, model='gpt-3.5-turbo')
        model = ChatOpenAI(openai_api_key=GPT4_OPENAI_API_KEY, model='gpt-4')
        qa = setup_chain(model, retriever)

        interactive_chat(qa)


if __name__ == "__main__":
    main()