// Court Data Fetcher - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeFormValidation();
    initializeLoadingSpinner();
    initializeAutoHideAlerts();
    initializeTooltips();
    initializeCopyToClipboard();
    initializeSearchHistory();
});

// Form Validation
function initializeFormValidation() {
    const form = document.getElementById('searchForm');
    if (!form) return;

    const caseTypeSelect = document.getElementById('case_type');
    const caseNumberInput = document.getElementById('case_number');
    const filingYearSelect = document.getElementById('filing_year');

    // Real-time validation
    if (caseNumberInput) {
        caseNumberInput.addEventListener('input', function() {
            validateCaseNumber(this.value);
        });
    }

    if (filingYearSelect) {
        filingYearSelect.addEventListener('change', function() {
            validateFilingYear(this.value);
        });
    }

    // Form submission validation
    form.addEventListener('submit', function(e) {
        let isValid = true;

        // Validate case type
        if (!caseTypeSelect.value) {
            showFieldError(caseTypeSelect, 'Please select a case type');
            isValid = false;
        } else {
            clearFieldError(caseTypeSelect);
        }

        // Validate case number
        if (!caseNumberInput.value.trim()) {
            showFieldError(caseNumberInput, 'Please enter a case number');
            isValid = false;
        } else if (!isValidCaseNumber(caseNumberInput.value)) {
            showFieldError(caseNumberInput, 'Please enter a valid case number');
            isValid = false;
        } else {
            clearFieldError(caseNumberInput);
        }

        // Validate filing year
        if (!filingYearSelect.value) {
            showFieldError(filingYearSelect, 'Please select a filing year');
            isValid = false;
        } else if (!isValidFilingYear(filingYearSelect.value)) {
            showFieldError(filingYearSelect, 'Please select a valid filing year');
            isValid = false;
        } else {
            clearFieldError(filingYearSelect);
        }

        if (!isValid) {
            e.preventDefault();
            showAlert('Please correct the errors above before submitting.', 'danger');
        }
    });
}

// Validation functions
function validateCaseNumber(value) {
    const input = document.getElementById('case_number');
    if (!value.trim()) {
        showFieldError(input, 'Case number is required');
        return false;
    }
    if (value.length < 3) {
        showFieldError(input, 'Case number must be at least 3 characters');
        return false;
    }
    if (value.length > 50) {
        showFieldError(input, 'Case number must be less than 50 characters');
        return false;
    }
    if (!/^[A-Za-z0-9\s\-\.\/]+$/.test(value)) {
        showFieldError(input, 'Case number contains invalid characters');
        return false;
    }
    clearFieldError(input);
    return true;
}

function validateFilingYear(value) {
    const select = document.getElementById('filing_year');
    const currentYear = new Date().getFullYear();
    const year = parseInt(value);
    
    if (!value) {
        showFieldError(select, 'Filing year is required');
        return false;
    }
    if (year < 1950) {
        showFieldError(select, 'Filing year cannot be before 1950');
        return false;
    }
    if (year > currentYear + 1) {
        showFieldError(select, `Filing year cannot be after ${currentYear + 1}`);
        return false;
    }
    clearFieldError(select);
    return true;
}

function isValidCaseNumber(value) {
    return value.trim().length >= 3 && 
           value.trim().length <= 50 && 
           /^[A-Za-z0-9\s\-\.\/]+$/.test(value);
}

function isValidFilingYear(value) {
    const currentYear = new Date().getFullYear();
    const year = parseInt(value);
    return year >= 1950 && year <= currentYear + 1;
}

// Field error handling
function showFieldError(element, message) {
    element.classList.add('is-invalid');
    let feedback = element.parentNode.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        element.parentNode.appendChild(feedback);
    }
    feedback.textContent = message;
}

function clearFieldError(element) {
    element.classList.remove('is-invalid');
    const feedback = element.parentNode.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.textContent = '';
    }
}

// Loading Spinner
function initializeLoadingSpinner() {
    const spinner = document.getElementById('loadingSpinner');
    if (!spinner) return;

    // Show spinner on form submission
    const form = document.getElementById('searchForm');
    if (form) {
        form.addEventListener('submit', function() {
            spinner.classList.remove('d-none');
        });
    }

    // Hide spinner when page loads
    window.addEventListener('load', function() {
        spinner.classList.add('d-none');
    });
}

// Auto-hide alerts
function initializeAutoHideAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Show custom alert
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('main .container');
    if (!alertContainer) return;

    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="fas fa-${type === 'danger' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    alertContainer.insertAdjacentHTML('afterbegin', alertHtml);
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        const newAlert = alertContainer.querySelector('.alert');
        if (newAlert) {
            const bsAlert = new bootstrap.Alert(newAlert);
            bsAlert.close();
        }
    }, 5000);
}

// Tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Copy to clipboard functionality
function initializeCopyToClipboard() {
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            copyToClipboard(textToCopy);
            
            // Show feedback
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
            this.classList.add('btn-success');
            this.classList.remove('btn-outline-secondary');
            
            setTimeout(() => {
                this.innerHTML = originalText;
                this.classList.remove('btn-success');
                this.classList.add('btn-outline-secondary');
            }, 2000);
        });
    });
}

function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        textArea.remove();
    }
}

// Search History
function initializeSearchHistory() {
    const historyTable = document.querySelector('#searchHistoryTable');
    if (!historyTable) return;

    // Add click handlers for re-search
    const reSearchButtons = historyTable.querySelectorAll('.btn-re-search');
    reSearchButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const caseType = this.getAttribute('data-case-type');
            const caseNumber = this.getAttribute('data-case-number');
            const filingYear = this.getAttribute('data-filing-year');
            
            // Fill the search form
            document.getElementById('case_type').value = caseType;
            document.getElementById('case_number').value = caseNumber;
            document.getElementById('filing_year').value = filingYear;
            
            // Scroll to search form
            document.getElementById('searchForm').scrollIntoView({ 
                behavior: 'smooth' 
            });
        });
    });
}

// Download progress
function initializeDownloadProgress() {
    const downloadButtons = document.querySelectorAll('.btn-download');
    downloadButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Downloading...';
            this.disabled = true;
            
            // Re-enable after 3 seconds (simulate download time)
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 3000);
        });
    });
}

// API calls
async function fetchCaseTypes() {
    try {
        const response = await fetch('/api/case-types');
        const data = await response.json();
        return data.case_types;
    } catch (error) {
        console.error('Error fetching case types:', error);
        return [];
    }
}

async function fetchSearchHistory() {
    try {
        const response = await fetch('/api/search-history');
        const data = await response.json();
        return data.history;
    } catch (error) {
        console.error('Error fetching search history:', error);
        return [];
    }
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for global use
window.CourtDataFetcher = {
    showAlert,
    copyToClipboard,
    formatDate,
    formatFileSize,
    fetchCaseTypes,
    fetchSearchHistory
}; 