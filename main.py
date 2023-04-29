import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain


def load_docs(root_dir):
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
    texts = text_splitter.split_documents(docs)
    db = FAISS.from_documents(texts, embeddings)
    return db


def setup_retriever(db):
    retriever = db.as_retriever()
    retriever.search_kwargs['distance_metric'] = 'cos'
    retriever.search_kwargs['fetch_k'] = 20
    retriever.search_kwargs['maximal_marginal_relevance'] = True
    retriever.search_kwargs['k'] = 20
    return retriever


def setup_chain(model, retriever):
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


# root_dir = '../../../..'

# docs = load_docs(root_dir)
# text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
# embeddings = OpenAIEmbeddings(disallowed_special=())

# db = create_faiss_db(docs, text_splitter, embeddings)
# db.save_local('langchain-db')
# dbb = FAISS.load_local('langchain-db', embeddings=embeddings)

# retriever = setup_retriever(dbb)
# model = ChatOpenAI(model='gpt-3.5-turbo')
# qa = setup_chain(model, retriever)

# questions = [
#     "How can I store and load FAISS vector stores?",
# ]

# ask_questions(questions, qa)

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

    # Start interactive chat
    parser_chat = subparsers.add_parser("chat", help="Start interactive chat")

    args = parser.parse_args()

    if args.command == "init":
        init_cheatcode_directory()
        # ...

    elif args.command == "chat":
        root_dir = '../../../..'
        docs = load_docs(root_dir)
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        embeddings = OpenAIEmbeddings(disallowed_special=())

        db_path = os.path.join(".cheatcode/db", "langchain-db")
        db = FAISS.load_local(db_path, embeddings=embeddings)
        retriever = setup_retriever(db)
        model = ChatOpenAI(model='gpt-3.5-turbo')
        qa = setup_chain(model, retriever)

        interactive_chat(qa)


if __name__ == "__main__":
    main()