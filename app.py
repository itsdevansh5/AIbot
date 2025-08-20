import os
import re
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import cohere
import logging

# Set up logging for better feedback
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Load your Cohere API key
load_dotenv()
cohere_api_key = os.getenv("COHERE_API_KEY")
if not cohere_api_key:
    logging.error("COHERE_API_KEY not found. Please set it in your .env file.")
    exit(1)

# Initialize Cohere client
co = cohere.Client(cohere_api_key)

# A simple list to act as your "knowledge base" for this example
data_chunks = []
data_file_path = "data/raw_data.txt"

def chunk_text(text, max_chunk_size=500):
    """
    Splits text into chunks of a maximum size.
    """
    chunks = []
    split_points = re.split(r'(\.|\?|!|\n\n)', text)
    current_chunk = ""
    for point in split_points:
        if len(current_chunk) + len(point) <= max_chunk_size:
            current_chunk += point
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = point.strip()
    if current_chunk:
        chunks.append(current_chunk.strip())
    return [chunk for chunk in chunks if chunk]

# Check if the data file exists and load it
if os.path.exists(data_file_path):
    with open(data_file_path, "r", encoding="utf-8") as f:
        raw_content = f.read()
    data_chunks = chunk_text(raw_content)
    logging.info(f"Loaded and chunked {len(data_chunks)} documents from {data_file_path}")
else:
    logging.warning(f"Data file not found at {data_file_path}. The chatbot will not be grounded.")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask_chatbot():
    user_query = request.json.get("query")
    if not user_query:
        return jsonify({"answer": "Please enter a query."})
    
    full_response = ""
    
    # New and improved preamble with a personality and strict instructions
    preamble = "You are a very sweet and helpful college admissions and hostel chatbot. Your purpose is to provide accurate and concise answers. You must only use the information provided in the documents. Do not guess, make up facts, or provide information that is not explicitly available in the documents. If a question cannot be answered from the provided documents, politely state that you do not have that information."

    try:
        response = co.chat(
            model="command-r",
            message=user_query,
            documents=[{"id": str(i), "text": doc} for i, doc in enumerate(data_chunks)],
            preamble=preamble
        )

        answer = response.text
        
        full_response = answer
        
        return jsonify({"answer": full_response})

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"answer": "Sorry, I am unable to process your request at the moment. Please try again later."})

if __name__ == "__main__":
    app.run(debug=True)