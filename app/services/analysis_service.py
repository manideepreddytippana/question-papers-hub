"""
Analysis service — subject analysis and learning plan generation.

Extracted from main.py's analyze_subject and generate_learning_plan
route handlers, keeping only the business logic.
"""

import json
import os
import numpy as np

from app.services.question_processor import QuestionExtractor, QuestionAnalyzer
from app.services import gemini_service


# ─── Subject analysis ─────────────────────────────────────

async def analyze_subject(filenames, upload_folder):
    """Analyze papers for repeated questions and important topics.

    Args:
        filenames: List of PDF filenames to analyze.
        upload_folder: Path to the uploads directory.

    Returns:
        Dictionary with repeated_questions, important_topics,
        total_questions_found, and similar_patterns.
    """
    from werkzeug.utils import secure_filename

    extractor = QuestionExtractor()
    analyzer = QuestionAnalyzer()
    all_questions = []

    for filename in filenames:
        filepath = os.path.join(upload_folder, secure_filename(filename))
        if os.path.exists(filepath):
            text = extractor.extract_text_from_pdf(filepath)
            questions = extractor.split_into_questions(text)
            all_questions.extend(questions)

    if not all_questions:
        return {
            "repeated_questions": [],
            "important_topics": [],
            "total_questions_found": 0,
            "similar_patterns": 0,
        }

    question_texts = [q for q in all_questions]
    similar_groups = analyzer.find_similar_questions(question_texts, threshold=0.6)

    importance_scores = analyzer.calculate_importance(question_texts, len(filenames))
    repeated_questions = []
    for group in sorted(similar_groups, key=lambda x: x['count'], reverse=True)[:10]:
        group_questions = [all_questions[i] for i in group['indices']]
        avg_importance = int(np.mean([importance_scores.get(i, 0) for i in group['indices']]))
        repeated_questions.append({
            'question_text': (
                group_questions[0][:200] + '...'
                if len(group_questions[0]) > 200
                else group_questions[0]
            ),
            'frequency': group['count'],
            'importance': min(100, max(0, avg_importance)),
        })

    # Try AI-powered topic extraction, fall back to keyword-based
    try:
        sample_questions = "\n".join(all_questions[:20])
        important_topics = await gemini_service.get_summary(
            f"Analyze these exam questions and identify 5 most important topics to study. "
            f"Return as a numbered list:\n\n{sample_questions}"
        )
        topics = parse_important_topics(important_topics)
    except Exception:
        topics = extract_topics_from_questions(all_questions)

    return {
        'repeated_questions': repeated_questions,
        'important_topics': topics,
        'total_questions_found': len(all_questions),
        'similar_patterns': len(similar_groups),
    }


# ─── Learning plan generation ─────────────────────────────

async def generate_learning_plan(filenames, branch, year, upload_folder):
    """Generate a personalized learning plan from exam papers.

    Args:
        filenames: List of PDF filenames to analyze.
        branch: The academic branch (e.g. "CSE").
        year: The year-semester string (e.g. "2-1").
        upload_folder: Path to the uploads directory.

    Returns:
        Dictionary with recommended_study_period, difficulty_progression,
        focus_areas, and strategy.
    """
    from werkzeug.utils import secure_filename

    extractor = QuestionExtractor()
    all_questions = []
    question_types = {}
    difficulties = {}

    for filename in filenames:
        filepath = os.path.join(upload_folder, secure_filename(filename))
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
        return {
            'recommended_study_period': '4-6 weeks',
            'difficulty_progression': 'Easy → Medium → Hard',
            'focus_areas': [
                {
                    'topic': 'Core Concepts',
                    'description': 'Focus on fundamental concepts',
                    'priority': 'High',
                    'estimated_hours': 20,
                }
            ],
            'strategy': 'Study systematically and practice regularly',
        }

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
        api_response = await gemini_service.get_summary(prompt)
        json_start = api_response.find('{')
        json_end = api_response.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = api_response[json_start:json_end]
            plan_data = json.loads(json_str)
        else:
            plan_data = create_default_learning_plan(question_types, difficulties)
    except Exception:
        plan_data = create_default_learning_plan(question_types, difficulties)

    return plan_data


# ─── Helper functions ──────────────────────────────────────

def parse_important_topics(gemini_response):
    """Parse Gemini's numbered-list response into structured topics."""
    topics = []
    lines = gemini_response.split('\n')

    for line in lines[:10]:
        line = line.strip()
        if line and len(line) > 5:
            clean_line = line.lstrip('0123456789.). ')
            if clean_line:
                topics.append({
                    'name': clean_line.split('-')[0].strip() if '-' in clean_line else clean_line,
                    'description': clean_line,
                })

    return topics[:5]


def extract_topics_from_questions(questions):
    """Fallback topic extraction based on keyword frequency."""
    topics = []
    topic_keywords = {
        'Derivation': ['derive', 'derive', 'prove', 'prove'],
        'Problem Solving': ['solve', 'calculate', 'compute', 'find'],
        'Definitions': ['define', 'define', 'state', 'discuss'],
        'Applications': ['apply', 'application', 'example', 'implement'],
        'Analysis': ['analyze', 'compare', 'explain', 'analyze'],
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
                'description': f'Found in {count} questions',
            })

    return topics[:5]


def create_default_learning_plan(question_types, difficulties):
    """Create a default learning plan based on question statistics."""
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
            'estimated_hours': 10,
        })

    if question_types.get('Short Answer', 0) > 0:
        focus_areas.append({
            'topic': 'Short Answer Questions',
            'description': f'Practice {question_types.get("Short Answer", 0)} short answer questions',
            'priority': 'High',
            'estimated_hours': 15,
        })

    if question_types.get('Essay', 0) > 0:
        focus_areas.append({
            'topic': 'Essay Questions',
            'description': f'Write essays for {question_types.get("Essay", 0)} questions',
            'priority': 'High',
            'estimated_hours': 20,
        })

    if not focus_areas:
        focus_areas.append({
            'topic': 'Core Concepts',
            'description': 'Master fundamental concepts',
            'priority': 'High',
            'estimated_hours': 20,
        })

    focus_areas.append({
        'topic': 'Revision & Mock Tests',
        'description': 'Final revision and practice tests',
        'priority': 'Medium',
        'estimated_hours': 10,
    })

    return {
        'recommended_study_period': period,
        'difficulty_progression': f"Easy (focus on {difficulties.get('Easy', 0)} questions) → Medium → Hard",
        'focus_areas': focus_areas[:5],
        'strategy': 'Study systematically from easy to hard questions, practice regularly, and take mock tests before the exam.',
    }
