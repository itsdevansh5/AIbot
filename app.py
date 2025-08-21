import os
import re
import json
import time
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import cohere
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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

# Global variables for our knowledge base
data_chunks = []
vectorizer = None
tfidf_matrix = None
knowledge_base = {}
data_file_path = "data/data.json"

# Common greetings to identify simple hello messages
GREETINGS = [
    "hello", "hi", "hey", "greetings", "good morning", "good afternoon", 
    "good evening", "howdy", "hola", "what's up", "yo"
]

# Predefined answers for common questions
PREDEFINED_ANSWERS = {
    "application deadline": "The application deadline for most programs is June 15th for the fall semester and November 15th for the spring semester.",
    "application fee": "The application fee is ₹1,400 for SRMJEEE exam. For regular admission, there's a one-time non-refundable registration fee of ₹10,000 or ₹15,000 depending on the program.",
    "required documents": "You'll need to submit your academic transcripts, recommendation letters, statement of purpose, and test scores (if applicable).",
    "hostel fees": "Hostel fees range from ₹1.5 lakhs to ₹3.5 lakhs per year depending on the campus and room type.",
    "hostel facilities": "Our hostels provide Wi-Fi, laundry facilities, common rooms, 24/7 security, gymnasium, playgrounds, and meal plans with multiple cuisine options.",
    "contact information": "For more information, please contact the admissions office at admissions@srmist.edu.in or call (044) 27450000.",
    "scholarships": "We offer merit-based and need-based scholarships. The application deadline for scholarships is the same as the admission deadline.",
    "email": "The college email address is admissions@srmist.edu.in. For hostel queries, contact hostel.helpdesk.ktr@srmist.edu.in.",
    "email address": "The college email address is admissions@srmist.edu.in. For hostel queries, contact hostel.helpdesk.ktr@srmist.edu.in.",
    "admission procedure": "Admission is done through SRMJEEE entrance exam or based on qualifying exam marks. You need to apply online via SRM's application portal, submit required documents, and appear for counseling if selected.",
    "admission process": "Admission is done through SRMJEEE entrance exam or based on qualifying exam marks. You need to apply online via SRM's application portal, submit required documents, and appear for counseling if selected.",
    "how to apply": "Apply online via SRM's application portal with e-payment. All fields marked * are mandatory. Upload scanned photo (200x230 px) and signature (140x60 px). Save your application number after submission."
}

def chunk_text(text, max_chunk_size=500):
    """
    Splits text into chunks of a maximum size, prioritizing complete sentences.
    """
    chunks = []
    # Split by sentences while preserving the delimiters
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def preprocess_data():
    """
    Preprocess the data and create TF-IDF vectors for faster retrieval.
    """
    global data_chunks, vectorizer, tfidf_matrix, knowledge_base
    
    if not os.path.exists(data_file_path):
        logging.warning(f"Data file not found at {data_file_path}. The chatbot will not be grounded.")
        return
    
    try:
        # Load the JSON data
        with open(data_file_path, "r", encoding="utf-8") as f:
            knowledge_base = json.load(f)
        
        # Convert the JSON structure to text for chunking
        text_content = json.dumps(knowledge_base, ensure_ascii=False)
        data_chunks = chunk_text(text_content)
            
        logging.info(f"Loaded and chunked {len(data_chunks)} documents from {data_file_path}")
        
        # Create TF-IDF vectors for faster retrieval
        if data_chunks:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(data_chunks)
    
    except Exception as e:
        logging.error(f"Error loading data: {e}")

def get_relevant_chunks(query, top_k=3):
    """
    Use TF-IDF to quickly find the most relevant chunks for the query.
    """
    if not data_chunks or tfidf_matrix is None:
        return []
    
    # Vectorize the query
    query_vec = vectorizer.transform([query])
    
    # Calculate cosine similarities
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    # Get indices of top_k most similar chunks
    relevant_indices = np.argsort(similarities)[-top_k:][::-1]
    
    # Return the most relevant chunks
    return [data_chunks[i] for i in relevant_indices if similarities[i] > 0.1]

