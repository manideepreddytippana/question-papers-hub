/**
 * Papers module — paper grid rendering and interactions.
 *
 * Handles display, selection, deletion, batch download,
 * analysis actions, and learning plan display.
 */

import * as api from './api.js';
import * as filters from './filters.js';
import { showMessage, showLoadingModal, closeModal, showResultModal } from './ui.js';

// ─── State ───────────────────────────────────────

let selectedFiles = [];
let deleteFilename = null;

// ─── Elements ────────────────────────────────────

const papersGrid = document.getElementById('papers-grid');
const analysisResultsDiv = document.getElementById('analysis-results');
const analyzeBtn = document.getElementById('analyze-selected-btn');
const selectedCountSpan = document.getElementById('selected-count');
const batchDownloadBtn = document.getElementById('batch-download-btn');
const analyzeSubjectBtn = document.getElementById('analyze-subject-btn');
const generatePlanBtn = document.getElementById('generate-plan-btn');

// Confirm modal
const confirmModal = document.getElementById('confirm-modal');
const confirmTitle = document.getElementById('confirm-title');
const confirmMessage = document.getElementById('confirm-message');
const confirmBtn = document.getElementById('confirm-btn');
const cancelBtn = document.getElementById('cancel-btn');

// ─── Public API ──────────────────────────────────

export function init(fetchPapersCallback) {
    // Confirm modal listeners
    confirmBtn.addEventListener('click', async () => {
        if (!deleteFilename) return;

        const filename = deleteFilename;
        confirmModal.style.display = 'none';

        try {
            const { ok, result } = await api.deletePaper(filename);

            if (ok) {
                const card = document.querySelector(`[data-filename="${filename}"]`)?.closest('.paper-card');
                if (card) card.remove();
                showMessage('File deleted successfully!', 'success');
                await fetchPapersCallback();
            } else {
                throw new Error(result.error || 'Failed to delete file.');
            }
        } catch (error) {
            console.error('Delete error:', error);
            showMessage(`Error: ${error.message}`, 'error');
        }

        deleteFilename = null;
    });

    cancelBtn.addEventListener('click', () => {
        confirmModal.style.display = 'none';
        deleteFilename = null;
    });

    // Keyboard shortcuts for confirm modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && confirmModal.style.display === 'flex') {
            confirmModal.style.display = 'none';
            deleteFilename = null;
        }
        if (e.key === 'Enter' && confirmModal.style.display === 'flex') {
            confirmBtn.click();
        }
    });

    // Action buttons
    analyzeBtn.addEventListener('click', () => handleAnalyzeMultiple());
    batchDownloadBtn.addEventListener('click', () => handleBatchDownload());
    analyzeSubjectBtn.addEventListener('click', () => handleAnalyzeSubject());
    generatePlanBtn.addEventListener('click', () => handleGenerateLearningPlan());
}

export function displayPapers(papers) {
    papersGrid.innerHTML = '';
    if (papers.length === 0) {
        papersGrid.innerHTML = '<p>No question papers found.</p>';
        return;
    }

    papers.forEach(paper => {
        const card = document.createElement('div');
        card.className = 'paper-card';

        card.innerHTML = `
            <div class="paper-card-header">
                 <input type="checkbox" class="select-checkbox" data-filename="${paper.filename}">
                 <button class="btn-delete" data-filename="${paper.filename}" title="Delete Paper">&times;</button>
            </div>
            <div class="paper-card-content">
                <h3>${paper.subject}</h3>
                <p><strong>Branch:</strong> ${paper.branch}</p>
                <p><strong>Regulation:</strong> ${paper.regulation}</p>
                <p><strong>Uploaded:</strong> ${new Date(paper.upload_date).toLocaleDateString()}</p>
            </div>
            <div class="paper-card-footer">
                <a href="/uploads/${paper.filename}" class="btn-download" target="_blank" rel="noopener noreferrer">View</a>
                <a href="/summary/${paper.filename}" class="btn-analyze" data-filename="${paper.filename}">Analyze</a>
            </div>
        `;
        papersGrid.appendChild(card);
    });

    attachCheckboxListeners();
}

export function updateActionButtonStates() {
    const hasBranch = filters.hasBranchSelected();
    batchDownloadBtn.disabled = !hasBranch;
    analyzeSubjectBtn.disabled = !hasBranch;
    generatePlanBtn.disabled = !hasBranch;
}

// ─── Private helpers ─────────────────────────────

function attachCheckboxListeners() {
    document.querySelectorAll('.select-checkbox').forEach(checkbox => {
        checkbox.removeEventListener('change', handleFileSelection);
        checkbox.addEventListener('change', handleFileSelection);
    });

    papersGrid.removeEventListener('click', handleDeleteClick);
    papersGrid.addEventListener('click', handleDeleteClick);
}

