import os
from pathlib import Path

from langchain import PromptTemplate
from langchain import hub
from langchain.docstore.document import Document
from langchain.schema import StrOutputParser
from langchain.schema.prompt_template import format_document
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader

from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter


from langchain_qdrant import Qdrant

import requests


os.environ["OPENAI_API_KEY"] = "" #APIキーを入力

current_dir = os.getcwd()

pdf_file_path = r"" #参考資料（pdf）のファイルパスを入力
pdf_loader2 = PyPDFLoader(pdf_file_path)
pdf_data2 = pdf_loader2.load()
 
txt_file_path = r"" #参考資料（txt）のファイルパスを入力
txt_loader = TextLoader(txt_file_path,encoding='utf-8')
txt_data = txt_loader.load()

all_pages = pdf_data2 + txt_data
combined_text = "\n".join([page.page_content for page in all_pages])

print("\n\n資料を読み込みました。エンベディングとDB格納を開始します。\n\n")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
    add_start_index=True
)

docs = text_splitter.create_documents([combined_text])

embeddings = OpenAIEmbeddings()

url = "http://localhost:6333"
qdrant = Qdrant.from_documents(
    docs,
    embeddings,
    url=url,
    prefer_grpc=True,
    collection_name="ChildCare_PdfData",
)

retriever = qdrant.as_retriever(search_kwargs={"k": 4})

print("\n\nVectorDBへの格納が完了しました！\n\n")
