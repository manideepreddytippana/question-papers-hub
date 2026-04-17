import os
from flask import Flask, request, jsonify, send_from_directory, url_for, send_file
from werkzeug.utils import secure_filename
import database as db
import PyPDF2
import requests
from dotenv import load_dotenv
import io
import zipfile
import json
from datetime import datetime
import numpy as np
from question_processor import QuestionExtractor, QuestionAnalyzer

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

aiml_subjects = {
    "1-1": [
        "Matrices and Calculus (M1)",
        "Applied Physics (AP)",
        "Programming for Problem Solving (PPS)",
        "English for Skill Enhancement",
        "Environmental Science (ES)"
    ],
    "1-2": [
        "Ordinary Differential Equations and Vector Calculus (ODE)",
        "Engineering Chemistry",
        "Computer Aided Engineering Graphics (CAEG)",
        "Basic Electrical Engineering (BEE)",
        "Electronic Devices and Circuits (EDC)"
    ],
    "2-1": [
        "Mathematical and Statistical Foundations (MSF)",
        "Data Structures (DS)",
        "Computer Organization and Architecture (COA)",
        "Software Engineering",
        "Operating Systems (OS)"
    ],
    "2-2": [
        "Discrete Mathematics (DM)",
        "Automata Theory and Compiler Design (ATCD)",
        "Database Management Systems (DBMS)",
        "Introduction to Artificial Intelligence (AI)",
        "Object Oriented Programming through Java (OOP)"
    ],
    "3-1": [
        "Design and Analysis of Algorithms (DAA)",
        "Machine Learning (ML)",
        "Computer Networks (CN)",
        "Business Economics & Financial Analysis (BEFA)",
        "Web Programming (WP)",
        "Intellectual Property Rights (IPR)"
    ],
    "3-2": [
        "Fundamentals of Internet of Things (FIOT)",
        "Software Testing Methodologies (STM)",
        "Knowledge Representation and Reasoning (KRR)",
        "Data Analytics (DA)",
        "Natural Language Processing (NLP)"
    ],
    "4-1": [
        "Semantic Web (SW)",
        "Deep Learning (DL)",
        "Cloud Computing (CC)",
        "Nature Inspired Computing (NIC)",
        "Electronics for Health Care (EHC)",
        "Professional Practice, Law & Ethics (PPLE)"
    ],
    "4-2": [
        "Conversational AI (CA)",
        "AD HOC & Sensor Networks (ASN)",
        "Fundamentals of Social Network (FSN)"
    ]
}

aids_subjects = {
    "1-1": [
        "Matrices and Calculus (M1)",
        "Applied Physics (AP)",
        "Programming for Problem Solving (PPS)",
        "English for Skill Enhancement (ESE)",
        "Elements of Computer Science & Engineering (ECSE)",
        "Environmental Science (ES)"
    ],
    "1-2": [
        "Ordinary Differential Equations and Vector Calculus (ODE&VC)",
        "Engineering Chemistry (EC)",
        "Computer Aided Engineering Graphics (CAEG)",
        "Basic Electrical Engineering (BEE)",
        "Electronic Devices and Circuits (EDC)"
    ],
    "2-1": [
        "Mathematical and Statistical Foundations (MSF)",
        "Digital Electronics (DE)",
        "Data Structures (DS)",
        "Object Oriented Programming through Java (OOPJ)",
        "Computer Organization and Architecture (COA)"
    ],
    "2-2": [
        "Discrete Mathematics (DM)",
        "Introduction to Artificial Intelligence (AI)",
        "Database Management Systems (DBMS)",
        "Operating Systems (OS)",
        "Software Engineering (SE)"
    ],
    "3-1": [
        "Design and Analysis of Algorithms (DAA)",
        "Introduction to Data Science (IDS)",
        "Computer Networks (CN)",
        "Business Economics & Financial Analysis (BEFA)",
        "WEB PROGRAMMING (WP)",
        "Intellectual Property Rights (IPR)"
    ],
    "3-2": [
        "Automata Theory and Compiler Design (ATCD)",
        "Machine Learning (ML)",
        "Big Data Analytics (BDA)",
        "SOFTWARE TESTING METHODOLOGIES (STM)",
        "FUNDAMENTALS OF INTERNET OF THINGS (FIOT)",
        "Environmental Science (ES)"
    ],
    "4-1": [
        "Introduction to Predictive Analytics (IPA)",
        "Web and Social Media Analytics (WSMA)",
        "ELECTRONICS FOR HEALTH CARE (EHC)",
        "Professional Practice, Law & Ethics (PPLE)",
        "CRYPTOGRAPHY AND NETWORK SECURITY (CNS)",
        "CLOUD COMPUTING (CC)"
    ],
    "4-2": [
        "Professional Elective - V (PE5)",
        "Professional Elective - VI (PE6)",
        "Open Elective - III (OE3)",
        "Project Stage - II (Project)"
    ]
}

