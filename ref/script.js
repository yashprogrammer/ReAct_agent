const API_URL = 'http://localhost:8000';

// DOM Elements
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatMessages = document.getElementById('chat-messages');
const calendarDate = document.getElementById('calendar-date');
const calendarEvents = document.getElementById('calendar-events');
const notesList = document.getElementById('notes-list');

// State
let chatHistory = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Set today's date
    const today = new Date().toISOString().split('T')[0];
    calendarDate.value = today;
    
    // Initial fetches
    fetchCalendar(today);
    fetchNotes();
});

// Event Listeners
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    // Add user message
    addMessage(message, 'user');
    userInput.value = '';

    // Send to API
    try {
        setLoading(true);
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                history: chatHistory
            })
        });

        if (!response.ok) throw new Error('API Error');

        const data = await response.json();
        
        // Add AI response
        addMessage(data.response, 'ai');
        
        // Update history
        chatHistory.push({ role: 'user', content: message });
        chatHistory.push({ role: 'assistant', content: data.response });

        // Refresh sidebar data as it might have changed
        fetchNotes();
        fetchCalendar(calendarDate.value);

    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, something went wrong. Please try again.', 'ai');
    } finally {
        setLoading(false);
    }
});

calendarDate.addEventListener('change', (e) => {
    fetchCalendar(e.target.value);
});

// Functions
function addMessage(content, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const avatar = type === 'ai' ? '🤖' : '👤';
    
    messageDiv.innerHTML = `
        <div class="avatar">${avatar}</div>
        <div class="content">
            <p>${formatMessage(content)}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatMessage(text) {
    // Simple markdown-like formatting
    return text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

function setLoading(isLoading) {
    const button = chatForm.querySelector('button');
    if (isLoading) {
        button.disabled = true;
        button.innerHTML = '<div class="loading-spinner" style="width: 16px; height: 16px;"></div>';
    } else {
        button.disabled = false;
        button.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 2L11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
    }
}

async function fetchCalendar(date) {
    calendarEvents.innerHTML = '<div class="loading-spinner"></div>';
    
    try {
        const response = await fetch(`${API_URL}/calendar?date=${date}`);
        const data = await response.json();
        
        calendarEvents.innerHTML = '';
        
        if (data.events && data.events.length > 0) {
            data.events.forEach(event => {
                const eventEl = document.createElement('div');
                eventEl.className = 'event-item';
                eventEl.innerHTML = `
                    <span class="event-time">${event.time}</span>
                    <span class="event-title">${event.event}</span>
                `;
                calendarEvents.appendChild(eventEl);
            });
        } else {
            calendarEvents.innerHTML = '<div class="empty-state">No events found for this date.</div>';
        }
    } catch (error) {
        console.error('Error fetching calendar:', error);
        calendarEvents.innerHTML = '<div class="empty-state">Error loading events.</div>';
    }
}

async function fetchNotes() {
    notesList.innerHTML = '<div class="loading-spinner"></div>';
    
    try {
        const response = await fetch(`${API_URL}/notes`);
        const data = await response.json();
        
        notesList.innerHTML = '';
        
        if (data.notes && data.notes.length > 0) {
            data.notes.forEach(note => {
                const noteEl = document.createElement('div');
                noteEl.className = 'note-item';
                noteEl.textContent = note;
                notesList.appendChild(noteEl);
            });
        } else {
            notesList.innerHTML = '<div class="empty-state">No pending notes.</div>';
        }
    } catch (error) {
        console.error('Error fetching notes:', error);
        notesList.innerHTML = '<div class="empty-state">Error loading notes.</div>';
    }
}
