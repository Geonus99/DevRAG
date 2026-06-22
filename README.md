cat > .gitignore << 'EOF'
# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/
*.egg-info/

# 환경변수
.env
.env.local
.env.production

# Node
node_modules/
.next/
out/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
EOF