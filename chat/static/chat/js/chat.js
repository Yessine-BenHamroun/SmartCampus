// WebSocket Chat Logic pour SmartCampus
console.log('🚀 Initialisation du chat en temps réel...');

// Déterminer le protocole WebSocket (ws:// ou wss://)
const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const wsUrl = wsProtocol + window.location.host + '/ws/chat/' + roomSlug + '/';

console.log('📡 Connexion WebSocket à:', wsUrl);

// Créer la connexion WebSocket
const chatSocket = new WebSocket(wsUrl);

// Éléments DOM
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('chat-message-input');
const chatForm = document.getElementById('chat-form');
const typingIndicator = document.getElementById('typing-indicator');
const typingUsername = document.getElementById('typing-username');

let typingTimer;
const typingDelay = 1000; // 1 seconde

// ==============================================================================
// ÉVÉNEMENTS WEBSOCKET
// ==============================================================================

// Connexion établie
chatSocket.onopen = function(e) {
    console.log('✅ WebSocket connecté avec succès');
};

// Réception de messages
chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log('📨 Message reçu:', data);
    
    if (data.type === 'message') {
        addMessage(data);
    } else if (data.type === 'user_status') {
        updateUserStatus(data.user_id, data.username, data.status);
    } else if (data.type === 'typing') {
        showTypingIndicator(data.username, data.is_typing);
    } else if (data.type === 'message_deleted') {
        handleMessageDeleted(data.message_id, data.deleted_text);
    } else if (data.type === 'message_edited') {
        handleMessageEdited(data.message_id, data.content);
    }
};

// Erreur WebSocket
chatSocket.onerror = function(e) {
    console.error('❌ Erreur WebSocket:', e);
    showNotification('Erreur de connexion au chat', 'danger');
};

// Déconnexion
chatSocket.onclose = function(e) {
    console.log('⚠️ WebSocket déconnecté');
    if (e.code !== 1000) {
        showNotification('Connexion au chat perdue. Rechargement...', 'warning');
        setTimeout(() => location.reload(), 3000);
    }
};

// ==============================================================================
// ENVOI DE MESSAGE
// ==============================================================================

chatForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    if (message === '') return;
    
    console.log('📤 Envoi du message:', message);
    
    chatSocket.send(JSON.stringify({
        'type': 'message',
        'message': message
    }));
    
    messageInput.value = '';
    stopTyping();
});

// ==============================================================================
// INDICATEUR "EN TRAIN D'ÉCRIRE..."
// ==============================================================================

messageInput.addEventListener('input', function() {
    clearTimeout(typingTimer);
    
    if (messageInput.value.trim() !== '') {
        chatSocket.send(JSON.stringify({
            'type': 'typing',
            'is_typing': true
        }));
        
        typingTimer = setTimeout(stopTyping, typingDelay);
    } else {
        stopTyping();
    }
});

function stopTyping() {
    chatSocket.send(JSON.stringify({
        'type': 'typing',
        'is_typing': false
    }));
}

// ==============================================================================
// FONCTIONS D'AFFICHAGE
// ==============================================================================