function handleDeleteClick(event) {
    if (event.target.classList.contains('btn-delete')) {
        handleDelete(event);
    }
}

function handleFileSelection(event) {
    const filename = event.target.dataset.filename;
    if (event.target.checked) {
        if (!selectedFiles.includes(filename)) {
            selectedFiles.push(filename);
        }
    } else {
        selectedFiles = selectedFiles.filter(f => f !== filename);
    }
    updateAnalyzeButtonState();
}

function updateAnalyzeButtonState() {
    const count = selectedFiles.length;
    selectedCountSpan.textContent = count;
    analyzeBtn.disabled = count < 2;
}

function handleDelete(event) {
    const button = event.target;
    const filename = button.dataset.filename;
    deleteFilename = filename;

    confirmTitle.textContent = 'Confirm Deletion';
    confirmMessage.textContent = `Are you sure you want to delete the paper "${filename}"? This action cannot be undone.`;
    confirmModal.style.display = 'flex';
    confirmBtn.focus();
}

// ─── Action handlers ─────────────────────────────

async function handleAnalyzeMultiple() {
    const userPrompt = prompt(
        "Please enter your analysis instruction (e.g., 'Find repeated or similar questions between these papers'):"
    );
    if (!userPrompt) return;

    showLoadingModal("Analyzing selected files...");

    try {
        const result = await api.analyzeMultiple(selectedFiles, userPrompt);
        closeModal();
        showResultModal("Analysis Result", formatAnalysisHtml(result.analysis_result));
    } catch (error) {
        console.error('Multi-file analysis error:', error);
        closeModal();
        showMessage(`Error: ${error.message}`, 'error');
    }
}

