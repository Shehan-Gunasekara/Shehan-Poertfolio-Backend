import pinecone
import openai
import tiktoken
import os
def tokens_from_string(string, encoding_name):
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

# given an list of dictionaries with metadata, score, retrieve the item with the highest score and print metadata
def get_highest_score_resault(items):
    highest_score = 0
    highest_score_item = None
    for item in items:
        if item["score"] > highest_score:
            highest_score = item["score"]
            highest_score_item = item

    return highest_score_item["metadata"]["text"]

def get_final_resault(items):
     resaultArray=[]
     for item in items:
        resaultArray.append(item["metadata"]["text"])
     return resaultArray
          
# get the Pinecone API key and environment
def getDataSet(query):
    pinecone_api = os.environ.get('PINECONE_API_KEY')
    pinecone_env = os.environ.get('PINECONE_ENVIRONMENT')
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    pinecone.init(api_key=pinecone_api, environment=pinecone_env)

    index = pinecone.Index(os.environ.get('PINECONE_INDEX'))

    your_query = query

    token =tokens_from_string(your_query, "cl100k_base")
    print("token---------------",token)
    query_vector = openai.Embedding.create(
        input=your_query,
        model="text-embedding-ada-002"
    )["data"][0]["embedding"]

    search_response = index.query(
        top_k=1,
        vector=query_vector,
        include_metadata=True)

    print("Question -------------------------------------------", your_query)
    print("Highest score resault: ", get_highest_score_resault(search_response['matches']))
    final_resault = get_final_resault(search_response['matches'])
    reponse={"token":token,"final_resault":final_resault}
    print("Resault -------------------------------------------", reponse)
    return reponse
