
document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const papersGrid = document.getElementById('papers-grid');
    const messageBox = document.getElementById('message-box');
    const searchInput = document.getElementById('search-input');
    
    const analyzeBtn = document.getElementById('analyze-selected-btn');
    const selectedCountSpan = document.getElementById('selected-count');
    const analysisModal = document.getElementById('analysis-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const analysisResultsDiv = document.getElementById('analysis-results');
    
    // Confirm Modal Elements
    const confirmModal = document.getElementById('confirm-modal');
    const confirmTitle = document.getElementById('confirm-title');
    const confirmMessage = document.getElementById('confirm-message');
    const confirmBtn = document.getElementById('confirm-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    
    // Upload Form Elements
    const branchSelect = document.getElementById('branch');
    const regulationSelect = document.getElementById('regulation');
    const semesterSelect = document.getElementById('semester');
    const subjectSelect = document.getElementById('subject');
    
    const branchFilterSelect = document.getElementById('branch-filter');
    const regulationFilterSelect = document.getElementById('regulation-filter');
    const yearFilterSelect = document.getElementById('year-filter');
    const semesterFilterSelect = document.getElementById('semester-filter');
    const subjectModeRadios = document.querySelectorAll('input[name="subject-mode"]');
    const subjectCheckboxesContainer = document.getElementById('subject-checkboxes-container');
    
    const batchDownloadBtn = document.getElementById('batch-download-btn');
    const analyzeSubjectBtn = document.getElementById('analyze-subject-btn');
    const generatePlanBtn = document.getElementById('generate-plan-btn');

    let allPapers = [];
    let allSubjects = [];
    let filteredPapers = [];
    let selectedFiles = [];
    let deleteFilename = null;  // Store filename for deletion

    async function initializeAll() {
        await populateDropdowns();
        await fetchPapers();
        attachUploadFormListeners();
    }

    async function populateDropdowns() {
        try {
            const [subjects, branches] = await Promise.all([
                fetch('/api/subjects').then(res => res.json()),
                fetch('/api/branches').then(res => res.json())
            ]);
            
            allSubjects = subjects;
            populateSelect('branch', branches);
            const regulations = await fetch('/api/regulations').then(r => r.json());
            populateSelect('regulation', regulations);
            populateSelect('subject', subjects);
            populateSelect('branch-filter', branches);
            populateSelect('regulation-filter', regulations);
            populateSubjectCheckboxes(subjects);
        } catch (error) {
            console.error('Error populating dropdowns:', error);
            showMessage('Failed to load form options.', 'error');
        }
    }

    function populateSelect(elementId, options) {
        const select = document.getElementById(elementId);
        if (!select) return;
        
        const currentValue = select.value;
        select.innerHTML = '<option value="">Select an option</option>';
        options.forEach(option => {
            const opt = document.createElement('option');
            opt.value = typeof option === 'string' ? option : option;
            opt.textContent = typeof option === 'string' ? option : option;
            select.appendChild(opt);
        });
        select.value = currentValue;
    }

    async function updateSemestersAndSubjects() {
        const branch = branchSelect.value;
        const regulation = regulationSelect.value;
        const hasSemesterSubjects = regulation === 'R22' && ['CSE (AI & ML)', 'CSE (AI & DS)'].includes(branch);
        
        semesterSelect.value = '';
        subjectSelect.value = '';
        
        if (hasSemesterSubjects) {
            semesterSelect.disabled = false;
            
            try {
                const semesters = await fetch(`/api/semesters?branch=${encodeURIComponent(branch)}&regulation=${encodeURIComponent(regulation)}`)
                    .then(res => res.json());
                
                populateSelect('semester', semesters);
            } catch (error) {
                console.error('Error fetching semesters:', error);
            }
        } else {
            semesterSelect.disabled = true;
        }
        
        subjectSelect.disabled = true;
    }

    async function updateSubjectsForSemester() {
        const branch = branchSelect.value;
        const regulation = regulationSelect.value;
        const semester = semesterSelect.value;
        const hasSemesterSubjects = regulation === 'R22' && ['CSE (AI & ML)', 'CSE (AI & DS)'].includes(branch);
        
        if (hasSemesterSubjects && semester) {
            try {
                const subjects = await fetch(`/api/subjects-by-criteria?branch=${encodeURIComponent(branch)}&regulation=${encodeURIComponent(regulation)}&semester=${encodeURIComponent(semester)}`)
                    .then(res => res.json());
                
                populateSelect('subject', subjects);
                subjectSelect.disabled = false;
                subjectSelect.value = ''; 
            } catch (error) {
                console.error('Error fetching subjects:', error);
                subjectSelect.disabled = true;
            }
        } else {
            subjectSelect.disabled = true;
            subjectSelect.value = '';
        }
    }

    function attachUploadFormListeners() {
        branchSelect.addEventListener('change', updateSemestersAndSubjects);
        regulationSelect.addEventListener('change', updateSemestersAndSubjects);
        semesterSelect.addEventListener('change', updateSubjectsForSemester);
    }

    function populateSubjectCheckboxes(subjects) {
        subjectCheckboxesContainer.innerHTML = '';
        subjects.forEach(subject => {
            const div = document.createElement('div');
            div.className = 'subject-checkbox';
            div.innerHTML = `
                <input type="checkbox" id="subject-${subject}" value="${subject}" name="subject" checked>
                <label for="subject-${subject}">${subject}</label>
            `;
            subjectCheckboxesContainer.appendChild(div);
            
            div.querySelector('input').addEventListener('change', () => {
                applyFilters();
            });
        });
    }

    subjectModeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'individual') {
                subjectCheckboxesContainer.style.display = 'grid';
                document.querySelectorAll('.subject-checkbox input').forEach(cb => {
                    cb.disabled = false;
                });
            } else {
                subjectCheckboxesContainer.style.display = 'none';
                // Select all when in "Select All" mode
                document.querySelectorAll('.subject-checkbox input').forEach(cb => {
                    cb.checked = true;
                });
            }
            applyFilters();
        });
    });

    function getSelectedSubjects() {
        const mode = document.querySelector('input[name="subject-mode"]:checked').value;
        if (mode === 'all') {
            return []; // Return empty array to show all subjects
        } else {
            return Array.from(document.querySelectorAll('.subject-checkbox input:checked'))
                .map(cb => cb.value);
        }
    }

    function getSelectedYearSemester() {
        const yearValue = yearFilterSelect.value;
        const semesterValue = semesterFilterSelect.value;
        return (yearValue && semesterValue) ? `${yearValue}-${semesterValue}` : null;
    }

    async function fetchPapers() {
        try {
            const response = await fetch('/api/papers');
            if (!response.ok) throw new Error('Network response was not ok');
            allPapers = await response.json();
            applyFilters();
            attachCheckboxListeners();
        } catch (error) {
            console.error('Error fetching papers:', error);
            papersGrid.innerHTML = '<p>Could not fetch papers. Please try again later.</p>';
        }
    }

    async function applyFilters() {
        const branch = branchFilterSelect.value || null;
        const regulation = regulationFilterSelect.value || null;
        const year = getSelectedYearSemester();
        const subjects = getSelectedSubjects();
        
        try {
            const response = await fetch('/api/filter-papers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ branch, regulation, year, subjects: subjects.length > 0 ? subjects : null })
            });
            
            filteredPapers = await response.json();
            displayPapers(filteredPapers);
            attachCheckboxListeners();
        } catch (error) {
            console.error('Error filtering papers:', error);
            filteredPapers = allPapers;
            displayPapers(allPapers);
            attachCheckboxListeners();
        }
    }

    async function updateFilterSubjects() {
        const branch = branchFilterSelect.value;
        const regulation = regulationFilterSelect.value;
        const yearValue = yearFilterSelect.value;
        const semesterValue = semesterFilterSelect.value;
        const semester = (yearValue && semesterValue) ? `${yearValue}-${semesterValue}` : '';
        const hasSemesterSubjects = regulation === 'R22' && ['CSE (AI & ML)', 'CSE (AI & DS)'].includes(branch) && !!semester;

        subjectCheckboxesContainer.innerHTML = '';

        if (hasSemesterSubjects) {
            try {
                const subjects = await fetch(`/api/subjects-by-criteria?branch=${encodeURIComponent(branch)}&regulation=${encodeURIComponent(regulation)}&semester=${encodeURIComponent(semester)}`)
                    .then(res => res.json());
                populateSubjectCheckboxes(subjects);
            } catch (error) {
                console.error('Error fetching filter subjects:', error);
                populateSubjectCheckboxes(allSubjects);
            }
        } else {
            if (branch && regulation && yearValue && semesterValue) {
                populateSubjectCheckboxes(allSubjects);
            } else {
                subjectCheckboxesContainer.innerHTML = '<p>Select branch, regulation, year, and semester to load individual subjects.</p>';
            }
        }

        const selectedMode = document.querySelector('input[name="subject-mode"]:checked').value;
        subjectCheckboxesContainer.style.display = selectedMode === 'individual' ? 'grid' : 'none';
    }

    async function handleFilterCriteriaChange() {
        await updateFilterSubjects();
        await applyFilters();
    }

    function displayPapers(papers) {
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

    function attachCheckboxListeners() {
        document.querySelectorAll('.select-checkbox').forEach(checkbox => {
            checkbox.removeEventListener('change', handleFileSelection);
            checkbox.addEventListener('change', handleFileSelection);
        });

        papersGrid.removeEventListener('click', handleDelete);
        papersGrid.addEventListener('click', function(event) {
            if (event.target.classList.contains('btn-delete')) {
                handleDelete(event);
            }
        });
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
        if (count >= 2) {
            analyzeBtn.disabled = false;
        } else {
            analyzeBtn.disabled = true;
        }
    }

    async function handleDelete(event) {
        const button = event.target;
        const filename = button.dataset.filename;
        deleteFilename = filename;  // Store for later use
        
        // Show confirm modal
        confirmTitle.textContent = 'Confirm Deletion';
        confirmMessage.textContent = `Are you sure you want to delete the paper "${filename}"? This action cannot be undone.`;
        confirmModal.style.display = 'flex';
        
        // Focus on delete button for enter key
        confirmBtn.focus();
    }

    // Confirm Modal Event Listeners
    confirmBtn.addEventListener('click', async () => {
        if (!deleteFilename) return;
        
        const filename = deleteFilename;
        confirmModal.style.display = 'none';
        
        try {
            const response = await fetch(`/api/paper/delete/${filename}`, {
                method: 'DELETE',
            });

            const result = await response.json();

            if (response.ok) {
                // Find and remove the card
                const card = document.querySelector(`[data-filename="${filename}"]`).closest('.paper-card');
                if (card) card.remove();
                
                showMessage('File deleted successfully!', 'success');
                await fetchPapers();
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

    // Close modal on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && confirmModal.style.display === 'flex') {
            confirmModal.style.display = 'none';
            deleteFilename = null;
        }
        
        // Confirm deletion on Enter key
        if (e.key === 'Enter' && confirmModal.style.display === 'flex') {
            confirmBtn.click();
        }
    });

    async function handleBatchDownload() {
        const papers = filteredPapers.length > 0 ? filteredPapers : allPapers;

        if (papers.length === 0) {
            showMessage('No papers found to download.', 'error');
            return;
        }

        showLoadingModal(`Preparing ${papers.length} papers...`);

        try {
            const response = await fetch('/api/batch-download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    filenames: papers.map(p => p.filename)
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Batch download failed');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `papers-${new Date().toISOString().split('T')[0]}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();

            closeModal();
            showMessage(`Downloaded ${papers.length} papers!`, 'success');
        } catch (error) {
            console.error('Download error:', error);
            closeModal();
            showMessage(`Error: ${error.message}`, 'error');
        }
    }

    async function handleAnalyzeSubject() {
        const papers = filteredPapers.length > 0 ? filteredPapers : allPapers;

        if (papers.length === 0) {
            showMessage('No papers found to analyze.', 'error');
            return;
        }

        showLoadingModal(`Analyzing ${papers.length} papers for patterns...`);

        try {
            const response = await fetch('/api/analyze-subject', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    filenames: papers.map(p => p.filename),
                    branch: branchFilterSelect.value,
                    year: getSelectedYearSemester(),
                    subjects: getSelectedSubjects()
                })
            });

            const result = await response.json();
            closeModal();
            displayAnalysisResults(result);
        } catch (error) {
            console.error('Analysis error:', error);
            closeModal();
            showMessage('Error analyzing papers: ' + error.message, 'error');
        }
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

        // Most Repeated Questions
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

        // Important Topics
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

    async function handleGenerateLearningPlan() {
        const papers = filteredPapers.length > 0 ? filteredPapers : allPapers;

        if (papers.length === 0) {
            showMessage('No papers found to analyze.', 'error');
            return;
        }

        showLoadingModal('Generating personalized learning plan...');

        try {
            const response = await fetch('/api/generate-learning-plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    filenames: papers.map(p => p.filename),
                    branch: branchFilterSelect.value,
                    year: getSelectedYearSemester(),
                    subjects: getSelectedSubjects()
                })
            });

            const result = await response.json();
            closeModal();
            displayLearningPlan(result);
        } catch (error) {
            console.error('Learning plan error:', error);
            closeModal();
            showMessage('Error generating learning plan: ' + error.message, 'error');
        }
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

    async function analyzeMultipleFiles() {
        const userPrompt = prompt("Please enter your analysis instruction (e.g., 'Find repeated or similar questions between these papers'):");
        if (!userPrompt) {
            return;
        }

        showLoadingModal("Analyzing selected files...");

        try {
            const response = await fetch('/api/analyze-multiple', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    filenames: selectedFiles,
                    prompt: userPrompt
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Analysis failed.');
            }
            
            closeModal();
            modalTitle.textContent = "Analysis Result";
            modalBody.innerHTML = `<p>${result.analysis_result}</p>`;
            analysisModal.style.display = 'flex';

        } catch (error) {
            console.error('Multi-file analysis error:', error);
            closeModal();
            showMessage(`Error: ${error.message}`, 'error');
        }
    }

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(uploadForm);
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                showMessage('File uploaded successfully!', 'success');
                uploadForm.reset();
                semesterSelect.disabled = true;
                subjectSelect.disabled = true;
                await fetchPapers();
            } else {
                showMessage('Upload failed: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            showMessage('Upload error: ' + error.message, 'error');
        }
    });

    function showLoadingModal(message) {
        modalTitle.textContent = 'Processing...';
        modalBody.innerHTML = `<p>${message}</p><div class="loading-spinner"></div>`;
        analysisModal.style.display = 'flex';
    }

    function closeModal() {
        analysisModal.style.display = 'none';
    }

    closeModalBtn.addEventListener('click', closeModal);

    function showMessage(msg, type) {
        messageBox.className = `message-box ${type}`;
        messageBox.textContent = msg;
        messageBox.style.display = 'block';
        setTimeout(() => {
            messageBox.style.display = 'none';
        }, 5000);
    }

    branchFilterSelect.addEventListener('change', handleFilterCriteriaChange);
    regulationFilterSelect.addEventListener('change', handleFilterCriteriaChange);
    yearFilterSelect.addEventListener('change', handleFilterCriteriaChange);
    semesterFilterSelect.addEventListener('change', handleFilterCriteriaChange);
    
    analyzeBtn.addEventListener('click', analyzeMultipleFiles);
    batchDownloadBtn.addEventListener('click', handleBatchDownload);
    analyzeSubjectBtn.addEventListener('click', handleAnalyzeSubject);
    generatePlanBtn.addEventListener('click', handleGenerateLearningPlan);

    // Search functionality
    searchInput.addEventListener('input', (e) => {
        const search = e.target.value.toLowerCase();
        const filtered = allPapers.filter(p => 
            p.subject.toLowerCase().includes(search) || 
            p.branch.toLowerCase().includes(search)
        );
        displayPapers(filtered);
        attachCheckboxListeners();
    });

    initializeAll().then(updateFilterSubjects);
});
