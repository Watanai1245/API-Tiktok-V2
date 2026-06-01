// ======================================
// ใช้ในชีต: =GET_TIKTOK_VIDEO_STATS_V2(A2)
// คืนค่า 7 คอลัมน์: Reach, Engagement, Views, Reaction, Comment, Share, Save
// ======================================

var API_BASE_VIDEO = "https://api-tiktok-v2.vercel.app";

function _cacheGet_video_(key) {
  return CacheService.getScriptCache().get(key);
}

function _cachePut_video_(key, value, ttl) {
  CacheService.getScriptCache().put(key, value, ttl);
}

function _backoffFetch_video_(url, options, maxRetries) {
  var delay = 500;
  for (var i = 0; i < maxRetries; i++) {
    try {
      var resp = UrlFetchApp.fetch(url, options);
      if (resp.getResponseCode() !== 429) return resp;
      Utilities.sleep(delay);
      delay *= 2;
    } catch (e) {
      if (i === maxRetries - 1) throw e;
      Utilities.sleep(delay);
      delay *= 2;
    }
  }
}

function GET_TIKTOK_VIDEO_STATS_V2(videoUrl) {
  if (!videoUrl) return [["", "", "", "", "", "", ""]];

  var cacheKey = "video::" + String(videoUrl).trim();
  var cached = _cacheGet_video_(cacheKey);
  if (cached !== null) return [JSON.parse(cached)];

  var url = API_BASE_VIDEO + "/api/video?url=" + encodeURIComponent(videoUrl);

  try {
    var resp = _backoffFetch_video_(url, { method: "get", muteHttpExceptions: true }, 3);
    if (resp.getResponseCode() !== 200) return [["", "", "", "", "", "", ""]];

    var data = JSON.parse(resp.getContentText());

    if (data && data.success) {
      var result = [
        Number(data.estimated_reach) || 0,
        Number(data.engagement)      || 0,
        Number(data.view)            || 0,
        Number(data.like)            || 0,
        Number(data.comment)         || 0,
        Number(data.share)           || 0,
        Number(data.save)            || 0
      ];
      _cachePut_video_(cacheKey, JSON.stringify(result), 600);
      return [result];
    }

    return [["", "", "", "", "", "", ""]];
  } catch (e) {
    return [["", "", "", "", "", "", ""]];
  }
}
