/**
 * API module — all fetch calls to the backend.
 *
 * Each function returns the parsed JSON response.
 */

export async function fetchPapers() {
    const response = await fetch('/api/papers');
    if (!response.ok) throw new Error('Network response was not ok');
    return response.json();
}

export async function uploadPaper(formData) {
    const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
    });
    const data = await response.json();
    return { ok: response.ok, data };
}

export async function deletePaper(filename) {
    const response = await fetch(`/api/paper/delete/${filename}`, {
        method: 'DELETE',
    });
    const result = await response.json();
    return { ok: response.ok, result };
}

export async function filterPapers({ branch, regulation, year, subjects }) {
    const response = await fetch('/api/filter-papers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            branch,
            regulation,
            year,
            subjects: subjects && subjects.length > 0 ? subjects : null,
        }),
    });
    return response.json();
}

export async function analyzeMultiple(filenames, prompt) {
    const response = await fetch('/api/analyze-multiple', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filenames, prompt }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Analysis failed.');
    return result;
}

export async function analyzeSubject({ filenames, branch, year, subjects }) {
    const response = await fetch('/api/analyze-subject', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filenames, branch, year, subjects }),
    });
    return response.json();
}

export async function generateLearningPlan({ filenames, branch, year, subjects }) {
    const response = await fetch('/api/generate-learning-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filenames, branch, year, subjects }),
    });
    return response.json();
}

export async function batchDownload(filenames) {
    const response = await fetch('/api/batch-download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filenames }),
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Batch download failed');
    }
    return response.blob();
}

export async function fetchSubjects() {
    return fetch('/api/subjects').then(r => r.json());
}

export async function fetchBranches() {
    return fetch('/api/branches').then(r => r.json());
}

export async function fetchRegulations() {
    return fetch('/api/regulations').then(r => r.json());
}

export async function fetchSemesters(branch, regulation) {
    return fetch(
        `/api/semesters?branch=${encodeURIComponent(branch)}&regulation=${encodeURIComponent(regulation)}`
    ).then(r => r.json());
}

export async function fetchSubjectsByCriteria(branch, regulation, semester) {
    return fetch(
        `/api/subjects-by-criteria?branch=${encodeURIComponent(branch)}&regulation=${encodeURIComponent(regulation)}&semester=${encodeURIComponent(semester)}`
    ).then(r => r.json());
}