async function handleBatchDownload() {
    if (!filters.hasBranchSelected()) {
        showMessage('Select a branch to enable batch download.', 'error');
        return;
    }

    // Get current filtered papers from the grid
    const paperCards = papersGrid.querySelectorAll('.paper-card');
    const filenames = Array.from(paperCards).map(card =>
        card.querySelector('.select-checkbox')?.dataset.filename
    ).filter(Boolean);

    if (filenames.length === 0) {
        showMessage('No papers found to download.', 'error');
        return;
    }

    showLoadingModal(`Preparing ${filenames.length} papers...`);

    try {
        const blob = await api.batchDownload(filenames);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `papers-${new Date().toISOString().split('T')[0]}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

        closeModal();
        showMessage(`Downloaded ${filenames.length} papers!`, 'success');
    } catch (error) {
        console.error('Download error:', error);
        closeModal();
        showMessage(`Error: ${error.message}`, 'error');
    }
}

async function handleAnalyzeSubject() {
    if (!filters.hasBranchSelected()) {
        showMessage('Select a branch to enable subject analysis.', 'error');
        return;
    }

    const paperCards = papersGrid.querySelectorAll('.paper-card');
    const filenames = Array.from(paperCards).map(card =>
        card.querySelector('.select-checkbox')?.dataset.filename
    ).filter(Boolean);

    if (filenames.length === 0) {
        showMessage('No papers found to analyze.', 'error');
        return;
    }

    showLoadingModal(`Analyzing ${filenames.length} papers for patterns...`);

    try {
        const filterValues = filters.getFilterValues();
        const result = await api.analyzeSubject({
            filenames,
            branch: filterValues.branch,
            year: filterValues.year,
            subjects: filterValues.subjects,
        });
        closeModal();
        displayAnalysisResults(result);
    } catch (error) {
        console.error('Analysis error:', error);
        closeModal();
        showMessage('Error analyzing papers: ' + error.message, 'error');
    }
}

async function handleGenerateLearningPlan() {
    if (!filters.hasBranchSelected()) {
        showMessage('Select a branch to enable learning plan generation.', 'error');
        return;
    }

    const paperCards = papersGrid.querySelectorAll('.paper-card');
    const filenames = Array.from(paperCards).map(card =>
        card.querySelector('.select-checkbox')?.dataset.filename
    ).filter(Boolean);

    if (filenames.length === 0) {
        showMessage('No papers found to analyze.', 'error');
        return;
    }

    showLoadingModal('Generating personalized learning plan...');

    try {
        const filterValues = filters.getFilterValues();
        const result = await api.generateLearningPlan({
            filenames,
            branch: filterValues.branch,
            year: filterValues.year,
            subjects: filterValues.subjects,
        });
        closeModal();
        displayLearningPlan(result);
    } catch (error) {
        console.error('Learning plan error:', error);
        closeModal();
        showMessage('Error generating learning plan: ' + error.message, 'error');
    }
}

// ─── Display helpers ─────────────────────────────

function formatAnalysisHtml(text) {
    if (!text) {
        return '<p>No analysis result returned.</p>';
    }

    const lines = text.split('\n');
    let html = '';
    let inList = false;
    let listType = 'ul';

    const formatBold = (value) => value.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    const closeList = () => {
        if (inList) {
            html += `</${listType}>`;
            inList = false;
        }
    };
    const openList = (type) => {
        if (!inList || listType !== type) {
            closeList();
            listType = type;
            html += `<${listType}>`;
            inList = true;
        }
    };

    lines.forEach((line) => {
        const trimmed = line.trim();

        if (trimmed === '---') {
            closeList();
            html += '<hr>';
            return;
        }

        if (trimmed.startsWith('### ')) {
            closeList();
            html += `<h3>${formatBold(trimmed.replace('### ', ''))}</h3>`;
            return;
        }

        if (trimmed.startsWith('## ')) {
            closeList();
            html += `<h2>${formatBold(trimmed.replace('## ', ''))}</h2>`;
            return;
        }

        if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
            closeList();
            html += `<h3>${formatBold(trimmed.replace(/\*\*/g, ''))}</h3>`;
            return;
        }

        if (/^\d+\.\s+/.test(trimmed)) {
            openList('ol');
            html += `<li>${formatBold(trimmed.replace(/^\d+\.\s+/, ''))}</li>`;
            return;
        }

        if (trimmed.startsWith('*') || trimmed.startsWith('-')) {
            openList('ul');
            html += `<li>${formatBold(trimmed.replace(/^(-|\*)\s+/, ''))}</li>`;
            return;
        }

        if (trimmed !== '') {
            closeList();
            html += `<p>${formatBold(trimmed)}</p>`;
        }
    });

    closeList();

    return `<div class="analysis-text">${html}</div>`;
}

function displayAnalysisResults(result) {
    analysisResultsDiv.style.display = 'block';
    let html = '<h2>📊 Subject Analysis Results</h2>';

    html += `
        <div class="question-pattern-card">
            <h4>Analysis Summary</h4>
            <p><strong>Total Questions Found:</strong> ${result.total_questions_found}</p>
            <p><strong>Similar Question Groups:</strong> ${result.similar_patterns}</p>
        </div>
    `;

    html += '<h3>🔄 Most Repeated Questions</h3>';
    if (result.repeated_questions && result.repeated_questions.length > 0) {
        result.repeated_questions.forEach((q, idx) => {
            html += `
                <div class="question-pattern-card">
                    <h4>Question ${idx + 1}</h4>
                    <p>${q.question_text}</p>
                    <div>
                        <span class="importance-badge">Appears ${q.frequency} time(s)</span>
                        <span class="importance-badge" style="background: rgba(40,167,69,0.2); color: #28a745; border-color: rgba(40,167,69,0.3);">Importance: ${q.importance}%</span>
                    </div>
                </div>
            `;
        });
    } else {
        html += '<p>No repeated questions found.</p>';
    }

    html += '<h3>📌 Important Topics to Focus On</h3>';
    if (result.important_topics && result.important_topics.length > 0) {
        result.important_topics.forEach(topic => {
            html += `
                <div class="question-pattern-card">
                    <h4>${topic.name}</h4>
                    <p>${topic.description}</p>
                </div>
            `;
        });
    } else {
        html += '<p>No specific topics identified.</p>';
    }

    analysisResultsDiv.innerHTML = html;
    analysisResultsDiv.scrollIntoView({ behavior: 'smooth' });
}

function displayLearningPlan(plan) {
    analysisResultsDiv.style.display = 'block';

    let html = `
        <div class="learning-plan-container">
            <h2>📚 Personalized Learning Plan</h2>
            <p><strong>Recommended Study Duration:</strong> ${plan.recommended_study_period}</p>
            <p><strong>Difficulty Progression:</strong> ${plan.difficulty_progression}</p>
            
            <h3>Study Focus Areas</h3>
    `;

    if (plan.focus_areas && plan.focus_areas.length > 0) {
        plan.focus_areas.forEach((area, idx) => {
            html += `
                <div class="study-focus-area">
                    <strong>${idx + 1}. ${area.topic}</strong>
                    <p>${area.description}</p>
                    <small><strong>Priority:</strong> ${area.priority} | <strong>Estimated Time:</strong> ${area.estimated_hours}h</small>
                </div>
            `;
        });
    }

    html += `
            <h3>Study Strategy</h3>
            <p>${plan.strategy}</p>
        </div>
    `;

    analysisResultsDiv.innerHTML = html;
    analysisResultsDiv.scrollIntoView({ behavior: 'smooth' });
}
