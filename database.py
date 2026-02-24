"""
Idea Tracker - Database Module
Stores business ideas and research findings
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "ideas.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            problem TEXT NOT NULL,
            description TEXT,
            existing_solutions TEXT,
            source TEXT,
            category TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            research_notes TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS research_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_term TEXT,
            source TEXT,
            findings TEXT,
            researched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if we need to add initial data
    c.execute('SELECT COUNT(*) as count FROM ideas')
    if c.fetchone()[0] == 0:
        # Add ideas from real web research
        initial_ideas = [
            ('Musik-Bibliothek Bereiniger', 'Musiksammlungen sind unorganisiert und haben Duplikate', 'App die Musik automatisch sortiert, Duplike findet und fehlende Metadaten ergänzt', 'Tunes, MusicBrainz, Soundiiz', 'Web Research', 'productivity'),
            ('Weiterbildungs-Tracker', 'Keine einfache Übersicht über Zertifizierungen und Fortbildungen', 'Tool um berufliche Weiterbildung zu tracken mit Erinnerungen an Verlängerungen', 'LinkedIn Learning, Coursera', 'Web Research', 'education'),
            ('Familien-Online-Sicherheit', 'Eltern wollen wissen was ihre Kinder online machen, ohne privacy zu verletzen', 'App die Online-Aktivitäten überwacht aber nicht intrusiv ist', 'Bark, Qustodio, Google Family Link', 'Web Research', 'security'),
            ('Vereinfachte ROM-Installation', 'Custom Android ROMs zu installieren ist zu kompliziert für normale Nutzer', 'App die ROM-Installation so einfach macht wie eine normale App zu installieren', 'ODIN, Fastboot, ADB', 'Web Research', 'tech'),
            ('Unified Messaging Hub', 'Zu viele verschiedene Messenger Apps', 'Eine App die SMS, WhatsApp, Telegram, Messenger zentral vereint', 'Pulse, Disa', 'Web Research', 'communication'),
            ('Automatische Rechnungsstellung', 'Kleine Unternehmen verschwenden Zeit mit manuellem Rechnungswesen', 'Einfache Lösung für automatische Rechnungen, Mahnungen und Buchhaltung', 'Lexoffice, SevDesk, DATEV', 'Web Research', 'finance'),
            ('Smart Home simplified', 'Smart Home Geräte sind zu kompliziert einzurichten und zu steuern', 'Eine zentrale App die alle Smart Home Geräte einfach verbindet und steuert', 'Home Assistant, Apple HomeKit, Google Home', 'Web Research', 'lifestyle'),
            ('Automatische Post-Benachrichtigung', 'Man weiß nie was heute in der Post kommt', 'Digitale Vorschau der täglichen Post', 'USPS Informed Delivery (nur USA)', 'Web Research', 'productivity'),
            ('Lead-Management für kleine Unternehmen', 'Kleine Unternehmen haben chaotisches Verkaufs- und Lead-Management', 'Einfache, günstige CRM-Lösung ohne komplizierte Enterprise-Features', 'Salesforce, HubSpot, Pipedrive', 'Web Research', 'business'),
            ('Automatische Datensicherung', 'Backups werden vergessen oder sind kompliziert einzurichten', 'Automatische, unsichtbare Datensicherung für Normalnutzer', 'Time Machine, Backblaze, Carbonite', 'Web Research', 'tech'),
            ('Meeting-Planer für Teams', 'Meetings zu planen nimmt zu viel Zeit in Anspruch', 'Tool das automatisch freie Zeiten findet und Meetings organisiert', 'Calendly, ChiliPiper, Microsoft Bookings', 'Web Research', 'productivity'),
            ('Gesunde Essensplanung', 'Gesund zu essen ist planerisch aufwändig', 'App die automatisch Mahlzeiten plant, Einkaufslisten erstellt und Lieferungen koordiniert', 'Mealime, HelloFresh, Paprika', 'Web Research', 'health'),
            ('Social Media Aggregator', 'Zu viele verschiedene Social Media Apps und Feeds', 'App die verschiedene Social Media Feeds zentral vereint und personalisierbar macht', 'TweetDeck, Pulse, Buffer', 'Web Research', 'communication'),
            ('Self-Hosted App Store', 'Viele Apps können nicht einfach selbst gehostet werden', 'Marktplatz für einfach selbst-hostbare Apps mit One-Click-Installation', 'Sandstorm, Yunohost, CasaOS', 'Web Research', 'tech'),
            ('Fitness Krafttraining Tracker', 'Fitness-Apps sind nicht gut für Krafttraining mit Satz/Reps-Tracking', 'App die jeden Satz und jede Wiederholung trackt mit automatischer Progression', 'Strong, Hevy, JEFIT', 'Web Research', 'health'),
            ('Food Cravings Predictor', 'Man weiß nicht was man essen soll basierend auf Stimmung', 'App die basierend auf deiner Stimmung/Emotion vorschlägt was du essen solltest', 'Keine echten Alternativen', 'Web Research', 'health'),
            ('Kleine Unternehmen Integration Hub', 'CRM, Buchhaltung und Inventory Software synchronisieren nicht', 'Einfache Integrationslösung für kleine Unternehmen ohne IT-Team', 'Zapier, Make (zu kompliziert)', 'Web Research', 'business'),
            ('Automatischer Rechnungsassistent', 'Kleine Unternehmen verschwenden Zeit mit manuellen Rechnungen und Mahnungen', 'Tool für automatische Rechnungen, Mahnungen und Payment Tracking', 'Lexoffice, SevDesk (zu teuer)', 'Web Research', 'finance'),
            ('Termin-Bestätigungsautomat', 'Terminbestätigungen manuell nachverfolgen ist nervig', 'Automatische Terminbestätigungen und Erinnerungen per SMS/Email', 'Calendly (nur Buchung)', 'Web Research', 'productivity'),
            ('Datenverbrauch Monitor', 'Keine einfache Übersicht über App-Datenverbrauch', 'Tool das allen Datenverbrauch über alle Apps zentral trackt', 'Android Built-in (nicht detailliert)', 'Web Research', 'tech'),
            ('Einfache USB-Geräteverwaltung', 'USB-Geräte am Computer zu verwalten ist kompliziert', 'App die USB-Geräte einfach verwaltet und Backups ermöglicht', 'Windows Device Manager (zu kompliziert)', 'Web Research', 'tech'),
            ('Passwort-Familien-Manager', 'Passwörter mit Familie teilen ist unsicher oder kompliziert', 'Sichere, einfache Möglichkeit Passwörter mit Familienmitgliedern zu teilen', '1Password Families, LastPass (teuer)', 'Web Research', 'security'),
            ('Streaming-Abonnement-Manager', 'Man weiß nicht ob man einen Film auf Netflix, Disney+ oder Amazon hat', 'App die zeigt auf welcher Plattform ein Film/Serie verfügbar ist', 'JustWatch, Can I Stream It', 'Web Research', 'productivity'),
            ('Persönlicher Daten-Hub', 'Versicherungen, Arzt, Steuer sind nicht miteinander verbunden', 'Zentrale App die alle persönlichen Daten verbindet und automatisch Informationen teilt', 'Google Takeout, Apple Health', 'Web Research', 'lifestyle'),
            ('Einfacher Rechnungs-Tracker', 'Zu komplizierte Apps um Rechnungen zu bezahlen', 'Einfache Checkliste für Rechnungen ohne Extra-Tasten', 'Alle existierenden Apps sind zu kompliziert', 'Web Research', 'finance'),
            ('Rätsel-Ersteller', 'Es gibt keine einfache App um Kreuzworträtsel zu erstellen', 'Einfache App um Rätsel zu erstellen mit Farben und Buchstaben', 'Puzzle Maker Apps (zu kompliziert)', 'Web Research', 'education'),
            ('Besserer Lehrbuch-Reader', 'Lern-Apps sind nur Quick-Hacks die nicht funktionieren', 'Echte Lösung zum effektiven Lernen von Lehrbüchern', 'Anki, Quizlet (funktionieren nicht gut)', 'Web Research', 'education'),
            ('Plattform-Übergreifender Musik-Manager', 'Musik ist auf Spotify, Apple Music, YouTube verteilt', 'Eine App die alle Musik-Dienste zentral verwaltet', 'Soundiiz, TunemyMusic', 'Web Research', 'productivity'),
        ]
        c.executemany('INSERT INTO ideas (title, problem, description, existing_solutions, source, category) VALUES (?, ?, ?, ?, ?, ?)', initial_ideas)
    
    conn.commit()
    conn.close()

def add_idea(title, problem, description="", existing_solutions="", source="", category="", research_notes=""):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO ideas (title, problem, description, existing_solutions, source, category, research_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, problem, description, existing_solutions, source, category, research_notes))
    conn.commit()
    idea_id = c.lastrowid
    conn.close()
    return idea_id

def get_all_ideas():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM ideas ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_ideas_by_status(status):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM ideas WHERE status = ? ORDER BY created_at DESC', (status,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_idea_status(idea_id, status):
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE ideas SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (status, idea_id))
    conn.commit()
    conn.close()

def log_research(search_term, source, findings):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO research_log (search_term, source, findings) VALUES (?, ?, ?)', 
              (search_term, source, findings))
    conn.commit()
    conn.close()

def get_research_log():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM research_log ORDER BY researched_at DESC LIMIT 20')
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_categories():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT DISTINCT category FROM ideas WHERE category != ""')
    rows = c.fetchall()
    conn.close()
    return [r['category'] for r in rows if r['category']]

def get_stats():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) as total FROM ideas')
    total = c.fetchone()['total']
    
    c.execute("SELECT COUNT(*) as count FROM ideas WHERE status = 'new'")
    new_count = c.fetchone()['count']
    
    c.execute("SELECT COUNT(*) as count FROM ideas WHERE status = 'interesting'")
    interesting = c.fetchone()['count']
    
    c.execute("SELECT COUNT(*) as count FROM ideas WHERE status = 'reject'")
    rejected = c.fetchone()['count']
    
    c.execute('SELECT COUNT(*) as count FROM ideas WHERE status = "validated"')
    validated = c.fetchone()['count']
    
    conn.close()
    
    return {"total": total, "new": new_count, "interesting": interesting, "rejected": rejected, "validated": validated}

if __name__ == "__main__":
    init_db()
    print("Database initialized!")
