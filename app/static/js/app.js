/**
 * App — main entry point.
 *
 * Initializes all modules, populates dropdowns, and wires everything together.
 */

import * as api from './api.js';
import * as filters from './filters.js';
import * as papers from './papers.js';
import { populateSelect, populateSubjectCheckboxes, showMessage } from './ui.js';

document.addEventListener('DOMContentLoaded', () => {
    // Upload form elements
    const uploadForm = document.getElementById('upload-form');
    const branchSelect = document.getElementById('branch');
    const regulationSelect = document.getElementById('regulation');
    const semesterSelect = document.getElementById('semester');
    const subjectSelect = document.getElementById('subject');
    const searchInput = document.getElementById('search-input');

    // Sidebar navigation
    const allPapersLink = document.getElementById('all-papers-link');
    const papersSection = document.getElementById('papers-section');
    const papersSectionTitle = document.getElementById('papers-section-title');

    let allPapers = [];
    let allSubjects = [];

    // ─── Initialization ──────────────────────────

    async function initializeAll() {
        await populateDropdowns();
        await fetchAndDisplayPapers();
        attachUploadFormListeners();
    }

    async function populateDropdowns() {
        try {
            const [subjects, branches] = await Promise.all([
                api.fetchSubjects(),
                api.fetchBranches(),
            ]);

            allSubjects = subjects;
            populateSelect('branch', branches);

            const regulations = await api.fetchRegulations();
            populateSelect('regulation', regulations);
            populateSelect('subject', subjects);
            populateSelect('branch-filter', branches);
            populateSelect('regulation-filter', regulations);

            // Initialize subject checkboxes in filter panel
            const container = document.getElementById('subject-checkboxes-container');
            populateSubjectCheckboxes(subjects, container, applyFilters);
        } catch (error) {
            console.error('Error populating dropdowns:', error);
            showMessage('Failed to load form options.', 'error');
        }
    }

    // ─── Data fetching ───────────────────────────

    async function fetchAndDisplayPapers() {
        try {
            allPapers = await api.fetchPapers();
            applyFilters();
        } catch (error) {
            console.error('Error fetching papers:', error);
            document.getElementById('papers-grid').innerHTML =
                '<p>Could not fetch papers. Please try again later.</p>';
        }
    }

    async function applyFilters() {
        const filterValues = filters.getFilterValues();
        papers.updateActionButtonStates();

        try {
            const filteredPapers = await api.filterPapers(filterValues);
            papers.displayPapers(filteredPapers);
        } catch (error) {
            console.error('Error filtering papers:', error);
            papers.displayPapers(allPapers);
        }
    }

    // ─── Upload form ─────────────────────────────

    async function updateSemestersAndSubjects() {
        const branch = branchSelect.value;
        const regulation = regulationSelect.value;
        const hasSemesterSubjects = regulation === 'R22'
            && ['CSE', 'CSE (AI & ML)', 'CSE (AI & DS)'].includes(branch);

        semesterSelect.value = '';
        subjectSelect.value = '';

        if (hasSemesterSubjects) {
            semesterSelect.disabled = false;
            try {
                const semesters = await api.fetchSemesters(branch, regulation);
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
        const hasSemesterSubjects = regulation === 'R22'
            && ['CSE', 'CSE (AI & ML)', 'CSE (AI & DS)'].includes(branch);

        if (hasSemesterSubjects && semester) {
            try {
                const subjects = await api.fetchSubjectsByCriteria(branch, regulation, semester);
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

    // ─── Upload submission ───────────────────────

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(uploadForm);

        try {
            const { ok, data } = await api.uploadPaper(formData);

            if (ok) {
                showMessage('File uploaded successfully!', 'success');
                uploadForm.reset();
                semesterSelect.disabled = true;
                subjectSelect.disabled = true;
                await fetchAndDisplayPapers();
            } else {
                showMessage('Upload failed: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            showMessage('Upload error: ' + error.message, 'error');
        }
    });

    // ─── Search ──────────────────────────────────

    searchInput.addEventListener('input', (e) => {
        const search = e.target.value.toLowerCase();
        const filtered = allPapers.filter(p =>
            p.subject.toLowerCase().includes(search) ||
            p.branch.toLowerCase().includes(search)
        );
        papers.displayPapers(filtered);
    });

    // ─── Sidebar navigation ─────────────────────

    if (allPapersLink && papersSection && papersSectionTitle) {
        allPapersLink.addEventListener('click', (e) => {
            e.preventDefault();
            papersSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            setTimeout(() => papersSectionTitle.focus(), 250);
        });
    }

    // ─── Boot ────────────────────────────────────

    // Initialize filter module
    filters.init(allSubjects, applyFilters);

    // Initialize papers module
    papers.init(fetchAndDisplayPapers);

    // Start the app
    initializeAll().then(async () => {
        await filters.updateFilterSubjects();
        papers.updateActionButtonStates();
    });
});
