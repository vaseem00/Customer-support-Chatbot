from flask import Flask, render_template, session, request,jsonify, send_from_directory, render_template_string
from flask_cors import CORS

#from chat import get_response
from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import ElasticVectorSearch, Pinecone, Weaviate, FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import os
os.environ["OPENAI_API_KEY"] = "API_KEY"


app = Flask(__name__)
CORS(app, supports_credentials=True)

reader = PdfReader('gate.pdf')

# read data from the file and put them into a variable called raw_text
raw_text = ''
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    if text:
        raw_text += text

# We need to split the text that we read into smaller chunks so that during information retreival we don't hit the token size limits. 

text_splitter = CharacterTextSplitter(        
    separator = "\n",
    chunk_size = 1000,
    chunk_overlap  = 200,
    length_function = len,
)
texts = text_splitter.split_text(raw_text)

embeddings = OpenAIEmbeddings()
docsearch = FAISS.from_texts(texts, embeddings)
chain = load_qa_chain(OpenAI(), chain_type="stuff")

@app.get("/")
def index_get():
    return render_template('base.html')

@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    # cehck if text is valid
    #response =  get_response(text)
    docs = docsearch.similarity_search(text)
    response = chain.run(input_documents=docs, question=text)
    message =  {"answer": response}
    print(message)
    return jsonify(message)

@app.route("/chatbox_embed.js")
def embed_js():
    return render_template_string(open("chatbox_embed.js").read()), 200, {'Content-Type': 'application/javascript'}



if __name__ == "__main__":
    app.run(debug=True)
