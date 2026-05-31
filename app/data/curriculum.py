"""
Curriculum data for all branches and regulations.

Extracted from the original main.py to keep route files clean.
Update subject lists here when the curriculum changes.
"""

# ──────────────────────────────────────────────
# R22 Semester → Subject mappings per branch
# ──────────────────────────────────────────────

aiml_subjects = {
    "1-1": [
        "Matrices and Calculus (M1)",
        "Applied Physics (AP)",
        "Programming for Problem Solving (PPS)",
        "English for Skill Enhancement",
        "Environmental Science (ES)",
    ],
    "1-2": [
        "Ordinary Differential Equations and Vector Calculus (ODE)",
        "Engineering Chemistry",
        "Computer Aided Engineering Graphics (CAEG)",
        "Basic Electrical Engineering (BEE)",
        "Electronic Devices and Circuits (EDC)",
    ],
    "2-1": [
        "Mathematical and Statistical Foundations (MSF)",
        "Data Structures (DS)",
        "Computer Organization and Architecture (COA)",
        "Software Engineering",
        "Operating Systems (OS)",
    ],
    "2-2": [
        "Discrete Mathematics (DM)",
        "Automata Theory and Compiler Design (ATCD)",
        "Database Management Systems (DBMS)",
        "Introduction to Artificial Intelligence (AI)",
        "Object Oriented Programming through Java (OOP)",
    ],
    "3-1": [
        "Design and Analysis of Algorithms (DAA)",
        "Machine Learning (ML)",
        "Computer Networks (CN)",
        "Business Economics & Financial Analysis (BEFA)",
        "Web Programming (WP)",
        "Intellectual Property Rights (IPR)",
    ],
    "3-2": [
        "Fundamentals of Internet of Things (FIOT)",
        "Software Testing Methodologies (STM)",
        "Knowledge Representation and Reasoning (KRR)",
        "Data Analytics (DA)",
        "Natural Language Processing (NLP)",
    ],
    "4-1": [
        "Semantic Web (SW)",
        "Deep Learning (DL)",
        "Cloud Computing (CC)",
        "Nature Inspired Computing (NIC)",
        "Electronics for Health Care (EHC)",
        "Professional Practice, Law & Ethics (PPLE)",
    ],
    "4-2": [
        "Conversational AI (CA)",
        "AD HOC & Sensor Networks (ASN)",
        "Fundamentals of Social Network (FSN)",
    ],
}

aids_subjects = {
    "1-1": [
        "Matrices and Calculus (M1)",
        "Applied Physics (AP)",
        "Programming for Problem Solving (PPS)",
        "English for Skill Enhancement (ESE)",
        "Elements of Computer Science & Engineering (ECSE)",
        "Environmental Science (ES)",
    ],
    "1-2": [
        "Ordinary Differential Equations and Vector Calculus (ODE&VC)",
        "Engineering Chemistry (EC)",
        "Computer Aided Engineering Graphics (CAEG)",
        "Basic Electrical Engineering (BEE)",
        "Electronic Devices and Circuits (EDC)",
    ],
    "2-1": [
        "Mathematical and Statistical Foundations (MSF)",
        "Digital Electronics (DE)",
        "Data Structures (DS)",
        "Object Oriented Programming through Java (OOPJ)",
        "Computer Organization and Architecture (COA)",
    ],
    "2-2": [
        "Discrete Mathematics (DM)",
        "Introduction to Artificial Intelligence (AI)",
        "Database Management Systems (DBMS)",
        "Operating Systems (OS)",
        "Software Engineering (SE)",
    ],
    "3-1": [
        "Design and Analysis of Algorithms (DAA)",
        "Introduction to Data Science (IDS)",
        "Computer Networks (CN)",
        "Business Economics & Financial Analysis (BEFA)",
        "WEB PROGRAMMING (WP)",
        "Intellectual Property Rights (IPR)",
    ],
    "3-2": [
        "Automata Theory and Compiler Design (ATCD)",
        "Machine Learning (ML)",
        "Big Data Analytics (BDA)",
        "SOFTWARE TESTING METHODOLOGIES (STM)",
        "FUNDAMENTALS OF INTERNET OF THINGS (FIOT)",
        "Environmental Science (ES)",
    ],
    "4-1": [
        "Introduction to Predictive Analytics (IPA)",
        "Web and Social Media Analytics (WSMA)",
        "ELECTRONICS FOR HEALTH CARE (EHC)",
        "Professional Practice, Law & Ethics (PPLE)",
        "CRYPTOGRAPHY AND NETWORK SECURITY (CNS)",
        "CLOUD COMPUTING (CC)",
    ],
    "4-2": [
        "Professional Elective - V (PE5)",
        "Professional Elective - VI (PE6)",
        "Open Elective - III (OE3)",
        "Project Stage - II (Project)",
    ],
}

