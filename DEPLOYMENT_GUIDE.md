# NFC IET Portal — Multi-Location Deployment Guide

## Can You Use This From Different Locations?

**YES!** This is a web application. Once deployed on a server, anyone with internet access and a browser can use it from anywhere.

---

## Deployment Options

### Option 1: Local Network (Same Building/Campus)

**Best for:** Single campus, all users on same WiFi/network

1. Find your server's IP address:
```bash
ipconfig   # Windows
ifconfig   # Linux/Mac
```

2. Update `app.py` to listen on all interfaces:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

3. Other computers access via:
```
http://YOUR_SERVER_IP:5000
```

**Example:** If server IP is `192.168.1.100`, users type `http://192.168.1.100:5000`

---

### Option 2: Cloud/Internet (Anywhere in the world)

**Best for:** Multiple campuses, remote access, official institutional use

#### A) PythonAnywhere (Free tier available)
1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your files via their web interface
3. Set up a MySQL database (they provide one)
4. Configure WSGI file
5. Get a free subdomain: `yourname.pythonanywhere.com`

#### B) VPS/Dedicated Server (DigitalOcean, Linode, AWS)
1. Rent a VPS (~$5-10/month)
2. Install: `sudo apt update && sudo apt install python3-pip mysql-server nginx`
3. Upload your code via Git or SCP
4. Run with **Gunicorn** (production WSGI server):
```bash
pip install gunicorn
# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```
5. Put **Nginx** in front as reverse proxy
6. Point your domain (e.g., `portal.nfc.edu.pk`) to the server IP

#### C) Railway / Render / Heroku (Platform-as-a-Service)
1. Push code to GitHub
2. Connect Railway/Render to your repo
3. Add MySQL database (usually paid)
4. Auto-deploys on every git push

---

### Option 3: On-Premises Server (Institutional)

**Best for:** Full control, data privacy, institutional infrastructure

**Requirements:**
- A dedicated PC/server (even an old i5 with 8GB RAM works)
- Ubuntu Server or Windows Server
- Static IP or dynamic DNS (No-IP, DuckDNS)
- Port forwarding on router (port 80/443)

**Setup:**
```bash
# Install dependencies
sudo apt install python3-pip mysql-server nginx
pip install flask pymysql werkzeug gunicorn

# Copy your portal code
# Configure MySQL database
# Run with systemd service for auto-start
```

---

## Security Checklist for Production

| Task | Why |
|------|-----|
| **Use hashed passwords** | Plaintext passwords are dangerous |
| **Enable HTTPS** | Encrypt data in transit (Let's Encrypt free SSL) |
| **Set `debug=False`** | Debug mode exposes code |
| **Use strong MySQL password** | Protect database |
| **Add rate limiting** | Prevent brute force attacks |
| **Session timeout** | Auto-logout inactive users |
| **Backup database daily** | Prevent data loss |

---

## Quick Production Fix for app.py

Add this to `app.py` before the `if __name__` block:

```python
# Production configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.debug = False
    # Use environment variables for secrets
    app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
```

Change the run block to:
```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    app.run(host=host, port=port, debug=False, threaded=True)
```

---

## Example: Running on Your PC for Campus Access

```bash
# 1. Find your IP
ipconfig
# Look for "IPv4 Address" under your active connection

# 2. Update app.py host
app.run(host='0.0.0.0', port=5000)

# 3. Run
python app.py

# 4. On other computers, open browser and type:
# http://192.168.1.100:5000
```

**Note:** Your PC must stay ON. If it sleeps/shuts down, the portal goes down.

---

## Need Help?

If you tell me:
1. Where you want to host it (local PC / cloud / campus server)
2. How many users (10 / 100 / 1000+)
3. Your budget (free / $5/mo / $50/mo)

I can give you the exact step-by-step setup for your situation.
