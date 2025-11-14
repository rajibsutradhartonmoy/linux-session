// Tauri API
const { invoke } = window.__TAURI__.tauri;

// State
let currentApps = [];
let sessions = {};
let selectedForDeletion = new Map(); // sessionName -> Set of indices

// Toast notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '✓',
        error: '✗',
        info: 'ℹ'
    };

    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(400px)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Tab switching
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;

            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Update active content
            tabContents.forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${targetTab}-tab`).classList.add('active');

            // Load data when switching tabs
            if (targetTab === 'sessions') {
                loadSessions();
            }
        });
    });
}

// Scan current apps
async function scanApps() {
    const scanBtn = document.getElementById('scan-apps');
    const originalText = scanBtn.innerHTML;
    scanBtn.innerHTML = '<span class="spinner"></span> Scanning...';
    scanBtn.disabled = true;

    try {
        currentApps = await invoke('get_running_apps');
        renderCurrentApps();
        showToast(`Found ${currentApps.length} running application(s)`, 'success');
    } catch (error) {
        showToast(`Error scanning apps: ${error}`, 'error');
        console.error('Error:', error);
    } finally {
        scanBtn.innerHTML = originalText;
        scanBtn.disabled = false;
    }
}

// Render current apps
function renderCurrentApps() {
    const container = document.getElementById('current-apps-list');
    const emptyState = document.getElementById('empty-apps');
    const saveContainer = document.getElementById('save-session-container');

    if (currentApps.length === 0) {
        container.innerHTML = '';
        emptyState.classList.add('active');
        saveContainer.style.display = 'none';
        return;
    }

    emptyState.classList.remove('active');
    saveContainer.style.display = 'block';

    container.innerHTML = currentApps.map((app, index) => `
        <div class="app-item">
            <span class="app-name">${escapeHtml(app.name)}</span>
            <span class="app-command">${escapeHtml(app.command)}</span>
        </div>
    `).join('');
}

// Load sessions
async function loadSessions() {
    try {
        sessions = await invoke('get_sessions');
        renderSessions();
    } catch (error) {
        showToast(`Error loading sessions: ${error}`, 'error');
        console.error('Error:', error);
    }
}

// Render sessions
function renderSessions() {
    const container = document.getElementById('sessions-list');
    const emptyState = document.getElementById('empty-sessions');

    const sessionNames = Object.keys(sessions);

    if (sessionNames.length === 0) {
        container.innerHTML = '';
        emptyState.classList.add('active');
        return;
    }

    emptyState.classList.remove('active');

    container.innerHTML = sessionNames.map(name => {
        const session = sessions[name];
        const date = new Date(session.created);
        const dateStr = date.toLocaleDateString();
        const timeStr = date.toLocaleTimeString();

        const isEditing = selectedForDeletion.has(name);
        const selectedIndices = selectedForDeletion.get(name) || new Set();

        return `
            <div class="session-card" data-session="${escapeHtml(name)}">
                <div class="session-header">
                    <div class="session-info">
                        <h3>${escapeHtml(name)}</h3>
                        <div class="session-meta">
                            <span>📅 ${dateStr} ${timeStr}</span>
                            <span>📦 ${session.apps.length} app(s)</span>
                        </div>
                    </div>
                    <div class="session-actions">
                        ${isEditing ? `
                            <button class="btn btn-danger btn-small" onclick="updateSession('${escapeHtml(name)}')">
                                Remove Selected
                            </button>
                            <button class="btn btn-secondary btn-small" onclick="cancelEdit('${escapeHtml(name)}')">
                                Cancel
                            </button>
                        ` : `
                            <button class="btn btn-success btn-small" onclick="loadSession('${escapeHtml(name)}')">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                                </svg>
                                Load
                            </button>
                            <button class="btn btn-secondary btn-small" onclick="editSession('${escapeHtml(name)}')">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                                </svg>
                                Edit
                            </button>
                            <button class="btn btn-danger btn-small" onclick="deleteSession('${escapeHtml(name)}')">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="3 6 5 6 21 6"></polyline>
                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                </svg>
                                Delete
                            </button>
                        `}
                    </div>
                </div>
                <div class="session-apps">
                    <h4>Applications:</h4>
                    <div class="app-list">
                        ${session.apps.map((app, index) => `
                            <div class="app-item ${isEditing ? 'selectable' : ''} ${selectedIndices.has(index) ? 'selected' : ''}"
                                 ${isEditing ? `onclick="toggleAppSelection('${escapeHtml(name)}', ${index})"` : ''}>
                                ${isEditing ? `
                                    <input type="checkbox"
                                           class="app-checkbox"
                                           ${selectedIndices.has(index) ? 'checked' : ''}
                                           onclick="event.stopPropagation(); toggleAppSelection('${escapeHtml(name)}', ${index})">
                                ` : ''}
                                <span class="app-name">${escapeHtml(app.name)}</span>
                                <span class="app-command">${escapeHtml(app.command)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Toggle app selection for deletion
function toggleAppSelection(sessionName, index) {
    if (!selectedForDeletion.has(sessionName)) {
        selectedForDeletion.set(sessionName, new Set());
    }

    const selected = selectedForDeletion.get(sessionName);
    if (selected.has(index)) {
        selected.delete(index);
    } else {
        selected.add(index);
    }

    renderSessions();
}

// Enter edit mode
function editSession(name) {
    selectedForDeletion.set(name, new Set());
    renderSessions();
}

// Cancel edit mode
function cancelEdit(name) {
    selectedForDeletion.delete(name);
    renderSessions();
}

// Update session (remove selected apps)
async function updateSession(name) {
    const selected = selectedForDeletion.get(name);
    if (!selected || selected.size === 0) {
        showToast('No apps selected to remove', 'error');
        return;
    }

    const indices = Array.from(selected);

    try {
        const result = await invoke('update_session', { name, indices });
        showToast(result, 'success');
        selectedForDeletion.delete(name);
        await loadSessions();
    } catch (error) {
        showToast(`Error updating session: ${error}`, 'error');
        console.error('Error:', error);
    }
}

// Save session
async function saveSession() {
    const nameInput = document.getElementById('session-name');
    const name = nameInput.value.trim();

    if (!name) {
        showToast('Please enter a session name', 'error');
        return;
    }

    if (currentApps.length === 0) {
        showToast('No apps to save', 'error');
        return;
    }

    const saveBtn = document.getElementById('save-session-btn');
    const originalText = saveBtn.innerHTML;
    saveBtn.innerHTML = '<span class="spinner"></span> Saving...';
    saveBtn.disabled = true;

    try {
        const result = await invoke('save_session', { name, apps: currentApps });
        showToast(result, 'success');
        nameInput.value = '';

        // Switch to sessions tab
        document.querySelector('.tab[data-tab="sessions"]').click();
        await loadSessions();
    } catch (error) {
        showToast(`Error saving session: ${error}`, 'error');
        console.error('Error:', error);
    } finally {
        saveBtn.innerHTML = originalText;
        saveBtn.disabled = false;
    }
}

// Load session
async function loadSession(name) {
    try {
        const result = await invoke('load_session', { name });
        showToast(result, 'success');
    } catch (error) {
        showToast(`Error loading session: ${error}`, 'error');
        console.error('Error:', error);
    }
}

// Delete session
async function deleteSession(name) {
    if (!confirm(`Are you sure you want to delete the session "${name}"?`)) {
        return;
    }

    try {
        const result = await invoke('delete_session', { name });
        showToast(result, 'success');
        await loadSessions();
    } catch (error) {
        showToast(`Error deleting session: ${error}`, 'error');
        console.error('Error:', error);
    }
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    loadSessions();

    document.getElementById('scan-apps').addEventListener('click', scanApps);
    document.getElementById('save-session-btn').addEventListener('click', saveSession);
    document.getElementById('refresh-sessions').addEventListener('click', loadSessions);

    // Allow Enter key to save session
    document.getElementById('session-name').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            saveSession();
        }
    });
});
