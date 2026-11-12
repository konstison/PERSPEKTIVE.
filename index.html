import os
import json
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from google import genai
from google.genai import types

# Initialisiert den kostenlosen Gemini-Client über die Umgebungsvariable GEMINI_API_KEY
client = genai.Client()
MODEL_NAME = "gemini-2.5-flash"  # Im Google AI Studio Free Tier kostenlos nutzbar

RSS_FEEDS = [
    {"name": "Tagesschau", "land": "Deutschland", "url": "https://www.tagesschau.de/xml/rss2/"},
    {"name": "Deutschlandfunk", "land": "Deutschland", "url": "https://www.deutschlandfunk.de/nachrichten-100.rss"},
    {"name": "Neue Zürcher Zeitung", "land": "Schweiz", "url": "https://www.nzz.ch/recent.rss"},
    {"name": "The Guardian", "land": "Großbritannien", "url": "https://www.theguardian.com/world/rss"},
    {"name": "FAZ Aktuell", "land": "Deutschland", "url": "https://www.faz.net/rss/aktuell/"}
]


def fetch_rss_headlines(limit_per_feed=12):
    """Liest aktuelle Schlagzeilen und Kurzbeschreibungen aus offenen RSS-Feeds."""
    items = []
    for feed in RSS_FEEDS:
        try:
            req = urllib.request.Request(feed["url"], headers={"User-Agent": "PerspektiveBot/1.0"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                xml_data = resp.read()
            root = ET.fromstring(xml_data)
            for item in root.findall(".//item")[:limit_per_feed]:
                title = (item.findtext("title") or "").strip()
                desc = (item.findtext("description") or "").strip()
                link = (item.findtext("link") or "").strip()
                if title and link:
                    items.append({
                        "medium": feed["name"],
                        "land": feed["land"],
                        "titel": title,
                        "kurztext": desc[:350],
                        "url": link
                    })
        except Exception as e:
            print(f"Warnung bei Feed {feed['name']}: {e}")
    return items


def fetch_wikimedia_image(search_query):
    """Sucht ein lizenzfreies Bild auf Wikimedia Commons inkl. automatischem Lizenzhinweis."""
    try:
        encoded = urllib.parse.quote(search_query)
        api_url = (
            f"https://commons.wikimedia.org/w/api.php?action=query&generator=search"
            f"&gsrsearch=filetype:bitmap+{encoded}&gsrnamespace=6&gsrlimit=3"
            f"&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=1280&format=json"
        )
        req = urllib.request.Request(api_url, headers={"User-Agent": "PerspektiveNewspaper/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]
            thumb = info.get("thumburl")
            meta = info.get("extmetadata", {})
            license_short = meta.get("LicenseShortName", {}).get("value", "Wikimedia Commons")
            if thumb and ("CC" in license_short or "Public domain" in license_short):
                return {
                    "url": thumb,
                    "beschreibung": f"Archivaufnahme zum Themenfeld: {search_query}",
                    "lizenz": f"Foto: Wikimedia Commons ({license_short})"
                }
    except Exception as e:
        print(f"Bildsuche fehlgeschlagen für '{search_query}': {e}")
    return None


def check_copyright_overlap(generated_text, source_items, n=8):
    """Prüft, ob eine Wortfolge von >= n Wörtern wörtlich aus den Quellen übernommen wurde."""
    clean_gen = " ".join(generated_text.lower().split())
    for src in source_items:
        src_words = src["kurztext"].lower().split()
        if len(src_words) < n:
            continue
        for i in range(len(src_words) - n + 1):
            phrase = " ".join(src_words[i:i + n])
            if phrase in clean_gen:
                return False, phrase
    return True, None


def cluster_top_5_topics(rss_items):
    """Wählt die 5 wichtigsten Themen mit Relevanz für Deutschland/DACH aus."""
    prompt = f"""
    Du bist Chefredakteur einer anspruchsvollen deutschen Tageszeitung (Stil: NZZ / Die Zeit / FAZ).
    Analysiere die folgenden aktuellen RSS-Meldungen und wähle exakt 5 herausragende Themen aus,
    die für den deutschsprachigen Leseraum (Deutschland/Europa) heute von höchster strategischer,
    gesellschaftlicher, wirtschaftlicher oder geopolitischer Bedeutung sind.

    Liefere ein reines JSON-Array mit 5 Objekten:
    [
      {{
        "rubrik": "z.B. Geopolitik & Europa / Wirtschaft & Ordnung / Staat & Gesellschaft / Wissenschaft & Zukunft",
        "arbeitstitel": "Prägnantes Thema",
        "bild_suchbegriff": "Englischer Suchbegriff für Wikimedia Commons (z.B. 'European Central Bank Frankfurt' oder 'Bundestag Berlin')",
        "relevante_quellen_indizes": [0, 3, 14]
      }}
    ]

    Meldungen:
    {json.dumps(rss_items, ensure_ascii=False)}
    """
    resp = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(resp.text)


def generate_deep_essay(topic, sources):
    """Erzeugt in verketteten Schritten einen tiefen 1.500-2.000 Wörter Essay inkl. historischer Anker."""
    # Schritt 1: Fakten-Tresor (striktes Abstandsgebot zum Quellentext)
    facts_prompt = f"""
    Extrahiere aus diesen Meldungen ausschließlich neutrale Fakten, Daten, Akteure und
    die Positionen der einzelnen Medien (in eigenen Worten, keine langen Zitate).
    Thema: {topic['arbeitstitel']}
    Quellen: {json.dumps(sources, ensure_ascii=False)}
    """
    facts = client.models.generate_content(model=MODEL_NAME, contents=facts_prompt).text
    time.sleep(4)  # Schont die kostenlosen Rate-Limits

    # Schritt 2: Essay-Schmiede (1.600 - 2.000 Wörter Langform)
    essay_prompt = f"""
    Schreibe einen hoch-eloquenten, akademisch-journalistischen Langform-Essay (Zielumfang: 1.600 bis 2.000 Wörter,
    ca. 15 Minuten Lesezeit) für eine deutsche Qualitätszeitung.

    STIL-REGELN:
    - Keine KI-Floskeln ("In einer Welt voller...", "Zusammenfassend lässt sich sagen", "Es bleibt abzuwarten").
    - Einstieg über eine präzise politische/historische Szene oder Beobachtung.
    - Gliedere den Text mit 3 bis 4 römisch nummerierten Zwischenüberschriften (<h2>I. ...</h2>, <h2>II. ...</h2>).
    - Stelle tiefe strukturelle Zusammenhänge her: Warum handeln die Akteure so? Welche historischen Linien
      (z.B. 19. Jahrhundert, Nachkriegsordnung, Wendejahre) wiederholen oder brechen sich hier?
    - Arbeite exakt 2 historische Vergleichsbegriffe mit <span class="history-anchor" onclick="showHistory('anker1')">Begriff</span>
      in den Fließtext ein und definiere sie im JSON-Feld "historische_anker".
    - Widme das letzte Kapitel explizit den Konsequenzen für Deutschland und Europa.
    - Erstelle unter "weltspiegel" zu jeder Quelle eine eigene, urheberrechtlich saubere 2-Satz-Zusammenfassung.

    Gib das Ergebnis als valides JSON zurück:
    {{
      "titel": "Konzeptuelle Doppelpunkt-Schlagzeile (z.B. Anatomie einer Illusion: Warum...)",
      "untertitel": "Zweizeiliger, analytischer Untertitel",
      "leitthese": "Prägnante Kernthese in 1-2 Sätzen für die Marginalie",
      "historische_anker": {{
        "anker1": {{"titel": "Historisches Ereignis (Jahr)", "text": "Erklärung der Parallele in 3 Sätzen."}},
        "anker2": {{"titel": "Zweites Ereignis (Jahr)", "text": "Erklärung der Parallele in 3 Sätzen."}}
      }},
      "inhalt_html": "<p>Vollständiger Essay mit <p>, <h2> und <blockquote>...</p>",
      "weltspiegel": [
        {{"medium": "Name (Land)", "tenor": "Kurze Tonfall-Einordnung", "zusammenfassung": "Eigene Zusammenfassung", "url": "Link"}}
      ]
    }}

    Faktenbasis:
    {facts}
    Quellen-Links:
    {json.dumps(sources, ensure_ascii=False)}
    """
    resp = client.models.generate_content(
        model=MODEL_NAME,
        contents=essay_prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(resp.text)


def main():
    print("1. Lese offene RSS-Feeds...")
    rss_items = fetch_rss_headlines()
    print(f"   {len(rss_items)} Meldungen geladen.")

    print("2. Wähle die 5 relevantesten DACH/Welt-Themen...")
    topics = cluster_top_5_topics(rss_items)
    time.sleep(4)

    fertige_artikel = []
    for idx, topic in enumerate(topics[:5], start=1):
        print(f"3.{idx} Schreibe Essay: {topic['arbeitstitel']}...")
        src_subset = [rss_items[i] for i in topic.get("relevante_quellen_indizes", []) if i < len(rss_items)]
        if not src_subset:
            src_subset = rss_items[:3]

        essay_data = generate_deep_essay(topic, src_subset)
        ok, overlap = check_copyright_overlap(essay_data["inhalt_html"], src_subset)
        if not ok:
            print(f"   Hinweis: Überlappung entdeckt ('{overlap}'), regeneriere...")
            time.sleep(4)
            essay_data = generate_deep_essay(topic, src_subset)

        bild = fetch_wikimedia_image(topic.get("bild_suchbegriff", "Berlin Reichstag"))
        word_count = len(essay_data["inhalt_html"].split())
        lesezeit = f"{max(10, round(word_count / 130))} Min. Lesezeit"

        fertige_artikel.append({
            "id": f"artikel-{idx}",
            "rubrik": topic["rubrik"],
            "lesezeit": lesezeit,
            "titel": essay_data["titel"],
            "untertitel": essay_data["untertitel"],
            "leitthese": essay_data["leitthese"],
            "bild": bild,
            "historische_anker": essay_data.get("historische_anker", {}),
            "inhalt_html": essay_data["inhalt_html"],
            "weltspiegel": essay_data.get("weltspiegel", [])
        })
        time.sleep(5)

    os.makedirs("data", exist_ok=True)
    ausgabe = {
        "datum": datetime.now().strftime("%d.%m.%Y"),
        "ausgabe_nr": str((datetime.now() - datetime(2026, 1, 1)).days + 1),
        "artikel": fertige_artikel
    }
    with open("data/ausgabe.json", "w", encoding="utf-8") as f:
        json.dump(ausgabe, f, ensure_ascii=False, indent=2)
    print("Fertig! data/ausgabe.json wurde aktualisiert.")


if __name__ == "__main__":
    main()
