from flask import Flask
from api.followers import followers_route
from api.video import video_route
from api.date import date_route
from api.avatar import avatar_route

app = Flask(__name__)

app.add_url_rule("/api/followers", view_func=followers_route, endpoint="followers_v1")
app.add_url_rule("/api/v2/followers", view_func=followers_route, endpoint="followers_v2")
app.add_url_rule("/api/video", view_func=video_route, endpoint="video_v1")
app.add_url_rule("/api/v2/video", view_func=video_route, endpoint="video_v2")
app.add_url_rule("/api/date", view_func=date_route, endpoint="date_v1")
app.add_url_rule("/api/v2/date", view_func=date_route, endpoint="date_v2")
app.add_url_rule("/api/avatar", view_func=avatar_route, endpoint="avatar_v1")
app.add_url_rule("/api/v2/avatar", view_func=avatar_route, endpoint="avatar_v2")

@app.get("/")
def home():
    return {"status": "API running"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)