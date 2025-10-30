/**
 * AI Sentiment Analysis Integration pour le chat en temps réel
 * Analyse automatiquement le sentiment des messages
 */

class ChatAISentiment {
    constructor(roomSlug) {
        this.roomSlug = roomSlug;
        this.enabled = true;
        this.autoAnalyze = true; // Analyser automatiquement les nouveaux messages
        this.cache = new Map(); // Cache des analyses
    }

    /**
     * Analyser le sentiment d'un message
     */
    async analyzeMessage(messageId, text) {
        try {
            const response = await fetch('/chat/api/ai/analyze-sentiment/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({
                    message_id: messageId,
                    text: text
                })
            });

            const data = await response.json();

            if (data.success) {
                // Mettre en cache
                this.cache.set(messageId, data.analysis);
                return data.analysis;
            } else {
                console.error('Error analyzing sentiment:', data.error);
                return null;
            }
        } catch (error) {
            console.error('Error analyzing sentiment:', error);
            return null;
        }
    }

    /**
     * Afficher le sentiment sur un message dans l'UI
     */
    displaySentiment(messageElement, analysis) {
        if (!analysis) return;

        // Créer l'élément de sentiment
        const sentimentBadge = document.createElement('span');
        sentimentBadge.className = `sentiment-badge sentiment-${analysis.sentiment.toLowerCase()}`;
        sentimentBadge.innerHTML = `
            ${analysis.emoji}
            <span class="sentiment-label">${analysis.sentiment}</span>
            <span class="sentiment-score">${(analysis.score * 100).toFixed(0)}%</span>
        `;
        sentimentBadge.title = `Sentiment: ${analysis.sentiment} (${(analysis.score * 100).toFixed(1)}%)`;

        // Ajouter au message
        const messageContent = messageElement.querySelector('.message-content');
        if (messageContent && !messageContent.querySelector('.sentiment-badge')) {
            messageContent.appendChild(sentimentBadge);
        }
    }

    /**
     * Obtenir les statistiques de sentiment du salon
     */
    async getRoomStats() {
        try {
            const response = await fetch(`/chat/api/ai/room/${this.roomSlug}/sentiment-stats/`);
            const data = await response.json();

            if (data.success) {
                return data.sentiment_stats;
            }
            return null;
        } catch (error) {
            console.error('Error getting room stats:', error);
            return null;
        }
    }

    /**
     * Afficher les statistiques du salon
     */
    async displayRoomStats(container) {
        const stats = await this.getRoomStats();

        if (!stats || stats.total === 0) {
            container.innerHTML = '<p class="text-muted">Aucune analyse disponible</p>';
            return;
        }

        container.innerHTML = `
            <div class="sentiment-stats">
                <h5>📊 Ambiance de la conversation</h5>
                <div class="stats-grid">
                    <div class="stat-item positive">
                        <span class="stat-emoji">😊</span>
                        <div class="stat-info">
                            <div class="stat-label">Positif</div>
                            <div class="stat-value">${stats.positive_percentage}%</div>
                            <div class="stat-count">${stats.positive} messages</div>
                        </div>
                    </div>
                    <div class="stat-item neutral">
                        <span class="stat-emoji">😐</span>
                        <div class="stat-info">
                            <div class="stat-label">Neutre</div>
                            <div class="stat-value">${stats.neutral_percentage}%</div>
                            <div class="stat-count">${stats.neutral} messages</div>
                        </div>
                    </div>
                    <div class="stat-item negative">
                        <span class="stat-emoji">😞</span>
                        <div class="stat-info">
                            <div class="stat-label">Négatif</div>
                            <div class="stat-value">${stats.negative_percentage}%</div>
                            <div class="stat-count">${stats.negative} messages</div>
                        </div>
                    </div>
                </div>
                <div class="stats-total">
                    Total: ${stats.total} messages analysés
                </div>
            </div>
        `;
    }

    /**
     * Analyser toute la conversation
     */
    async analyzeConversation() {
        try {
            console.log('🔍 Analyzing conversation for room:', this.roomSlug);
            const response = await fetch(`/chat/api/ai/room/${this.roomSlug}/analyze/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            console.log('📡 Response status:', response.status);
            const data = await response.json();
            console.log('📦 Response data:', data);

            if (data.success && data.insights) {
                console.log('✅ Analysis successful');
                return data.insights;
            }
            
            console.warn('⚠️ No insights in response:', data);
            return null;
        } catch (error) {
            console.error('❌ Error analyzing conversation:', error);
            return null;
        }
    }

    /**
     * Afficher les insights de la conversation
     */
    async displayInsights(container) {
        container.innerHTML = '<div class="text-center"><div class="spinner-border text-primary"></div><p>Analyse en cours...</p></div>';

        const insights = await this.analyzeConversation();

        if (!insights) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    <strong>Erreur lors de l'analyse</strong>
                    <p class="mb-0">Consultez la console du navigateur (F12) pour plus de détails.</p>
                </div>
            `;
            return;
        }

        const moodEmoji = {
            'POSITIVE': '😊',
            'NEGATIVE': '😞',
            'NEUTRAL': '😐'
        }[insights.overall_mood] || '😐';

        let recommendationsHTML = '';
        if (insights.recommendations && insights.recommendations.length > 0) {
            recommendationsHTML = `
                <div class="recommendations">
                    <h6>💡 Recommandations</h6>
                    ${insights.recommendations.map(rec => `
                        <div class="alert alert-${rec.type === 'warning' ? 'warning' : rec.type === 'alert' ? 'danger' : rec.type === 'success' ? 'success' : 'info'} alert-sm">
                            ${rec.message}
                        </div>
                    `).join('')}
                </div>
            `;
        }

        container.innerHTML = `
            <div class="conversation-insights">
                <h5>🤖 Analyse AI de la conversation</h5>
                
                <div class="insight-card">
                    <div class="insight-mood">
                        <span class="mood-emoji">${moodEmoji}</span>
                        <div>
                            <div class="mood-label">Ambiance générale</div>
                            <div class="mood-value">${insights.overall_mood}</div>
                        </div>
                    </div>
                </div>

                <div class="insight-card">
                    <h6>Distribution des sentiments</h6>
                    <div class="sentiment-bars">
                        <div class="sentiment-bar">
                            <span class="bar-label">😊 Positif</span>
                            <div class="bar">
                                <div class="bar-fill positive" style="width: ${insights.sentiment_distribution.positive}%"></div>
                            </div>
                            <span class="bar-value">${insights.sentiment_distribution.positive}%</span>
                        </div>
                        <div class="sentiment-bar">
                            <span class="bar-label">😐 Neutre</span>
                            <div class="bar">
                                <div class="bar-fill neutral" style="width: ${insights.sentiment_distribution.neutral}%"></div>
                            </div>
                            <span class="bar-value">${insights.sentiment_distribution.neutral}%</span>
                        </div>
                        <div class="sentiment-bar">
                            <span class="bar-label">😞 Négatif</span>
                            <div class="bar">
                                <div class="bar-fill negative" style="width: ${insights.sentiment_distribution.negative}%"></div>
                            </div>
                            <span class="bar-value">${insights.sentiment_distribution.negative}%</span>
                        </div>
                    </div>
                </div>

                ${recommendationsHTML}

                <div class="text-muted text-sm">
                    ${insights.total_messages_analyzed} messages analysés
                </div>
            </div>
        `;
    }

    /**
     * Analyser automatiquement un nouveau message
     */
    async onNewMessage(messageElement, messageData) {
        if (!this.autoAnalyze || !this.enabled) return;

        const analysis = await this.analyzeMessage(messageData.id, messageData.content);
        
        if (analysis) {
            this.displaySentiment(messageElement, analysis);
        }
    }

    /**
     * Toggle l'analyse automatique
     */
    toggleAutoAnalyze() {
        this.autoAnalyze = !this.autoAnalyze;
        return this.autoAnalyze;
    }

    /**
     * Activer/désactiver l'AI
     */
    toggle() {
        this.enabled = !this.enabled;
        return this.enabled;
    }

    /**
     * Helper pour obtenir le cookie CSRF
     */
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Export pour utilisation globale
window.ChatAISentiment = ChatAISentiment;
