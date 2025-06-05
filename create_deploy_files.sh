#!/bin/bash

echo "🚀 Creating deployment files..."

# Create render.yaml
cat > render.yaml << 'EOF'
databases:
  - name: dairy-farm-db
    databaseName: dairy_farm_db
    user: dairy_farm_user

services:
  - type: web
    name: dairy-farm-api
    env: python
    buildCommand: "./build.sh"
    startCommand: "gunicorn dairy_farm.wsgi:application"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: dairy-farm-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: False
      - key: EMAIL_HOST_USER
        value: einsteinmokua100@gmail.com
      - key: EMAIL_HOST_PASSWORD
        value: "qeii jxyl rrjs alxv"
      - key: DEFAULT_FROM_EMAIL
        value: einsteinmokua100@gmail.com
      - key: ALLOWED_HOSTS
        value: "*"
      - key: CORS_ALLOWED_ORIGINS
        value: "https://localhost:3000,http://localhost:3000"
EOF

# Create build.sh
cat > build.sh << 'EOF'
#!/usr/bin/env bash
set -o errexit

echo "🔧 Installing dependencies..."
pip install -r requirements.txt

echo "📁 Creating required directories..."
mkdir -p logs
mkdir -p staticfiles

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🗄️ Running database migrations..."
python manage.py migrate

echo "✅ Build completed successfully!"
EOF

# Make build.sh executable
chmod +x build.sh

# Create runtime.txt for Python version
echo "python-3.10.12" > runtime.txt

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Environment variables
.env
.env.local
.env.production

# Virtual environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Media files (for production, use cloud storage)
media/

# Static files (collected automatically)
staticfiles/

# Logs
logs/
EOF

echo "✅ Deployment files created successfully!"
echo ""
echo "📁 Files created:"
echo "  - render.yaml (Render configuration)"
echo "  - build.sh (Build script)"
echo "  - runtime.txt (Python version)"
echo "  - .gitignore (Git ignore rules)"
echo ""
echo "🚀 Next steps:"
echo "1. Initialize git: git init"
echo "2. Add files: git add ."
echo "3. Commit: git commit -m 'Initial dairy farm backend'"
echo "4. Create GitHub repo and push"
echo "5. Deploy on Render.com"
EOF