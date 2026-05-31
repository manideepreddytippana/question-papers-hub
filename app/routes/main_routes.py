"""
Main routes — static page serving.
"""

import os
from flask import Blueprint, send_from_directory, current_app

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return send_from_directory(os.path.join(current_app.root_path, 'static', 'pages'), 'index.html')


@main_bp.route('/summary/<filename>')
def summary_page(filename):
    return send_from_directory(os.path.join(current_app.root_path, 'static', 'pages'), 'summary.html')
