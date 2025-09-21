// RIMSI-T Terminal API wiring for frontend
// Assumes Flask backend is running on same host/port

async function rimsiSendCommand(command) {
  const res = await fetch('/api/rimsi/command', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({command})
  });
  return await res.json();
}

async function rimsiCodegen(model, prompt) {
  const res = await fetch('/api/rimsi/codegen', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({model, prompt})
  });
  return await res.json();
}

async function rimsiBacktest(code) {
  const res = await fetch('/api/rimsi/backtest', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({code})
  });
  return await res.json();
}

async function rimsiRisk(code) {
  const res = await fetch('/api/rimsi/risk', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({code})
  });
  return await res.json();
}

async function rimsiHistory(q = '') {
  const res = await fetch('/api/rimsi/history?q=' + encodeURIComponent(q));
  return await res.json();
}

// Example: wire to terminal input (replace your terminalSubmit)
window.rimsiTerminalSubmit = async function() {
  const txt = terminalInput.value.trim();
  if (!txt) return;
  appendTerminal(txt, 'user');
  terminalHistory.push(txt);
  if (terminalHistory.length > 300) terminalHistory.shift();
  histPos = terminalHistory.length;
  localStorage.setItem('terminal_history', JSON.stringify(terminalHistory));
  pushActivity('command', txt);

  // Command routing
  if (/^generate-pine|^generate python|^generate code/i.test(txt)) {
    appendTerminal('Generating code via LLM...');
    const model = txt.includes('pine') ? 'pine' : 'python';
    const out = await rimsiCodegen(model, txt);
    appendTerminal(out.code, 'ai');
    editor.setValue(out.code, -1);
    pushActivity('codegen', txt);
  } else if (/^backtest/i.test(txt)) {
    appendTerminal('Running backtest...');
    const code = editor.getValue();
    const out = await rimsiBacktest(code);
    appendTerminal('Backtest Results: ' + JSON.stringify(out.results), 'ai');
    pushActivity('backtest', txt);
  } else if (/^analyze-risk|^risk/i.test(txt)) {
    appendTerminal('Analyzing risk...');
    const code = editor.getValue();
    const out = await rimsiRisk(code);
    appendTerminal('Risk: ' + out.summary + '\nSuggestions: ' + out.suggestions.join('; '), 'ai');
    pushActivity('risk', txt);
  } else {
    // Default: send to LLM
    const out = await rimsiSendCommand(txt);
    appendTerminal(out.output, 'ai');
    pushActivity('llm', txt);
  }
  terminalInput.value = '';
};

// Example: wire to history panel
window.rimsiRenderHistory = async function(q = '') {
  const feed = document.getElementById('historyFeed');
  const data = await rimsiHistory(q);
  feed.innerHTML = '';
  document.getElementById('historyCount').innerText = data.length;
  if (data.length === 0) {
    feed.innerHTML = '<div class="muted">No history yet.</div>';
    return;
  }
  for (const item of data) {
    const div = document.createElement('div');
    div.className = 'hitem';
    div.innerHTML = `<div style="max-width:220px"><div style="font-weight:600;color:#fff">${escapeHtml(item.output||item.code||item.summary||'')}</div><div class="muted" style="font-size:12px">${escapeHtml(item.type||'')}</div></div><div class="hmeta"><div>${escapeHtml(item.timestamp||'')}</div></div>`;
    feed.appendChild(div);
  }
};
