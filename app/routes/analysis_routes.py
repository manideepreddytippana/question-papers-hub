"""
Analysis routes — PDF analysis, multi-file comparison, subject analysis, learning plans.
"""

import os

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from app.services import gemini_service, analysis_service
from app.services.pdf_service import extract_text

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/api/analyze/<filename>', methods=['GET'])
async def analyze_pdf(filename):
    filepath = os.path.join(
        current_app.config['UPLOAD_FOLDER'], secure_filename(filename)
    )
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found."}), 404

    try:
        text = extract_text(filepath)

        if not text.strip():
            return jsonify({"error": "Could not extract any text from this PDF."}), 400

        prompt_for_gemini = (
            f"Summarize the key topics and question types from this question paper:\n\n{text}"
        )
        summary = await gemini_service.get_summary(prompt_for_gemini)

        return jsonify({"filename": filename, "summary": summary})

    except Exception as e:
        print(f"Error during PDF analysis for {filename}: {e}")
        return jsonify({"error": f"An unexpected error occurred during analysis: {e}"}), 500


@analysis_bp.route('/api/analyze-multiple', methods=['POST'])
async def analyze_multiple_pdfs():
    data = request.get_json()
    filenames = data.get('filenames')
    user_prompt = data.get('prompt')

    if not filenames or not isinstance(filenames, list) or len(filenames) < 2:
        return jsonify({"error": "Please select at least two files for analysis."}), 400

    if not user_prompt:
        return jsonify({"error": "An analysis instruction is required."}), 400

    upload_folder = current_app.config['UPLOAD_FOLDER']
    combined_text = ""

    for filename in filenames:
        filepath = os.path.join(upload_folder, secure_filename(filename))

        if not os.path.exists(filepath):
            return jsonify({"error": f"File not found: {filename}"}), 404

        try:
            text = extract_text(filepath)
            combined_text += (
                f"--- START OF DOCUMENT: {filename} ---\n\n"
                f"{text}\n\n"
                f"--- END OF DOCUMENT: {filename} ---\n\n"
            )

        except Exception as e:
            return jsonify({"error": f"Failed to read or parse {filename}: {e}"}), 500

    final_prompt = (
        f"You are an expert academic assistant. Your task is to perform a detailed "
        f"comparative analysis of the following university question papers.\n\n"
        f"USER'S INSTRUCTION: \"{user_prompt}\"\n\n"
        f"Based on the user's instruction, analyze the content of the documents provided below. "
        f"When comparing questions, consider both direct textual matches and semantic similarities "
        f"(i.e., questions asking the same thing with different wording). Present your findings in "
        f"a clear, well-structured, and easy-to-read format. Use markdown for formatting if "
        f"appropriate.\n\n{combined_text}"
    )

    try:
        analysis_result = await gemini_service.get_summary(final_prompt)
        return jsonify({"analysis_result": analysis_result})

    except Exception as e:
        print(f"Error during multi-file analysis: {e}")
        return jsonify({"error": f"An unexpected error occurred during analysis: {e}"}), 500


@analysis_bp.route('/api/analyze-subject', methods=['POST'])
async def analyze_subject():
    data = request.json
    filenames = data.get('filenames', [])

    if not filenames:
        return jsonify({"error": "No files to analyze"}), 400

    try:
        result = await analysis_service.analyze_subject(
            filenames, current_app.config['UPLOAD_FOLDER']
        )
        return jsonify(result)

    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@analysis_bp.route('/api/generate-learning-plan', methods=['POST'])
async def generate_learning_plan():
    data = request.json
    filenames = data.get('filenames', [])
    branch = data.get('branch', 'General')
    year = data.get('year', '1-1')

    if not filenames:
        return jsonify({"error": "No files to analyze"}), 400

    try:
        plan_data = await analysis_service.generate_learning_plan(
            filenames, branch, year, current_app.config['UPLOAD_FOLDER']
        )
        return jsonify(plan_data)

    except Exception as e:
        print(f"Learning plan error: {e}")
        return jsonify({"error": f"Plan generation failed: {str(e)}"}), 500
