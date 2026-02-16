# 🚀 Deployment Guide - Smart Grievance System

This guide covers deploying the Smart Grievance System to production using GitHub Actions.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [GitHub Actions Setup](#github-actions-setup)
3. [Deployment Options](#deployment-options)
4. [Environment Configuration](#environment-configuration)
5. [Database Setup](#database-setup)
6. [Production Checklist](#production-checklist)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ GitHub repository with the code
- ✅ Python 3.9+ on your server
- ✅ Domain name (optional)
- ✅ SSL certificate (recommended)
- ✅ Gmail account for SMTP (or other email service)

---

## GitHub Actions Setup

### 1. Enable GitHub Actions

The repository includes two workflows:

1. **`status-badge.yml`** - Quick build status check
2. **`ci-cd.yml`** - Complete CI/CD pipeline with security checks

### 2. Workflow Triggers

Workflows run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` branch

### 3. View Workflow Status

Go to: `https://github.com/YOUR_USERNAME/smart-grievance-system/actions`

You'll see:
- ✅ Build Status
- ✅ Code Quality & Security
- ✅ Tests
- ✅ Health Checks
- ✅ Deployment Package

---

## Deployment Options

### Option 1: Download Deployment Package (Recommended)

1. Go to GitHub Actions → Latest successful run
2. Download the `deployment-package` artifact
3. Extract on your server:
   ```bash
   tar -xzf smart-grievance-system.tar.gz
   cd deployment/
   ```

### Option 2: Direct Git Clone

```bash
git clone https://github.com/YOUR_USERNAME/smart-grievance-system.git
cd smart-grievance-system
```

### Option 3: Automated Deployment (Advanced)

Add deployment secrets to GitHub:
- `SERVER_HOST` - Your server IP/domain
- `SERVER_USER` - SSH username
- `SSH_PRIVATE_KEY` - SSH private key

---

## Environment Configuration

### 1. Create `.env` file

```bash
cp .env.example .env
nano .env
```

### 2. Configure Environment Variables

```env
# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database
DATABASE_URL=sqlite:///grievance.db  # Or PostgreSQL for production

# Email (Gmail SMTP)
DEMO_EMAIL_MODE=false
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=Smart Grievance System <noreply@grievance.gov>

# Application
PORT=8000
FLASK_ENV=production
```

### 3. Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Database Setup

### 1. Initialize Database

```bash
python -c "from backend.app import create_app; from backend.extensions import db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ Database created')"
```

### 2. Run Migrations (if needed)

```bash
python migrate_db.py
```

### 3. Create Demo Users (Optional)

```bash
python create_demo_hierarchy.py
```

### 4. Train ML Model

```bash
python ml/train.py
```

---

## Production Deployment

### Option 1: Using Gunicorn (Recommended)

1. **Install Gunicorn:**
   ```bash
   pip install gunicorn
   ```

2. **Create `wsgi.py`:**
   ```python
   from backend.app import create_app
   
   app = create_app()
   
   if __name__ == "__main__":
       app.run()
   ```

3. **Run with Gunicorn:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
   ```

### Option 2: Using systemd Service

1. **Create service file:**
   ```bash
   sudo nano /etc/systemd/system/grievance.service
   ```

2. **Add configuration:**
   ```ini
   [Unit]
   Description=Smart Grievance System
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/smart-grievance-system
   Environment="PATH=/var/www/smart-grievance-system/venv/bin"
   ExecStart=/var/www/smart-grievance-system/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start:**
   ```bash
   sudo systemctl enable grievance
   sudo systemctl start grievance
   sudo systemctl status grievance
   ```

### Option 3: Using Docker (Advanced)

1. **Create `Dockerfile`:**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 8000
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "wsgi:app"]
   ```

2. **Build and run:**
   ```bash
   docker build -t smart-grievance-system .
   docker run -p 8000:8000 --env-file .env smart-grievance-system
   ```

---

## Nginx Reverse Proxy (Recommended)

### 1. Install Nginx

```bash
sudo apt update
sudo apt install nginx
```

### 2. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/grievance
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/smart-grievance-system/frontend;
    }
}
```

### 3. Enable site

```bash
sudo ln -s /etc/nginx/sites-available/grievance /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Add SSL (Recommended)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Production Checklist

### Security

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `FLASK_ENV=production`
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (allow only 80, 443, 22)
- [ ] Set up fail2ban for SSH protection
- [ ] Use strong database passwords
- [ ] Enable CORS only for your domain
- [ ] Review and update security headers

### Database

- [ ] Use PostgreSQL instead of SQLite for production
- [ ] Set up regular database backups
- [ ] Configure database connection pooling
- [ ] Enable database encryption at rest

### Email

- [ ] Set `DEMO_EMAIL_MODE=false`
- [ ] Configure Gmail App Password or SMTP service
- [ ] Test email delivery
- [ ] Set up email rate limiting

### Monitoring

- [ ] Set up application logging
- [ ] Configure error tracking (Sentry, etc.)
- [ ] Monitor server resources (CPU, RAM, Disk)
- [ ] Set up uptime monitoring
- [ ] Configure alerts for errors

### Performance

- [ ] Enable Gunicorn with multiple workers
- [ ] Configure Nginx caching
- [ ] Optimize database queries
- [ ] Set up CDN for static files (optional)
- [ ] Enable gzip compression

### Backup

- [ ] Database backup schedule
- [ ] File backup schedule
- [ ] Test restore procedures
- [ ] Off-site backup storage

---

## GitHub Actions Monitoring

### View Build Status

1. Go to your repository
2. Click "Actions" tab
3. See all workflow runs

### Workflow Jobs

The CI/CD pipeline includes:

1. **Code Quality** - Flake8, Bandit security scan
2. **Tests** - Database, models, security tests
3. **Deploy** - Creates deployment package
4. **Health Check** - Tests API endpoints
5. **Documentation** - Checks README completeness
6. **Security Audit** - Dependency vulnerability scan
7. **Summary** - Overall build status

### Download Artifacts

After a successful build:
1. Click on the workflow run
2. Scroll to "Artifacts" section
3. Download `deployment-package`
4. Extract and deploy to your server

---

## Troubleshooting

### Workflow Fails

1. Check the logs in GitHub Actions
2. Common issues:
   - Missing dependencies in `requirements.txt`
   - Database connection errors
   - Port already in use
   - Permission issues

### Deployment Issues

1. **Port already in use:**
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

2. **Permission denied:**
   ```bash
   sudo chown -R $USER:$USER /var/www/smart-grievance-system
   ```

3. **Database locked:**
   ```bash
   # Use PostgreSQL instead of SQLite in production
   ```

4. **Email not sending:**
   - Check Gmail App Password
   - Verify SMTP settings
   - Check firewall rules for port 587

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/YOUR_USERNAME/smart-grievance-system/issues
- Email: your-email@example.com

---

## License

MIT License - See LICENSE file for details
