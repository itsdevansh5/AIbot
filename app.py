import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext, set_global_service_context
from llama_index.llms.cohere import Cohere

# Load environment variables from .env file
load_dotenv()

COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY environment variable not set. Please check your .env file.")

DATA_DIR = "data"

# LlamaIndex setup
llm = Cohere(api_key=COHERE_API_KEY)
service_context = ServiceContext.from_defaults(llm=llm)
set_global_service_context(service_context)

documents = SimpleDirectoryReader(DATA_DIR).load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_query = request.json.get("query", "")
    response = query_engine.query(user_query)
    return jsonify({"response": response.response})

if __name__ == "__main__":
    app.run(debug=True)
