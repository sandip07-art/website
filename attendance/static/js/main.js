// Main JavaScript for Attendance Management System

// Global variables
let currentUser = null;
let scannerActive = false;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize application
function initializeApp() {
    // Set up tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Set up form validation
    setupFormValidation();
    
    // Set up real-time updates
    setupRealTimeUpdates();
    
    // Initialize QR scanner if on student page
    if (window.location.pathname.includes('/student')) {
        initializeQRScanner();
    }
}

// Form validation
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

// Real-time updates
function setupRealTimeUpdates() {
    // Update time every second
    setInterval(updateTime, 1000);
    
    // Check for new notifications every 30 seconds
    setInterval(checkNotifications, 30000);
}

// Update time display
function updateTime() {
    const timeElements = document.querySelectorAll('.current-time');
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    
    timeElements.forEach(element => {
        element.textContent = timeString;
    });
}

// Check for notifications
function checkNotifications() {
    // This would typically make an AJAX call to check for new notifications
    // For now, we'll just log it
    console.log('Checking for notifications...');
}

// QR Scanner functionality
function initializeQRScanner() {
    // Check if browser supports camera access
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showAlert('Camera access is not supported in this browser.', 'warning');
        return;
    }
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container') || createAlertContainer();
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alert-container';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Loading states
function showLoading(element) {
    element.classList.add('loading');
    element.disabled = true;
}

function hideLoading(element) {
    element.classList.remove('loading');
    element.disabled = false;
}

// AJAX helper
function makeRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    return fetch(url, mergedOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('Request failed:', error);
            showAlert('Request failed. Please try again.', 'danger');
            throw error;
        });
}

// Export functions
function exportToCSV(data, filename) {
    const csv = convertToCSV(data);
    downloadFile(csv, filename, 'text/csv');
}

function exportToExcel(data, filename) {
    // This would typically use a library like SheetJS
    console.log('Export to Excel:', data);
    showAlert('Excel export functionality will be implemented.', 'info');
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvHeaders = headers.join(',');
    
    const csvRows = data.map(row => {
        return headers.map(header => {
            const value = row[header];
            return typeof value === 'string' ? `"${value}"` : value;
        }).join(',');
    });
    
    return [csvHeaders, ...csvRows].join('\n');
}

// Session management
function startSession(sessionData) {
    return makeRequest('/api/sessions', {
        method: 'POST',
        body: JSON.stringify(sessionData)
    });
}

function endSession(sessionId) {
    return makeRequest(`/api/sessions/${sessionId}/end`, {
        method: 'POST'
    });
}

// Attendance functions
function markAttendance(qrData) {
    return makeRequest('/api/attendance', {
        method: 'POST',
        body: JSON.stringify({ qr_data: qrData })
    });
}

function getAttendanceHistory(userId) {
    return makeRequest(`/api/attendance/history/${userId}`);
}

// User management
function createUser(userData) {
    return makeRequest('/api/users', {
        method: 'POST',
        body: JSON.stringify(userData)
    });
}

function updateUser(userId, userData) {
    return makeRequest(`/api/users/${userId}`, {
        method: 'PUT',
        body: JSON.stringify(userData)
    });
}

function deleteUser(userId) {
    return makeRequest(`/api/users/${userId}`, {
        method: 'DELETE'
    });
}

// QR Code functions
function generateQRCode(data) {
    return makeRequest('/api/qr/generate', {
        method: 'POST',
        body: JSON.stringify({ data: data })
    });
}

function scanQRCode(imageData) {
    return makeRequest('/api/qr/scan', {
        method: 'POST',
        body: JSON.stringify({ image_data: imageData })
    });
}

// Print functions
function printElement(elementId) {
    const element = document.getElementById(elementId);
    if (!element) {
        showAlert('Element not found for printing.', 'warning');
        return;
    }
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
            <head>
                <title>Print</title>
                <style>
                    body { font-family: Arial, sans-serif; }
                    .print-only { display: block; }
                    @media print {
                        .no-print { display: none; }
                    }
                </style>
            </head>
            <body>
                ${element.innerHTML}
            </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
}

// Theme functions
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
}

// Initialize theme on load
loadTheme();

// Error handling
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    showAlert('An unexpected error occurred. Please refresh the page.', 'danger');
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showAlert('A network error occurred. Please check your connection.', 'warning');
});

// Export functions to global scope for use in templates
window.showAlert = showAlert;
window.makeRequest = makeRequest;
window.printElement = printElement;
window.toggleTheme = toggleTheme;