cse_subjects = {
    "1-1": [
        "Matrices and Calculus (M&C)",
        "Engineering Chemistry (EC)",
        "Programming for Problem Solving (PPS)",
        "Basic Electrical Engineering (BEE)",
        "Computer Aided Engineering Graphics (CAEG)"
    ],
    "1-2": [
        "Ordinary Differential Equations & Vector Calculus (ODE&VC)",
        "Applied Physics (AP)",
        "Engineering Workshop (EW)",
        "English for Skill Enhancement (ESE)",
        "Electronic Devices and Circuits (EDC)"
    ],
    "2-1": [
        "Digital Electronics (DE)",
        "Data Structures (DS)",
        "Computer Oriented Statistical Methods (COSM)",
        "Computer Organization & Architecture (COA)",
        "Object Oriented Programming through Java (OOPJ)"
    ],
    "2-2": [
        "Discrete Mathematics (DM)",
        "Business Economics & Financial Analysis (BEFA)",
        "Operating Systems (OS)",
        "Database Management Systems (DBMS)",
        "Software Engineering (SE)"
    ],
    "3-1": [
        "Design and Analysis of Algorithms (DAA)",
        "Computer Networks (CN)",
        "DevOps (DO)",
        "EMBEDDED SYSTEMS (ES)",
        "DATA ANALYTICS (DA)",
        "Intellectual Property Rights (IPR)"
    ],
    "3-2": [
        "Machine Learning (ML)",
        "Formal Languages & Automata Theory (FLAT)",
        "Artificial Intelligence (AI)",
        "FUNDAMENTALS OF INTERNET OF THINGS (FIOT)",
        "SOFTWARE TESTING METHODOLOGIES (STM)"
    ],
    "4-1": [
        "Cryptography & Network Security (CNS)",
        "Compiler Design (CD)",
        "ELECTRONICS FOR HEALTH CARE (EHC)",
        "CYBER SECURITY (CS)",
        "BLOCKCHAIN TECHNOLOGY (BT)"
    ],
    "4-2": [
        "Organizational Behavior (OB)",
        "Professional Elective-VI (PE6)",
        "Open Elective-III (OE3)"
    ]
}

R22_SEMESTER_SUBJECTS = {
    'CSE': cse_subjects,
    'CSE (AI & ML)': aiml_subjects,
    'CSE (AI & DS)': aids_subjects,
}

STATIC_SUBJECTS = [
    'Mathematics-I',
    'Physics',
    'Chemistry',
    'Programming in C',
    'Data Structures',
    'Database Management Systems'
]

STATIC_BRANCHES = [
    'CSE',
    'CSE (AI & ML)',
    'CSE (Cyber Security)',
    'CSE (Data Science)',
    'CSE (IoT)',
    'CSE (AI & DS)'
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

async def get_summary_from_gemini(text):
    chatHistory = [{"role": "user", "parts": [{"text": text}]}]
    payload = {"contents": chatHistory}
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
    if not filename:
        return jsonify({"error": "Invalid filename provided"}), 400

    safe_filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)

    try:
        db.delete_paper(safe_filename)

        if os.path.exists(filepath):
            os.remove(filepath)

        return jsonify({"success": f"Paper '{safe_filename}' deleted successfully."}), 200

    except Exception as e:
        print(f"Error deleting paper {safe_filename}: {e}")
        return jsonify({"error": "An internal error occurred. Could not delete the paper."}), 500


@app.route('/api/analyze-multiple', methods=['POST'])
async def analyze_multiple_pdfs():
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

    final_prompt = f"You are an expert academic assistant. Your task is to perform a detailed comparative analysis of the following university question papers.\n\nUSER'S INSTRUCTION: \"{user_prompt}\"\n\nBased on the user's instruction, analyze the content of the documents provided below. When comparing questions, consider both direct textual matches and semantic similarities (i.e., questions asking the same thing with different wording). Present your findings in a clear, well-structured, and easy-to-read format. Use markdown for formatting if appropriate.\n\n{combined_text}"

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
    semester = request.form.get('semester')

    if not all([subject, branch, regulation]):
        return jsonify({"error": "Missing subject, branch, or regulation"}), 400

    year = None
    if semester:
        try:
            year = int(semester.split('-')[0])
        except (ValueError, IndexError):
            year = None

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
            db.add_paper(subject, branch, regulation, filename, semester, year)
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

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    return jsonify(STATIC_SUBJECTS)

@app.route('/api/branches', methods=['GET'])
def get_branches():
    return jsonify(STATIC_BRANCHES)

@app.route('/api/regulations', methods=['GET'])
def get_regulations():
    return jsonify(STATIC_REGULATIONS)