def is_greeting(message):
    """
    Check if the message is a simple greeting.
    """
    message_lower = message.lower().strip()
    return any(greeting in message_lower for greeting in GREETINGS)

def check_predefined_answers(query):
    """
    Check if the query matches any predefined questions.
    """
    query_lower = query.lower()
    for key in PREDEFINED_ANSWERS:
        if key in query_lower:
            return PREDEFINED_ANSWERS[key]
    return None

def extract_direct_answer(query):
    """
    Try to extract a direct answer from the knowledge base for specific queries.
    """
    query_lower = query.lower()
    
    # Check for email queries
    if "email" in query_lower:
        if "hostel" in query_lower:
            return "For hostel queries, please contact hostel.helpdesk.ktr@srmist.edu.in or call 044-27453159."
        else:
            return "The college admission email is admissions@srmist.edu.in. You can also call +91-44-27450000."
    
    # Check for contact information
    if "contact" in query_lower or "phone" in query_lower or "number" in query_lower:
        return "For admissions: admissions@srmist.edu.in or +91-44-27450000. For hostel: hostel.helpdesk.ktr@srmist.edu.in or 044-27453159."
    
    # Check for specific program fees
    if "fee" in query_lower or "fees" in query_lower or "cost" in query_lower:
        if "b.tech" in query_lower or "computer" in query_lower:
            return "B.Tech Computer Science and Engineering fees range from ₹2.25 lakhs to ₹5 lakhs per year depending on the campus."
        elif "m.tech" in query_lower:
            return "M.Tech fees are approximately ₹1.5-1.6 lakhs per year."
        elif "hostel" in query_lower:
            return "Hostel fees range from ₹1.5 lakhs to ₹3.5 lakhs per year depending on the campus and room type."
    
    return None

# Preprocess data at startup
preprocess_data()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask_chatbot():
    start_time = time.time()
    user_query = request.json.get("query")
    if not user_query:
        return jsonify({"answer": "Please enter a query."})
    
    # Check for greetings
    if is_greeting(user_query):
        response_time = time.time() - start_time
        logging.info(f"Response time: {response_time:.2f} seconds")
        return jsonify({"answer": "Hello! I'm here to help with college admission and hostel queries. How can I assist you today?"})
    
    # Check for predefined answers
    predefined_answer = check_predefined_answers(user_query)
    if predefined_answer:
        response_time = time.time() - start_time
        logging.info(f"Response time: {response_time:.2f} seconds")
        return jsonify({"answer": predefined_answer})
    
    # Try to extract a direct answer
    direct_answer = extract_direct_answer(user_query)
    if direct_answer:
        response_time = time.time() - start_time
        logging.info(f"Response time: {response_time:.2f} seconds")
        return jsonify({"answer": direct_answer})
    
    # Use hybrid approach: TF-IDF for retrieval, then Cohere for answering
    relevant_chunks = get_relevant_chunks(user_query)
    
    if not relevant_chunks:
        # If no relevant chunks found, use Cohere without documents
        try:
            response = co.chat(
                model="command-r",
                message=user_query,
                preamble="You are a helpful college admissions and hostel chatbot for SRM Institute of Science and Technology. If you don't know the answer, suggest contacting the admissions office at admissions@srmist.edu.in."
            )
            answer = response.text
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            answer = "Sorry, I am unable to process your request at the moment. Please try again later or contact admissions@srmist.edu.in for assistance."
    else:
        # Use Cohere with only the most relevant documents
        try:
            preamble = "You are a helpful college admissions and hostel chatbot for SRM Institute of Science and Technology. Use the provided documents to answer the question accurately and concisely. If the information isn't in the documents, say you don't know and suggest contacting admissions@srmist.edu.in."
            
            response = co.chat(
                model="command-r",
                message=user_query,
                documents=[{"id": str(i), "text": doc} for i, doc in enumerate(relevant_chunks)],
                preamble=preamble
            )
            answer = response.text
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            answer = "Sorry, I am unable to process your request at the moment. Please try again later or contact admissions@srmist.edu.in for assistance."
    
    response_time = time.time() - start_time
    logging.info(f"Response time: {response_time:.2f} seconds")
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)