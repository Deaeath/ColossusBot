// File: dashboard/static/js/script.js

/**
 * State for managing auto-scroll functionality in the console log viewer.
 */
let autoScroll = true;

/**
 * Toggles the auto-scroll feature on or off and updates the button label.
 */
function toggleAutoScroll() {
    autoScroll = !autoScroll;
    const button = document.getElementById('toggleButton');
    button.textContent = autoScroll ? 'Disable Autoscroll' : 'Enable Autoscroll';
}

/**
 * Fetches the latest console logs from the server and updates the console log viewer.
 */
function fetchConsoleLogs() {
    fetch('/api/console')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => updateConsoleLogs(data.logs))
        .catch(error => console.error('Error fetching console logs:', error));
}

/**
 * Updates the console log viewer with new log data.
 * @param {string[]} logs - Array of log strings to display.
 */
function updateConsoleLogs(logs) {
    const consoleOutput = document.getElementById('consoleOutput');
    consoleOutput.innerHTML = logs.join('<br>');
    if (autoScroll) {
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }
}

// Periodically fetch console logs from the server every 2 seconds.
setInterval(fetchConsoleLogs, 2000);