@app.route('/api/semesters', methods=['GET'])
def get_semesters():
    branch = request.args.get('branch', '')
    regulation = request.args.get('regulation', '')
    
    if regulation == 'R22' and branch in R22_SEMESTER_SUBJECTS:
        semesters = list(R22_SEMESTER_SUBJECTS[branch].keys())
        return jsonify(semesters)
    
    return jsonify([])

@app.route('/api/subjects-by-criteria', methods=['GET'])
def get_subjects_by_criteria():
    branch = request.args.get('branch', '')
    regulation = request.args.get('regulation', '')
    semester = request.args.get('semester', '')
    
    subjects_by_sem = R22_SEMESTER_SUBJECTS.get(branch, {}) if regulation == 'R22' else {}

    if semester in subjects_by_sem:
        subjects = subjects_by_sem[semester]
        return jsonify(subjects)
    
    return jsonify(STATIC_SUBJECTS)


@app.route('/api/years', methods=['GET'])
def get_years_api():
    years = db.get_years()
    return jsonify(years)

@app.route('/api/filter-papers', methods=['POST'])
def filter_papers():
    data = request.json
    branch = data.get('branch') or None
    regulation = data.get('regulation') or None
    year = data.get('year') or None
    subjects = data.get('subjects', [])
    
    papers = db.get_papers_by_filters(branch, regulation, year, subjects if subjects else None)
    return jsonify(papers)

@app.route('/api/batch-download', methods=['POST'])
def batch_download():
    data = request.json
    filenames = data.get('filenames', [])
    
    if not filenames:
        return jsonify({"error": "No files to download"}), 400
    
    memory_file = io.BytesIO()
    try:
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename in filenames:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
                if os.path.exists(filepath):
                    arcname = os.path.basename(filepath)
                    zf.write(filepath, arcname=arcname)
        
        memory_file.seek(0)
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'papers_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        )
    except Exception as e:
        return jsonify({"error": f"Error creating ZIP: {str(e)}"}), 500

@app.route('/api/analyze-subject', methods=['POST'])
async def analyze_subject():
    data = request.json
    filenames = data.get('filenames', [])
    
    if not filenames:
        return jsonify({"error": "No files to analyze"}), 400
    
    extractor = QuestionExtractor()
    analyzer = QuestionAnalyzer()
    all_questions = []
    
    for filename in filenames:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(filepath):
            text = extractor.extract_text_from_pdf(filepath)
            questions = extractor.split_into_questions(text)
            all_questions.extend(questions)
    
    if not all_questions:
        return jsonify({
            "repeated_questions": [],
            "important_topics": [],
            "total_questions_found": 0,
            "similar_patterns": 0
        })
    
    try:
        question_texts = [q for q in all_questions]
        similar_groups = analyzer.find_similar_questions(question_texts, threshold=0.6)
        
        importance_scores = analyzer.calculate_importance(question_texts, len(filenames))
        repeated_questions = []
        for group in sorted(similar_groups, key=lambda x: x['count'], reverse=True)[:10]:
            group_questions = [all_questions[i] for i in group['indices']]
            avg_importance = int(np.mean([importance_scores.get(i, 0) for i in group['indices']]))
            repeated_questions.append({
                'question_text': group_questions[0][:200] + '...' if len(group_questions[0]) > 200 else group_questions[0],
                'frequency': group['count'],
                'importance': min(100, max(0, avg_importance))
            })
        
        try:
            sample_questions = "\n".join(all_questions[:20])
            important_topics = await get_summary_from_gemini(
                f"Analyze these exam questions and identify 5 most important topics to study. "
                f"Return as a numbered list:\n\n{sample_questions}"
            )
            topics = parse_important_topics(important_topics)
        except:
            topics = extract_topics_from_questions(all_questions)
        
        return jsonify({
            'repeated_questions': repeated_questions,
            'important_topics': topics,
            'total_questions_found': len(all_questions),
            'similar_patterns': len(similar_groups)
        })
    
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route('/api/generate-learning-plan', methods=['POST'])
async def generate_learning_plan():
    data = request.json
    filenames = data.get('filenames', [])
    branch = data.get('branch', 'General')
    year = data.get('year', '1-1')
    
    if not filenames:
        return jsonify({"error": "No files to analyze"}), 400
    
    extractor = QuestionExtractor()
    all_questions = []
    question_types = {}
    difficulties = {}
    
    try:
        for filename in filenames:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
            if os.path.exists(filepath):
                text = extractor.extract_text_from_pdf(filepath)
                questions = extractor.split_into_questions(text)
                
                for q in questions:
                    all_questions.append(q)
                    q_type = extractor.classify_question_type(q)
                    difficulty = extractor.estimate_difficulty(q, q_type)
                    
                    question_types[q_type] = question_types.get(q_type, 0) + 1
                    difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
        
        if not all_questions:
            return jsonify({
                'recommended_study_period': '4-6 weeks',
                'difficulty_progression': 'Easy → Medium → Hard',
                'focus_areas': [
                    {
                        'topic': 'Core Concepts',
                        'description': 'Focus on fundamental concepts',
                        'priority': 'High',
                        'estimated_hours': 20
                    }
                ],
                'strategy': 'Study systematically and practice regularly'
            })
        
        prompt = f"""
        Based on {len(filenames)} exam papers for {branch}, Year {year}, create a learning plan.
        
        Question Statistics:
        - Total Questions: {len(all_questions)}
        - By Type: {json.dumps(question_types)}
        - By Difficulty: {json.dumps(difficulties)}
        
        Sample Questions:
        {chr(10).join(all_questions[:15])}
        
        Generate a JSON response with:
        {{
            "recommended_study_period": "number of weeks",
            "difficulty_progression": "progression strategy",
            "focus_areas": [
                {{"topic": "Example", "description": "Why focus", "priority": "High", "estimated_hours": 10}}
            ],
            "strategy": "Overall study strategy"
        }}
        """
        
        try:
            api_response = await get_summary_from_gemini(prompt)
            json_start = api_response.find('{')
            json_end = api_response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = api_response[json_start:json_end]
                plan_data = json.loads(json_str)
            else:
                plan_data = create_default_learning_plan(question_types, difficulties)
        except:
            plan_data = create_default_learning_plan(question_types, difficulties)
        
        return jsonify(plan_data)
    
    except Exception as e:
        print(f"Learning plan error: {e}")
        return jsonify({"error": f"Plan generation failed: {str(e)}"}), 500

