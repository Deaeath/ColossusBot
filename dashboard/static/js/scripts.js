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
 * Displays or hides the loading indicator.
 * @param {boolean} show - Whether to show the loading indicator.
 */
function showLoading(show) {
    const consoleOutput = document.getElementById('consoleOutput');
    if (!consoleOutput) return;

    if (show) {
        // Add a spinner only if it's not already present
        if (!consoleOutput.querySelector('.spinner-border')) {
            const spinnerDiv = document.createElement('div');
            spinnerDiv.classList.add('d-flex', 'justify-content-center', 'align-items-center');
            spinnerDiv.style.height = '100%';
            spinnerDiv.innerHTML = `
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>`;
            consoleOutput.appendChild(spinnerDiv);
        }
    } else {
        // Remove the spinner if it exists
        const spinnerDiv = consoleOutput.querySelector('.spinner-border');
        if (spinnerDiv) {
            spinnerDiv.parentElement.remove();
        }
    }
}

/**
 * Displays an error message in the console output area.
 * @param {string} message - The error message to display.
 */
function displayError(message) {
    const consoleOutput = document.getElementById('consoleOutput');
    if (!consoleOutput) return;

    // Clear existing content and display the error
    consoleOutput.innerHTML = `<div class="text-danger">${message}</div>`;
}

/**
 * Appends new log entries to the console output.
 * @param {string[]} newLogs - Array of new log strings to append.
 */
function appendConsoleLogs(newLogs) {
    const consoleOutput = document.getElementById('consoleOutput');
    if (!consoleOutput) return;

    newLogs.forEach(log => {
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
        // Show loading indicator only during the first fetch
        if (lastLogIndex === 0) {
            showLoading(true);
        }
        const response = await fetch('/api/console');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        if (lastLogIndex === 0) {
            showLoading(false); // Remove the spinner after the first fetch
        }

        const newLogs = data.logs.slice(lastLogIndex);
        if (newLogs.length > 0) {
            appendConsoleLogs(newLogs);
            lastLogIndex = data.logs.length;
        }
    } catch (error) {
        console.error('Error fetching console logs:', error);
        displayError(`Failed to fetch console logs: ${error.message}`);
        if (lastLogIndex === 0) {
            showLoading(false); // Ensure spinner is removed even on error
        }
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
    const consoleOutput = document.getElementById('consoleOutput');
    const toggleButton = document.getElementById('toggleButton');

    if (consoleOutput) {
        if (toggleButton) {
            toggleButton.addEventListener('click', toggleAutoScroll);
        }
        fetchConsoleLogs(); // Initial fetch
        setInterval(fetchConsoleLogs, 5000); // Fetch every 5 seconds
    }
});
