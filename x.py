from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Please provide a search query using ?q='}), 400

    url = f'https://xhamster.com/search/{query.replace(" ", "%20")}'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    videos = []

    for tag in soup.select('div.video-thumb-info-wrapper'):
        title_tag = tag.select_one('a.video-thumb-info__name')
        if not title_tag:
            continue

        title = title_tag.text.strip()
        video_url = 'https://xhamster.com' + title_tag['href']

        # get the actual video URL
        video_page = requests.get(video_url, headers=headers)
        video_soup = BeautifulSoup(video_page.text, 'html.parser')

        script_tag = video_soup.find('script', string=lambda s: s and 'sources' in s)
        if not script_tag:
            continue

        try:
            import re, json
            match = re.search(r'sources:\s*(\[[^\]]+\])', script_tag.string)
            if match:
                sources_json = match.group(1).replace("'", '"')
                sources = json.loads(sources_json)
                video_file = sources[0].get('src', '')

                videos.append({
                    'title': title,
                    'page': video_url,
                    'video': video_file
                })
        except:
            continue

        if len(videos) >= 5:
            break

    return jsonify(videos)

if __name__ == '__main__':
    app.run(debug=True)
