// RIMSI-T Terminal API - Enhanced Version
// Advanced AI-powered financial terminal with LLM integration

// API Functions
async function rimsiSendCommand(command, context = {}) {
  const res = await fetch('/api/rimsi/command', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({command, context})
  });
  return await res.json();
}

async function rimsiCodegen(model, prompt, context = {}) {
  const res = await fetch('/api/rimsi/codegen', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({model, prompt, context})
  });
  return await res.json();
}

async function rimsiBacktest(code, config = {}) {
  const res = await fetch('/api/rimsi/backtest', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      code,
      symbol: config.symbol || 'SPY',
      start_date: config.start_date || '2022-01-01',
      end_date: config.end_date || '2023-12-31',
      initial_capital: config.initial_capital || 100000,
      engine: config.engine || 'auto'
    })
  });
  return await res.json();
}

async function rimsiRisk(codeOrSymbol, context = {}) {
  const res = await fetch('/api/rimsi/risk', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      code: typeof codeOrSymbol === 'string' && codeOrSymbol.includes('def') ? codeOrSymbol : '',
      symbol: typeof codeOrSymbol === 'string' && !codeOrSymbol.includes('def') ? codeOrSymbol : '',
      context
    })
  });
  return await res.json();
}

async function rimsiPortfolio(symbols, config = {}) {
  const res = await fetch('/api/rimsi/portfolio', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      symbols,
      method: config.method || 'auto',
      objective: config.objective || 'sharpe',
      total_value: config.total_value || 100000,
      max_weight: config.max_weight || 0.4,
      min_weight: config.min_weight || 0.0
    })
  });
  return await res.json();
}

async function rimsiExplain(topic, context = {}) {
  const res = await fetch('/api/rimsi/explain', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({topic, context})
  });
  return await res.json();
}

async function rimsiHistory(q = '', type = '', limit = 100) {
  const params = new URLSearchParams();
  if (q) params.append('q', q);
  if (type) params.append('type', type);
  if (limit) params.append('limit', limit.toString());
  
  const res = await fetch('/api/rimsi/history?' + params.toString());
  return await res.json();
}

// Advanced Terminal Management
class RIMSITerminal {
  constructor() {
    this.history = [];
    this.context = {};
    this.isProcessing = false;
    this.callbacks = {
      onLLMResponse: null,
      onRiskResult: null,
      onBacktestResult: null,
      onCodeGenerated: null,
      onError: null
    };
  }

  async sendCommand(command, context = {}) {
    if (this.isProcessing) {
      throw new Error('Another command is being processed');
    }

    this.isProcessing = true;
    
    try {
      // Merge with global context
      const fullContext = {...this.context, ...context};
      
      // Route command to appropriate handler
      const commandType = this.detectCommandType(command);
      let result;

      switch (commandType) {
        case 'codegen':
          result = await this.handleCodeGeneration(command, fullContext);
          break;
        case 'backtest':
          result = await this.handleBacktest(command, fullContext);
          break;
        case 'risk':
          result = await this.handleRiskAnalysis(command, fullContext);
          break;
        case 'portfolio':
          result = await this.handlePortfolioOptimization(command, fullContext);
          break;
        case 'explain':
          result = await this.handleExplanation(command, fullContext);
          break;
        default:
          result = await rimsiSendCommand(command, fullContext);
          break;
      }

      // Add to history
      this.history.unshift({
        command,
        result,
        timestamp: new Date().toISOString(),
        type: commandType
      });

      // Trigger callbacks
      this.triggerCallbacks(result, commandType);

      return result;

    } finally {
      this.isProcessing = false;
    }
  }

  detectCommandType(command) {
    const cmd = command.toLowerCase();
    
    if (cmd.includes('generate') || cmd.includes('build') || cmd.includes('create') || cmd.includes('code')) {
      return 'codegen';
    } else if (cmd.includes('backtest') || cmd.includes('test') || cmd.includes('performance')) {
      return 'backtest';
    } else if (cmd.includes('risk') || cmd.includes('var') || cmd.includes('volatility')) {
      return 'risk';
    } else if (cmd.includes('portfolio') || cmd.includes('optimize') || cmd.includes('allocation')) {
      return 'portfolio';
    } else if (cmd.includes('explain') || cmd.includes('what is') || cmd.includes('how does')) {
      return 'explain';
    } else {
      return 'general';
    }
  }

  async handleCodeGeneration(command, context) {
    // Extract language/model from command
    const language = this.extractLanguage(command);
    const result = await rimsiCodegen(language, command, context);
    
    if (this.callbacks.onCodeGenerated) {
      this.callbacks.onCodeGenerated(result);
    }
    
    return result;
  }

  async handleBacktest(command, context) {
    // Get code from context or last generated code
    const code = context.code || this.getLastGeneratedCode();
    if (!code) {
      throw new Error('No strategy code available for backtesting');
    }

    // Extract parameters from command
    const config = this.extractBacktestConfig(command);
    const result = await rimsiBacktest(code, config);
    
    if (this.callbacks.onBacktestResult) {
      this.callbacks.onBacktestResult(result);
    }
    
    return result;
  }

