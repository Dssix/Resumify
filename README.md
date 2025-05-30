# Resumify - Your Personal AI Resume Coach

Resumify is a web application that helps you practice for job interviews by generating questions based on your resume and providing feedback on your answers.

## Prerequisites

*   Python 3.x
*   pip (Python package installer)

## Setup

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository-url>
    cd Resumify
    ```

2.  **Create and activate a virtual environment:**

    *   **Windows:**
        ```bash
        python -m venv .venv
        .venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables (Optional but Recommended):**
    Create a `.env` file in the root directory of the project and add any necessary environment variables. For example, API keys for LLM services if you are using them directly.
    ```
    # .env file example
    # OPENAI_API_KEY=your_openai_api_key_here
    ```
    The application uses `python-dotenv` to load these variables. Refer to `config.py` to see how environment variables might be used.

## Running the Application

1.  **Ensure your virtual environment is activated.** (See step 2 in Setup)

2.  **Start the Flask application:**
    ```bash
    python app.py
    ```

3.  **Open your web browser and navigate to:**
    [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## How to Use

1.  Once the application is running, open the web interface.
2.  Upload your resume (PDF format is supported).
3.  The application will process your resume and generate interview questions.
4.  Answer the questions one by one. You can use voice input if your browser and system support it.
5.  After answering all questions, the application will generate a feedback report.
6.  You can click "Start Over" to begin a new session with a different resume or the same one.

## Project Structure

*   `.venv/`: Virtual environment directory.
*   `backend/`: Contains the Python backend logic.
    *   `data_processing/`: Scripts for PDF conversion and data loading.
    *   `RAG/`: Components for the Retrieval Augmented Generation pipeline (LLM interface, vector store, etc.).
    *   `call.py`: Handles calls to generate questions and reports.
    *   `Question_Display.py`: Manages question display logic (Note: was previously `Question_Disply.py`).
*   `config.py`: Configuration settings for the application.
*   `data/`: Sample data files (if any, for testing or default use).
*   `frontend/`: Contains the HTML, CSS, and JavaScript for the user interface.
    *   `index.html`: The main page of the application.
    *   `script.js`: Client-side JavaScript for interactivity.
    *   `style.css`: Styles for the application.
*   `reports/`: Directory where generated reports might be stored (if implemented).
*   `uploads/`: Directory where uploaded resumes are temporarily stored.
*   `vector_index/`: Directory for storing the vector database for RAG.
*   `app.py`: The main Flask application file.
*   `input_voice.py`: Utility for voice input (if used directly by backend components).
*   `keyword_store.py`: Manages keyword indexing and searching.
*   `main.py`: A script for potentially running parts of the backend logic directly (e.g., for testing).
*   `requirements.txt`: A list of Python packages required for the project.
*   `speech.py`: Utility for text-to-speech functionality.

## Stopping the Application

*   To stop the Flask development server, press `Ctrl+C` in the terminal where it's running.
*   To deactivate the virtual environment:
    ```bash
    deactivate
    ```