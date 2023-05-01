#! /usr/bin/env python3
import os
import argparse
import subprocess
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') # free credits
# OPENAI_API_KEY_GPT4 = os.environ.get('OPENAI_API_KEY_GPT4') # waitlist access
MAX_TOKENS_LIMIT = 10000 # don't wanna be broke $$$


def load_docs(root_dir, changed_files_only=False):
    """
    Load documents from the specified root directory.

    Args:
        root_dir (str): Root directory to search for documents.
        changed_files_only (bool): If True, only load documents that have changed since the last commit.

    Returns:
        list: Loaded documents.
    """
    print("Loading source files.")
    docs = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith('.py') and '/.venv/' not in dirpath:
                try: 
                    loader = TextLoader(os.path.join(dirpath, file), encoding='utf-8')
                    docs.extend(loader.load_and_split())
                except Exception as e: 
                    print(f"Error loading file {file}: {e}")

    ### EXPERIMENTAL
    # if changed_files_only:
    #     git_command = "git diff --name-only HEAD"
    #     changed_files = subprocess.check_output(git_command.split(), cwd=root_dir).decode("utf-8").splitlines()

    # for dirpath, dirnames, filenames in os.walk(root_dir):
    #     for file in filenames:
    #         if file.endswith('.py') and '/.venv/' not in dirpath:
    #             file_path = os.path.join(dirpath, file)
    #             if not changed_files_only or file_path in changed_files:
    #                 try:
    #                     loader = TextLoader(file_path, encoding='utf-8')
    #                     docs.extend(loader.load_and_split())
    #                 except Exception as e:
    #                     print(f"Error loading file {file_path}: {e}")
    return docs


def create_faiss_db(docs, text_splitter, embeddings):
    """
    Create a FAISS database from the provided documents.

    Args:
        docs (list): List of documents to be indexed.
        text_splitter (CharacterTextSplitter): Text splitter instance.
        embeddings (OpenAIEmbeddings): Embeddings instance.

    Returns:
        FAISS: FAISS database instance.
    """
    print("Creating FAISS database.")
    texts = text_splitter.split_documents(docs)
    db = FAISS.from_documents(texts, embeddings)
    return db


def setup_retriever(db):
    """
    Set up a retriever instance using the given FAISS database.

    Args:
        db (FAISS): FAISS database instance.

    Returns:
        Retriever: Configured retriever instance.
    """
    print("Setting up retriever.")
    retriever = db.as_retriever()
    retriever.search_kwargs['distance_metric'] = 'cos'
    retriever.search_kwargs['fetch_k'] = 20
    retriever.search_kwargs['maximal_marginal_relevance'] = True
    retriever.search_kwargs['k'] = 3
    return retriever


def setup_chain(model, retriever):
    """
    Set up a conversational retrieval chain using the given model and retriever instances.

    Args:
        model (ChatOpenAI): Chat model instance.
        retriever (Retriever): Retriever instance.

    Returns:
        ConversationalRetrievalChain: Configured conversational retrieval chain.
    """
    print("Setting up chain.")
    return ConversationalRetrievalChain.from_llm(model, retriever=retriever, max_tokens_limit=MAX_TOKENS_LIMIT, return_source_documents=True)

def setup_qa(root_dir):
    embeddings = OpenAIEmbeddings(disallowed_special=())

    db_path = os.path.join(root_dir, ".cheatcode/db")
    db = FAISS.load_local(db_path, embeddings=embeddings)
    retriever = setup_retriever(db)

    model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model='gpt-3.5-turbo')
    # model = ChatOpenAI(openai_api_key=OPENAI_API_KEY_GPT4, model='gpt-4')

    qa = setup_chain(model, retriever)
    return qa

def ask_questions(questions, qa):
    """
    Ask a list of questions and print the answers.

    Args:
        questions (list): List of questions to ask.
        qa (ConversationalRetrievalChain): Conversational retrieval chain instance.
    """
    chat_history = []
    for question in questions:
        result = qa({"question": question, "chat_history": chat_history})
        chat_history.append((question, result['answer']))
        print(f"-> **Question**: {question} \n")
        print(f"**Answer**: {result['answer']} \n")


def init_cheatcode_directory():
    """
    Initialize CheatCode directory structure.
    """
    os.makedirs(".cheatcode", exist_ok=True)
    os.makedirs(".cheatcode/db", exist_ok=True)


def interactive_chat(qa):
    """
    Start an interactive chat session with the user.

    Args:
        qa (ConversationalRetrievalChain): Conversational retrieval chain instance.
    """
    print("Starting interactive chat. Type 'exit' to end the chat.")
    chat_history = []

    while True:
        question = input("-> **Question**: ")
        if question.lower() == "exit":
            break

        result = qa({"question": question, "chat_history": chat_history})
        chat_history.append((question, result['answer']))
        print(f"**Answer**: {result['answer']} \n")
        # print(f"Source documents: {result['source_documents']} \n")
        # print(f"**Chat history**: {chat_history} \n")

def main():
    parser = argparse.ArgumentParser(description="CheatCode CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    # initialize CheatCode
    parser_init = subparsers.add_parser("init", help="Initialize CheatCode")
    parser_init.add_argument("directory", nargs="?", default=".", help="Directory to initialize CheatCode in (default: current directory)")

    # start interactive chat
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
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY ,disallowed_special=())

        db = create_faiss_db(docs, text_splitter, embeddings)
        print(f"Saving database to {db_path}")
        db.save_local(db_path)

        print("CheatCode initialized and database stored in .cheatcode/db.")

    elif args.command == "chat":
        # root_dir = args.directory
        root_dir = "/home/rasdani/git/mp-transformer"
        qa = setup_qa(root_dir)

        interactive_chat(qa)


if __name__ == "__main__":
    main()