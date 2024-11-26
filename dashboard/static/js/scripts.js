// File: dashboard/static/js/scripts.js

/**
 * State for managing auto-scroll functionality in the console log viewer.
 */
let autoScroll = true;
let isFetching = false;

/**
 * Toggles the auto-scroll feature on or off and updates the button label.
 */
export function toggleAutoScroll() {
    autoScroll = !autoScroll;
    const button = document.getElementById('toggleButton');
    button.textContent = autoScroll ? 'Disable Autoscroll' : 'Enable Autoscroll';
    button.setAttribute('aria-pressed', autoScroll);
}

/**
 * Displays or hides the loading indicator.
 * @param {boolean} show - Whether to show the loading indicator.
 */
function showLoading(show) {
    const consoleOutput = document.getElementById('consoleOutput');
    if (show) {
        consoleOutput.innerHTML = `
            <div class="d-flex justify-content-center align-items-center" style="height: 100%;">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>`;
    }
}

/**
 * Displays an error message in the console output area.
 * @param {string} message - The error message to display.
 */
function displayError(message) {
    const consoleOutput = document.getElementById('consoleOutput');
    consoleOutput.innerHTML = `<div class="text-danger">${message}</div>`;
}

/**
 * Updates the console log viewer with new log data.
 * @param {string[]} logs - Array of log strings to display.
 */
function updateConsoleLogs(logs) {
    const consoleOutput = document.getElementById('consoleOutput');
    // Clear existing logs
    consoleOutput.innerHTML = '';
    // Populate with new logs
    logs.forEach(log => {
        const logEntry = document.createElement('div');
        logEntry.textContent = log;
        consoleOutput.appendChild(logEntry);
    });
    // Handle autoscroll
    if (autoScroll) {
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }
}

/**
 * Fetches the latest console logs from the server and updates the console log viewer.
 */
export async function fetchConsoleLogs() {
    if (isFetching) return; // Prevent overlapping fetches
    isFetching = true;
    try {
        showLoading(true);
        const response = await fetch('/api/console');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        updateConsoleLogs(data.logs);
    } catch (error) {
        console.error('Error fetching console logs:', error);
        displayError(`Failed to fetch console logs: ${error.message}`);
    } finally {
        showLoading(false);
        isFetching = false;
    }
}

// Initialize log fetching on DOM content loaded
document.addEventListener('DOMContentLoaded', () => {
    fetchConsoleLogs(); // Initial fetch
    setInterval(fetchConsoleLogs, 5000); // Fetch every 5 seconds
});
