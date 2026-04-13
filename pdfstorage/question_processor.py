import re
import os
import PyPDF2
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class QuestionExtractor:
    """Extracts and processes questions from PDFs."""
    
    def __init__(self):
        self.question_patterns = [
            r'^\s*(\d+[\.\)]\s+)',  # Numbered questions
            r'^\s*Q[\.\)]\s*(\d+)',  # Q1, Q2, etc.
            r'^(Answer|Ans)[:.]',    # Answer sections
            r'^(Part|Section)\s+[A-Za-z0-9]'
        ]
    
    def extract_text_from_pdf(self, filepath):
        """Extracts all text from PDF."""
        text = ""
        try:
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            print(f"Error extracting PDF: {e}")
        return text
    
    def split_into_questions(self, text):
        """Splits text into individual questions."""
        lines = text.split('\n')
        questions = []
        current_question = ""
        
        for line in lines:
            line = line.strip()
            
            # Check if line starts a new question
            if any(re.match(pattern, line) for pattern in self.question_patterns):
                if current_question:
                    questions.append(current_question.strip())
                current_question = line
            else:
                if current_question:
                    current_question += " " + line
        
        if current_question:
            questions.append(current_question.strip())
        
        # Filter very short texts
        return [q for q in questions if len(q.split()) > 3]
    
    def classify_question_type(self, question_text):
        """Classifies question type."""
        q_lower = question_text.lower()
        
        if question_text.count('(a)') >= 2 or question_text.count('(i)') >= 2:
            return "MCQ"
        elif len(question_text.split()) > 100:
            return "Essay"
        elif " or " in q_lower and "?" in question_text:
            return "Either-Or"
        else:
            return "Short Answer"
    
    def estimate_difficulty(self, question_text, question_type="Short Answer"):
        """Estimates question difficulty."""
        score = 0
        
        hard_keywords = ['derive', 'prove', 'explain', 'analyze', 'complex', 'discuss']
        medium_keywords = ['describe', 'compare', 'calculate', 'compute']
        easy_keywords = ['define', 'state', 'list', 'name', 'write']
        
        q_lower = question_text.lower()
        
        for keyword in hard_keywords:
            if keyword in q_lower:
                score += 3
        for keyword in medium_keywords:
            if keyword in q_lower:
                score += 2
        for keyword in easy_keywords:
            if keyword in q_lower:
                score += 1
        
        word_count = len(question_text.split())
        if word_count > 100:
            score += 1
        
        if score >= 5:
            return "Hard"
        elif score >= 3:
            return "Medium"
        else:
            return "Easy"


class QuestionAnalyzer:
    """Analyzes questions for patterns and similarity."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
    
    def find_similar_questions(self, questions, threshold=0.6):
        """Finds similar/repeated questions."""
        if len(questions) < 2:
            return []
        
        try:
            # Ensure we have strings
            questions = [str(q) for q in questions]
            
            # Vectorize questions
            tfidf_matrix = self.vectorizer.fit_transform(questions)
            
            # Calculate similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Find similar pairs
            similar_groups = []
            processed = set()
            
            for i in range(len(similarity_matrix)):
                if i in processed:
                    continue
                
                group = [i]
                for j in range(i + 1, len(similarity_matrix)):
                    if j not in processed and similarity_matrix[i][j] > threshold:
                        group.append(j)
                        processed.add(j)
                
                if len(group) > 1:
                    similar_groups.append({
                        'indices': group,
                        'similarity_score': float(np.mean(similarity_matrix[i][group])),
                        'count': len(group)
                    })
                
                processed.add(i)
            
            return similar_groups
        except Exception as e:
            print(f"Similarity analysis error: {e}")
            return []
    
    def calculate_importance(self, questions, papers_count=1):
        """Calculates importance score for questions."""
        importance_scores = {}
        
        # Frequency-based scoring
        word_freq = {}
        for q in questions:
            words = str(q).lower().split()
            for word in words:
                if len(word) > 4:  # Ignore short words
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        for idx, question in enumerate(questions):
            score = 0
            words = str(question).lower().split()
            
            # Score based on repeated keywords
            for word in words:
                score += word_freq.get(word, 0)
            
            # Normalize by paper count
            if papers_count > 0:
                importance_scores[idx] = int((score / (papers_count * 10)) * 100)
            else:
                importance_scores[idx] = 0
        
        return importance_scores
