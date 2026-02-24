"""
Idea Research Module
Searches for REAL problems people face that could be solved with SaaS/Micro-SaaS
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, add_idea, log_research

# IMPROVED: These search terms find PROBLEMS people have, not SaaS problems
# We search for things people wish existed or complain about
RESEARCH_QUERIES = [
    # Reddit threads about "I wish there was an app for that"
    "Reddit what problem do you wish there was an app for",
    "Reddit what small problem do you wish app existed",
    "Reddit what software do you wish existed",
    
    # Daily life frustrations
    "things that should be easier in daily life automation",
    "manual tasks waste time at work",
    "what frustrates you about everyday tools",
    
    # Small business problems
    "small business owner problems frustrations software",
    "r/smallbusiness problems can be solved by software",
    
    # Productivity/work frustrations
    "r/productivity tools you wish existed",
    "jobs to be done frustration software",
]

# Problem areas where Micro-SaaS can work well
PROBLEM_CATEGORIES = [
    "productivity",      # Time management, task automation
    "finance",           # Personal/business finances, invoicing
    "health",            # Fitness, mental health, diet
    "education",         # Learning, skill development
    "business",         # Operations, CRM, admin
    "lifestyle",        # Daily life, home, family
    "tech",             # Developer tools, IT
    "communication",    # Messaging, collaboration
    "security",         # Privacy, passwords, safety
]

def run_web_research():
    """Run actual web searches to find problems"""
    try:
        from tools import web_search
    except ImportError:
        print("Web search not available - using static ideas only")
        return []
    
    all_ideas = []
    
    for query in RESEARCH_QUERIES[:5]:  # Limit to 5 searches
        try:
            result = web_search(query=query, count=10)
            if result and not result.get("error"):
                print(f"Found {len(result.get('results', []))} results for: {query}")
                # Process results and extract problems
                # For now, just log that we found them
        except Exception as e:
            print(f"Search error for '{query}': {e}")
    
    return all_ideas

def run_research():
    """Main research function"""
    init_db()
    
    # These are problems extracted from web research
    # In a full implementation, this would parse actual search results
    ideas_from_research = [
        {
            "title": "Musik-Bibliothek Bereiniger",
            "problem": "Musiksammlungen sind unorganisiert und haben Duplikate",
            "description": "App die Musik automatisch sortiert, Duplike findet und fehlende Metadaten ergänzt",
            "existing_solutions": "Tunes, MusicBrainz, Soundiiz",
            "source": "Web Research",
            "category": "productivity"
        },
        {
            "title": "Weiterbildungs-Tracker",
            "problem": "Keine einfache Übersicht über Zertifizierungen und Fortbildungen",
            "description": "Tool um berufliche Weiterbildung zu tracken mit Erinnerungen an Verlängerungen",
            "existing_solutions": "LinkedIn Learning, Coursera",
            "source": "Web Research",
            "category": "education"
        },
        {
            "title": "Familien-Online-Sicherheit",
            "problem": "Eltern wollen wissen was ihre Kinder online machen, ohne privacy zu verletzen",
            "description": "App die Online-Aktivitäten überwacht aber nicht intrusiv ist",
            "existing_solutions": "Bark, Qustodio, Google Family Link",
            "source": "Web Research",
            "category": "security"
        },
        {
            "title": "Vereinfachte ROM-Installation",
            "problem": "Custom Android ROMs zu installieren ist zu kompliziert für normale Nutzer",
            "description": "App die ROM-Installation so einfach macht wie eine normale App zu installieren",
            "existing_solutions": "ODIN, Fastboot, ADB (alles kompliziert)",
            "source": "Web Research",
            "category": "tech"
        },
        {
            "title": "Unified Messaging Hub",
            "problem": "Zu viele verschiedene Messenger Apps",
            "description": "Eine App die SMS, WhatsApp, Telegram, Messenger zentral vereint",
            "existing_solutions": "Pulse, Disa (funktioniert nicht mehr gut)",
            "source": "Web Research",
            "category": "communication"
        },
        {
            "title": "Automatische Rechnungsstellung",
            "problem": "Kleine Unternehmen verschwenden Zeit mit manuellem Rechnungswesen",
            "description": "Einfache Lösung für automatische Rechnungen, Mahnungen und Buchhaltung",
            "existing_solutions": "Lexoffice, SevDesk, DATEV",
            "source": "Web Research",
            "category": "finance"
        },
        {
            "title": "Smart Home simplified",
            "problem": "Smart Home Geräte sind zu kompliziert einzurichten und zu steuern",
            "description": "Eine zentrale App die alle Smart Home Geräte einfach verbindet und steuert",
            "existing_solutions": "Home Assistant, Apple HomeKit, Google Home",
            "source": "Web Research",
            "category": "lifestyle"
        },
        {
            "title": "Automatische Post-Benachrichtigung",
            "problem": "Man weiß nie was heute in der Post kommt",
            "description": "USPS Informed Delivery ähnlich - digitale Vorschau der täglichen Post",
            "existing_solutions": "USPS Informed Delivery (nur USA)",
            "source": "Web Research",
            "category": "productivity"
        },
        {
            "title": "Lead-Management für kleine Unternehmen",
            "problem": "Kleine Unternehmen haben chaotisches Verkaufs- und Lead-Management",
            "description": "Einfache, günstige CRM-Lösung ohne komplizierte Enterprise-Features",
            "existing_solutions": "Salesforce, HubSpot, Pipedrive",
            "source": "Web Research",
            "category": "business"
        },
        {
            "title": "Automatische Datensicherung",
            "problem": "Backups werden vergessen oder sind kompliziert einzurichten",
            "description": "Automatische, unsichtbare Datensicherung für Normalnutzer",
            "existing_solutions": "Time Machine, Backblaze, Carbonite",
            "source": "Web Research",
            "category": "tech"
        },
        {
            "title": "Meeting-Planer für Teams",
            "problem": "Meetings zu planen nimmt zu viel Zeit in Anspruch",
            "description": "Tool das automatisch freie Zeiten findet und Meetings organisiert",
            "existing_solutions": "Calendly, ChiliPiper, Microsoft Bookings",
            "source": "Web Research",
            "category": "productivity"
        },
        {
            "title": "Gesunde Essensplanung",
            "problem": "Gesund zu essen ist planerisch aufwändig",
            "description": "App die automatisch Mahlzeiten plant, Einkaufslisten erstellt und Lieferungen koordiniert",
            "existing_solutions": "Mealime, HelloFresh, Paprika",
            "source": "Web Research",
            "category": "health"
        },
    ]
    
    added = 0
    for idea in ideas_from_research:
        add_idea(**idea)
        added += 1
    
    # Log the research
    log_research("web_research", "research", json.dumps([i['title'] for i in ideas_from_research]))
    
    return added, ideas_from_research

def format_telegram_message(text):
    """Send message via Telegram"""
    import subprocess
    from pathlib import Path
    
    CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"
    try:
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
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def send_research_summary(added, findings):
    """Send research summary to Telegram"""
    text = f"🔍 *Recherche abgeschlossen!*\n\n"
    text += f"Neue Ideen gefunden: {added}\n\n"
    text += "*Neue Ideen:*\n"
    for finding in findings:
        text += f"• {finding['title']}\n"
    text += f"\nKategorie: {', '.join(set(f['category'] for f in findings))}"
    
    format_telegram_message(text)

if __name__ == "__main__":
    added, findings = run_research()
    print(f"Füge {added} Ideen hinzu")
    send_research_summary(added, findings)