cse_subjects = {
    "1-1": [
        "Matrices and Calculus (M&C)",
        "Engineering Chemistry (EC)",
        "Programming for Problem Solving (PPS)",
        "Basic Electrical Engineering (BEE)",
        "Computer Aided Engineering Graphics (CAEG)",
    ],
    "1-2": [
        "Ordinary Differential Equations & Vector Calculus (ODE&VC)",
        "Applied Physics (AP)",
        "Engineering Workshop (EW)",
        "English for Skill Enhancement (ESE)",
        "Electronic Devices and Circuits (EDC)",
    ],
    "2-1": [
        "Digital Electronics (DE)",
        "Data Structures (DS)",
        "Computer Oriented Statistical Methods (COSM)",
        "Computer Organization & Architecture (COA)",
        "Object Oriented Programming through Java (OOPJ)",
    ],
    "2-2": [
        "Discrete Mathematics (DM)",
        "Business Economics & Financial Analysis (BEFA)",
        "Operating Systems (OS)",
        "Database Management Systems (DBMS)",
        "Software Engineering (SE)",
    ],
    "3-1": [
        "Design and Analysis of Algorithms (DAA)",
        "Computer Networks (CN)",
        "DevOps (DO)",
        "EMBEDDED SYSTEMS (ES)",
        "DATA ANALYTICS (DA)",
        "Intellectual Property Rights (IPR)",
    ],
    "3-2": [
        "Machine Learning (ML)",
        "Formal Languages & Automata Theory (FLAT)",
        "Artificial Intelligence (AI)",
        "FUNDAMENTALS OF INTERNET OF THINGS (FIOT)",
        "SOFTWARE TESTING METHODOLOGIES (STM)",
    ],
    "4-1": [
        "Cryptography & Network Security (CNS)",
        "Compiler Design (CD)",
        "ELECTRONICS FOR HEALTH CARE (EHC)",
        "CYBER SECURITY (CS)",
        "BLOCKCHAIN TECHNOLOGY (BT)",
    ],
    "4-2": [
        "Organizational Behavior (OB)",
        "Professional Elective-VI (PE6)",
        "Open Elective-III (OE3)",
    ],
}

# ──────────────────────────────────────────────
# Aggregate lookup: regulation → branch → semesters
# ──────────────────────────────────────────────

R22_SEMESTER_SUBJECTS = {
    "CSE": cse_subjects,
    "CSE (AI & ML)": aiml_subjects,
    "CSE (AI & DS)": aids_subjects,
}

# Branches that support R22 semester-subject lookup
R22_SUPPORTED_BRANCHES = list(R22_SEMESTER_SUBJECTS.keys())

# ──────────────────────────────────────────────
# Static dropdown options (fallback / non-R22)
# ──────────────────────────────────────────────

STATIC_SUBJECTS = [
    "Mathematics-I",
    "Physics",
    "Chemistry",
    "Programming in C",
    "Data Structures",
    "Database Management Systems",
]

STATIC_BRANCHES = [
    "CSE",
    "CSE (AI & ML)",
    "CSE (Cyber Security)",
    "CSE (Data Science)",
    "CSE (IoT)",
    "CSE (AI & DS)",
]

STATIC_REGULATIONS = [
    "R16",
    "R18",
    "R20",
    "R22",
]
