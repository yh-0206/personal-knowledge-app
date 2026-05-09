# LINE秘書Bot デプロイメント＆実装完全ガイド

このガイドは、LINE秘書Botをセットアップから本番運用まで、ステップバイステップで進める完全な手順です。

## 全体の流れ（4段階）

```
Step 1: 環境準備 (SETUP_GUIDE.md参照)
    ↓
Step 2: GASコード実装
    ↓
Step 3: Webhook接続＆動作確認
    ↓
Step 4: 運用開始
```

---

## Step 2: GASコード実装（詳細）

### 前提条件
- SETUP_GUIDE.mdの Step 1～5-2 を完了していること
- GASエディタで7つのファイルが作成済みであること

### 2-1. Code.gs の実装

GASエディタで「Code.gs」を開き、以下をすべてコピー＆ペーストしてください：

```javascript
const LINE_CHANNEL_ACCESS_TOKEN = PropertiesService.getScriptProperties().getProperty('LINE_CHANNEL_ACCESS_TOKEN');
const LINE_USER_ID = PropertiesService.getScriptProperties().getProperty('LINE_USER_ID');
const CLAUDE_API_KEY = PropertiesService.getScriptProperties().getProperty('CLAUDE_API_KEY');
const SPREADSHEET_ID = PropertiesService.getScriptProperties().getProperty('SPREADSHEET_ID');

function doPost(e) {
  const json = JSON.parse(e.postData.contents);
  const userId = json.events[0].source.userId;
  const userMessage = json.events[0].message.text;
  const eventType = json.events[0].type;

  if (eventType !== 'message') {
    return ContentService.createTextOutput('OK');
  }

  Logger.log('Received message: ' + userMessage);
  Logger.log('User ID: ' + userId);

  route(userMessage, userId);

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
  } else if (isDiaryTime()) {
    diaryRecord(message, userId);
  } else {
    replyToLine(userId, 'コマンドが認識されませんでした。以下のコマンドをお試しください:\n- 追加 タスク名\n- タスク\n- 完了\n- 日記\n- URL（URLの自動要約）');
  }
}

function isUserAuthorized(userId) {
  return userId === LINE_USER_ID;
}

function replyToLine(userId, messageText) {
  const url = 'https://api.line.biz/v2/bot/message/push';
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
```

### 2-2. Sheet.gs の実装

GASエディタで「Sheet.gs」を開き、以下をペースト：

```javascript
function getSheet(sheetName) {
  const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
  return spreadsheet.getSheetByName(sheetName);
}

function appendRow(sheetName, values) {
  const sheet = getSheet(sheetName);
  sheet.appendRow(values);
}

function getAllRows(sheetName) {
  const sheet = getSheet(sheetName);
  const range = sheet.getDataRange();
  return range.getValues();
}

function updateCell(sheetName, row, col, value) {
  const sheet = getSheet(sheetName);
  sheet.getRange(row, col).setValue(value);
}

function getNextId(sheetName) {
  const rows = getAllRows(sheetName);
  if (rows.length <= 1) return 1;
  const lastRow = rows[rows.length - 1];
  const lastId = parseInt(lastRow[0]);
  return lastId + 1;
}

function findRowByValue(sheetName, columnIndex, value) {
  const rows = getAllRows(sheetName);
  for (let i = 1; i < rows.length; i++) {
    if (rows[i][columnIndex - 1] === value) {
      return i + 1;
    }
  }
  return -1;
}

function deleteRow(sheetName, rowIndex) {
  const sheet = getSheet(sheetName);
  if (rowIndex > 1) {
    sheet.deleteRow(rowIndex);
  }
}

function getCurrentDateTime() {
  return new Date().toISOString();
}

function getDateString(date) {
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  const dd = String(date.getDate()).padStart(2, '0');
  return yyyy + '-' + mm + '-' + dd;
}

function getDayOfWeek(date) {
  const days = ['日', '月', '火', '水', '木', '金', '土'];
  return days[date.getDay()];
}

function getLastNDaysEntries(sheetName, days) {
  const rows = getAllRows(sheetName);
  const result = [];
  const today = new Date();
  const nDaysAgo = new Date(today.getTime() - days * 24 * 60 * 60 * 1000);

  for (let i = 1; i < rows.length; i++) {
    const dateStr = rows[i][0];
    const date = new Date(dateStr);
    if (date >= nDaysAgo && date <= today) {
      result.push({
        date: dateStr,
        content: rows[i][2]
      });
    }
  }

  return result;
}
```

### 2-3. Claude.gs の実装

GASエディタで「Claude.gs」を開き、以下をペースト：

