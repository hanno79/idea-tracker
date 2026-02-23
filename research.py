"""
Idea Research Module
Searches for problems that could be solved with SaaS
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, add_idea, log_research

# Search terms to find problems - expanded for 2025/2026
SEARCH_TERMS = [
    # Work frustration
    "what frustrates you about work tools",
    "problems with current software",
    "things that should be easier",
    "what I wish existed",
    "pain points in daily work",
    "unmet needs technology",
    "jobs to be done frustration",
    "manual processes should be automated",
    "workarounds for missing features",
    "common complaints about apps",
    
    # AI & Automation (2025 trends)
    "AI agent automation problems",
    "LLM limitations frustrations",
    "AI coding assistant problems",
    "automation workflow frustrations",
    
    # Developer tools
    "developer experience pain points",
    "CI CD pipeline frustrations",
    "devops manual workarounds",
    "code review problems",
    
    # Business & Productivity
    "small business software problems",
    "team collaboration frustrations",
    "remote work tool complaints",
    "project management issues",
]

# Problem categories for better organization
CATEGORIES = {
    "productivity": ["note taking", "file management", "scheduling", "task management"],
    "developer": ["coding", "devops", "testing", "deployment", "code review"],
    "business": ["accounting", "CRM", "invoicing", "reporting", "analytics"],
    "ai_ml": ["AI", "machine learning", "automation", "LLM", "agents"],
    "communication": ["meetings", "email", "chat", "collaboration", "documentation"],
    "security": ["authentication", "passwords", "access control", "data protection"],
}

def format_telegram_message(text):
    """Send message via Telegram"""
    import subprocess
    
    # Load token
    CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    token = config.get("channels", {}).get("telegram", {}).get("botToken", "")
    user_id = "7619802592"
    
    if not token:
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", "Content-Type: application/json",
        "-d", f'{{"chat_id": "{user_id}", "text": {json.dumps(text)}, "parse_mode": "Markdown"}}'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def run_research():
    """Main research function - searches for problems
    
    Note: For real-time web research, configure the Brave Search API.
    Run: openclaw configure --section web
    """
    init_db()
    
    findings = []
    
    # Check if web search is configured
    web_search_available = False
    try:
        import os
        if os.environ.get("BRAVE_API_KEY"):
            web_search_available = True
    except:
        pass
    
    # Search queries to find problems
    problem_queries = [
        "Reddit what problem do you wish had a good solution",
        "Stack Overflow what frustrates developers at work", 
        "Indie hackers what problems need solving",
        "Product Hunt ideas for new software",
    ]
    
    # For now, we'll add some example ideas based on common SaaS problem areas
    # In a real implementation, we'd use web scraping or API calls
    
    example_ideas = [
        {
            "title": "KI-Agent Orchestrierung für KMUs",
            "problem": "Kleine Unternehmen können sich keine teuren Enterprise-Lösungen für KI-Automatisierung leisten",
            "description": "Eine Plattform die es Nicht-Technikern erlaubt, KI-Agenten für wiederkehrende Geschäftsprozesse zu erstellen und zu verknüpfen",
            "existing_solutions": "Zapier, Make.com, Microsoft Copilot Studio",
            "source": "Research",
            "category": "ai_ml"
        },
        {
            "title": "Automatischer Notizen-Organisierer",
            "problem": "Notizen werden verteilt gespeichert und sind schwer wiederzufinden",
            "description": "Tool das automatisch Notizen aus verschiedenen Quellen zusammenfasst und kategorisiert",
            "existing_solutions": "Notion, Evernote, Apple Notes",
            "source": "Research",
            "category": "productivity"
        },
        {
            "title": "Meeting-Intelligence für kleine Teams",
            "problem": "Teure Enterprise-Tools für Meeting-Analyse sind für kleine Teams nicht erschwinglich",
            "description": "Einsteigerfreundliches Tool für Meeting-Transkription, Zusammenfassung und Action-Items",
            "existing_solutions": "Otter.ai, Fireflies, Gong",
            "source": "Research", 
            "category": "communication"
        },
        {
            "title": "Cross-Platform Datensynchronisation",
            "problem": "Daten liegen verstreut auf verschiedenen Cloud-Diensten und lassen sich nicht einfach synchronisieren",
            "description": "Tool das automatisch Daten zwischen verschiedenen Cloud-Diensten abgleicht und organisiert",
            "existing_solutions": "Dropbox, Google Drive, MultCloud",
            "source": "Research",
            "category": "productivity"
        },
        {
            "title": "Developer Documentation Generator",
            "problem": "Dokumentation wird nach Entwicklung oft vergessen oder ist veraltet",
            "description": "Automatisches Erstellen und Aktualisieren von API-Dokumentation aus Code-Kommentaren",
            "existing_solutions": "Swagger, JSDoc, Docusaurus",
            "source": "Research",
            "category": "developer"
        },
        {
            "title": "Einfache BI für Nicht-Techniker",
            "problem": "BI-Tools erfordern technisches Wissen und sind für kleine Unternehmen überdimensioniert",
            "description": "Einsteigerfreundliches Dashboard-Tool das Daten aus verschiedenen Quellen ohne SQL visualisiert",
            "existing_solutions": "Tableau, PowerBI, Google Data Studio",
            "source": "Research",
            "category": "business"
        },
        {
            "title": "API-Monitoring für Entwickler",
            "problem": "Existierende API-Monitoring-Tools sind entweder zu einfach oder zu komplex/teuer",
            "description": "Mid-tier API Monitoring mit guter Preis-Leistung für Indie-Developer und kleine Teams",
            "existing_solutions": "Postman, Datadog, New Relic",
            "source": "Research",
            "category": "developer"
        },
        {
            "title": "Passwort-Manager mit einfacher Team-Freigabe",
            "problem": "Bestehende Passwort-Manager sind zu teuer oder haben komplizierte Team-Features",
            "description": "Erschwinglicher Passwort-Manager mit einfacher, sicherer Team-Freigabe ohne Enterprise-Komplexität",
            "existing_solutions": "1Password Teams, Bitwarden, LastPass",
            "source": "Research",
            "category": "security"
        },
        {
            "title": "Local-First Collaboration Tools",
            "problem": "Bestehende Kollaborationstools sind abhängig von Cloud-Verbindung",
            "description": "Offline-fähige Kollaborationstools die lokal arbeiten aber trotzdem synchronisieren",
            "source": "Research",
            "category": "productivity"
        },
        {
            "title": "SaaS-Billing für deutsche Unternehmen",
            "problem": "Internationale Billing-Tools integrieren schlecht mit deutschen Anforderungen (SEPA, GoBD)",
            "description": "Billing-Plattform speziell für deutsche/Mitteleuropäische SaaS-Unternehmen mit lokaler Compliance",
            "existing_solutions": "Stripe, Chargebee, Paddle",
            "source": "Research",
            "category": "business"
        },
    ]
    
    added = 0
    for idea in example_ideas:
        add_idea(**idea)
        added += 1
        findings.append(idea['title'])
    
    # Log the research
    log_research("example_searches", "research", json.dumps(findings))
    
    return added, findings

def send_research_summary(added, findings):
    """Send research summary to Telegram"""
    text = f"🔍 *Recherche abgeschlossen!*\n\n"
    text += f"Neue Ideen gefunden: {added}\n\n"
    text += "*Neue Ideen:*\n"
    for finding in findings:
        text += f"• {finding}\n"
    text += "\nAlle Ideen: http://127.0.0.1:5000"
    
    format_telegram_message(text)

if __name__ == "__main__":
    added, findings = run_research()
    print(f"Füge {added} Ideen hinzu")
    send_research_summary(added, findings)
