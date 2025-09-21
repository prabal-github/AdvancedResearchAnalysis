import requests
import json
import os
from typing import Optional, List, Dict

class LLMClient:
    def __init__(self, model_name="mistral:latest", port=None, host=None):
        # Prefer environment overrides (OLLAMA_PORT / OLLAMA_HOST) unless explicitly provided
        env_port = os.getenv('LLM_PORT') or os.getenv('OLLAMA_PORT')
        self.port = int(port or env_port or 11434)
        self.model_name = model_name
        self.host = host or os.getenv('LLM_HOST') or os.getenv('OLLAMA_HOST') or 'localhost'
        self.base_url = f"http://{self.host}:{self.port}"
        # Allow configurable generation timeout (model load can be slow first time)
        try:
            self.gen_timeout = int(os.getenv('LLM_GEN_TIMEOUT') or 60)
        except Exception:
            self.gen_timeout = 60
        # Keep a rolling window of recent generation attempt diagnostics
        self.last_errors: List[Dict] = []  # each: {'stage': str, 'error': str, 'status': int|None}

    def _record_err(self, stage: str, error: str = "", status: Optional[int] = None):
        try:
            self.last_errors.append({"stage": stage, "error": str(error)[:500], "status": status})
            # Limit to last 8 entries
            if len(self.last_errors) > 8:
                self.last_errors = self.last_errors[-8:]
        except Exception:
            pass

    def generate(self, prompt, model=None, max_tokens=512):
        chosen_model = model or self.model_name
        # Attempt 1 (+ retries): Ollama native /api/generate with adaptive timeout
        base_timeout = self.gen_timeout
        for attempt in range(3):
            try:
                payload = {"model": chosen_model, "prompt": prompt, "stream": False}
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=base_timeout * (attempt + 1)
                )
                if response.status_code == 200:
                    try:
                        resp_json = response.json()
                    except Exception as je:
                        self._record_err('ollama_api_generate_json', f'JSON decode fail: {je}')
                        break
                    text_val = resp_json.get("response", "")
                    if not text_val:
                        # Record an empty response anomaly
                        self._record_err('ollama_api_generate_empty', f'Empty response field; keys={list(resp_json.keys())}')
                    return text_val
                else:
                    self._record_err('ollama_api_generate', f"HTTP {response.status_code} {response.text[:200]} (attempt {attempt+1})", response.status_code)
                    # Don't retry 4xx except maybe 408; break early
                    if 400 <= response.status_code < 500 and response.status_code not in (408, 429):
                        break
            except requests.exceptions.ReadTimeout as te:
                self._record_err('ollama_api_generate_timeout', f'Read timeout after {base_timeout * (attempt + 1)}s (attempt {attempt+1})')
                continue  # retry
            except Exception as e:
                self._record_err('ollama_api_generate', f'{e} (attempt {attempt+1})')
                # For connection errors, retry once or twice
                continue
        # End of /api/generate attempts

        # Attempt 2: OpenAI-compatible /v1/generate
        try:
            payload = {"model": chosen_model, "prompt": prompt, "max_tokens": max_tokens}
            response = requests.post(f"{self.base_url}/v1/generate", json=payload, timeout=self.gen_timeout)
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                except Exception as je:
                    self._record_err('openai_compat_generate_json', f'JSON decode fail: {je}')
                    return ""
                text_val = resp_json.get("text", "")
                if not text_val:
                    self._record_err('openai_compat_generate_empty', f'Empty text field; keys={list(resp_json.keys())}')
                return text_val
            else:
                self._record_err('openai_compat_generate', f"HTTP {response.status_code} {response.text[:200]}", response.status_code)
        except Exception as e:
            self._record_err('openai_compat_generate', str(e))

        # Attempt 3: Hugging Face Inference (remote) if token and remote-style model
        hf_token = os.getenv('HF_API_TOKEN')
        if hf_token:
            remote_model = chosen_model
            if remote_model.startswith('hf:'):
                remote_model = remote_model[3:]
            if '/' in remote_model:  # heuristic for remote
                try:
                    headers = {"Authorization": f"Bearer {hf_token}"}
                    params = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens, "return_full_text": False}}
                    r = requests.post(f"https://api-inference.huggingface.co/models/{remote_model}", headers=headers, json=params, timeout=60)
                    if r.status_code == 200:
                        data = r.json()
                        if isinstance(data, list) and data and 'generated_text' in data[0]:
                            return data[0]['generated_text']
                        if isinstance(data, dict):
                            if 'generated_text' in data:
                                return data['generated_text']
                            if 'answer' in data:
                                return data['answer']
                        return str(data)[:4000]
                    else:
                        if r.status_code == 503:
                            self._record_err('hf_inference', 'Model loading (503)')
                            return "[HuggingFace model loading] Please retry in a few seconds."
                        self._record_err('hf_inference', f"HTTP {r.status_code} {r.text[:200]}", r.status_code)
                except Exception as e:
                    self._record_err('hf_inference', str(e))

        return ""

    # Backwards-compatible wrapper name used in app.py
    def generate_response(self, prompt, max_tokens=512, model=None):
        """Return a model response or detailed fallback with recent diagnostics."""
        text = self.generate(prompt, model=model, max_tokens=max_tokens)
        if text:
            return text
        preview = (prompt[:300] + '...') if len(prompt) > 300 else prompt
        diag_lines = []
        if self.last_errors:
            diag_lines.append("Recent attempts:")
            for ent in self.last_errors[-5:]:
                diag_lines.append(f" - {ent['stage']}: {ent.get('error','')[:160]}")
        else:
            diag_lines.append("No error records captured (generation not attempted or silent failure).")
        hint = (f"Check that your local model server (e.g. Ollama) is running and accessible at {self.base_url}. "
                f"Try: curl -X POST {self.base_url}/api/generate -d '{{}}' (with proper JSON).")
        return (
            "[LLM unavailable: fallback]\n" +
            "Prompt preview:\n" + preview + "\n---\n" +
            "\n".join(diag_lines) + "\n" + hint
        )

    def list_models(self):
        """Return list of available local models (Ollama tags)."""
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if r.ok:
                data = r.json()
                # Ollama returns {'models':[{'name':'mistral:latest', ...}, ...]}
                models = [m.get('name') for m in data.get('models', []) if m.get('name')]
                return models
        except Exception:
            pass
        return []

    def model_status(self, model_name=None):
        """Improved health check:
        1. /api/tags to confirm server up
        2. If model listed, /api/show for metadata
        3. No generation unless explicitly warmed (avoid slow timeouts)
        """
        model_to_check = model_name or self.model_name
        status = {"model": model_to_check}
        # Step 1: server tags
        try:
            tags_resp = requests.get(f"{self.base_url}/api/tags", timeout=4)
            if not tags_resp.ok:
                status.update({"ready": False, "server_up": False, "status": tags_resp.status_code})
                return status
            data = tags_resp.json()
            names = [m.get('name') for m in data.get('models', []) if m.get('name')]
            status['server_up'] = True
            status['listed'] = model_to_check in names
            status['available_models'] = names
            if not status['listed']:
                status['ready'] = False
                status['note'] = 'Model not listed; pull it (e.g. ollama pull).'
                return status
        except Exception as e:
            # Server unreachable
            hf_token = os.getenv('HF_API_TOKEN')
            if hf_token and (model_to_check.startswith('hf:') or '/' in model_to_check):
                return {"model": model_to_check, "ready": True, "remote": True, "server_up": False}
            return {"model": model_to_check, "ready": False, "server_up": False, "error": str(e)}

        # Step 2: show metadata (fast)
        try:
            show_resp = requests.post(f"{self.base_url}/api/show", json={"name": model_to_check}, timeout=6)
            if show_resp.ok:
                status['metadata'] = show_resp.json()
                status['ready'] = True  # Consider available if metadata accessible
                return status
            else:
                status['ready'] = False
                status['status'] = show_resp.status_code
                status['body'] = show_resp.text[:120]
                return status
        except Exception as e:
            status['ready'] = False
            status['error'] = str(e)
            return status

    def warm_model(self, model_name=None, prompt="Hello", timeout=None):
        """Trigger a short generation to fully load model (longer timeout)."""
        chosen = model_name or self.model_name
        to = timeout or max(self.gen_timeout, 120)
        try:
            payload = {"model": chosen, "prompt": prompt, "stream": False}
            r = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=to)
            if r.status_code == 200:
                return {"ok": True, "loaded": True, "chars": len(r.text)}
            return {"ok": False, "status": r.status_code, "body": r.text[:200]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def diagnostics(self):
        """Return a snapshot of current configuration and recent error attempts."""
        return {
            'host': self.host,
            'port': self.port,
            'base_url': self.base_url,
            'gen_timeout': self.gen_timeout,
            'default_model': self.model_name,
            'available_models': self.list_models(),
            'default_model_status': self.model_status(self.model_name),
            'recent_errors': self.last_errors[-8:],
            'env_overrides': {
                'LLM_HOST': os.getenv('LLM_HOST'),
                'LLM_PORT': os.getenv('LLM_PORT'),
                'OLLAMA_HOST': os.getenv('OLLAMA_HOST'),
                'OLLAMA_PORT': os.getenv('OLLAMA_PORT'),
                'HF_API_TOKEN_SET': bool(os.getenv('HF_API_TOKEN'))
            }
        }

    def update_config(self, host=None, port=None, model=None, gen_timeout=None):
        """Mutate current client configuration without recreating global reference."""
        changed = {}
        if host and host != self.host:
            self.host = host
            changed['host'] = host
        if port and int(port) != self.port:
            self.port = int(port)
            changed['port'] = self.port
        if model and model != self.model_name:
            self.model_name = model
            changed['model'] = model
        if gen_timeout:
            try:
                g = int(gen_timeout)
                if g != self.gen_timeout:
                    self.gen_timeout = g
                    changed['gen_timeout'] = g
            except Exception as e:
                self._record_err('update_config', f'Invalid gen_timeout {gen_timeout}: {e}')
        # Rebuild base_url
        self.base_url = f"http://{self.host}:{self.port}"
        return changed

class LocalLLMClient:
    def __init__(self, model_name, port):
        self.model_name = model_name
        self.port = port
        self.base_url = f"http://localhost:{port}/v1/generate"

    def generate(self, prompt, max_tokens=512):
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        response = requests.post(self.base_url, json=payload)
        response.raise_for_status()
        return response.json().get("text", "")