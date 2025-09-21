async function fetchJSON(url){ const r = await fetch(url); if(!r.ok) throw new Error(r.status); return r.json(); }
function metric(title,value){ return `<div class="metric"><h4>${title}</h4><div class="value">${value}</div></div>`; }

async function loadAll(){
  try {
    const [risk, market, tech, econ, opt] = await Promise.all([
      fetchJSON('/api/investor_terminal/risk_analytics'),
      fetchJSON('/api/investor_terminal/market_analytics'),
      fetchJSON('/api/investor_terminal/technical_signals'),
      fetchJSON('/api/investor_terminal/economic_events'),
      fetchJSON('/api/investor_terminal/options_analytics')
    ]);

    // Risk
    const riskDiv = document.getElementById('riskMetrics');
    riskDiv.innerHTML = [
      metric('VaR (1D)', `₹${Math.abs(risk.var_1d)}`),
      metric('Sharpe', risk.sharpe_ratio),
      metric('Beta', risk.beta),
      metric('Max DD', risk.max_drawdown + '%'),
      metric('Volatility', risk.volatility + '%')
    ].join('');

    // Market
    const marketDiv = document.getElementById('marketAnalytics');
    marketDiv.innerHTML = [
      metric('VIX', market.vix),
      metric('Put/Call', market.put_call_ratio)
    ].join('');

    // Technical
    const techDiv = document.getElementById('techSignals');
    techDiv.innerHTML = [
      metric('RSI', tech.rsi.value),
      metric('MACD', tech.macd.signal),
      metric('Bands', tech.bollinger_bands.signal)
    ].join('');

    // Economic
    const econDiv = document.getElementById('economicEvents');
    econDiv.innerHTML = `<div class='card'><h3>Economic Events</h3>${econ.events.map(e=>`<div class='event ${e.impact}'>${e.title} <span style='float:right;'>${e.impact}</span><div style='font-size:11px; color:#bbb;'>${e.date} ${e.time} | Forecast ${e.forecast}</div></div>`).join('')}<h4 style='margin:8px 0 4px;'>News</h4>${econ.news.map(n=>`<div class='news-item'>• ${n}</div>`).join('')}</div>`;

    // Options
    const optDiv = document.getElementById('optionsAnalytics');
    optDiv.innerHTML = `<div class='card'><h3>Options Analytics</h3>
      <div class='flex'>${metric('IV', opt.implied_volatility.current + '%') + metric('IV PCTL', opt.implied_volatility.percentile) + metric('PCR', opt.options_chain.pcr)}</div>
      <div style='font-size:12px; margin-top:6px;'>Max Pain: ${opt.options_chain.max_pain} | Call OI: ${opt.options_chain.total_call_oi} | Put OI: ${opt.options_chain.total_put_oi}</div>
    </div>`;
  } catch(err){
    console.error('Load error', err);
  }
}

window.addEventListener('DOMContentLoaded', loadAll);
