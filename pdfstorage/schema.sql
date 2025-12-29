DROP TABLE IF EXISTS papers;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS branches;
DROP TABLE IF EXISTS regulations;

CREATE TABLE papers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject VARCHAR(255) NOT NULL,
    branch VARCHAR(255) NOT NULL,
    regulation VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
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

-- Insert sample data for the dropdowns
INSERT INTO subjects (name) VALUES
('Mathematics-I'),
('Physics'),
('Chemistry'),
('Programming in C'),
('Data Structures'),
('Database Management Systems');

INSERT INTO branches (name) VALUES
('Computer Science'),
('Information Technology'),
('Electronics and Communication'),
('Mechanical Engineering'),
('Civil Engineering');

INSERT INTO regulations (name) VALUES
('R16'),
('R18'),
('R20'),
('R22');