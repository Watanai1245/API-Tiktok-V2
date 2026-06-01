import re
import json
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from flask import request, jsonify


def extract_video_id(value):
    if value.isdigit():
        return value

    match = re.search(r"/video/(\d+)", value)
    return match.group(1) if match else None

def resolve_short_url(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=10)
        return r.url
    except requests.RequestException:
        return url

def get_video_stats():

    value = request.args.get("url")

    if not value:
        return jsonify({"success": False, "error": "url is required"}), 400

    try:
        if "vt.tiktok.com" in value:
            value = resolve_short_url(value)

        video_id = extract_video_id(value)

        if not video_id:
            return jsonify({"success": False, "error": "Invalid video URL"}), 400

        video_url = f"https://www.tiktok.com/video/{video_id}" if value.isdigit() else value

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.tiktok.com/"
        }

        r = requests.get(video_url, headers=headers, timeout=10)

        if r.status_code != 200:
            return jsonify({"success": False, "error": "Failed to fetch page"}), 500

        soup = BeautifulSoup(r.text, "html.parser")
        script_tag = soup.find("script", id="__UNIVERSAL_DATA_FOR_REHYDRATION__")

        if not script_tag:
            return jsonify({"success": False, "error": "Rehydration data not found"}), 500

        data = json.loads(script_tag.string)

        item = data["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]
        stats = item["stats"]

        posted_at = datetime.fromtimestamp(int(item["createTime"]), tz=timezone.utc).strftime("%d/%m/%Y")

        like = stats["diggCount"]
        comment = stats["commentCount"]
        share = stats["shareCount"]
        save = int(stats["collectCount"])

        return jsonify({
            "success": True,
            "video_id": video_id,
            "author": item["author"]["uniqueId"],
            "posted_at": posted_at,
            "view": stats["playCount"],
            "estimated_reach": int(stats["playCount"] / 1.5),
            "engagement": like + comment + share + save,
            "like": like,
            "comment": comment,
            "share": share,
            "save": save
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def video_route():
    return get_video_stats()
