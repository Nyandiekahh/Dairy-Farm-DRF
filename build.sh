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
