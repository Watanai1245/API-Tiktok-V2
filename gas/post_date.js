// ======================================
// ใช้ในชีต: =GET_TIKTOK_POST_DATE(A2)
// คืนค่า: วันที่โพสต์ในรูปแบบ DD/MM/YYYY
// ======================================

var API_BASE_DATE = "https://api-tiktok-v2.vercel.app";

function _cacheGet_date_(key) {
  return CacheService.getScriptCache().get(key);
}

function _cachePut_date_(key, value, ttl) {
  CacheService.getScriptCache().put(key, value, ttl);
}

function _backoffFetch_date_(url, options, maxRetries) {
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

function GET_TIKTOK_POST_DATE(videoUrl) {
  if (!videoUrl) return "";

  var cacheKey = "date::" + String(videoUrl).trim();
  var cached = _cacheGet_date_(cacheKey);
  if (cached !== null) return cached;

  var url = API_BASE_DATE + "/api/date?url=" + encodeURIComponent(videoUrl);

  try {
    var resp = _backoffFetch_date_(url, { method: "get", muteHttpExceptions: true }, 3);
    if (resp.getResponseCode() !== 200) return "";

    var data = JSON.parse(resp.getContentText());

    if (data && data.success && data.posted_at) {
      _cachePut_date_(cacheKey, data.posted_at, 86400);
      return data.posted_at;
    }

    return "";
  } catch (e) {
    return "";
  }
}