function addMessage(data) {
    // Créer un conteneur wrapper avec flexbox
    const messageWrapper = document.createElement('div');
    
    const isOwnMessage = data.user_id === currentUserId;
    
    // Utiliser les classes CSS pour l'alignement
    messageWrapper.className = isOwnMessage ? 'message-wrapper-own' : 'message-wrapper-other';
    
    const messageDiv = document.createElement('div');
    messageDiv.className = isOwnMessage ? 'message message-own' : 'message message-other';
    messageDiv.dataset.messageId = data.message_id;
    messageDiv.dataset.senderId = data.user_id;
    
    const timestamp = new Date(data.timestamp).toLocaleTimeString('fr-FR', {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    // Utiliser display_name si disponible, sinon username
    const displayName = data.display_name || data.username;
    
    // Construire le HTML du message
    let messageHTML = `
        <div class="message-header">
            <strong>${escapeHtml(displayName)}</strong>
        </div>
        <div class="message-content" id="content-${data.message_id}">${escapeHtml(data.message)}</div>
        <div class="message-footer">
            <div class="message-time">${timestamp}</div>
    `;
    
    // Ajouter le menu à 3 points si c'est notre propre message
    if (isOwnMessage) {
        messageHTML += `
            <div class="message-actions">
                <div class="message-menu">
                    <button class="message-menu-btn" onclick="toggleMenu(${data.message_id}, event)" title="Options">
                        <i class="bi bi-three-dots-vertical"></i>
                    </button>
                    <div class="message-dropdown" id="menu-${data.message_id}">
                        <button class="dropdown-item edit-item" onclick="editMessage(${data.message_id}, event)">
                            <i class="bi bi-pencil"></i> Modifier
                        </button>
                        <button class="dropdown-item delete-item" onclick="deleteMessage(${data.message_id}, event)">
                            <i class="bi bi-trash"></i> Supprimer
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    messageHTML += `
        </div>
    `;
    
    messageDiv.innerHTML = messageHTML;
    messageWrapper.appendChild(messageDiv);
    chatMessages.appendChild(messageWrapper);
    scrollToBottom();
}

function updateUserStatus(userId, username, status) {
    console.log(`👤 ${username} est maintenant ${status}`);
    
    const participantItem = document.querySelector(`.participant-item[data-user-id="${userId}"]`);
    
    if (status === 'online') {
        // Ajouter le participant s'il n'existe pas
        if (!participantItem) {
            const participantsList = document.getElementById('participants-list');
            const newParticipant = document.createElement('div');
            newParticipant.className = 'participant-item';
            newParticipant.dataset.userId = userId;
            newParticipant.innerHTML = `
                <span class="status-indicator status-online"></span>
                <span class="username">${escapeHtml(username)}</span>
            `;
            participantsList.appendChild(newParticipant);
        } else {
            // Mettre à jour le statut
            const indicator = participantItem.querySelector('.status-indicator');
            indicator.className = 'status-indicator status-online';
        }
    } else if (status === 'offline') {
        if (participantItem) {
            const indicator = participantItem.querySelector('.status-indicator');
            indicator.className = 'status-indicator status-offline';
        }
    }
}

function showTypingIndicator(username, isTyping) {
    if (username === currentUser) return;
    
    if (isTyping) {
        typingUsername.textContent = username;
        typingIndicator.style.display = 'block';
    } else {
        typingIndicator.style.display = 'none';
    }
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'info') {
    // Créer une notification Bootstrap
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    // Auto-dismiss après 5 secondes
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// ==============================================================================
// INITIALISATION
// ==============================================================================

// Scroll automatique vers le bas au chargement
window.addEventListener('DOMContentLoaded', function() {
    scrollToBottom();
    console.log('✅ Chat initialisé avec succès');
});

// ==============================================================================
// SUPPRESSION DE MESSAGE
// ==============================================================================

function deleteMessage(messageId, event) {
    if (event) event.preventDefault();
    
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce message ?')) {
        return;
    }
    
    console.log('🗑️ Suppression du message:', messageId);
    
    // Envoyer via WebSocket pour mise à jour en temps réel
    chatSocket.send(JSON.stringify({
        'type': 'delete_message',
        'message_id': messageId
    }));
}

function editMessage(messageId, event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    // Fermer le menu déroulant
    const menu = document.getElementById(`menu-${messageId}`);
    if (menu) {
        menu.classList.remove('show');
    }
    
    const messageDiv = document.querySelector(`.message[data-message-id="${messageId}"]`);
    if (!messageDiv) return;
    
    const contentDiv = messageDiv.querySelector('.message-content');
    if (!contentDiv) return;
    
    const originalContent = contentDiv.textContent;
    
    // Ajouter classe d'édition au message
    messageDiv.classList.add('edit-mode');
    
    // Cacher temporairement les boutons d'actions
    const actionsMenu = messageDiv.querySelector('.message-actions');
    if (actionsMenu) {
        actionsMenu.style.display = 'none';
    }
    
    // Rendre le contenu éditable
    contentDiv.contentEditable = true;
    contentDiv.style.cursor = 'text';
    
    // Focus et sélection du texte avec un délai pour éviter le bug du curseur
    setTimeout(() => {
        contentDiv.focus();
        
        // Sélectionner tout le texte
        const range = document.createRange();
        range.selectNodeContents(contentDiv);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
    }, 10);
    
    // Créer les boutons de validation/annulation
    const footer = messageDiv.querySelector('.message-footer');
    if (!footer) return;
    
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'edit-actions';
    actionsDiv.id = `edit-actions-${messageId}`;
    actionsDiv.innerHTML = `
        <button class="btn btn-sm btn-primary" onclick="saveEdit(${messageId})">
            <i class="bi bi-check-lg"></i> Enregistrer
        </button>
        <button class="btn btn-sm btn-secondary" onclick="cancelEdit(${messageId}, '${escapeHtml(originalContent)}')">
            <i class="bi bi-x-lg"></i> Annuler
        </button>
    `;
    
    footer.appendChild(actionsDiv);
    
    // Empêcher la perte du focus
    contentDiv.addEventListener('blur', function(e) {
        // Ne pas perdre le focus si on clique sur les boutons
        if (e.relatedTarget && e.relatedTarget.closest(`#edit-actions-${messageId}`)) {
            e.preventDefault();
            setTimeout(() => contentDiv.focus(), 0);
        }
    }, { once: true });
}

