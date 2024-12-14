// File: dashboard/static/js/scripts.js

/**
 * State for managing auto-scroll functionality in the console log viewer.
 */
let autoScroll = true;
let isFetching = false;
let lastLogIndex = 0; // To keep track of the last fetched log

/**
 * Toggles the auto-scroll feature on or off and updates the button label.
 */
export function toggleAutoScroll() {
    autoScroll = !autoScroll;
    const button = document.getElementById('toggleButton');
    if (button) {
        button.textContent = autoScroll ? 'Disable Autoscroll' : 'Enable Autoscroll';
        button.setAttribute('aria-pressed', autoScroll);
    }
}

/**
 * Shows or hides the loading spinner.
 * @param {boolean} show - Whether to show the spinner.
 */
function showSpinner(show) {
    const spinner = document.getElementById('spinner');
    if (spinner) {
        spinner.style.display = show ? 'flex' : 'none';
    }
}

/**
 * Displays an error message in the console output area.
 * @param {string} message - The error message to display.
 */
function displayError(message) {
    const logsContainer = document.getElementById('logsContainer');
    const spinner = document.getElementById('spinner');
    if (!logsContainer || !spinner) return;

    // Hide spinner and clear existing logs
    showSpinner(false);
    logsContainer.innerHTML = `<div class="text-danger">${message}</div>`;
}

/**
 * Appends new log entries to the console output.
 * @param {string[]} newLogs - Array of new log strings to append.
 */
function appendConsoleLogs(newLogs) {
    const logsContainer = document.getElementById('logsContainer');
    if (!logsContainer) return;

    newLogs.forEach(log => {
        if (log.trim() === "") return; // Skip empty log entries
        const logEntry = document.createElement('div');
        logEntry.textContent = log;
        logsContainer.appendChild(logEntry);
    });
    // Handle autoscroll
    if (autoScroll) {
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }
}

/**
 * Fetches the latest console logs from the server and updates the console log viewer.
 */
export async function fetchConsoleLogs() {
    if (isFetching) return; // Prevent overlapping fetches
    isFetching = true;
    try {
        // Show spinner only during the initial fetch
        if (lastLogIndex === 0) {
            showSpinner(true);
        }
        const response = await fetch('/api/console');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        if (lastLogIndex === 0) {
            showSpinner(false); // Hide spinner after the first fetch
        }

        const newLogs = data.logs.slice(lastLogIndex);
        if (newLogs.length > 0) {
            appendConsoleLogs(newLogs);
            lastLogIndex = data.logs.length;
        }
    } catch (error) {
        console.error('Error fetching console logs:', error);
        displayError(`Failed to fetch console logs: ${error.message}`);
    } finally {
        isFetching = false;
    }
}

/**
 * Debounce function to limit the rate at which a function can fire.
 * @param {Function} func - The function to debounce.
 * @param {number} delay - Delay in milliseconds.
 * @returns {Function} - The debounced function.
 */
function debounce(func, delay) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

// Initialize log fetching and auto-scroll toggling when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const toggleButton = document.getElementById('toggleButton');

    if (toggleButton) {
        toggleButton.addEventListener('click', toggleAutoScroll);
    }
    fetchConsoleLogs(); // Initial fetch
    setInterval(fetchConsoleLogs, 5000); // Fetch every 5 seconds
});
