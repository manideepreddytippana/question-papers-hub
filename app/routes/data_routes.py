"""
Data routes — subjects, branches, regulations, semesters.

Serves the static dropdown data and R22 semester-subject lookups.
"""

from flask import Blueprint, request, jsonify

from app.data.curriculum import (
    R22_SEMESTER_SUBJECTS,
    STATIC_SUBJECTS,
    STATIC_BRANCHES,
    STATIC_REGULATIONS,
)
from app.models import paper as paper_model

data_bp = Blueprint('data', __name__)


@data_bp.route('/api/subjects', methods=['GET'])
def get_subjects():
    return jsonify(STATIC_SUBJECTS)


@data_bp.route('/api/branches', methods=['GET'])
def get_branches():
    return jsonify(STATIC_BRANCHES)


@data_bp.route('/api/regulations', methods=['GET'])
def get_regulations():
    return jsonify(STATIC_REGULATIONS)


@data_bp.route('/api/semesters', methods=['GET'])
def get_semesters():
    branch = request.args.get('branch', '')
    regulation = request.args.get('regulation', '')

    if regulation == 'R22' and branch in R22_SEMESTER_SUBJECTS:
        semesters = list(R22_SEMESTER_SUBJECTS[branch].keys())
        return jsonify(semesters)

    return jsonify([])


@data_bp.route('/api/subjects-by-criteria', methods=['GET'])
def get_subjects_by_criteria():
    branch = request.args.get('branch', '')
    regulation = request.args.get('regulation', '')
    semester = request.args.get('semester', '')

    subjects_by_sem = R22_SEMESTER_SUBJECTS.get(branch, {}) if regulation == 'R22' else {}

    if semester in subjects_by_sem:
        subjects = subjects_by_sem[semester]
        return jsonify(subjects)

    return jsonify(STATIC_SUBJECTS)


@data_bp.route('/api/years', methods=['GET'])
def get_years_api():
    years = paper_model.get_years()
    return jsonify(years)
