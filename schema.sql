DROP TABLE IF EXISTS question_patterns;
DROP TABLE IF EXISTS learning_plans;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS papers;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS branches;
DROP TABLE IF EXISTS regulations;
DROP TABLE IF EXISTS years;

CREATE TABLE years (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    semester VARCHAR(10),
    UNIQUE KEY (year, semester)
);

CREATE TABLE papers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject VARCHAR(255) NOT NULL,
    branch VARCHAR(255) NOT NULL,
    regulation VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    year INT,
    semester VARCHAR(10),
    is_analyzed BOOLEAN DEFAULT FALSE,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE branches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE regulations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paper_id INT NOT NULL,
    question_text LONGTEXT NOT NULL,
    question_number INT,
    question_type VARCHAR(50),
    difficulty_level VARCHAR(20),
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    FULLTEXT KEY (question_text)
);

CREATE TABLE question_patterns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    branch_id INT NOT NULL,
    pattern_group_id INT,
    similar_questions LONGTEXT,
    occurrence_count INT DEFAULT 1,
    importance_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (branch_id) REFERENCES branches(id)
);

CREATE TABLE learning_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    branch_id INT NOT NULL,
    year INT NOT NULL,
    analysis_result LONGTEXT,
    top_questions LONGTEXT,
    study_focus_areas LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id),
    FOREIGN KEY (branch_id) REFERENCES branches(id)
);

-- Insert sample years data
INSERT INTO years (year, semester) VALUES
(1, '1'),
(1, '2'),
(2, '1'),
(2, '2'),
(3, '1'),
(3, '2'),
(4, '1'),
(4, '2');

-- Insert sample data for the dropdowns
INSERT INTO subjects (name) VALUES
('Mathematics-I'),
('Physics'),
('Chemistry'),
('Programming in C'),
('Data Structures'),
('Database Management Systems');

INSERT INTO branches (name) VALUES
('CSE'),
('CSE (AI & ML)'),
('CSE (Cyber Security)'),
('CSE (Data Science)'),
('CSE (IoT)'),
('CSE (AI & DS)');

INSERT INTO regulations (name) VALUES
('R16'),
('R18'),
('R20'),
('R22');