```javascript
function callClaude(prompt) {
  const url = 'https://api.anthropic.com/v1/messages';

  const headers = {
    'Content-Type': 'application/json',
    'x-api-key': CLAUDE_API_KEY,
    'anthropic-version': '2023-06-01'
  };

  const payload = {
    model: 'claude-haiku-4-5-20251001',
    max_tokens: 500,
    messages: [{
      role: 'user',
      content: prompt
    }]
  };

  const options = {
    method: 'post',
    headers: headers,
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const result = JSON.parse(response.getContentText());

    if (response.getResponseCode() === 200) {
      const textContent = result.content.find(c => c.type === 'text');
      return textContent ? textContent.text : 'エラー: レスポンスが不正です';
    } else {
      Logger.log('Claude API Error: ' + response.getContentText());
      return 'エラー: Claude APIが応答しませんでした';
    }
  } catch (e) {
    Logger.log('Exception in callClaude: ' + e);
    return 'エラー: Claude APIへのアクセスに失敗しました';
  }
}

function summarizeText(text) {
  const prompt = '以下のテキストを3行で要約してください:\n\n' + text;
  return callClaude(prompt);
}

function generateDiarySummary(diaryEntries) {
  let entriesText = '';
  for (let i = 0; i < diaryEntries.length; i++) {
    entriesText += '【' + diaryEntries[i].date + '】\n' + diaryEntries[i].content + '\n\n';
  }

  const prompt = '以下の1週間の日記を振り返り、200字程度のサマリーを作成してください:\n\n' + entriesText;
  return callClaude(prompt);
}
```

### 2-4. Task.gs の実装

GASエディタで「Task.gs」を開き、以下をペースト：

```javascript
function taskAdd(taskName, userId) {
  const id = getNextId('タスク');
  const createdAt = getCurrentDateTime();
  const values = [id, taskName, '未完了', createdAt, ''];

  appendRow('タスク', values);
  replyToLine(userId, '✅ 「' + taskName + '」をタスクに追加しました。');
}

function taskList(userId) {
  const rows = getAllRows('タスク');

  if (rows.length <= 1) {
    replyToLine(userId, 'タスクがありません。');
    return;
  }

  let incompleteCount = 0;
  let taskList = '';

  for (let i = 1; i < rows.length; i++) {
    const taskData = rows[i];
    const id = taskData[0];
    const taskName = taskData[1];
    const status = taskData[2];

    if (status === '未完了') {
      incompleteCount++;
      taskList += incompleteCount + '. ' + taskName + '\n';
    }
  }

  if (incompleteCount === 0) {
    replyToLine(userId, 'すべてのタスクが完了しています！🎉');
  } else {
    const message = '📋 未完了タスク (' + incompleteCount + '件)\n\n' + taskList;
    replyToLine(userId, message);
  }
}

function taskDone(keyword, userId) {
  const rows = getAllRows('タスク');
  let foundIndex = -1;

  for (let i = 1; i < rows.length; i++) {
    const taskName = rows[i][1];
    if (taskName.includes(keyword)) {
      foundIndex = i + 1;
      break;
    }
  }

  if (foundIndex === -1) {
    replyToLine(userId, '「' + keyword + '」というタスクが見つかりません。');
    return;
  }

  const completedAt = getCurrentDateTime();
  updateCell('タスク', foundIndex, 3, '完了');
  updateCell('タスク', foundIndex, 5, completedAt);

  const taskName = rows[foundIndex - 1][1];
  replyToLine(userId, '✅ 「' + taskName + '」を完了にしました。');
}

function taskDoneLatest(userId) {
  const rows = getAllRows('タスク');

  if (rows.length <= 1) {
    replyToLine(userId, 'タスクがありません。');
    return;
  }

  let lastIncompleteIndex = -1;

  for (let i = rows.length - 1; i > 0; i--) {
    if (rows[i][2] === '未完了') {
      lastIncompleteIndex = i + 1;
      break;
    }
  }

  if (lastIncompleteIndex === -1) {
    replyToLine(userId, 'すべてのタスクが完了しています！');
    return;
  }

  const completedAt = getCurrentDateTime();
  updateCell('タスク', lastIncompleteIndex, 3, '完了');
  updateCell('タスク', lastIncompleteIndex, 5, completedAt);

  const taskName = rows[lastIncompleteIndex - 1][1];
  replyToLine(userId, '✅ 「' + taskName + '」を完了にしました。');
}

function taskDelete(keyword, userId) {
  const rows = getAllRows('タスク');
  let foundIndex = -1;

  for (let i = 1; i < rows.length; i++) {
    const taskName = rows[i][1];
    if (taskName.includes(keyword)) {
      foundIndex = i + 1;
      break;
    }
  }

  if (foundIndex === -1) {
    replyToLine(userId, '「' + keyword + '」というタスクが見つかりません。');
    return;
  }

  const taskName = rows[foundIndex - 1][1];
  deleteRow('タスク', foundIndex);
  replyToLine(userId, '🗑️ 「' + taskName + '」を削除しました。');
}

function morningBriefing() {
  const rows = getAllRows('タスク');

  let incompleteCount = 0;
  let taskList = '';

  for (let i = 1; i < rows.length; i++) {
    const taskData = rows[i];
    const taskName = taskData[1];
    const status = taskData[2];

    if (status === '未完了') {
      incompleteCount++;
      taskList += incompleteCount + '. ' + taskName + '\n';
    }
  }

  let message = '';
  if (incompleteCount === 0) {
    message = 'おはようございます！☀️\n\n今日のタスクはありません。素晴らしい！';
  } else {
    message = 'おはようございます！☀️\n\n📋 今日のタスク (' + incompleteCount + '件)\n\n' + taskList;
  }

  pushToLine(LINE_USER_ID, message);
}
```

