
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ----------------------------
# 🔐 CLÉS API À REMPLIR CI-DESSOUS
# ----------------------------
RIJKS_KEY = "oYaDp2WS"
HARVARD_KEY = "bfb9265c-d4cf-442c-9c5c-77707503d4b0"
EUROPEANA_KEY = "dintiprefrep"
# ----------------------------

# 🎨 Art Institute of Chicago
def fetch_artic(query):
    try:
        url = f"https://api.artic.edu/api/v1/artworks/search?q={query}"
        res = requests.get(url).json()
        return [{
            "title": art.get("title"),
            "artist": art.get("artist_display"),
            "source": "Art Institute of Chicago",
            "image_url": f"https://www.artic.edu/iiif/2/{art.get('image_id')}/full/843,/0/default.jpg"
        } for art in res.get("data", [])[:3] if art.get("image_id")]
    except:
        return []

# 🖼️ Rijksmuseum
def fetch_rijks(query):
    try:
        url = f"https://www.rijksmuseum.nl/api/en/collection?key={RIJKS_KEY}&q={query}&imgonly=True"
        res = requests.get(url).json()
        return [{
            "title": art.get("title"),
            "artist": art.get("principalOrFirstMaker"),
            "source": "Rijksmuseum",
            "image_url": art.get("webImage", {}).get("url")
        } for art in res.get("artObjects", [])[:3]]
    except:
        return []

# 🧠 Harvard Art Museums
def fetch_harvard(query):
    try:
        url = f"https://api.harvardartmuseums.org/object?q={query}&size=3&apikey={HARVARD_KEY}"
        res = requests.get(url).json()
        return [{
            "title": art.get("title"),
            "artist": art.get("people", [{}])[0].get("name", "Unknown"),
            "source": "Harvard Art Museums",
            "image_url": art.get("primaryimageurl")
        } for art in res.get("records", [])]
    except:
        return []

# 🎨 WikiArt (JSON statique)
def fetch_wikiart(style):
    try:
        url = "https://raw.githubusercontent.com/mesozoic/wikiart-stats/master/style-artists.json"
        res = requests.get(url).json()
        for item in res:
            if style.lower() in item["styleName"].lower():
                return [{
                    "title": f"Works by {artist}",
                    "artist": artist,
                    "source": "WikiArt",
                    "image_url": None
                } for artist in item["artists"][:3]]
        return []
    except:
        return []

# 🌍 Europeana
def fetch_europeana(query):
    try:
        url = f"https://api.europeana.eu/record/v2/search.json?wskey={EUROPEANA_KEY}&query={query}&rows=3"
        res = requests.get(url).json()
        return [{
            "title": item.get("title", ["Untitled"])[0],
            "artist": item.get("dataProvider", "Unknown"),
            "source": "Europeana",
            "image_url": item.get("edmIsShownBy")
        } for item in res.get("items", [])]
    except:
        return []

# 🖼️ MET Museum (Open Access)
def fetch_met(query):
    try:
        search = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={query}").json()
        objectIDs = search.get("objectIDs", [])[:3]
        results = []
        for oid in objectIDs:
            art = requests.get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{oid}").json()
            results.append({
                "title": art.get("title"),
                "artist": art.get("artistDisplayName"),
                "source": "MET Museum",
                "image_url": art.get("primaryImageSmall")
            })
        return results
    except:
        return []

# 📚 Wikipedia summary
def fetch_wikipedia_summary(query):
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
        res = requests.get(url).json()
        return res.get("extract", "No summary available.")
    except:
        return "Wikipedia summary unavailable."

# 🎨 Colormind Palette Generator
def fetch_colormind():
    try:
        res = requests.post("http://colormind.io/api/", json={"model": "default"}).json()
        return ["rgb" + str(tuple(c)) for c in res.get("result", [])]
    except:
        return []

# 🧠 DBpedia (RDF Lookup)
def fetch_dbpedia_info(query):
    try:
        url = f"http://dbpedia.org/data/{query.replace(' ', '_')}.json"
        res = requests.get(url).json()
        desc_key = f"http://dbpedia.org/resource/{query.replace(' ', '_')}"
        abstract = res.get(desc_key, {}).get("http://dbpedia.org/ontology/abstract", [])
        for entry in abstract:
            if entry.get("lang") == "en":
                return entry.get("value")
        return "No DBpedia data found."
    except:
        return "DBpedia fetch failed."

# 🌐 MAIN ROUTE
@app.route("/analyze_artworks_and_generate_prompt", methods=["POST"])
def analyze():
    data = request.json
    query = data.get("style", "") or data.get("artist", "") or data.get("period", "")
    results = (
        fetch_artic(query) +
        fetch_rijks(query) +
        fetch_harvard(query) +
        fetch_wikiart(query) +
        fetch_europeana(query) +
        fetch_met(query)
    )

    return jsonify({
        "summary": fetch_wikipedia_summary(query),
        "dbpedia": fetch_dbpedia_info(query),
        "palette": fetch_colormind(),
        "artworks": results
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
