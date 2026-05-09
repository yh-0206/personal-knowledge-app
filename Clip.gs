function clipUrl(message, userId) {
  const urlMatch = message.match(/https?:\/\/[^\s]+/);

  if (!urlMatch) {
    replyToLine(userId, 'URLが見つかりません。');
    return;
  }

  const url = urlMatch[0];
  const pageText = fetchPageText(url);

  if (!pageText) {
    replyToLine(userId, '⚠️ URLの内容を取得できませんでした。');
    return;
  }

  const summary = summarizeText(pageText);
  const savedAt = getCurrentDateTime();
  const title = extractTitle(pageText);

  const values = [savedAt, url, title, summary];
  appendRow('クリップ', values);

  const message_response = '✂️ URLをクリップしました。\n\n【要約】\n' + summary;
  replyToLine(userId, message_response);
}

function fetchPageText(url) {
  try {
    const response = UrlFetchApp.fetch(url, {
      muteHttpExceptions: true,
      followRedirects: true,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });

    if (response.getResponseCode() !== 200) {
      return null;
    }

    const html = response.getContentText();
    const text = extractTextFromHtml(html);

    return text.substring(0, 2000);
  } catch (e) {
    Logger.log('Error fetching URL: ' + e);
    return null;
  }
}

function extractTextFromHtml(html) {
  let text = html;

  text = text.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '');
  text = text.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '');
  text = text.replace(/<[^>]+>/g, ' ');
  text = text.replace(/\s+/g, ' ');

  return text.trim();
}

function extractTitle(html) {
  const titleMatch = html.match(/<title[^>]*>([^<]+)<\/title>/i);
  if (titleMatch && titleMatch[1]) {
    return titleMatch[1].substring(0, 100);
  }

  const ogMatch = html.match(/<meta\s+property="og:title"\s+content="([^"]+)"/i);
  if (ogMatch && ogMatch[1]) {
    return ogMatch[1].substring(0, 100);
  }

  return 'タイトル取得不可';
}
