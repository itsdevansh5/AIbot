# SRM Admission Assistant Chatbot

This project is an AI-powered chatbot designed to assist with college admission and hostel-related queries for the SRM Institute of Science and Technology. It uses a Retrieval-Augmented Generation (RAG) architecture to provide accurate and relevant answers based on a custom, pre-defined knowledge base.

### Live Demo

You can view a live demonstration of the chatbot here:
**[https://srm-admission-assistant.netlify.app/](https://srm-admission-assistant.netlify.app/)**

***

## Key Features

* **Python Flask Backend:** A lightweight and efficient web server for handling API requests.
* **Cohere API:** Utilizes a powerful Large Language Model (LLM) from Cohere for natural language understanding and response generation.
* **Retrieval-Augmented Generation (RAG):** The chatbot's knowledge is grounded in a local JSON file, ensuring responses are relevant and do not hallucinate.
* **Responsive Frontend:** A modern, mobile-friendly web interface for a seamless user experience.

***

## Project Structure

Your project is organized as follows:

I can't generate a file directly, but I can give you the content formatted as a Markdown file. You can copy the text below and save it as README.md in your project's root directory.

Markdown

# SRM Admission Assistant Chatbot

This project is an AI-powered chatbot designed to assist with college admission and hostel-related queries for the SRM Institute of Science and Technology. It uses a Retrieval-Augmented Generation (RAG) architecture to provide accurate and relevant answers based on a custom, pre-defined knowledge base.

### Live Demo

You can view a live demonstration of the chatbot here:
**[https://srm-admission-assistant.netlify.app/](https://srm-admission-assistant.netlify.app/)**

***

## Key Features

* **Python Flask Backend:** A lightweight and efficient web server for handling API requests.
* **Cohere API:** Utilizes a powerful Large Language Model (LLM) from Cohere for natural language understanding and response generation.
* **Retrieval-Augmented Generation (RAG):** The chatbot's knowledge is grounded in a local JSON file, ensuring responses are relevant and do not hallucinate.
* **Responsive Frontend:** A modern, mobile-friendly web interface for a seamless user experience.

***

## Project Structure

Your project is organized as follows:

/srm_chatbot_project
|-- .env
|-- app.py
|-- start.sh
|-- requirements.txt
|-- /data
|   |-- data.json
|-- /templates
|   |-- index.html

* **`app.py`**: The core Python Flask application. It handles the web server, loads the RAG data, and communicates with the Cohere API.
* **`data/data.json`**: The RAG knowledge base. This file contains structured data (e.g., questions, answers, fees, eligibility) that the chatbot uses to find information.
* **`templates/index.html`**: The frontend of the chatbot, including all the HTML, CSS, and JavaScript for the user interface.
* **`requirements.txt`**: Lists all the necessary Python libraries for the project.
* **`start.sh`**: A shell script used for deploying the application to production environments like Render.
* **`.env`**: A hidden file for securely storing your Cohere API key.

***

## Local Setup

### 1. Prerequisites

Make sure you have the following installed on your machine:
* Python 3.11+
* pip (Python package installer)

### 2. Installation

1.  **Clone the repository:** Download or clone your project files to your local machine.

2.  **Set up a virtual environment** (recommended): This isolates your project's dependencies from your system's Python packages.
    ```bash
    python -m venv venv
    ```
    Activate the environment:
    * **On Windows:** `venv\Scripts\activate`
    * **On macOS/Linux:** `source venv/bin/activate`

3.  **Install dependencies:** Navigate to your project directory and install the required packages.
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuration

1.  **Get your Cohere API Key:** Sign up or log in to your Cohere account to get your API key.
2.  **Create the `.env` file:** In the root of your project directory, create a file named `.env`.
3.  **Add your key:** Add your API key to the file in the following format:
    ```
    COHERE_API_KEY="YOUR_COHERE_API_KEY"
    ```
    **Note:** Replace `"YOUR_COHERE_API_KEY"` with your actual key. Do not share this key publicly.

### 4. Running the Application

Once everything is set up, you can run the Flask server.
```bash
python app.py
Your chatbot will be live at http://127.0.0.1:5000.

# SRM Admission Assistant Chatbot

This project is an AI-powered chatbot designed to assist with college admission and hostel-related queries for the SRM Institute of Science and Technology. It uses a Retrieval-Augmented Generation (RAG) architecture to provide accurate and relevant answers based on a custom, pre-defined knowledge base.

### Live Demo


## Key Features