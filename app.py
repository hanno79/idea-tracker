#!/usr/bin/env python3
"""
Idea Tracker - Web Application
Simple Flask app to view and manage business ideas
"""

from flask import Flask, render_template_string, request, redirect, url_for
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import (
    init_db, get_all_ideas, get_ideas_by_status, update_idea_status,
    get_categories, get_stats, add_idea
)

app = Flask(__name__)

# Simple HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Idea Tracker - Geschäftsideen</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; margin-bottom: 20px; }
        
        .stats { display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap; }
        .stat { background: white; padding: 15px 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat strong { font-size: 24px; display: block; }
        .stat span { color: #666; font-size: 14px; }
        
        .filters { margin-bottom: 20px; display: flex; gap: 10px; flex-wrap: wrap; }
        .filter { padding: 8px 16px; background: white; border: 1px solid #ddd; border-radius: 20px; text-decoration: none; color: #333; }
        .filter.active { background: #007bff; color: white; border-color: #007bff; }
        
        .ideas { display: grid; gap: 20px; }
        .idea { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .idea h3 { margin-bottom: 10px; color: #333; }
        .idea .problem { color: #e65100; font-weight: 500; margin-bottom: 10px; }
        .idea .description { color: #666; margin-bottom: 10px; line-height: 1.5; }
        .idea .meta { display: flex; gap: 15px; font-size: 12px; color: #999; flex-wrap: wrap; }
        .idea .tags { display: flex; gap: 5px; margin-top: 10px; flex-wrap: wrap; }
        .tag { padding: 4px 8px; background: #e3f2fd; border-radius: 4px; font-size: 12px; }
        
        .status-form { margin-top: 15px; display: flex; gap: 10px; }
        .status-btn { padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; }
        .status-new { background: #e3f2fd; }
        .status-interesting { background: #fff3e0; }
        .status-validated { background: #e8f5e9; }
        .status-reject { background: #ffebee; }
        
        .add-form { background: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
        .add-form h2 { margin-bottom: 15px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 500; }
        .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .form-group textarea { min-height: 80px; }
        .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>💡 Idea Tracker</h1>
        
        <div class="stats">
            <div class="stat"><strong>{{ stats.total }}</strong><span>Ideen</span></div>
            <div class="stat"><strong>{{ stats.new }}</strong><span>Neu</span></div>
            <div class="stat"><strong>{{ stats.interesting }}</strong><span>Interessant</span></div>
            <div class="stat"><strong>{{ stats.validated }}</strong><span>Validiert</span></div>
            <div class="stat"><strong>{{ stats.rejected }}</strong><span>Verworfen</span></div>
        </div>
        
        <div class="filters">
            <a href="/" class="filter {{ 'active' if not request.args.get('status') else '' }}">Alle</a>
            <a href="/?status=new" class="filter {{ 'active' if request.args.get('status') == 'new' else '' }}">Neu</a>
            <a href="/?status=interesting" class="filter {{ 'active' if request.args.get('status') == 'interesting' else '' }}">Interessant</a>
            <a href="/?status=validated" class="filter {{ 'active' if request.args.get('status') == 'validated' else '' }}">Validiert</a>
            <a href="/?status=reject" class="filter {{ 'active' if request.args.get('status') == 'reject' else '' }}">Verworfen</a>
        </div>
        
        <div class="add-form">
            <h2>Neue Idee hinzufügen</h2>
            <form method="POST" action="/add">
                <div class="form-group">
                    <label>Titel</label>
                    <input type="text" name="title" required placeholder="Kurze Zusammenfassung">
                </div>
                <div class="form-group">
                    <label>Problem</label>
                    <textarea name="problem" required placeholder="Welches Problem wird gelöst?"></textarea>
                </div>
                <div class="form-group">
                    <label>Beschreibung (optional)</label>
                    <textarea name="description" placeholder="Mehr Details..."></textarea>
                </div>
                <div class="form-group">
                    <label>Existierende Lösungen</label>
                    <textarea name="existing_solutions" placeholder="Was gibt es schon?"></textarea>
                </div>
                <div class="form-group">
                    <label>Quelle</label>
                    <input type="text" name="source" placeholder="z.B. Reddit, StackOverflow...">
                </div>
                <div class="form-group">
                    <label>Kategorie</label>
                    <select name="category">
                        <option value="">-- Kategorie --</option>
                        <option value="productivity">Produktivität</option>
                        <option value="finance">Finanzen</option>
                        <option value="health">Gesundheit</option>
                        <option value="education">Bildung</option>
                        <option value="business">Business</option>
                        <option value="lifestyle">Lifestyle</option>
                        <option value="tech">Technologie</option>
                        <option value="other">Sonstiges</option>
                    </select>
                </div>
                <button type="submit" class="btn">Idee speichern</button>
            </form>
        </div>
        
        <div class="ideas">
            {% for idea in ideas %}
            <div class="idea">
                <h3>{{ idea.title }}</h3>
                <p class="problem">Problem: {{ idea.problem }}</p>
                {% if idea.description %}
                <p class="description">{{ idea.description }}</p>
                {% endif %}
                {% if idea.existing_solutions %}
                <p><strong>Bestehende Lösungen:</strong> {{ idea.existing_solutions }}</p>
                {% endif %}
                <div class="meta">
                    <span>📅 {{ idea.created_at[:10] }}</span>
                    {% if idea.source %}<span>📌 {{ idea.source }}</span>{% endif %}
                    {% if idea.category %}<span class="tag">{{ idea.category }}</span>{% endif %}
                </div>
                <form class="status-form" method="POST" action="/update/{{ idea.id }}">
                    <button type="submit" name="status" value="new" class="status-btn status-new">Neu</button>
                    <button type="submit" name="status" value="interesting" class="status-btn status-interesting">Interessant</button>
                    <button type="submit" name="status" value="validated" class="status-btn status-validated">Validiert</button>
                    <button type="submit" name="status" value="reject" class="status-btn status-reject">Verwerfen</button>
                </form>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    status = request.args.get('status')
    if status:
        ideas = get_ideas_by_status(status)
    else:
        ideas = get_all_ideas()
    stats = get_stats()
    return render_template_string(HTML_TEMPLATE, ideas=ideas, stats=stats)

@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    problem = request.form.get('problem')
    description = request.form.get('description', '')
    existing_solutions = request.form.get('existing_solutions', '')
    source = request.form.get('source', '')
    category = request.form.get('category', '')
    
    add_idea(title, problem, description, existing_solutions, source, category)
    return redirect(url_for('index'))

@app.route('/update/<int:idea_id>', methods=['POST'])
def update(idea_id):
    status = request.form.get('status')
    update_idea_status(idea_id, status)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    print("Idea Tracker läuft auf http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
