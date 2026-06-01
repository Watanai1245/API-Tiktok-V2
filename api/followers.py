import re, json, random, requests
from flask import request, jsonify

def followers_route():
    username = (request.args.get("username") or "").strip().lstrip("@")

    if not username:
        return jsonify({"success": False, "error": "username required"}), 400

    result = fetch_followers(username)

    return jsonify(result)

def fetch_followers(username):
    url = f"https://www.tiktok.com/@{username}?lang=en"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    cookies = {
        "tt_webid_v2": ''.join(random.choices('0123456789', k=19))
    }

    try:
        r = requests.get(url, headers=headers, cookies=cookies, timeout=15)
    except requests.RequestException as e:
        return {"success": False, "error": f"Network error: {e}"}

    if r.status_code != 200:
        return {"success": False, "status_code": r.status_code}

    match = re.search(
        r'<script[^>]+id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
        r.text,
        re.DOTALL
    )

    if not match:
        return {"success": False, "error": "TikTok JSON not found (possibly blocked)"}

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON parse error: {e}"}

    try:
        user_data = (
            data["__DEFAULT_SCOPE__"]
            ["webapp.user-detail"]
            ["userInfo"]
        )

        stats = user_data.get("stats") or user_data.get("user", {}).get("stats")

        return {
            "success": True,
            "username": username,
            "followers_int": stats["followerCount"],
            "following_int": stats["followingCount"],
            "likes_int": stats["heartCount"],
            "video_count": stats["videoCount"]
        }

    except Exception as e:
        return {"success": False, "error": f"Parse error: {e}"}
