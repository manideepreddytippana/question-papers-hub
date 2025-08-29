// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const papersGrid = document.getElementById('papers-grid');
    const messageBox = document.getElementById('message-box');
    const searchInput = document.getElementById('search-input');
    
    // --- START: New Element Selectors ---
    const analyzeBtn = document.getElementById('analyze-selected-btn');
    const selectedCountSpan = document.getElementById('selected-count');
    const analysisModal = document.getElementById('analysis-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    const closeModalBtn = document.getElementById('close-modal-btn');
    // --- END: New Element Selectors ---

    let allPapers = [];
    let selectedFiles = []; // Array to store selected filenames

    // --- Populate Dropdowns ---
    async function populateDropdowns() {
        try {
            const [subjects, branches, regulations] = await Promise.all([
                fetch('/api/subjects').then(res => res.json()),
                fetch('/api/branches').then(res => res.json()),
                fetch('/api/regulations').then(res => res.json())
            ]);
            populateSelect('subject', subjects);
            populateSelect('branch', branches);
            populateSelect('regulation', regulations);
        } catch (error) {
            console.error('Error populating dropdowns:', error);
            showMessage('Failed to load form options.', 'error');
        }
    }

    function populateSelect(elementId, options) {
        const select = document.getElementById(elementId);
        select.innerHTML = '<option value="">Select an option</option>';
        options.forEach(option => {
            const opt = document.createElement('option');
            opt.value = option;
            opt.textContent = option;
            select.appendChild(opt);
        });
    }

    // --- Fetch and Display Papers ---
    async function fetchPapers() {
        try {
            const response = await fetch('/api/papers');
            if (!response.ok) throw new Error('Network response was not ok');
            allPapers = await response.json();
            displayPapers(allPapers);
        } catch (error) {
            console.error('Error fetching papers:', error);
            papersGrid.innerHTML = '<p>Could not fetch papers. Please try again later.</p>';
        }
    }

// In script.js, find the displayPapers function and modify the card.innerHTML

function displayPapers(papers) {
    papersGrid.innerHTML = '';
    if (papers.length === 0) {
        papersGrid.innerHTML = '<p>No question papers found.</p>';
        return;
    }
    papers.forEach(paper => {
        const card = document.createElement('div');
        card.className = 'paper-card';
        
        // MODIFICATION: Added the new delete button inside .paper-card-header
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

    // This listener for checkboxes can remain as is
    document.querySelectorAll('.select-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', handleFileSelection);
    });
}
    // Add this code to your script.js file

// Use event delegation for the delete buttons
papersGrid.addEventListener('click', function(event) {
    if (event.target.classList.contains('btn-delete')) {
        handleDelete(event);
    }
});

async function handleDelete(event) {
    const button = event.target;
    const filename = button.dataset.filename;

    // Ask for confirmation before deleting
    if (!confirm(`Are you sure you want to delete the paper "${filename}"? This action cannot be undone.`)) {
        return;
    }

    try {
        const response = await fetch(`/api/paper/delete/${filename}`, {
            method: 'DELETE',
        });

        const result = await response.json();

        if (response.ok) {
            // Remove the card from the UI on success
            button.closest('.paper-card').remove();
            showMessage('File deleted successfully!', 'success');
        } else {
            throw new Error(result.error || 'Failed to delete file.');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showMessage(`Error: ${error.message}`, 'error');
    }
}
    
    // --- START: New Functions for Multi-File Analysis ---

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

    async function analyzeMultipleFiles() {
        const userPrompt = prompt("Please enter your analysis instruction (e.g., 'Find repeated or similar questions between these papers'):");
        if (!userPrompt) {
            return; // User cancelled the prompt
        }

        modalTitle.textContent = "Analyzing...";
        modalBody.textContent = "Please wait while the analysis is in progress. This may take a moment.";
        analysisModal.style.display = 'flex';

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
            
            modalTitle.textContent = "Analysis Result";
            modalBody.textContent = result.analysis_result;

        } catch (error) {
            console.error('Multi-file analysis error:', error);
            modalTitle.textContent = "Error";
            modalBody.textContent = `An error occurred: ${error.message}`;
        }
    }

    analyzeBtn.addEventListener('click', analyzeMultipleFiles);
    closeModalBtn.addEventListener('click', () => {
        analysisModal.style.display = 'none';
    });
    
    // --- END: New Functions for Multi-File Analysis ---

    // --- Handle Form Submission ---
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(uploadForm);
        const submitButton = uploadForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = 'Uploading...';
        showMessage('Uploading file...', 'info');
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            if (response.ok) {
                showMessage('File uploaded successfully!', 'success');
                uploadForm.reset();
                fetchPapers(); // Refresh the list
            } else {
                throw new Error(result.error || 'Upload failed');
            }
        } catch (error) {
            console.error('Upload error:', error);
            showMessage(`Error: ${error.message}`, 'error');
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Upload Paper';
        }
    });
    
    // --- Search/Filter Functionality ---
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const filteredPapers = allPapers.filter(paper => 
            paper.subject.toLowerCase().includes(searchTerm) ||
            paper.branch.toLowerCase().includes(searchTerm) ||
            paper.regulation.toLowerCase().includes(searchTerm)
        );
        displayPapers(filteredPapers);
    });

    // --- Utility Functions ---
    function showMessage(message, type) {
        messageBox.textContent = message;
        messageBox.className = `message-box ${type}`;
        messageBox.style.display = 'block';
        setTimeout(() => {
            messageBox.style.display = 'none';
        }, 5000);
    }

    // --- Initial Load ---
    populateDropdowns();
    fetchPapers();
});