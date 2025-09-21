"""Unified lightweight adapter layer for multiple AI provider chat APIs.
WARNING: This module stores API keys in plaintext if you choose to persist them.
In production use a secure secret store / vault and DO NOT commit provider_config.json.
"""
from __future__ import annotations
import os, json, time, requests, logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

SUPPORTED_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "openai": {
        "label": "OpenAI",
        "models_hint": "gpt-4o, gpt-4o-mini, gpt-3.5-turbo",
        "requires_base_url": False,
        "notes": "Standard OpenAI Chat Completions API.",
    },
    "anthropic": {
        "label": "Anthropic",
    "models_hint": "claude-sonnet-4-20250514, claude-3-5-sonnet-20241022, claude-3-opus-20240229",
        "requires_base_url": False,
        "notes": "Anthropic Messages API (version 2023-06-01).",
    },
    "ollama": {
        "label": "Ollama Local",
        "models_hint": "llama3, mistral, codellama, phi3",
        "requires_base_url": False,
        "notes": "Local Ollama server (no API key needed).",
        "default_model": "llama3"
    },
    "gemini": {
        "label": "Google Gemini",
        "models_hint": "gemini-1.5-pro, gemini-1.5-flash",
        "requires_base_url": False,
        "notes": "Google Generative Language API (key in query).",
    },
    "huggingface": {
        "label": "HuggingFace Inference",
        "models_hint": "bert-base-uncased, meta-llama/Meta-Llama-3-8B-Instruct",
        "requires_base_url": False,
        "notes": "Hosted inference endpoint (some models require waiting).",
    },
    "cohere": {
        "label": "Cohere",
        "models_hint": "command-r, command-r-plus",
        "requires_base_url": False,
        "notes": "Cohere Chat endpoint.",
    },
    "mistral": {
        "label": "Mistral AI",
        "models_hint": "mistral-large-latest, open-mixtral-8x7b",
        "requires_base_url": False,
        "notes": "Mistral hosted API.",
    },
    "openrouter": {
        "label": "OpenRouter",
        "models_hint": "meta-llama/llama-3-70b-instruct, google/gemini-pro",
        "requires_base_url": False,
        "notes": "Unified multi-provider gateway.",
    },
    "azure_openai": {
        "label": "Azure OpenAI",
        "models_hint": "deployment name (set by you)",
        "requires_base_url": True,
        "notes": "Base URL like https://YOUR-RESOURCE.openai.azure.com; model is deployment name.",
    },
    "perplexity": {
        "label": "Perplexity",
        "models_hint": "llama-3.1-sonar-small-128k-online, llama-3.1-sonar-large-128k-online",
        "requires_base_url": False,
        "notes": "Perplexity Chat Completions API (sonar models, online / offline).",
    },
}

CONFIG_PATH = os.path.join(os.getcwd(), 'provider_config.json')

_runtime_state: Dict[str, Any] = {
    "selected": None,
    "model": None,
}


