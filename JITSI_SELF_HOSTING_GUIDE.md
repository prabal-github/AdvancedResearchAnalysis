# Self-Hosted Jitsi Integration Guide

This guide shows how to replace public `meet.jit.si` with your own Jitsi deployment to remove lobby / prejoin friction and gain moderator control.

## 1. Why self-host?
Public meet.jit.si enforces anti-abuse measures (occasional lobby / host wait). A private instance lets you:
- Disable / control lobby & prejoin fully
- Enforce JWT auth so only your app can create rooms
- Tune performance (octo, scaling) and appearance
- Avoid random moderation policies

## 2. Quick Deployment (Docker Compose)
Create a VM (Ubuntu 22.04+). Point a DNS record `meet.yourdomain.com` to it.

Install Docker & clone official setup:
```bash
sudo apt update && sudo apt install -y git docker.io docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker

git clone https://github.com/jitsi/docker-jitsi-meet.git
cd docker-jitsi-meet
cp env.example .env
```
Edit `.env` (minimum):
```
HTTP_PORT=80
HTTPS_PORT=443
PUBLIC_URL=https://meet.yourdomain.com
ENABLE_LOBBY=0
ENABLE_PREJOIN_PAGE=0
TZ=UTC
```
(Optional) set max constraints:
```
JVB_ENABLE_APIS=rest,colibri
```
Bring it up:
```bash
docker compose up -d
```
Obtain valid TLS (automatic via Let's Encrypt if ports 80/443 open).

Test: visit `https://meet.yourdomain.com` and create a room—should open directly (no lobby).

## 3. Enabling JWT (Optional but Recommended)
Adds authentication so only tokens from your backend create rooms.

In `.env` set:
```
ENABLE_AUTH=1
ENABLE_GUESTS=1
AUTH_TYPE=jwt
JWT_APP_ID=your_app_id
JWT_APP_SECRET=super_long_secret_value
JWT_ALLOW_EMPTY=0
JWT_ACCEPTED_ISSUERS=your_app_id
JWT_ACCEPTED_AUDIENCES=your_app_id
```
Recreate containers:
```bash
docker compose down
sudo docker compose up -d
```

## 4. Backend Token Generation
If you set JWT, add `PyJWT` to `requirements.txt` and create a helper:
```python
import jwt, time
from flask import current_app

def build_jitsi_jwt(room, user_name, moderator=False, email=None):
    secret = current_app.config.get('JITSI_JWT_APP_SECRET')
    app_id = current_app.config.get('JITSI_JWT_APP_ID')
    if not secret or not app_id:
        return None
    now = int(time.time())
    payload = {
        'aud': app_id,
        'iss': app_id,
        'sub': '*',          # or your domain scope
        'room': room,        # a specific room
        'exp': now + 3600,
        'nbf': now - 30,
        'context': {
            'user': {
                'name': user_name,
                'email': email,
                'moderator': moderator
            }
        }
    }
    return jwt.encode(payload, secret, algorithm='HS256')
```
Attach token in iframe / external_api URL:
```
https://meet.yourdomain.com/ROOM_NAME?jwt=TOKEN
```
(Or pass through configOverwrite `jwt` when using External API.)

## 5. App Configuration (`config.py`)
Set:
```python
JITSI_BASE_URL = 'https://meet.yourdomain.com'
JITSI_JWT_APP_ID = 'your_app_id'
JITSI_JWT_APP_SECRET = 'super_long_secret_value'
```
Restart Flask.

## 6. Updating `create_jitsi_room`
Currently it returns plain room names. For JWT you can generate token after booking commit and append `?jwt=...` if you still want direct links (we now embed). For embedded approach, modify `embedded_meeting.html` to fetch a short-lived token via an AJAX call if needed.

## 7. Optional Hardening
- Set `ENABLE_RECORDING=1` and integrate Jibri for recordings.
- Configure `prosody` rate limits.
- Use TURN (coturn) for improved NAT traversal.

## 8. Troubleshooting
| Issue | Fix |
|-------|-----|
| Still see lobby | Ensure `ENABLE_LOBBY=0` and no participant enabled it manually; restart containers. |
| Token rejected | Check clock skew (NTP) and ensure aud/iss match settings. |
| Media blocked | Open UDP 10000/udp; verify firewall. |
| No TLS | Ports 80/443 must be open before first start for Let's Encrypt. |

## 9. Scaling Later
Use multiple JVBs and enable OCTO (set region + mapping) if high concurrency needed. For most MVP scenarios single host is enough.

## 10. Cleanup / Backups
Backup `.env` and any customized config volumes (look at `docker volume ls`).

---
After deploying, change `JITSI_BASE_URL` in `config.py` and restart the app. Meetings should now load instantly without public lobby friction.
