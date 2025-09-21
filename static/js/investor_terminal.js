/**
 * Investor Terminal JavaScript Module
 * Handles terminal functionality, command processing, and UI interactions
 */

class InvestorTerminal {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.commandHistory = [];
        this.historyIndex = -1;
        this.currentDirectory = '/';
        this.isExecuting = false;
        
        this.initializeTerminal();
        this.bindEvents();
        this.loadInitialData();
    }
    
    initializeTerminal() {
        this.terminalOutput = document.getElementById('terminal-output');
        this.terminalInput = document.getElementById('terminal-input');
        
        // Focus on terminal input
        if (this.terminalInput) {
            this.terminalInput.focus();
        }
        
        // Add welcome message
        this.addSystemMessage('Investor Terminal initialized successfully');
        this.addSystemMessage('Type "help" to see available commands');
    }
    
    bindEvents() {
        if (this.terminalInput) {
            this.terminalInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
            this.terminalInput.addEventListener('keyup', (e) => this.handleKeyUp(e));
        }
        
        // Bind quick command buttons
        document.querySelectorAll('.quick-command').forEach(button => {
            button.addEventListener('click', (e) => {
                const command = e.target.textContent.trim();
                this.insertCommand(command);
            });
        });
        
        // Auto-focus on terminal input when clicking on terminal area
        if (this.terminalOutput) {
            this.terminalOutput.addEventListener('click', () => {
                if (this.terminalInput) {
                    this.terminalInput.focus();
                }
            });
        }
    }
    
    loadInitialData() {
        // Load market overview
        this.updateMarketOverview();
        
        // Load watchlist
        this.updateWatchlist();
        
        // Load portfolio data
        this.updatePortfolio();
        
        // Load alerts
        this.updateAlerts();
        
        // Set up auto-refresh
        setInterval(() => {
            this.updateMarketOverview();
        }, 30000); // Refresh every 30 seconds
    }
    
    handleKeyDown(e) {
        switch (e.key) {
            case 'Enter':
                e.preventDefault();
                this.executeCommand();
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.navigateHistory(-1);
                break;
                
            case 'ArrowDown':
                e.preventDefault();
                this.navigateHistory(1);
                break;
                
            case 'Tab':
                e.preventDefault();
                this.autoComplete();
                break;
                
            case 'Escape':
                this.terminalInput.value = '';
                break;
        }
    }
    
    handleKeyUp(e) {
        // Handle any real-time input processing if needed
    }
    
    async executeCommand() {
        if (this.isExecuting) return;
        
        const command = this.terminalInput.value.trim();
        if (!command) return;
        
        this.isExecuting = true;
        
        // Add command to history
        this.commandHistory.push(command);
        this.historyIndex = this.commandHistory.length;
        
        // Save command history to localStorage
        localStorage.setItem('terminal_command_history', JSON.stringify(this.commandHistory.slice(-50)));
        
        // Display command in terminal
        this.addUserCommand(command);
        
        // Clear input
        this.terminalInput.value = '';
        
        // Show loading indicator
        const loadingElement = this.addLoadingMessage('Executing command...');
        
        try {
            const response = await fetch('/api/investor/terminal/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    command: command,
                    session_id: this.sessionId
                })
            });
            
            const data = await response.json();
            
            // Remove loading indicator
            this.removeElement(loadingElement);
            
            if (response.ok) {
                if (data.clear) {
                    this.clearTerminal();
                } else {
                    this.addCommandOutput(data.output, data.status);
                }
                
                // Update sidebar data if command affects it
                this.updateSidebarIfNeeded(command);
            } else {
                this.addErrorMessage(data.error || 'Command execution failed');
            }
        } catch (error) {
            this.removeElement(loadingElement);
            this.addErrorMessage(`Network error: ${error.message}`);
        }
        
        this.isExecuting = false;
        this.scrollToBottom();
        
        // Refocus on input
        this.terminalInput.focus();
    }
    
    navigateHistory(direction) {
        if (this.commandHistory.length === 0) return;
        
        this.historyIndex += direction;
        
        if (this.historyIndex < 0) {
            this.historyIndex = 0;
        } else if (this.historyIndex >= this.commandHistory.length) {
            this.historyIndex = this.commandHistory.length;
            this.terminalInput.value = '';
            return;
        }
        
        this.terminalInput.value = this.commandHistory[this.historyIndex] || '';
    }
    
    autoComplete() {
        const input = this.terminalInput.value.trim();
        const commands = [
            'help', 'quote', 'watch', 'portfolio', 'alerts', 'analyze', 
            'news', 'history', 'screener', 'clear'
        ];
        
        const matches = commands.filter(cmd => cmd.startsWith(input.toLowerCase()));
        
        if (matches.length === 1) {
            this.terminalInput.value = matches[0] + ' ';
        } else if (matches.length > 1) {
            this.addSystemMessage(`Available completions: ${matches.join(', ')}`);
        }
    }
    
    insertCommand(command) {
        this.terminalInput.value = command;
        this.terminalInput.focus();
    }
    
    addTerminalLine(content, className = '', animate = true) {
        const line = document.createElement('div');
        line.className = `terminal-line ${className}`;
        if (animate) line.classList.add('new');
        
        if (typeof content === 'string') {
            line.textContent = content;
        } else {
            line.appendChild(content);
        }
        
        this.terminalOutput.appendChild(line);
        return line;
    }
    
    addUserCommand(command) {
        const promptSpan = document.createElement('span');
        promptSpan.className = 'terminal-prompt';
        promptSpan.textContent = '$ ';
        
        const commandSpan = document.createElement('span');
        commandSpan.textContent = command;
        
        const container = document.createElement('div');
        container.appendChild(promptSpan);
        container.appendChild(commandSpan);
        
        return this.addTerminalLine(container, 'user');
    }
    
    addCommandOutput(output, status = 'success') {
        const className = status === 'error' ? 'error' : 
                         status === 'warning' ? 'warning' : 
                         status === 'info' ? 'info' : 'output';
        
        return this.addTerminalLine(output, className);
    }
    
    addSystemMessage(message) {
        return this.addTerminalLine(message, 'system');
    }
    
    addErrorMessage(message) {
        return this.addTerminalLine(`Error: ${message}`, 'error');
    }
    
    addLoadingMessage(message) {
        const loadingSpan = document.createElement('span');
        loadingSpan.className = 'terminal-loading';
        loadingSpan.textContent = message;
        
        return this.addTerminalLine(loadingSpan, 'system');
    }
    
    removeElement(element) {
        if (element && element.parentNode) {
            element.parentNode.removeChild(element);
        }
    }
    
    clearTerminal() {
        this.terminalOutput.innerHTML = '';
        this.addSystemMessage('Terminal cleared');
    }
    
    scrollToBottom() {
        this.terminalOutput.scrollTop = this.terminalOutput.scrollHeight;
    }
    
    updateSidebarIfNeeded(command) {
        const lowerCommand = command.toLowerCase();
        
        if (lowerCommand.startsWith('watch ')) {
            setTimeout(() => this.updateWatchlist(), 1000);
        } else if (lowerCommand === 'portfolio') {
            setTimeout(() => this.updatePortfolio(), 1000);
        } else if (lowerCommand === 'alerts') {
            setTimeout(() => this.updateAlerts(), 1000);
        }
    }
    
    async updateMarketOverview() {
        try {
            // For now, use simulated data
            // In production, fetch from real API
            const marketData = this.getSimulatedMarketData();
            this.renderMarketOverview(marketData);
        } catch (error) {
            console.error('Failed to update market overview:', error);
        }
    }
    
    getSimulatedMarketData() {
        // Simulate market data with small random changes
        const baseData = {
            '^GSPC': { name: 'S&P 500', basePrice: 4500, baseName: 'SPX' },
            '^DJI': { name: 'Dow Jones', basePrice: 35000, baseName: 'DJI' },
            '^IXIC': { name: 'NASDAQ', basePrice: 14500, baseName: 'NDX' },
            '^VIX': { name: 'VIX', basePrice: 18, baseName: 'VIX' }
        };
        
        const result = {};
        
        for (const [symbol, data] of Object.entries(baseData)) {
            const changePercent = (Math.random() - 0.5) * 4; // -2% to +2%
            const price = data.basePrice * (1 + changePercent / 100);
            const change = price - data.basePrice;
            
            result[symbol] = {
                name: data.name,
                price: price,
                change: change,
                change_percent: changePercent
            };
        }
        
        return result;
    }
    
    renderMarketOverview(marketData) {
        const container = document.getElementById('market-overview');
        if (!container) return;
        
        let html = '';
        
        for (const [symbol, data] of Object.entries(marketData)) {
            const changeClass = data.change >= 0 ? 'change-positive' : 'change-negative';
            const changeSymbol = data.change >= 0 ? '+' : '';
            
            html += `
                <div class="market-item">
                    <div>
                        <div class="symbol">${data.name}</div>
                        <div class="price">${data.price.toFixed(2)}</div>
                    </div>
                    <div class="${changeClass}">
                        <div>${changeSymbol}${data.change.toFixed(2)}</div>
                        <div>${changeSymbol}${data.change_percent.toFixed(2)}%</div>
                    </div>
                </div>
            `;
        }
        
        container.innerHTML = html;
    }
    
    async updateWatchlist() {
        try {
            const response = await fetch('/api/investor/watchlist');
            const data = await response.json();
            
            if (response.ok) {
                this.renderWatchlist(data.watchlists);
            }
        } catch (error) {
            console.error('Failed to update watchlist:', error);
        }
    }
    
    renderWatchlist(watchlists) {
        const container = document.getElementById('watchlist-content');
        if (!container) return;
        
        if (!watchlists || watchlists.length === 0) {
            container.innerHTML = '<p class="text-muted small">No watchlists found</p>';
            return;
        }
        
        let html = '';
        
        watchlists.forEach(watchlist => {
            html += `
                <div class="watchlist-item">
                    <div class="watchlist-name">${watchlist.name}</div>
                    <div class="watchlist-symbols">
                        ${watchlist.symbols.map(symbol => 
                            `<span class="symbol-badge" onclick="terminal.insertCommand('quote ${symbol}')">${symbol}</span>`
                        ).join('')}
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    async updatePortfolio() {
        try {
            const response = await fetch('/api/investor/portfolio');
            const data = await response.json();
            
            if (response.ok) {
                this.renderPortfolio(data.portfolios);
            }
        } catch (error) {
            console.error('Failed to update portfolio:', error);
        }
    }
    
    renderPortfolio(portfolios) {
        const container = document.getElementById('portfolio-summary');
        if (!container) return;
        
        if (!portfolios || portfolios.length === 0) {
            container.innerHTML = '<p class="text-muted small">No portfolios found</p>';
            return;
        }
        
        let html = '';
        
        portfolios.forEach(portfolio => {
            const changeClass = portfolio.profit_loss >= 0 ? 'positive' : 'negative';
            
            html += `
                <div class="portfolio-item">
                    <div class="portfolio-name">${portfolio.name}</div>
                    <div class="portfolio-stats">
                        <div class="portfolio-value">$${portfolio.total_value.toFixed(2)}</div>
                        <div class="portfolio-change ${changeClass}">
                            ${portfolio.profit_loss >= 0 ? '+' : ''}${portfolio.profit_loss_percentage.toFixed(2)}%
                        </div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    async updateAlerts() {
        try {
            const response = await fetch('/api/investor/alerts');
            const data = await response.json();
            
            if (response.ok) {
                this.renderAlerts(data.alerts);
            }
        } catch (error) {
            console.error('Failed to update alerts:', error);
        }
    }
    
    renderAlerts(alerts) {
        const container = document.getElementById('alerts-content');
        if (!container) return;
        
        if (!alerts || alerts.length === 0) {
            container.innerHTML = '<p class="text-muted small">No alerts set</p>';
            return;
        }
        
        let html = '';
        
        alerts.forEach(alert => {
            const statusClass = alert.is_triggered ? 'triggered' : 'active';
            const alertClass = alert.is_triggered ? 'alert-triggered' : '';
            
            html += `
                <div class="alert-item ${alertClass}">
                    <div class="alert-symbol">${alert.symbol}</div>
                    <div class="alert-condition">
                        ${alert.alert_type.replace('_', ' ')}
                        ${alert.condition_value ? '@ $' + alert.condition_value.toFixed(2) : ''}
                    </div>
                    <span class="alert-status ${statusClass}">
                        ${alert.is_triggered ? 'triggered' : 'active'}
                    </span>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    // Utility methods
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(amount);
    }
    
    formatPercent(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'percent',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value / 100);
    }
    
    formatNumber(value) {
        return new Intl.NumberFormat('en-US').format(value);
    }
    
    // Load command history from localStorage
    loadCommandHistory() {
        try {
            const saved = localStorage.getItem('terminal_command_history');
            if (saved) {
                this.commandHistory = JSON.parse(saved);
                this.historyIndex = this.commandHistory.length;
            }
        } catch (error) {
            console.error('Failed to load command history:', error);
        }
    }
}

// Modal management
class ModalManager {
    static show(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            return bsModal;
        }
    }
    
    static hide(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    }
}

// Watchlist management functions
async function addToWatchlist() {
    ModalManager.show('addWatchlistModal');
}

async function addSymbolToWatchlist() {
    const symbolInput = document.getElementById('watchlist-symbol');
    const symbol = symbolInput.value.trim().toUpperCase();
    
    if (!symbol) {
        alert('Please enter a stock symbol');
        return;
    }
    
    // Execute watch command through terminal
    if (window.terminal) {
        window.terminal.insertCommand(`watch ${symbol}`);
        window.terminal.executeCommand();
    }
    
    // Close modal and clear input
    ModalManager.hide('addWatchlistModal');
    symbolInput.value = '';
}

// Quick action functions
function getQuote(symbol) {
    if (window.terminal) {
        window.terminal.insertCommand(`quote ${symbol}`);
        window.terminal.executeCommand();
    }
}

function analyzeStock(symbol) {
    if (window.terminal) {
        window.terminal.insertCommand(`analyze ${symbol}`);
        window.terminal.executeCommand();
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to clear terminal
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        if (window.terminal) {
            window.terminal.clearTerminal();
        }
    }
    
    // Escape to focus on terminal input
    if (e.key === 'Escape') {
        if (window.terminal && window.terminal.terminalInput) {
            window.terminal.terminalInput.focus();
        }
    }
});

// Initialize terminal when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get session ID from the template
    const sessionId = document.querySelector('[data-session-id]')?.dataset.sessionId;
    
    if (sessionId) {
        window.terminal = new InvestorTerminal(sessionId);
    } else {
        console.error('Session ID not found');
    }
});

// Export for global access
window.InvestorTerminal = InvestorTerminal;
window.ModalManager = ModalManager;