def load_config() -> Dict[str, Any]:
    if os.path.isfile(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Failed reading provider config: %s", e)
    return {"providers": {}}


def save_config(cfg: Dict[str, Any]):
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("Failed saving provider config: %s", e)


def list_supported() -> List[Dict[str, Any]]:
    out = []
    cfg = load_config()
    for key, meta in SUPPORTED_PROVIDERS.items():
        prov_cfg = cfg.get('providers', {}).get(key, {})
        out.append({
            'key': key,
            'label': meta['label'],
            'configured': bool(prov_cfg.get('api_key')),
            'model': prov_cfg.get('model'),
            'selected': key == _runtime_state.get('selected'),
            'models_hint': meta.get('models_hint'),
            'requires_base_url': meta.get('requires_base_url', False),
            'notes': meta.get('notes'),
        })
    return out


def select_provider(provider: str, model: str | None):
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError("Unsupported provider")
    _runtime_state['selected'] = provider
    if model:
        _runtime_state['model'] = model  # type: ignore[assignment]


def _format_messages(messages: List[Dict[str, str]]) -> str:
    # Fallback for providers needing a single prompt
    parts = []
    for m in messages:
        role = m.get('role','user')
        content = m.get('content') or m.get('text') or ''
        parts.append(f"{role.upper()}: {content}")
    parts.append("ASSISTANT:")
    return '\n'.join(parts)


def call_provider(provider: str, messages: List[Dict[str, str]], override_model: str | None = None, system_prompt: Optional[str] = None) -> str:
    provider = provider.lower()
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError("Unsupported provider")
    cfg_all = load_config()
    prov_cfg = cfg_all.get('providers', {}).get(provider, {})
    # Key resolution priority: runtime env var specific (e.g. ANTHROPIC_API_KEY) > persisted config > generic env var mapping
    explicit_env = None
    if provider == 'anthropic':
        explicit_env = os.getenv('ANTHROPIC_API_KEY')
    api_key = explicit_env or prov_cfg.get('api_key') or os.getenv(prov_cfg.get('env_var',''))
    if provider not in ('ollama',) and not api_key:
        raise ValueError("API key not configured for provider")
    model = override_model or prov_cfg.get('model') or _runtime_state.get('model') or SUPPORTED_PROVIDERS[provider].get('default_model','')
    if not model:
        raise ValueError("Model not specified for provider")
    s = time.time()
    if provider == 'openai':
        url = 'https://api.openai.com/v1/chat/completions'
        payload = {"model": model, "messages": messages, "temperature": 0.2}
        r = requests.post(url, json=payload, headers={'Authorization': f'Bearer {api_key}'}, timeout=60)
        j = r.json()
        return j.get('choices',[{}])[0].get('message',{}).get('content','').strip()
    if provider == 'anthropic':
        url = 'https://api.anthropic.com/v1/messages'
        # Filter & convert to Anthropic expected schema: messages = [{role, content:[{type:'text',text:...}]}]
        mapped: List[Dict[str, Any]] = []
        for m in messages:
            role = m.get('role', 'user')
            if role == 'system':
                sys_txt = m.get('content') or m.get('text', '')
                system_prompt = (system_prompt + '\n' + sys_txt) if system_prompt else sys_txt
                continue
            raw_content = m.get('content') or m.get('text', '') or ''
            if isinstance(raw_content, list):
                content_obj = raw_content
            else:
                content_obj = [{'type': 'text', 'text': raw_content}]
            mapped.append({'role': role, 'content': content_obj})
        if not mapped:
            raise ValueError('No user/assistant messages provided')
        payload: Dict[str, Any] = {"model": model, "max_tokens": 800, "messages": mapped}
        if system_prompt:
            payload['system'] = system_prompt
        r = requests.post(url, json=payload, headers={'x-api-key': api_key, 'anthropic-version': '2023-06-01'}, timeout=60)
        try:
            j = r.json()
        except Exception:
            return r.text[:400]
        # Error surface
        if isinstance(j, dict) and 'error' in j:
            return j.get('error', {}).get('message', '') or str(j)[:400]
        # Standard list content
        if isinstance(j, dict) and 'content' in j:
            if isinstance(j['content'], list):
                text_parts = []
                for blk in j['content']:
                    if isinstance(blk, dict):
                        t = blk.get('text') or blk.get('value') or ''
                        if t:
                            text_parts.append(t)
                if text_parts:
                    return ''.join(text_parts).strip()
            elif isinstance(j['content'], dict):  # single block
                t = j['content'].get('text') or j['content'].get('value')
                if t:
                    return str(t).strip()
        # Some newer formats may wrap in 'message' or 'data'
        for key in ('message','data'):
            if isinstance(j, dict) and key in j:
                inner = j[key]
                if isinstance(inner, dict):
                    cont = inner.get('content')
                    if isinstance(cont, list):
                        parts = [blk.get('text','') for blk in cont if isinstance(blk, dict)]
                        if any(parts):
                            return ''.join(parts).strip()
        # Fallback: try to extract any 'text' fields anywhere shallow
        if isinstance(j, dict):
            texts = []
            for v in j.values():
                if isinstance(v, str) and len(v) < 800 and '\n' in v and ' ' in v:
                    # heuristically choose richer text
                    texts.append(v)
            if texts:
                # pick longest plausible
                texts.sort(key=len, reverse=True)
                return texts[0][:800].strip()
        # Final fallback: truncated raw (likely what previously showed only 'model: ...')
        return (str(j)[:400])
    if provider == 'ollama':
        # Ollama local chat endpoint
        base_url = prov_cfg.get('base_url') or os.getenv('OLLAMA_BASE_URL') or 'http://localhost:11434'
        url = f'{base_url.rstrip('/')}/api/chat'
        # Ollama expects messages with role/content (content string). If we used system_prompt, prepend as system message.
        send_messages = []
        if system_prompt:
            send_messages.append({'role': 'system', 'content': system_prompt})
        for m in messages:
            role = m.get('role','user')
            content = m.get('content') or m.get('text','') or ''
            send_messages.append({'role': role, 'content': content})
        payload = {"model": model, "messages": send_messages, "stream": False}
        try:
            r = requests.post(url, json=payload, timeout=120)
            j = r.json()
            # Newer Ollama chat returns {'message': {'role':'assistant','content':'...'}, ...}
            if isinstance(j, dict):
                if 'message' in j and isinstance(j['message'], dict):
                    return j['message'].get('content','').strip()
                if 'messages' in j and isinstance(j['messages'], list) and j['messages']:
                    # some variants
                    last = j['messages'][-1]
                    if isinstance(last, dict):
                        return last.get('content','').strip()
                if 'output' in j:
                    return str(j.get('output','')).strip()
            return str(j)[:400]
        except Exception as e:
            return f'Ollama error: {e}'[:400]
    if provider == 'gemini':
        url = f'https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={api_key}'
        prompt = _format_messages(messages)
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, json=payload, timeout=60)
        j = r.json()
        try:
            return j['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            return j.get('error',{}).get('message','')
    if provider == 'huggingface':
        prompt = _format_messages(messages)
        url = f'https://api-inference.huggingface.co/models/{model}'
        r = requests.post(url, headers={'Authorization': f'Bearer {api_key}'}, json={"inputs": prompt, "parameters": {"max_new_tokens": 512}}, timeout=120)
        try:
            j = r.json()
            if isinstance(j, list) and j and 'generated_text' in j[0]:
                # full text includes prompt; remove prefix
                gt = j[0]['generated_text']
                return gt[len(prompt):].strip() if gt.startswith(prompt) else gt.strip()
            if isinstance(j, dict):
                if 'generated_text' in j:
                    return j['generated_text']
                if 'error' in j:
                    return j.get('error','') or str(j)
            return str(j)[:400]
        except Exception:
            return r.text[:400]
    if provider == 'cohere':
        url = 'https://api.cohere.com/v1/chat'
        r = requests.post(url, headers={'Authorization': f'Bearer {api_key}'}, json={"model": model, "messages": messages, "max_tokens": 600}, timeout=60)
        j = r.json(); return j.get('text') or j.get('reply','') or j.get('message','') or j.get('response','') or ''
    if provider == 'mistral':
        url = 'https://api.mistral.ai/v1/chat/completions'
        r = requests.post(url, headers={'Authorization': f'Bearer {api_key}'}, json={"model": model, "messages": messages, "temperature": 0.2}, timeout=60)
        j = r.json(); return j.get('choices',[{}])[0].get('message',{}).get('content','').strip()
    if provider == 'openrouter':
        url = 'https://openrouter.ai/api/v1/chat/completions'
        r = requests.post(url, headers={'Authorization': f'Bearer {api_key}', 'HTTP-Referer': 'http://localhost', 'X-Title': 'VS-Terminal'}, json={"model": model, "messages": messages}, timeout=60)
        j = r.json(); return j.get('choices',[{}])[0].get('message',{}).get('content','').strip()
    if provider == 'perplexity':
        url = 'https://api.perplexity.ai/chat/completions'
        payload = {"model": model, "messages": messages, "temperature": 0.2}
        r = requests.post(url, headers={'Authorization': f'Bearer {api_key}', 'Content-Type':'application/json'}, json=payload, timeout=60)
        try:
            j = r.json()
            return j.get('choices',[{}])[0].get('message',{}).get('content','').strip()
        except Exception:
            return r.text[:400]
    if provider == 'azure_openai':
        base_url = prov_cfg.get('base_url') or os.getenv('AZURE_OPENAI_BASE')
        if not base_url:
            raise ValueError('Azure base_url not configured')
        # base_url like https://resource.openai.azure.com ; deployment name is model
        url = f"{base_url}/openai/deployments/{model}/chat/completions?api-version=2024-02-15-preview"
        r = requests.post(url, headers={'api-key': api_key}, json={"messages": messages, "temperature":0.2}, timeout=60)
        j = r.json(); return j.get('choices',[{}])[0].get('message',{}).get('content','').strip()
    raise ValueError('Provider not implemented')


__all__ = [
    'SUPPORTED_PROVIDERS','list_supported','select_provider','call_provider','load_config','save_config'
]