function saveEdit(messageId) {
    const messageDiv = document.querySelector(`.message[data-message-id="${messageId}"]`);
    if (!messageDiv) return;
    
    const contentDiv = messageDiv.querySelector('.message-content');
    if (!contentDiv) return;
    
    const newContent = contentDiv.textContent.trim();
    
    if (!newContent) {
        alert('Le message ne peut pas être vide');
        contentDiv.focus();
        return;
    }
    
    console.log('✏️ Modification du message:', messageId);
    
    // Envoyer via WebSocket
    chatSocket.send(JSON.stringify({
        'type': 'edit_message',
        'message_id': messageId,
        'content': newContent
    }));
    
    // Nettoyer l'interface
    contentDiv.contentEditable = false;
    contentDiv.style.cursor = '';
    messageDiv.classList.remove('edit-mode');
    
    const actionsDiv = document.getElementById(`edit-actions-${messageId}`);
    if (actionsDiv) actionsDiv.remove();
    
    // Réafficher le menu d'actions
    const messageActions = messageDiv.querySelector('.message-actions');
    if (messageActions) messageActions.style.display = '';
}

function cancelEdit(messageId, originalContent) {
    const messageDiv = document.querySelector(`.message[data-message-id="${messageId}"]`);
    if (!messageDiv) return;
    
    const contentDiv = messageDiv.querySelector('.message-content');
    if (!contentDiv) return;
    
    // Restaurer le contenu original
    contentDiv.textContent = originalContent;
    contentDiv.contentEditable = false;
    contentDiv.style.cursor = '';
    messageDiv.classList.remove('edit-mode');
    
    // Supprimer les boutons d'édition
    const actionsDiv = document.getElementById(`edit-actions-${messageId}`);
    if (actionsDiv) actionsDiv.remove();
    
    // Réafficher le menu d'actions
    const messageActions = messageDiv.querySelector('.message-actions');
    if (messageActions) messageActions.style.display = '';
}

function handleMessageDeleted(messageId, deletedText) {
    console.log('🗑️ Message supprimé:', messageId);
    
    const messageDiv = document.querySelector(`.message[data-message-id="${messageId}"]`);
    if (messageDiv) {
        // Ajouter la classe de message supprimé
        messageDiv.classList.add('message-deleted');
        
        // Remplacer le contenu
        messageDiv.innerHTML = `
            <div class="message-content deleted-content">
                <i class="bi bi-trash"></i>
                ${escapeHtml(deletedText)}
            </div>
            <div class="message-time">${messageDiv.querySelector('.message-time')?.textContent || ''}</div>
        `;
    }
}

function handleMessageEdited(messageId, newContent) {
    console.log('✏️ Message modifié:', messageId);
    
    const messageDiv = document.querySelector(`.message[data-message-id="${messageId}"]`);
    if (messageDiv) {
        const contentDiv = messageDiv.querySelector('.message-content');
        const timeDiv = messageDiv.querySelector('.message-time');
        
        if (contentDiv) {
            contentDiv.textContent = newContent;
            contentDiv.contentEditable = false;
        }
        
        // Ajouter le label "(modifié)" s'il n'existe pas déjà
        if (timeDiv && !timeDiv.querySelector('.edited-label')) {
            const editedLabel = document.createElement('span');
            editedLabel.className = 'edited-label';
            editedLabel.textContent = '(modifié)';
            timeDiv.appendChild(editedLabel);
        }
        
        // Supprimer les boutons d'édition si présents
        const actionsDiv = messageDiv.querySelector('.edit-actions');
        if (actionsDiv) actionsDiv.remove();
        
        // Réafficher les boutons d'action
        const messageActions = messageDiv.querySelector('.message-actions');
        if (messageActions) messageActions.style.display = '';
    }
}

// Garder le focus sur l'input
messageInput.addEventListener('blur', function() {
    setTimeout(() => messageInput.focus(), 100);
});

// Raccourcis clavier
document.addEventListener('keydown', function(e) {
    // Echap pour effacer le message
    if (e.key === 'Escape') {
        messageInput.value = '';
        stopTyping();
    }
});

console.log('✅ Script chat chargé avec succès');
