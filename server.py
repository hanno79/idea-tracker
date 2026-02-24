#!/usr/bin/env python3
import sys
import http.server
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import cgi
import hashlib
import secrets
import time

sys.path.insert(0, str(Path(__file__).parent))
from database import init_db, get_all_ideas, get_ideas_by_status, get_stats, add_idea, update_idea_status

# Simple password protection
# Change this to your desired password!
PASSWORD = "alfred2026"
SESSION_COOKIE_NAME = "idea_tracker_session"
SESSION_TIMEOUT = 60 * 60 * 24  # 24 hours

# In-memory session store (for single-instance server)
sessions = {}

def create_session():
    """Create a new session token"""
    token = secrets.token_hex(16)
    sessions[token] = time.time()
    return token

def validate_session(token):
    """Check if session is valid and not expired"""
    if not token:
        return False
    if token not in sessions:
        return False
    if time.time() - sessions[token] > SESSION_TIMEOUT:
        del sessions[token]
        return False
    # Extend session
    sessions[token] = time.time()
    return True

def generate_login_html():
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Idea Tracker</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0; }
        .login-container { background: #16213e; padding: 40px; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); width: 100%; max-width: 360px; }
        h1 { text-align: center; margin-bottom: 30px; color: #e94560; }
        input { width: 100%; padding: 14px; margin: 10px 0; border: 2px solid #0f3460; border-radius: 8px; background: #1a1a2e; color: #eee; font-size: 16px; box-sizing: border-box; }
        input:focus { outline: none; border-color: #e94560; }
        button { width: 100%; padding: 14px; background: #e94560; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 10px; }
        button:hover { background: #ff6b6b; }
        .error { color: #ff6b6b; text-align: center; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>🔐 Idea Tracker</h1>
        <form method="POST" action="/login">
            <input type="password" name="password" placeholder="Passwort eingeben" required>
            <button type="submit">Login</button>
        </form>
        {{ERROR}}
    </div>
</body>
</html>"""

HTML = open(Path(__file__).parent / "template.html").read()

def generate_html(status=None):
    ideas = get_ideas_by_status(status) if status else get_all_ideas()
    stats = get_stats()
    
    ideas_html = ""
    for idea in ideas:
        is_new = 'status-new' if idea['status'] == 'new' else ''
        is_interesting = 'status-interesting' if idea['status'] == 'interesting' else ''
        is_validated = 'status-validated' if idea['status'] == 'validated' else ''
        is_reject = 'status-reject' if idea['status'] == 'reject' else ''
        
        ideas_html += f"""
            <div class="idea">
                <h3>{idea['title']}</h3>
                <p class="problem">Problem: {idea['problem']}</p>
        """
        if idea['description']:
            ideas_html += f'<p class="description">{idea["description"]}</p>'
        if idea['existing_solutions']:
            ideas_html += f'<p><strong>Bestehende Lösungen:</strong> {idea["existing_solutions"]}</p>'
        
        ideas_html += f"""
                <div class="meta">
                    <span>📅 {idea['created_at'][:10]}</span>
        """
        if idea['source']:
            ideas_html += f'<span>📌 {idea["source"]}</span>'
        if idea['category']:
            ideas_html += f'<span class="tag">{idea["category"]}</span>'
        
        ideas_html += f"""
                </div>
                <div class="status-bar">
                    <span class="status-label">Status:</span>
                    <a href="/status/{idea['id']}/new" class="status-btn status-new {is_new}">Neu</a>
                    <a href="/status/{idea['id']}/interesting" class="status-btn status-interesting {is_interesting}">Interessant</a>
                    <a href="/status/{idea['id']}/validated" class="status-btn status-validated {is_validated}">Validiert</a>
                    <a href="/status/{idea['id']}/reject" class="status-btn status-reject {is_reject}">Verwerfen</a>
                </div>
            </div>"""
    
    html = HTML
    html = html.replace("{{TOTAL}}", str(stats['total']))
    html = html.replace("{{NEW}}", str(stats['new']))
    html = html.replace("{{INTERESTING}}", str(stats['interesting']))
    html = html.replace("{{VALIDATED}}", str(stats['validated']))
    html = html.replace("{{REJECTED}}", str(stats['rejected']))
    html = html.replace("{{IDEAS}}", ideas_html)
    
    # Active filter
    is_active = {"": "active", "new": "", "interesting": "", "validated": "", "reject": ""}
    if status:
        is_active[status] = "active"
    
    html = html.replace("{{IS_ALL}}", is_active.get("", ""))
    html = html.replace("{{IS_NEW}}", is_active.get("new", ""))
    html = html.replace("{{IS_INTERESTING}}", is_active.get("interesting", ""))
    html = html.replace("{{IS_VALIDATED}}", is_active.get("validated", ""))
    html = html.replace("{{IS_REJECT}}", is_active.get("reject", ""))
    
    return html

def get_session_from_cookie(self):
    """Extract session cookie"""
    cookie = self.headers.get('Cookie', '')
    for item in cookie.split(';'):
        item = item.strip()
        if item.startswith(f'{SESSION_COOKIE_NAME}='):
            return item.split('=', 1)[1]
    return None

def check_auth(self):
    """Check if user is authenticated"""
    token = self.get_session_from_cookie()
    return validate_session(token)

def send_login_page(self, error=False):
    """Send login page"""
    html = generate_login_html()
    if error:
        html = html.replace('{{ERROR}}', '<p class="error">Falsches Passwort</p>')
    else:
        html = html.replace('{{ERROR}}', '')
    
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(html.encode())

def send_redirect(self, location):
    """Send redirect"""
    self.send_response(302)
    self.send_header('Location', location)
    self.end_headers()

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        status_filter = query.get('status', [None])[0]
        
        # Login page
        if path == '/login':
            self.send_login_page()
            return
        
        # Logout
        if path == '/logout':
            cookie = self.headers.get('Cookie', '')
            for item in cookie.split(';'):
                item = item.strip()
                if item.startswith(f'{SESSION_COOKIE_NAME}='):
                    token = item.split('=', 1)[1]
                    sessions.pop(token, None)
            self.send_redirect('/')
            return
        
        # Check auth for all other routes - TEMPORARILY DISABLED FOR RAILWAY
        # if not self.check_auth():
        #     self.send_login_page()
        #     return
        
        # Handle status update URLs like /status/123/new
        if path.startswith('/status/'):
            parts = path.split('/')
            if len(parts) == 4:
                idea_id = int(parts[2])
                new_status = parts[3]
                update_idea_status(idea_id, new_status)
                # Redirect to home
                self.send_redirect('/')
                return
        
        html = generate_html(status_filter)
        
        # Add session cookie header
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Set-Cookie", f"{SESSION_COOKIE_NAME}=; Path=/; HttpOnly")
        self.end_headers()
        self.wfile.write(html.encode())
    
    def do_POST(self):
        parsed = urlparse(self.path)
        
        # Handle login
        if parsed.path == '/login':
            content_type = self.headers.get('Content-Type')
            if content_type:
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={
                        'REQUEST_METHOD': 'POST',
                        'CONTENT_TYPE': content_type,
                    }
                )
                
                password = form.getvalue('password', '')
                
                if password == PASSWORD:
                    token = create_session()
                    self.send_response(302)
                    self.send_header('Location', '/')
                    self.send_header('Set-Cookie', f'{SESSION_COOKIE_NAME}={token}; Path=/; HttpOnly; Max-Age={SESSION_TIMEOUT}')
                    self.end_headers()
                else:
                    self.send_login_page(error=True)
            return
        
        # Check auth for POST to /add
        if not self.check_auth():
            self.send_login_page()
            return
        
        if parsed.path == '/add':
            # Parse form data
            content_type = self.headers.get('Content-Type')
            if content_type:
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={
                        'REQUEST_METHOD': 'POST',
                        'CONTENT_TYPE': content_type,
                    }
                )
                
                title = form.getvalue('title', '')
                problem = form.getvalue('problem', '')
                description = form.getvalue('description', '')
                existing_solutions = form.getvalue('existing_solutions', '')
                source = form.getvalue('source', '')
                category = form.getvalue('category', '')
                
                if title and problem and source:
                    add_idea(title, problem, description, existing_solutions, source, category)
            
            # Redirect to home
            self.send_redirect('/')
            return
        
        self.send_redirect('/')

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    init_db()
    print(f"Idea Tracker: http://0.0.0.0:{port}")
    http.server.HTTPServer(("", port), Handler).serve_forever()