  async handleRiskAnalysis(command, context) {
    // Determine if analyzing code or symbol
    const target = context.code || this.extractSymbol(command) || this.getLastGeneratedCode();
    const result = await rimsiRisk(target, context);
    
    if (this.callbacks.onRiskResult) {
      this.callbacks.onRiskResult(result);
    }
    
    return result;
  }

  async handlePortfolioOptimization(command, context) {
    // Extract symbols from command
    const symbols = this.extractSymbols(command);
    const config = this.extractPortfolioConfig(command);
    const result = await rimsiPortfolio(symbols, config);
    
    return result;
  }

  async handleExplanation(command, context) {
    const topic = command.replace(/explain|what is|how does/i, '').trim();
    return await rimsiExplain(topic, context);
  }

  extractLanguage(command) {
    const cmd = command.toLowerCase();
    if (cmd.includes('pine') || cmd.includes('tradingview')) return 'pine_script';
    if (cmd.includes('r ') || cmd.includes(' r code')) return 'r';
    if (cmd.includes('matlab')) return 'matlab';
    if (cmd.includes('javascript') || cmd.includes('js')) return 'javascript';
    return 'python';
  }

  extractSymbol(command) {
    const match = command.match(/\b([A-Z]{1,5})\b/);
    return match ? match[1] : null;
  }

  extractSymbols(command) {
    const matches = command.match(/\b[A-Z]{1,5}\b/g);
    return matches ? matches.filter(s => s.length <= 5) : ['SPY', 'QQQ', 'IWM'];
  }

  extractBacktestConfig(command) {
    const config = {};
    
    // Extract symbol
    const symbol = this.extractSymbol(command);
    if (symbol) config.symbol = symbol;
    
    // Extract year
    const yearMatch = command.match(/\b(20\d{2})\b/);
    if (yearMatch) {
      const year = yearMatch[1];
      config.start_date = `${year}-01-01`;
      config.end_date = `${year}-12-31`;
    }
    
    // Extract capital
    const capitalMatch = command.match(/\$?([\d,]+)/);
    if (capitalMatch) {
      config.initial_capital = parseInt(capitalMatch[1].replace(/,/g, ''));
    }
    
    return config;
  }

  extractPortfolioConfig(command) {
    const config = {};
    
    if (command.includes('conservative')) {
      config.max_weight = 0.3;
      config.objective = 'volatility';
    } else if (command.includes('aggressive')) {
      config.max_weight = 0.6;
      config.objective = 'return';
    } else {
      config.objective = 'sharpe';
    }
    
    return config;
  }

  getLastGeneratedCode() {
    for (const item of this.history) {
      if (item.type === 'codegen' && item.result.code) {
        return item.result.code;
      }
    }
    return null;
  }

  triggerCallbacks(result, type) {
    if (result.success === false && this.callbacks.onError) {
      this.callbacks.onError(result);
      return;
    }

    switch (type) {
      case 'general':
        if (this.callbacks.onLLMResponse && result.output) {
          this.callbacks.onLLMResponse(result.output);
        }
        break;
      case 'risk':
        if (this.callbacks.onRiskResult) {
          this.callbacks.onRiskResult(result);
        }
        break;
      case 'backtest':
        if (this.callbacks.onBacktestResult) {
          this.callbacks.onBacktestResult(result);
        }
        break;
      case 'codegen':
        if (this.callbacks.onCodeGenerated) {
          this.callbacks.onCodeGenerated(result);
        }
        break;
    }
  }

  setContext(context) {
    this.context = {...this.context, ...context};
  }

  getContext() {
    return this.context;
  }

  async getHistory(filter = {}) {
    const { q, type, limit } = filter;
    return await rimsiHistory(q, type, limit);
  }

  clearHistory() {
    this.history = [];
  }

  onLLMResponse(callback) {
    this.callbacks.onLLMResponse = callback;
  }

  onRiskResult(callback) {
    this.callbacks.onRiskResult = callback;
  }

  onBacktestResult(callback) {
    this.callbacks.onBacktestResult = callback;
  }

  onCodeGenerated(callback) {
    this.callbacks.onCodeGenerated = callback;
  }

  onError(callback) {
    this.callbacks.onError = callback;
  }
}

// Global instance
window.rimsiTerminal = new RIMSITerminal();

// Legacy compatibility functions
window.rimsiTerminalSubmit = async function() {
  const input = document.getElementById('terminalInput');
  if (!input) return;
  
  const command = input.value.trim();
  if (!command) return;
  
  try {
    await window.rimsiTerminal.sendCommand(command);
    input.value = '';
  } catch (error) {
    console.error('Command failed:', error);
  }
};

// Export individual functions for backward compatibility
window.rimsiSendCommand = rimsiSendCommand;
window.rimsiCodegen = rimsiCodegen;
window.rimsiBacktest = rimsiBacktest;
window.rimsiRisk = rimsiRisk;
window.rimsiPortfolio = rimsiPortfolio;
window.rimsiExplain = rimsiExplain;
window.rimsiHistory = rimsiHistory;

// Utility function for HTML escaping
function escapeHtml(unsafe) {
  return unsafe.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
