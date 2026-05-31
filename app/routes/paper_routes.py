"""
Paper routes — upload, delete, list, filter, download.
"""

import io
import os
import zipfile
from datetime import datetime

from flask import Blueprint, request, jsonify, url_for, send_from_directory, send_file, current_app
from werkzeug.utils import secure_filename

from app.models import paper as paper_model
from app.services.pdf_service import allowed_file, generate_unique_filename

papers_bp = Blueprint('papers', __name__)


@papers_bp.route('/api/papers', methods=['GET'])
def get_papers():
    try:
        papers = paper_model.get_all_papers()
        return jsonify(papers)
    except Exception as e:
        print(f"Error fetching papers: {e}")
        return jsonify({"error": "Failed to fetch papers"}), 500


@papers_bp.route('/api/upload', methods=['POST'])
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
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filename = secure_filename(file.filename)
        filename = generate_unique_filename(upload_folder, filename)
        filepath = os.path.join(upload_folder, filename)

        file.save(filepath)

        try:
            paper_model.add_paper(subject, branch, regulation, filename, semester, year)
            file_url = url_for('papers.uploaded_file', filename=filename)
            return jsonify({
                "success": "File uploaded successfully",
                "filename": filename,
                "url": file_url,
            }), 201

        except Exception as e:
            print(f"Database error: {e}")
            os.remove(filepath)
            return jsonify({"error": "Failed to save paper details"}), 500

    return jsonify({"error": "File type not allowed"}), 400


@papers_bp.route('/uploads/<filename>', endpoint='uploaded_file')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@papers_bp.route('/api/paper/delete/<filename>', methods=['DELETE'])
def delete_paper_file(filename):
    if not filename:
        return jsonify({"error": "Invalid filename provided"}), 400

    safe_filename = secure_filename(filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_filename)

    try:
        paper_model.delete_paper(safe_filename)

        if os.path.exists(filepath):
            os.remove(filepath)

        return jsonify({"success": f"Paper '{safe_filename}' deleted successfully."}), 200

    except Exception as e:
        print(f"Error deleting paper {safe_filename}: {e}")
        return jsonify({"error": "An internal error occurred. Could not delete the paper."}), 500


@papers_bp.route('/api/filter-papers', methods=['POST'])
def filter_papers():
    data = request.json
    branch = data.get('branch') or None
    regulation = data.get('regulation') or None
    year = data.get('year') or None
    subjects = data.get('subjects', [])

    papers = paper_model.get_papers_by_filters(
        branch, regulation, year, subjects if subjects else None
    )
    return jsonify(papers)


@papers_bp.route('/api/batch-download', methods=['POST'])
def batch_download():
    data = request.json
    filenames = data.get('filenames', [])

    if not filenames:
        return jsonify({"error": "No files to download"}), 400

    upload_folder = current_app.config['UPLOAD_FOLDER']
    memory_file = io.BytesIO()
    try:
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename in filenames:
                filepath = os.path.join(upload_folder, secure_filename(filename))
                if os.path.exists(filepath):
                    arcname = os.path.basename(filepath)
                    zf.write(filepath, arcname=arcname)

        memory_file.seek(0)
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'papers_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip',
        )
    except Exception as e:
        return jsonify({"error": f"Error creating ZIP: {str(e)}"}), 500
