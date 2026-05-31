/**
 * Filters module — filter panel logic and subject selection.
 */

import * as api from './api.js';
import { populateSelect, populateSubjectCheckboxes } from './ui.js';

// ─── State ───────────────────────────────────────

let allSubjects = [];
let onFilterChangeCallback = null;

// ─── Elements ────────────────────────────────────

const branchFilterSelect = document.getElementById('branch-filter');
const regulationFilterSelect = document.getElementById('regulation-filter');
const yearFilterSelect = document.getElementById('year-filter');
const semesterFilterSelect = document.getElementById('semester-filter');
const subjectModeRadios = document.querySelectorAll('input[name="subject-mode"]');
const subjectCheckboxesContainer = document.getElementById('subject-checkboxes-container');

// ─── Public API ──────────────────────────────────

export function init(subjects, filterChangeCallback) {
    allSubjects = subjects;
    onFilterChangeCallback = filterChangeCallback;

    // Attach filter change listeners
    branchFilterSelect.addEventListener('change', handleFilterCriteriaChange);
    regulationFilterSelect.addEventListener('change', handleFilterCriteriaChange);
    yearFilterSelect.addEventListener('change', handleFilterCriteriaChange);
    semesterFilterSelect.addEventListener('change', handleFilterCriteriaChange);

    // Subject mode radio listeners
    subjectModeRadios.forEach(radio => {
        radio.addEventListener('change', async (e) => {
            if (e.target.value === 'individual') {
                subjectCheckboxesContainer.style.display = '';
                await updateFilterSubjects();
            } else {
                subjectCheckboxesContainer.style.display = 'none';
                document.querySelectorAll('.subject-checkbox input').forEach(cb => {
                    cb.checked = true;
                });
            }
            if (onFilterChangeCallback) await onFilterChangeCallback();
        });
    });
}

export function getSelectedSubjects() {
    const mode = document.querySelector('input[name="subject-mode"]:checked').value;
    if (mode === 'all') {
        return [];
    }
    return Array.from(document.querySelectorAll('.subject-checkbox input:checked'))
        .map(cb => cb.value);
}

export function getSelectedYearSemester() {
    const yearValue = yearFilterSelect.value;
    const semesterValue = semesterFilterSelect.value;
    if (!yearValue) return null;
    return semesterValue ? `${yearValue}-${semesterValue}` : yearValue;
}

export function getFilterValues() {
    return {
        branch: branchFilterSelect.value || null,
        regulation: regulationFilterSelect.value || null,
        year: getSelectedYearSemester(),
        subjects: getSelectedSubjects(),
    };
}

export function hasBranchSelected() {
    return !!branchFilterSelect.value;
}

export async function updateFilterSubjects() {
    const branch = branchFilterSelect.value;
    const regulation = regulationFilterSelect.value;
    const yearValue = yearFilterSelect.value;
    const semesterValue = semesterFilterSelect.value;
    const semester = (yearValue && semesterValue) ? `${yearValue}-${semesterValue}` : '';
    const isCriteriaComplete = !!(branch && regulation && yearValue && semesterValue);
    const hasSemesterSubjects = regulation === 'R22'
        && ['CSE', 'CSE (AI & ML)', 'CSE (AI & DS)'].includes(branch)
        && !!semester;

    subjectCheckboxesContainer.innerHTML = '';

    if (!isCriteriaComplete) {
        subjectCheckboxesContainer.innerHTML =
            '<p class="subject-selection-hint">Select branch, regulation, year, and semester to enable individual subjects.</p>';
        setSubjectPanelDisabledState(true);
    } else if (hasSemesterSubjects) {
        try {
            const subjects = await api.fetchSubjectsByCriteria(branch, regulation, semester);
            populateSubjectCheckboxes(subjects, subjectCheckboxesContainer, onFilterChangeCallback);
            setSubjectPanelDisabledState(false);
        } catch (error) {
            console.error('Error fetching filter subjects:', error);
            populateSubjectCheckboxes(allSubjects, subjectCheckboxesContainer, onFilterChangeCallback);
            setSubjectPanelDisabledState(false);
        }
    } else {
        populateSubjectCheckboxes(allSubjects, subjectCheckboxesContainer, onFilterChangeCallback);
        setSubjectPanelDisabledState(false);
    }

    const selectedMode = document.querySelector('input[name="subject-mode"]:checked').value;
    subjectCheckboxesContainer.style.display = selectedMode === 'individual' ? '' : 'none';
}

// ─── Private helpers ─────────────────────────────

function setSubjectPanelDisabledState(isDisabled) {
    subjectCheckboxesContainer.classList.toggle('is-disabled', isDisabled);
    document.querySelectorAll('.subject-checkbox input').forEach(cb => {
        cb.disabled = isDisabled;
    });
}

async function handleFilterCriteriaChange() {
    await updateFilterSubjects();
    if (onFilterChangeCallback) await onFilterChangeCallback();
}
