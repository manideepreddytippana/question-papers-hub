/**
 * UI module — DOM manipulation utilities.
 *
 * Handles messages, modals, and dropdown population.
 */

// ─── Elements (cached on first use) ─────────────

let _messageBox, _analysisModal, _modalTitle, _modalBody, _closeModalBtn;

function getElements() {
    if (!_messageBox) {
        _messageBox = document.getElementById('message-box');
        _analysisModal = document.getElementById('analysis-modal');
        _modalTitle = document.getElementById('modal-title');
        _modalBody = document.getElementById('modal-body');
        _closeModalBtn = document.getElementById('close-modal-btn');

        if (_closeModalBtn) {
            _closeModalBtn.addEventListener('click', closeModal);
        }
    }
}

// ─── Messages ────────────────────────────────────

export function showMessage(msg, type) {
    getElements();
    _messageBox.className = `message-box ${type}`;
    _messageBox.textContent = msg;
    _messageBox.style.display = 'block';
    setTimeout(() => {
        _messageBox.style.display = 'none';
    }, 5000);
}

// ─── Modal ───────────────────────────────────────

export function showLoadingModal(message) {
    getElements();
    _modalTitle.textContent = 'Processing...';
    _modalBody.innerHTML = `<p>${message}</p><div class="loading-spinner"></div>`;
    _analysisModal.style.display = 'flex';
}

export function closeModal() {
    getElements();
    _analysisModal.style.display = 'none';
}

export function showResultModal(title, bodyHtml) {
    getElements();
    _modalTitle.textContent = title;
    _modalBody.innerHTML = bodyHtml;
    _analysisModal.style.display = 'flex';
}

// ─── Dropdown helpers ────────────────────────────

export function populateSelect(elementId, options) {
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

export function populateSubjectCheckboxes(subjects, container, onChangeCallback) {
    container.innerHTML = '';
    subjects.forEach(subject => {
        const div = document.createElement('div');
        div.className = 'subject-checkbox';
        div.innerHTML = `
            <input type="checkbox" id="subject-${subject}" value="${subject}" name="subject" checked>
            <label for="subject-${subject}">${subject}</label>
        `;
        container.appendChild(div);

        div.querySelector('input').addEventListener('change', () => {
            if (onChangeCallback) onChangeCallback();
        });
    });
}
