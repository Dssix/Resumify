from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import sys

# Add the project root to the Python path to allow for absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from backend.data_processing.Convert_Pdf import text as data_from_pdf
from backend.RAG.rag_pipeline import initialize_rag
from backend.call import generate_question, generate_report
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, FORCE_RE_INDEX

app = Flask(__name__, static_folder='frontend')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file part'}), 400
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Initialize RAG (ensure this is done appropriately, maybe once at startup)
            # For now, let's assume it's handled or re-evaluate if it needs to be here
            # initialize_rag(force_reindex=True) # This might be time-consuming for each request
            
            json_resume_data, extracted_text_data = data_from_pdf(file_path)
            # Store data in session or pass to next step if needed
            # For now, just return it
            return jsonify({
                'message': 'Resume uploaded and processed successfully',
                'resume_json': json_resume_data, 
                'resume_text': extracted_text_data
            }), 200
        except Exception as e:
            return jsonify({'error': f'Error processing PDF: {str(e)}'}), 500
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/generate_questions', methods=['POST'])
def get_interview_questions():
    try:
        app.logger.info("Received request for /generate_questions")
        data = request.get_json()
        if not data or 'resume_json' not in data or 'resume_text' not in data:
            app.logger.error("Missing resume data in request")
            return jsonify({'error': 'Missing resume data in request'}), 400
        
        resume_json = data['resume_json']
        resume_text = data['resume_text']
        # Log the types to confirm they are as expected
        app.logger.info(f"In /generate_questions: resume_json type: {type(resume_json)}, resume_text type: {type(resume_text)}")
        
        questions = generate_question(resume_json, resume_text)
        app.logger.info("Successfully generated questions")
        return jsonify({'questions': questions}), 200
    except Exception as e:
        # Log the full exception details
        app.logger.error(f"Error in /generate_questions endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error generating questions: {str(e)}'}), 500

@app.route('/generate_report', methods=['POST'])
def create_interview_report():
    user_answers = request.get_json()
    if not user_answers:
        return jsonify({'error': 'No answers provided'}), 400
    
    try:
        report = generate_report(user_answers) # user_answers is a dict like {'Question 1': 'text', 'Answer 1': 'text', ...}
        return jsonify({'report': report}), 200
    except Exception as e:
        return jsonify({'error': f'Error generating report: {str(e)}'}), 500

# Placeholder for RAG initialization - ideally done once at startup
# initialize_rag(force_reindex=True)

if __name__ == '__main__':
    # Ensure RAG is initialized before starting the app
    # This might take time, consider logging or a loading indicator if run in production
    print("Initializing RAG system...")
    initialize_rag(force_reindex=FORCE_RE_INDEX) # Use FORCE_RE_INDEX from config
    print("RAG system initialized.")
    app.run(debug=True, use_reloader=False)