### 2-5. Diary.gs の実装

GASエディタで「Diary.gs」を開き、以下をペースト：

```javascript
function diaryRecord(diaryText, userId) {
  const today = new Date();
  const dateStr = getDateString(today);
  const dayOfWeek = getDayOfWeek(today);
  const recordedAt = getCurrentDateTime();

  const values = [dateStr, dayOfWeek, diaryText, recordedAt];
  appendRow('日記', values);

  replyToLine(userId, '📔 今日の日記を記録しました。');
}

function diaryWeekSummary(userId) {
  const entries = getLastNDaysEntries('日記', 7);

  if (entries.length === 0) {
    replyToLine(userId, '過去7日間の日記がありません。');
    return;
  }

  const summary = generateDiarySummary(entries);
  const message = '📊 今週の振り返り\n\n' + summary;
  replyToLine(userId, message);
}

function isDiaryTime() {
  const now = new Date();
  const hours = now.getHours();
  return hours >= 21 && hours < 24;
}

function eveningPrompt() {
  const message = '🌙 今日どうでした？ランニング・ヨガ・気づきなど何でも。';
  pushToLine(LINE_USER_ID, message);
}
```

### 2-6. Clip.gs の実装

GASエディタで「Clip.gs」を開き、以下をペースト：

```javascript
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
```

### 2-7. Trigger.gs の実装

GASエディタで「Trigger.gs」を開き、以下をペースト：

```javascript
function morningBriefing() {
  const rows = getAllRows('タスク');

  let incompleteCount = 0;
  let taskList = '';

  for (let i = 1; i < rows.length; i++) {
    const taskData = rows[i];
    const taskName = taskData[1];
    const status = taskData[2];

    if (status === '未完了') {
      incompleteCount++;
      taskList += incompleteCount + '. ' + taskName + '\n';
    }
  }

  let message = '';
  if (incompleteCount === 0) {
    message = 'おはようございます！☀️\n\n今日のタスクはありません。素晴らしい！';
  } else {
    message = 'おはようございます！☀️\n\n📋 今日のタスク (' + incompleteCount + '件)\n\n' + taskList;
  }

  pushToLine(LINE_USER_ID, message);
  Logger.log('Morning briefing sent');
}

function eveningPrompt() {
  const message = '🌙 今日どうでした？ランニング・ヨガ・気づきなど何でも。';
  pushToLine(LINE_USER_ID, message);
  Logger.log('Evening prompt sent');
}
```

### 2-8. 動作確認

すべてのコードをペーストしたら：

1. GASエディタで「💾 保存」をクリック
2. 左メニューの「実行ログ」を開く
3. GASの構文エラーが表示されていないか確認

---

## Step 3: Webhook接続＆動作確認

### 3-1. 既にStep 5-2（Webhook URL設定）が完了している場合

1. スプレッドシートIDとAPIキーが正しく設定されているか確認
2. LINEで「テスト」と送信
3. 返信が来れば接続OK

### 3-2. まだWebhook設定していない場合

SETUP_GUIDE.md の Step 5-2 を実行してください。

---

## Step 4: 運用開始チェックリスト

以下をすべてチェックしてから運用開始してください：

- [ ] Googleスプレッドシートが3シート（タスク・日記・クリップ）で構成されている
- [ ] GASで7つのファイルがすべてペーストされている
- [ ] スクリプトプロパティ4つが設定されている（トークン・ID・キー・スプレッドシートID）
- [ ] Webhookが設定済み、検証で「成功」と表示された
- [ ] LINE_USER_IDが正しく設定されている
- [ ] トリガーが2つ設定されている（朝7時・夜21時）
- [ ] テストメッセージを送信して返信が返ってくる

---

## よくあるトラブル＆解決策

| 症状 | 原因 | 解決策 |
|--|--|--|
| Bot が返信しない | スクリプトプロパティが未設定 | 「プロジェクトの設定」→「スクリプトプロパティ」を確認 |
| タスク が保存されない | スプレッドシートIDが誤っている | URLから ID をコピーし直す |
| 「権限がありません」と表示 | LINE_USER_IDが異なる | GASログから正しいUserIDを確認 |
| 朝・夜の通知がない | トリガーが設定されていない | GASの「トリガー」タブから2つのトリガーを設定 |
| Claude API「ク400エラー | APIキーが誤っている、または期限切れ | console.anthropic.com で新しいキーを発行 |

---

## 保守・アップデート

### 毎月の推奨タスク
- スプレッドシートのバックアップをダウンロード
- GASログを確認してエラーがないか確認
- Claude APIのQuotaを確認

### 機能改善（将来版向け）
- 複数ユーザー対応
- Googleカレンダー連携
- ランニングログ連携

---

**セットアップ完了！**

このガイドに従えば、LINE秘書Botは完全に機能します。
何か問題が発生した場合は、トラブルシューティングセクションを参照してください。

楽しい自動化ライフをお過ごしください！ 🎉
