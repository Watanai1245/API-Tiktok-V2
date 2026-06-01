import re
import json
import requests
from datetime import datetime, timezone
from flask import request, jsonify
from api.video import resolve_short_url, extract_video_id


def date_route():
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

        match = re.search(
            r'<script[^>]+id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
            r.text,
            re.DOTALL
        )

        if not match:
            return jsonify({"success": False, "error": "Rehydration data not found"}), 500

        data = json.loads(match.group(1))
        item = data["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]
        posted_at = datetime.fromtimestamp(int(item["createTime"]), tz=timezone.utc).strftime("%d/%m/%Y")

        return jsonify({
            "success": True,
            "video_id": video_id,
            "posted_at": posted_at
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