def parse_important_topics(gemini_response):
    topics = []
    lines = gemini_response.split('\n')
    
    for line in lines[:10]:
        line = line.strip()
        if line and len(line) > 5:
            clean_line = line.lstrip('0123456789.). ')
            if clean_line:
                topics.append({
                    'name': clean_line.split('-')[0].strip() if '-' in clean_line else clean_line,
                    'description': clean_line
                })
    
    return topics[:5]

def extract_topics_from_questions(questions):
    topics = []
    topic_keywords = {
        'Derivation': ['derive', 'derive', 'prove', 'prove'],
        'Problem Solving': ['solve', 'calculate', 'compute', 'find'],
        'Definitions': ['define', 'define', 'state', 'discuss'],
        'Applications': ['apply', 'application', 'example', 'implement'],
        'Analysis': ['analyze', 'compare', 'explain', 'analyze']
    }
    
    for topic_name, keywords in topic_keywords.items():
        count = 0
        for q in questions:
            for keyword in keywords:
                if keyword.lower() in q.lower():
                    count += 1
        if count > 0:
            topics.append({
                'name': topic_name,
                'description': f'Found in {count} questions'
            })
    
    return topics[:5]

def create_default_learning_plan(question_types, difficulties):
    """Creates a default learning plan based on question statistics."""
    
    total_questions = sum(question_types.values())
    if total_questions > 50:
        period = '6-8 weeks'
    elif total_questions > 30:
        period = '4-6 weeks'
    else:
        period = '2-4 weeks'
    
    focus_areas = []
    
    if question_types.get('MCQ', 0) > 0:
        focus_areas.append({
            'topic': 'Multiple Choice Questions',
            'description': f'Practice {question_types.get("MCQ", 0)} MCQ questions',
            'priority': 'High',
            'estimated_hours': 10
        })
    
    if question_types.get('Short Answer', 0) > 0:
        focus_areas.append({
            'topic': 'Short Answer Questions',
            'description': f'Practice {question_types.get("Short Answer", 0)} short answer questions',
            'priority': 'High',
            'estimated_hours': 15
        })
    
    if question_types.get('Essay', 0) > 0:
        focus_areas.append({
            'topic': 'Essay Questions',
            'description': f'Write essays for {question_types.get("Essay", 0)} questions',
            'priority': 'High',
            'estimated_hours': 20
        })
    
    if not focus_areas:
        focus_areas.append({
            'topic': 'Core Concepts',
            'description': 'Master fundamental concepts',
            'priority': 'High',
            'estimated_hours': 20
        })
    
    focus_areas.append({
        'topic': 'Revision & Mock Tests',
        'description': 'Final revision and practice tests',
        'priority': 'Medium',
        'estimated_hours': 10
    })
    
    return {
        'recommended_study_period': period,
        'difficulty_progression': f"Easy (focus on {difficulties.get('Easy', 0)} questions) → Medium → Hard",
        'focus_areas': focus_areas[:5],
        'strategy': 'Study systematically from easy to hard questions, practice regularly, and take mock tests before the exam.'
    }

if __name__ == '__main__':
    app.run(debug=True)