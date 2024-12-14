// File: dashboard/static/js/scripts.js

/**
 * State for managing auto-scroll functionality in the console log viewer.
 */
let autoScroll = true;
let isFetching = false;
let lastLogIndex = 2; // To keep track of the last fetched log

/**
 * Toggles the auto-scroll feature on or off and updates the button label.
 */
export function toggleAutoScroll() {
    autoScroll = !autoScroll;
    const button = document.getElementById('toggleButton');
    if (button) {
        button.textContent = autoScroll ? 'Disable Autoscroll' : 'Enable Autoscroll';
        button.setAttribute('aria-pressed', autoScroll);
        console.log(`Auto-scroll toggled. Now: ${autoScroll ? 'Enabled' : 'Disabled'}`);
    }
}

/**
 * Sanitizes a log entry by removing ANSI escape codes, control characters,
 * and all other non-printable characters.
 * @param {string} log - The raw log string to sanitize.
 * @returns {string} - The sanitized log string.
 */
function sanitizeLog(log) {
    // Remove ANSI escape codes
    let sanitized = log.replace(/\u001b\[[0-9;]*m/g, '');

    // Remove all control characters (Unicode category Cc)
    // This includes characters like \n, \r, \t, etc.
    sanitized = sanitized.replace(/[\u0000-\u001F\u007F]/g, '');

    // Remove Zero Width and other invisible characters (Unicode category Cf)
    sanitized = sanitized.replace(/[\u200B-\u200D\uFEFF]/g, '');

    // Trim any remaining whitespace from both ends
    sanitized = sanitized.trim();

    return sanitized;
}

/**
 * Displays an error message in the console output area.
 * @param {string} message - The error message to display.
 */
function displayError(message) {
    const logsContainer = document.getElementById('logsContainer');
    if (!logsContainer) {
        console.error('logsContainer element not found.');
        return;
    }

    // Clear existing logs and display the error
    logsContainer.innerHTML = `<div class="text-danger">${message}</div>`;
    console.log(`Error displayed: ${message}`);
}

/**
 * Appends new log entries to the console output, ignoring blank or whitespace-only entries.
 * @param {string[]} newLogs - Array of new log strings to append.
 */
function appendConsoleLogs(newLogs) {
    const logsContainer = document.getElementById('logsContainer');
    if (!logsContainer) {
        console.error('logsContainer element not found.');
        return;
    }

    // Filter out blank or whitespace-only log entries after sanitization
    const filteredLogs = newLogs.filter(log => {
        const cleanLog = sanitizeLog(log);
        return cleanLog !== "";
    });

    filteredLogs.forEach(log => {
        const logEntry = document.createElement('div');
        logEntry.textContent = log;
        logsContainer.appendChild(logEntry);
    });

    // Handle autoscroll
    if (autoScroll) {
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }
    console.log(`Appended ${filteredLogs.length} new log(s).`);
}

/**
 * Fetches the latest console logs from the server and updates the console log viewer.
 */
export async function fetchConsoleLogs() {
    if (isFetching) {
        console.log('Fetch in progress. Skipping this fetch.');
        return; // Prevent overlapping fetches
    }
    isFetching = true;
    console.log('Starting to fetch console logs.');
    try {
        const response = await fetch('/api/console');
        console.log(`Fetched /api/console with status: ${response.status}`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        console.log(`Received data: ${JSON.stringify(data)}`);

        // Check if the logs array is missing or empty
        if (!data.logs || data.logs.length === 0) {
            console.log('No logs found in the response.');
            return;
        }

        // Create a new array with all empty logs removed
        data.logs = data.logs.filter(log => log.trim() !== '');
        console.log(`Total logs received: ${data.logs.length}`);

        // Extract logs starting from the last index
        const newLogs = data.logs.slice(lastLogIndex);
        // Trim any leading/trailing whitespace from each log
        newLogs.forEach((log, index) => {
            newLogs[index] = log.trim();
        });
        // Remove any empty logs
        newLogs.filter(log => log !== '');
        // Log the new logs and last log index
        console.log('New logs:', newLogs);
        console.log(`Last log index: ${lastLogIndex}`);
        console.log(`New logs to append: ${newLogs.length}`);

        if (newLogs.length > 0) {
            appendConsoleLogs(newLogs);
        } else {
            console.log('No new logs to append.');
        }

        // Update lastLogIndex regardless of new logs
        lastLogIndex = data.logs.length;
        console.log(`Updated lastLogIndex to ${lastLogIndex}`);
    } catch (error) {
        console.error('Error fetching console logs:', error);
        displayError(`Failed to fetch console logs: ${error.message}`);
    } finally {
        isFetching = false;
        console.log('Fetch completed.');
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
        console.log('Toggle button event listener added.');
    }
    fetchConsoleLogs(); // Initial fetch
    setInterval(fetchConsoleLogs, 5000); // Fetch every 5 seconds
});
