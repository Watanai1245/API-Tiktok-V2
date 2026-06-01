// ======================================
// ใช้ในชีต: =GET_TIKTOK_FOLLOWERS(A2)
// คืนค่า: จำนวน followers (integer)
// ======================================

var API_BASE_FOLLOWERS = "https://api-tiktok-v2.vercel.app";

function _cacheGet_followers_(key) {
  return CacheService.getScriptCache().get(key);
}

function _cachePut_followers_(key, value, ttl) {
  CacheService.getScriptCache().put(key, value, ttl);
}

function _backoffFetch_followers_(url, options, maxRetries) {
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

function GET_TIKTOK_FOLLOWERS(username) {
  if (!username) return "";

  username = String(username).trim().replace(/^@/, "");
  var cacheKey = "followers::" + username.toLowerCase();

  var cached = _cacheGet_followers_(cacheKey);
  if (cached !== null) return Number(cached);

  var url = API_BASE_FOLLOWERS + "/api/followers?username=" + encodeURIComponent(username);
  var resp = _backoffFetch_followers_(url, { method: "get", muteHttpExceptions: true }, 3);

  if (resp.getResponseCode() !== 200) return "";

  try {
    var data = JSON.parse(resp.getContentText());

    if (data && data.success && typeof data.followers_int === "number") {
      _cachePut_followers_(cacheKey, String(data.followers_int), 600);
      return data.followers_int;
    }

    return "";
  } catch (e) {
    return "";
  }
}
