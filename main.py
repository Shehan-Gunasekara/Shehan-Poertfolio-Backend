import json
from chatbot.chat import chatWithBot
from flask import Flask, request, jsonify
import os
from decouple import config

from langchain.memory import MongoDBChatMessageHistory
from langchain.chains import ConversationChain

from langchain import OpenAI, LLMChain

from langchain.output_parsers import PydanticOutputParser

from langchain.prompts.prompt import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
import random
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.output_parsers import (
    OutputFixingParser,
    PydanticOutputParser,
    OutputFixingParser,
)

from pydantic import BaseModel, Field
from langchain.callbacks import get_openai_callback

import tiktoken
import requests

from langchain.schema import (
    AIMessage,
)

# from flask_cors import CORS
import io
import pinecone
from langchain.vectorstores import Pinecone
from embeddingData.retrieve import getDataSet
from embeddingData.store import storeDataSet
from pymongo import MongoClient
os.environ["OPENAI_API_KEY"] = config(
    "OPENAI_API_KEY"
)  # Fix the environment variable name

app = Flask(__name__)

class virtualAssistants(BaseModel):
    answer: str = Field(
        description="please provide answer for the question based on provided data set as a string"
    )

@app.route("/storeembedding", methods=["POST"])
def storeEmbedding():
     return  storeDataSet()

@app.route("/conversation", methods=["POST"])
def conversation():
    data = request.get_json()
    client = MongoClient('mongodb+srv://shehan:shehan2025@cluster0.d5gvyao.mongodb.net/')
    db = client['portfolio']
    collection = db['chat _history']

    if "sessionID" in data:
        sessionID = data.get("sessionID")
     
        question = data.get("question")

        conversation = {"sessionID": sessionID, "message": question , "user": "client"}

        reponse = collection.insert_one(conversation)
        print("reponse", reponse)

        print("question", question)

        embendingResault = getDataSet(question)
        data_set = ''.join(str(obj) for obj in embendingResault['final_resault'])
        embendingToken = embendingResault['token']

        connection_url = os.environ.get(
            "MONGODB_URL", "mongodb+srv://shehan:shehan2025@cluster0.d5gvyao.mongodb.net/"
        )
        message_history = MongoDBChatMessageHistory(
            connection_string=connection_url, session_id=sessionID
        )

        tokens = 0

        llm = OpenAI(temperature=0 ,model_name="gpt-3.5-turbo-1106")

        _DEFAULT_TEMPLATE = """Imagine you are my virtual assistant. when user ask about details of me you should refer the provided data set and  answer their question based on the provided data set.
        This is the question that user asked : {input}
        This is the provided data set about me : {data_set}
        This is conversation history between you and user : {history}. 
        Format the response based on the following instructions "{formatting_instructions}"
        """
        parser = PydanticOutputParser(pydantic_object=virtualAssistants)
        format_instructions = parser.get_format_instructions()
        PROMPT = PromptTemplate(
            input_variables=["history", "input"],
            template=_DEFAULT_TEMPLATE,
            partial_variables={"formatting_instructions": format_instructions , "data_set":data_set},
        )
        memories = ConversationBufferMemory(
            k=3,
            chat_memory=message_history,
        )

        conversation = ConversationChain(
            llm=llm,
            verbose=False,
            prompt=PROMPT,
            memory=memories,
        )
        with get_openai_callback() as cb:
            conv = conversation.predict(input=question)
            print("TOKEN USAGE END INTERVIEW : ")
            print(cb)
            tokens = tokens + cb.total_tokens
        print("ADD TO DB----------------------------------")
        print("conv", conv)
        try:
            response_obj = parser.parse(conv)
            encoding = tiktoken.encoding_for_model("text-davinci-003")
            output_tokens = len(encoding.encode(conv))
            tokens = tokens + output_tokens
            answer = response_obj.answer
            conversation = {"sessionID": sessionID, "message": answer , "user": "agent"}
            collection.insert_one(conversation)
            return jsonify({"data": {"answer": answer, "tokens": tokens}}), 201
        except (json.JSONDecodeError, TypeError):
            new_parser = OutputFixingParser.from_llm(parser=parser, llm=llm)
            response_obj = new_parser.parse(conv)
            encoding = tiktoken.encoding_for_model("text-davinci-003")
            output_tokens = len(encoding.encode(conv))
            tokens = tokens + output_tokens
            answer = response_obj.answer
            conversation = {"sessionID": sessionID, "message": answer , "user": "agent"}
            collection.insert_one(conversation)
            return jsonify({"data": {"answer": answer, "tokens": tokens}}), 201

    else:
        return jsonify({"error": "Invalid input data. Required fields are empty."}), 400

@app.route("/aibot", methods=["POST"])
def aibot():
    data = request.get_json()
    if "sessionID" in data:
        sessionID = data.get("sessionID")
        answer=chatWithBot(data.get("question"))
        return jsonify({"data": {"answer": answer}}), 201

    else:    
        return jsonify({"error": "Invalid input data. Required fields are empty."}), 400


if __name__ == "__main__":
    app.run(debug=True)
