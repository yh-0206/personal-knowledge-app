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
