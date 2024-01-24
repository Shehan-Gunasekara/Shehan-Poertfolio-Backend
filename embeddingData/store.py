import streamlit as st
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import FAISS
# from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
import os
from decouple import config
import json

from langchain.vectorstores import Pinecone,Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
from flask import  jsonify
os.environ["OPENAI_API_KEY"] = config(
    "OPENAI_API_KEY"
) 

def storeDataSet():
    try:
        class Document:
            def __init__(self, page_content, metadata):
                self.page_content = page_content
                self.metadata = metadata

        with open('embeddingData/data.json', 'r') as file:
            data = json.load(file)
            print(data)

        documents = []
        for i, item in enumerate(data):
            page_content = f'ï»¿questions: {item["question"]}\nAnswerr for the relevant question: {item["answer"]}'
            metadata = {'source': 'abcd.csv', 'row': i}
            document = Document(page_content, metadata)
            documents.append(document)


        embeddings = OpenAIEmbeddings()

        pinecone.init(api_key=os.environ.get('PINECONE_API_KEY'),
                      environment=os.environ.get('PINECONE_ENVIRONMENT'))
        index_name = os.environ.get('PINECONE_INDEX')

        docsearch=Pinecone.from_texts([t.page_content for t in documents], embeddings,index_name=index_name )

        return jsonify({"data": "Successfully stored data"}), 201
    except Exception as e:
       return jsonify({"data": f"Error storing data: {e}"}), 400

