import os
import uuid
import json
import hashlib
from datetime import datetime

# Import the Flask app context, db, and model from the application
from app import app, db


def get_published_model_class():
    """Late import to avoid circulars; returns PublishedModel class."""
    # Import inside function to ensure app module is initialized
    from app import PublishedModel  # type: ignore
    return PublishedModel


def get_artifact_root():
    """Return the secure artifacts root consistent with the app."""
    try:
        from app import ARTIFACT_ROOT  # type: ignore
        return ARTIFACT_ROOT
    except Exception:
        return os.path.join(os.getcwd(), 'secure_artifacts')


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def seed_model(name: str, code: str, readme: str, allowed_functions, visibility='public', category='Quantitative', version=None, author_key='seed:system'):
    PM = get_published_model_class()
    # Idempotency: skip if a model with this exact name already exists
    existing = PM.query.filter_by(name=name).first()
    if existing:
        return False, f"Model '{name}' already exists; skipping"

    model_id = str(uuid.uuid4())
    artifact_root = get_artifact_root()
    model_dir = os.path.join(artifact_root, model_id)
    ensure_dir(model_dir)
    artifact_file = os.path.join(model_dir, 'model.py')
    with open(artifact_file, 'w', encoding='utf-8') as f:
        f.write(code)

    version = version or datetime.utcnow().strftime('%Y%m%d%H%M%S')
    hash_sha256 = hashlib.sha256(code.encode('utf-8')).hexdigest()

    pm = PM()
    # Assign attributes explicitly to avoid static lint errors on constructor kwargs
    pm.id = model_id
    pm.name = name
    pm.version = version
    pm.author_user_key = author_key
    pm.readme_md = readme
    pm.artifact_path = artifact_file
    pm.allowed_functions = json.dumps(allowed_functions)
    pm.visibility = visibility
    pm.category = category
    pm.editors = json.dumps([])
    pm.hash_sha256 = hash_sha256
    pm.last_change_at = datetime.utcnow()
    pm.last_change_summary = 'Seeded model created'
    db.session.add(pm)
    db.session.commit()
    return True, f"Seeded model '{name}' (id={model_id})"


def main():
    # Minimal, safe demo models
    models = [
        {
            'name': 'SMA Crossover Strategy',
            'category': 'Quantitative',
            'allowed_functions': ['predict', 'backtest'],
            'readme': (
                "SMA Crossover Strategy\n\n"
                "Simple moving average crossover demo.\n\n"
                "Functions:\n- predict(prices: list[float]) -> dict\n- backtest(prices: list[float], short:int=5, long:int=20) -> dict\n"
            ),
            'code': (
                "def sma(values, window):\n"
                "    if not values or window <= 0: return []\n"
                "    out=[]\n"
                "    for i in range(len(values)):\n"
                "        start=max(0, i-window+1)\n"
                "        segment=values[start:i+1]\n"
                "        out.append(sum(segment)/len(segment))\n"
                "    return out\n\n"
                "def predict(prices):\n"
                "    short=sma(prices, 5)\n"
                "    long=sma(prices, 20)\n"
                "    signal='hold'\n"
                "    if len(prices) >= 20 and short[-1] > long[-1]: signal='buy'\n"
                "    elif len(prices) >= 20 and short[-1] < long[-1]: signal='sell'\n"
                "    return {'signal': signal, 'short': short[-1] if short else None, 'long': long[-1] if long else None}\n\n"
                "def backtest(prices, short=5, long=20):\n"
                "    cash=10000.0; position=0.0; last_price=None\n"
                "    def _sma(vals, w):\n"
                "        out=[]\n"
                "        for i in range(len(vals)):\n"
                "            start=max(0,i-w+1); seg=vals[start:i+1]; out.append(sum(seg)/len(seg))\n"
                "        return out\n"
                "    s=_sma(prices, short); l=_sma(prices, long)\n"
                "    for i,p in enumerate(prices):\n"
                "        last_price=p\n"
                "        if i==0 or i>=len(l) or i>=len(s): continue\n"
                "        if s[i] > l[i] and position==0:\n"
                "            position=cash/p; cash=0\n"
                "        elif s[i] < l[i] and position>0:\n"
                "            cash=position*p; position=0\n"
                "    final_value=cash if position==0 else cash+position*last_price\n"
                "    return {'final_value': final_value}\n"
            ),
        },
        {
            'name': 'Simple Volatility Score',
            'category': 'Risk',
            'allowed_functions': ['score'],
            'readme': (
                "Simple Volatility Score\n\n"
                "Computes a naive volatility metric from price returns.\n\n"
                "Functions:\n- score(prices: list[float]) -> dict\n"
            ),
            'code': (
                "def score(prices):\n"
                "    if not prices or len(prices)<2: return {'vol': None}\n"
                "    rets=[]\n"
                "    for i in range(1,len(prices)):\n"
                "        if prices[i-1]==0: continue\n"
                "        rets.append((prices[i]-prices[i-1])/prices[i-1])\n"
                "    if not rets: return {'vol': None}\n"
                "    mean=sum(rets)/len(rets)\n"
                "    var=sum((r-mean)**2 for r in rets)/len(rets)\n"
                "    vol=var**0.5\n"
                "    return {'vol': vol, 'n': len(rets)}\n"
            ),
        },
        {
            'name': 'Momentum Score',
            'category': 'Momentum',
            'allowed_functions': ['score'],
            'readme': (
                "Momentum Score\n\n"
                "Computes a simple momentum from last N days.\n\n"
                "Functions:\n- score(prices: list[float], window:int=10) -> dict\n"
            ),
            'code': (
                "def score(prices, window=10):\n"
                "    if not prices or len(prices)<window: return {'momentum': None}\n"
                "    start=prices[-window]; end=prices[-1]\n"
                "    if start==0: return {'momentum': None}\n"
                "    return {'momentum': (end-start)/start}\n"
            ),
        },
    ]

    results = []
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        for m in models:
            ok, msg = seed_model(
                name=m['name'],
                code=m['code'],
                readme=m['readme'],
                allowed_functions=m['allowed_functions'],
                visibility='public',
                category=m['category']
            )
            results.append((ok, msg))

    for ok, msg in results:
        print(('OK: ' if ok else 'SKIP: ') + msg)


if __name__ == '__main__':
    main()
