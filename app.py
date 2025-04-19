from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/analyze_artworks_and_generate_prompt', methods=['POST'])
def analyze_artworks():
    data = request.json
    style = data.get('style', '')
    artist = data.get('artist', '')
    period = data.get('period', '')
    subject = data.get('main_subject', '')
    environment = data.get('environment', '')
    format_ = data.get('format', '')

    aic_url = f"https://api.artic.edu/api/v1/artworks/search?q={style or artist or period}"
    aic_response = requests.get(aic_url).json()
    aic_results = aic_response.get('data', [])[:2]

    artworks = []
    for art in aic_results:
        artworks.append({
            "title": art.get('title', 'Untitled'),
            "artist": art.get('artist_display', 'Unknown'),
            "source": "Art Institute of Chicago",
            "image_url": f"https://www.artic.edu/iiif/2/{art.get('image_id')}/full/843,/0/default.jpg"
            if art.get('image_id') else None
        })

    influences = {
        "style": style,
        "color_palette": ["gold", "blue", "pastel green"],
        "common_motifs": ["decorative patterns", "natural elements", "symbolism"],
        "mood": "dreamy and elegant",
        "techniques": ["layered texture", "soft lighting"]
    }

    return jsonify({
        "influences": influences,
        "reference_artworks": artworks
    })

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
