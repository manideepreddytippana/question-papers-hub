import os
from flask import Flask, request, jsonify, send_from_directory, url_for
from werkzeug.utils import secure_filename
import database as db
import PyPDF2
import requests
from dotenv import load_dotenv
import aiohttp

load_dotenv()

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Static dropdown values (no dynamic population)
STATIC_SUBJECTS = [
    'Mathematics-I',
    'Physics',
    'Chemistry',
    'Programming in C',
    'Data Structures',
    'Database Management Systems'
]

STATIC_BRANCHES = [
    'Computer Science',
    'Information Technology',
    'Electronics and Communication',
    'Mechanical Engineering',
    'Civil Engineering'
]

STATIC_REGULATIONS = [
    'R16',
    'R18',
    'R20',
    'R22'
]

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Gemini API Helper Function ---
async def get_summary_from_gemini(text):
    """Sends text to Gemini API and gets a summary."""
    chatHistory = [{"role": "user", "parts": [{"text": text}]}]
    payload = {"contents": chatHistory}
    # IMPORTANT: Replace with your actual API Key
    apiKey = os.getenv('API_KEY')
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={apiKey}"
    
    try:
        response = requests.post(apiUrl, json=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        result = response.json()
        
        if (result.get('candidates') and result['candidates'][0].get('content') and
            result['candidates'][0]['content'].get('parts')):
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            print("API Response was not in the expected format:", result)
            return "Could not extract a valid summary from the API response."
            
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        return f"Error communicating with the analysis service: {e}"
    except (KeyError, IndexError, TypeError) as e:
        print(f"API Response Parsing Error: {e}")
        return "Error parsing the summary from the API response."

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/summary/<filename>')
def summary_page(filename):
    return send_from_directory('static', 'summary.html')

@app.route('/api/analyze/<filename>', methods=['GET'])
async def analyze_pdf(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found."}), 404

    try:
        text = ""
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()

        if not text.strip():
            return jsonify({"error": "Could not extract any text from this PDF."}), 400

        prompt_for_gemini = f"Summarize the key topics and question types from this question paper:\n\n{text}"
        summary = await get_summary_from_gemini(prompt_for_gemini)

        return jsonify({"filename": filename, "summary": summary})

    except Exception as e:
        print(f"Error during PDF analysis for {filename}: {e}")
        return jsonify({"error": f"An unexpected error occurred during analysis: {e}"}), 500

@app.route('/api/paper/delete/<filename>', methods=['DELETE'])
def delete_paper_file(filename):
    """API endpoint to delete a paper."""
    if not filename:
        return jsonify({"error": "Invalid filename provided"}), 400

    safe_filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)

    try:
        # Step 1: Delete the record from the database
        db.delete_paper(safe_filename)

        # Step 2: Delete the physical file from the server
        if os.path.exists(filepath):
            os.remove(filepath)
        else:
            print(f"Warning: File '{safe_filename}' not found on disk but DB entry was deleted.")

        return jsonify({"success": f"Paper '{safe_filename}' deleted successfully."}), 200

    except Exception as e:
        print(f"Error deleting paper {safe_filename}: {e}")
        return jsonify({"error": "An internal error occurred. Could not delete the paper."}), 500

# --- Multi-File Analysis Endpoint ---

@app.route('/api/analyze-multiple', methods=['POST'])
async def analyze_multiple_pdfs():
    """Extracts text from multiple PDFs and performs a comparative analysis."""
    data = request.get_json()
    filenames = data.get('filenames')
    user_prompt = data.get('prompt')

    if not filenames or not isinstance(filenames, list) or len(filenames) < 2:
        return jsonify({"error": "Please select at least two files for analysis."}), 400

    if not user_prompt:
        return jsonify({"error": "An analysis instruction is required."}), 400

    combined_text = ""

    for filename in filenames:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))

        if not os.path.exists(filepath):
            return jsonify({"error": f"File not found: {filename}"}), 404

        try:
            text = ""
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""

            combined_text += f"--- START OF DOCUMENT: {filename} ---\n\n{text}\n\n--- END OF DOCUMENT: {filename} ---\n\n"

        except Exception as e:
            return jsonify({"error": f"Failed to read or parse {filename}: {e}"}), 500

    final_prompt = (
        "You are an expert academic assistant. Your task is to perform a detailed comparative analysis of the following university question papers.\n\n"
        f"USER'S INSTRUCTION: \"{user_prompt}\"\n\n"
        "Based on the user's instruction, analyze the content of the documents provided below. "
        "When comparing questions, consider both direct textual matches and semantic similarities (i.e., questions asking the same thing with different wording). "
        "Present your findings in a clear, well-structured, and easy-to-read format. Use markdown for formatting if appropriate.\n\n"
        f"{combined_text}"
    )

    try:
        analysis_result = await get_summary_from_gemini(final_prompt)
        return jsonify({"analysis_result": analysis_result})

    except Exception as e:
        print(f"Error during multi-file analysis: {e}")
        return jsonify({"error": f"An unexpected error occurred during analysis: {e}"}), 500

@app.route('/api/papers', methods=['GET'])
def get_papers():
    try:
        papers = db.get_all_papers()
        return jsonify(papers)
    except Exception as e:
        print(f"Error fetching papers: {e}")
        return jsonify({"error": "Failed to fetch papers"}), 500

@app.route('/api/upload', methods=['POST'])
def upload_paper():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    subject = request.form.get('subject')
    branch = request.form.get('branch')
    regulation = request.form.get('regulation')

    if not all([subject, branch, regulation]):
        return jsonify({"error": "Missing subject, branch, or regulation"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if os.path.exists(filepath):
            base, extension = os.path.splitext(filename)
            i = 1
            while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], f"{base}_{i}{extension}")):
                i += 1
            filename = f"{base}_{i}{extension}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        file.save(filepath)

        try:
            db.add_paper(subject, branch, regulation, filename)
            file_url = url_for('uploaded_file', filename=filename)
            return jsonify({"success": "File uploaded successfully", "filename": filename, "url": file_url}), 201

        except Exception as e:
            print(f"Database error: {e}")
            os.remove(filepath)
            return jsonify({"error": "Failed to save paper details"}), 500

    return jsonify({"error": "File type not allowed"}), 400

@app.route('/uploads/<filename>', endpoint='uploaded_file')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Static dropdown endpoints - no database queries needed
@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    return jsonify(STATIC_SUBJECTS)

@app.route('/api/branches', methods=['GET'])
def get_branches():
    return jsonify(STATIC_BRANCHES)

@app.route('/api/regulations', methods=['GET'])
def get_regulations():
    return jsonify(STATIC_REGULATIONS)

if __name__ == '__main__':
    app.run(debug=True)