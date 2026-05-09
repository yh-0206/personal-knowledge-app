const LINE_CHANNEL_ACCESS_TOKEN = PropertiesService.getScriptProperties().getProperty('LINE_CHANNEL_ACCESS_TOKEN');
const LINE_USER_ID = PropertiesService.getScriptProperties().getProperty('LINE_USER_ID');
const CLAUDE_API_KEY = PropertiesService.getScriptProperties().getProperty('CLAUDE_API_KEY');
const SPREADSHEET_ID = PropertiesService.getScriptProperties().getProperty('SPREADSHEET_ID');

function doPost(e) {
  try {
    const json = JSON.parse(e.postData.contents);
    const userId = json.events[0].source.userId;
    const userMessage = json.events[0].message.text;
    const eventType = json.events[0].type;

    Logger.log('Webhook received');
    Logger.log('User ID: ' + userId);
    Logger.log('Message: ' + userMessage);

    if (eventType === 'message') {
      route(userMessage, userId);
    }
  } catch (error) {
    Logger.log('Error: ' + error);
  }

  return ContentService.createTextOutput('OK');
}

function route(message, userId) {
  const lowerMsg = message.toLowerCase();

  if (!isUserAuthorized(userId)) {
    replyToLine(userId, '権限がありません。');
    return;
  }

  if (lowerMsg.match(/^(追加|add)\s+/)) {
    const taskName = message.replace(/^(追加|add)\s+/, '');
    taskAdd(taskName, userId);
  } else if (lowerMsg.match(/^(タスク|タスク一覧|todo)$/)) {
    taskList(userId);
  } else if (lowerMsg.match(/^(完了|done)/)) {
    if (message === '完了' || message === 'done') {
      taskDoneLatest(userId);
    } else {
      const keyword = message.replace(/^(完了|done)\s+/, '');
      taskDone(keyword, userId);
    }
  } else if (lowerMsg.match(/^(削除|delete)\s+/)) {
    const keyword = message.replace(/^(削除|delete)\s+/, '');
    taskDelete(keyword, userId);
  } else if (lowerMsg.match(/^(日記|振り返り)$/)) {
    diaryWeekSummary(userId);
  } else if (message.includes('https://') || message.includes('http://')) {
    clipUrl(message, userId);
  } else {
    diaryRecord(message, userId);
  }
}

function isUserAuthorized(userId) {
  return userId === LINE_USER_ID;
}

function replyToLine(userId, messageText) {
  const url = 'https://api.line.me/v2/bot/message/push';
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + LINE_CHANNEL_ACCESS_TOKEN
  };

  const payload = {
    to: userId,
    messages: [{
      type: 'text',
      text: messageText
    }]
  };

  const options = {
    method: 'post',
    headers: headers,
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  const response = UrlFetchApp.fetch(url, options);
  Logger.log('LINE API Response: ' + response.getContentText());
}

function pushToLine(userId, messageText) {
  replyToLine(userId, messageText);
}

function testWebhookDetailed() {
  Logger.log('=== Detailed Webhook Test ===');

  const token = LINE_CHANNEL_ACCESS_TOKEN;
  const userId = LINE_USER_ID;

  Logger.log('Token length: ' + (token ? token.length : 'NOT SET'));
  Logger.log('User ID: ' + (userId ? userId : 'NOT SET'));
  Logger.log('User ID starts with U: ' + (userId ? userId.charAt(0) === 'U' : false));

  if (!userId || userId === 'NOT SET') {
    Logger.log('⚠️ ERROR: LINE_USER_ID が設定されていません！');
    Logger.log('手順: LINEボットにメッセージを送信 → GASログから「User ID: U...」を探す');
    return;
  }

  if (!token || token.length < 50) {
    Logger.log('⚠️ ERROR: LINE_CHANNEL_ACCESS_TOKEN が無効です！');
    return;
  }

  Logger.log('✅ すべての認証情報が設定されています');

  const url = 'https://api.line.me/v2/bot/message/push';
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  };

  const payload = {
    to: userId,
    messages: [{
      type: 'text',
      text: '🧪 詳細テスト: このメッセージが見えたら成功です！'
    }]
  };

  const options = {
    method: 'post',
    headers: headers,
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  const response = UrlFetchApp.fetch(url, options);
  Logger.log('HTTP Status: ' + response.getResponseCode());
  Logger.log('Response: ' + response.getContentText());
}
