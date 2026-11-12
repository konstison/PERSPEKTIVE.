import os
import json
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from google import genai
from google.genai import types

api_key = os.environ.get("GEMINI_API_KEY")
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "53810350049")

client = genai.Client(
    api_key=api_key,
    vertexai=True,
    project=project_id,
    location="us-central1"
)
MODEL_NAME = "gemini-2.5-flash"

RSS_FEEDS = [
    {"name": "Tagesschau", "land": "Deutschland", "url": "https://www.tagesschau.de/xml/rss2/"},
    {"name": "Deutschlandfunk", "land": "Deutschland", "url": "https://www.deutschlandfunk.de/nachrichten-100.rss"},
    {"name": "Neue Zürcher Zeitung", "land": "Schweiz", "url": "https://www.nzz.ch/recent.rss"},
    {"name": "The Guardian", "land": "Großbritannien", "url": "https://www.theguardian.com/world/rss"},
    {"name": "FAZ Aktuell", "land": "Deutschland", "url": "https://www.faz.net/rss/aktuell/"}
]

def fetch_rss_headlines(limit_per_feed=15):
    print("1. Lese offene RSS-Feeds...")
    items = []
    for feed in RSS_FEEDS:
        try:
            req = urllib.request.Request(feed["url"], headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                xml_data = resp.read()
            root = ET.fromstring(xml_data)
            entries = root.findall(".//item")
            if not entries:
                entries = root.findall("{http://www.w3.org/2005/Atom}entry")
                
            for item in entries[:limit_per_feed]:
                title_el = item.find("title")
                desc_el = item.find("description")
                if desc_el is None:
                    desc_el = item.find("{http://www.w3.org/2005/Atom}summary")
                link_el = item.find("link")
                
                title = (title_el.text if title_el is not None and title_el.text else "").strip()
                desc = (desc_el.text if desc_el is not None and desc_el.text else "").strip()
                link = link_el.text if link_el is not None and link_el.text else ""
                if not link and link_el is not None:
                    link = link_el.attrib.get("href", "")
                
                if title and link:
                    items.append({
                        "medium": feed["name"],
                        "land": feed["land"],
                        "titel": title,
                        "kurztext": desc[:400],
                        "url": link.strip()
                    })
        except Exception as e:
            print(f"Warnung bei Feed {feed['name']}: {e}")
    print(f"-> {len(items)} Meldungen geladen.")
    return items

def fetch_wikimedia_image(search_query):
    try:
        encoded = urllib.parse.quote(search_query)
        api_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=filetype:bitmap+{encoded}&gsrnamespace=6&gsrlimit=1&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=1280&format=json"
        req = urllib.request.Request(api_url, headers={"User-Agent": "PerspektiveNewspaper/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]
            thumb = info.get("thumburl")
            if thumb:
                return {
                    "url": thumb,
                    "beschreibung": f"Dokumentaraufnahme zum Thema: {search_query}",
                    "lizenz": "Foto: Wikimedia Commons"
                }
    except Exception as e:
        print(f"Bildsuche-Fehler: {e}")
    return {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Abu_Dhabi_skyline_from_Marina_Mall.jpg/1280px-Abu_Dhabi_skyline_from_Marina_Mall.jpg",
        "beschreibung": "Archivaufnahme",
        "lizenz": "Foto: Wikimedia Commons"
    }

def cluster_top_5_topics(rss_items):
    print("2. Wähle die 5 relevantesten DACH/Welt-Themen...")
    prompt = f"""
    Du bist Chefredakteur einer anspruchsvollen deutschen Tageszeitung (Stil: NZZ / FAZ).
    Wähle exakt 5 herausragende Themen aus den folgenden Meldungen aus.
    Liefere ein reines JSON-Array mit 5 Objekten:
    [
      {{
        "rubrik": "Geopolitik & Europa",
        "arbeitstitel": "Titel",
        "bild_suchbegriff": "Berlin",
        "relevante_quellen_indizes": [0, 1]
      }}
    ]
    Meldungen: {json.dumps(rss_items[:30], ensure_ascii=False)}
    """
    resp = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(resp.text)

def generate_deep_essay(topic, sources):
    essay_prompt = f"""
    Schreibe einen hocheloquenten Langform-Essay (ca. 1000 Wörter) zum Thema: {topic['arbeitstitel']}
    Liefere die Antwort als reines JSON:
    {{
      "titel": "Schlagzeile",
      "untertitel": "Untertitel",
      "leitthese": "Leitthese in 2 Sätzen.",
      "historische_anker": {{
        "key1": {{"titel": "Historischer Bezug", "text": "Erläuterung in 3 Sätzen."}}
      }},
      "inhalt_html": "<p>Absatz 1...</p><h2>I. Kapitel</h2><p>Absatz 2...</p>",
      "weltspiegel": [
        {{"medium": "Le Monde", "tenor": "Analytisch", "zusammenfassung": "Zusammenfassung.", "url": "https://www.lemonde.fr"}}
      ]
    }}
    Quellen: {json.dumps(sources, ensure_ascii=False)}
    """
    resp = client.models.generate_content(
        model=MODEL_NAME,
        contents=essay_prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(resp.text)

def main():
    rss_items = fetch_rss_headlines()
    if not rss_items:
        return
    topics = cluster_top_5_topics(rss_items)
    time.sleep(2)

    fertige_artikel = []
    for idx, topic in enumerate(topics[:5], start=1):
        print(f"Schreibe Essay {idx}/5...")
        src_subset = [rss_items[i] for i in topic.get("relevante_quellen_indizes", [0]) if i < len(rss_items)]
        if not src_subset:
            src_subset = rss_items[:2]

        essay_data = generate_deep_essay(topic, src_subset)
        bild = fetch_wikimedia_image(topic.get("bild_suchbegriff", "Berlin"))
        
        fertige_artikel.append({
            "id": f"essay-{idx}",
            "rubrik": topic.get("rubrik", "Zeitgeschehen"),
            "lesezeit": "12 Min. Lesezeit",
            "titel": essay_data.get("titel", topic["arbeitstitel"]),
            "untertitel": essay_data.get("untertitel", ""),
            "leitthese": essay_data.get("leitthese", ""),
            "bild": bild,
            "historische_anker": essay_data.get("historische_anker", {}),
            "inhalt_html": essay_data.get("inhalt_html", "<p>Inhalt wird geladen...</p>"),
            "weltspiegel": essay_data.get("weltspiegel", [])
        })
        time.sleep(2)

    os.makedirs("data", exist_ok=True)
    ausgabe = {
        "datum": datetime.now().strftime("%A, %d. %B %Y").replace("Monday", "Montag").replace("Tuesday", "Dienstag").replace("Wednesday", "Mittwoch").replace("Thursday", "Donnerstag").replace("Friday", "Freitag").replace("Saturday", "Samstag").replace("Sunday", "Sonntag"),
        "ausgabe_nr": "1",
        "artikel": fertige_artikel
    }
    with open("data/ausgabe.json", "w", encoding="utf-8") as f:
        json.dump(ausgabe, f, ensure_ascii=False, indent=2)
    print("Fertig!")

if __name__ == "__main__":
    main()
