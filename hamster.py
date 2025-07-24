from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def extract_m3u8(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(url, headers=headers).text
    match = re.search(r'"(https://.*?\.m3u8.*?)"', html)
    return match.group(1).replace("\\", "") if match else None

@app.route('/search', methods=['GET'])
def search_xhamster_with_video():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    headers = {"User-Agent": "Mozilla/5.0"}
    search_url = f"https://xhamster.com/search/{query.replace(' ', '%20')}"
    res = requests.get(search_url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')

    results = []
    for video in soup.select('div.video-thumb')[:5]:  # প্রথম ৫টা ভিডিও
        tag = video.select_one('.video-thumb-info__name a')
        if not tag: continue

        title = tag.get_text(strip=True)
        video_url = "https://xhamster.com" + tag['href']
        m3u8 = extract_m3u8(video_url)

        if m3u8:
            results.append({
                "title": title,
                "url": video_url,
                "stream": m3u8
            })

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
