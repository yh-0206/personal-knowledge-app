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

function eveningPrompt() {
  const message = '今日どうでした？ランニング・ヨガ・気づきなど何でも。';
  pushToLine(LINE_USER_ID, '🌙 ' + message);
}
