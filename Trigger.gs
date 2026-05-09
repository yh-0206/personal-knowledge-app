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
