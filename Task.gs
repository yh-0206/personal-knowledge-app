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

function taskDone(input, userId) {
  const rows = getAllRows('タスク');
  let foundIndex = -1;
  const taskNumber = parseInt(input);

  if (!isNaN(taskNumber)) {
    let incompleteCount = 0;
    for (let i = 1; i < rows.length; i++) {
      if (rows[i][2] === '未完了') {
        incompleteCount++;
        if (incompleteCount === taskNumber) {
          foundIndex = i + 1;
          break;
        }
      }
    }
    if (foundIndex === -1) {
      replyToLine(userId, 'タスク番号 ' + taskNumber + ' が見つかりません。');
      return;
    }
  } else {
    for (let i = 1; i < rows.length; i++) {
      const taskName = rows[i][1];
      if (taskName.includes(input)) {
        foundIndex = i + 1;
        break;
      }
    }
    if (foundIndex === -1) {
      replyToLine(userId, '「' + input + '」というタスクが見つかりません。');
      return;
    }
  }

  const completedAt = getCurrentDateTime();
  updateCell('タスク', foundIndex, 3, '完了');
  updateCell('タスク', foundIndex, 5, completedAt);

  const taskName = rows[foundIndex - 1][1];
  replyToLine(userId, '✅ 「' + taskName + '」を完了にしました。');

  const updatedRows = getAllRows('タスク');
  let hasIncomplete = false;
  for (let i = 1; i < updatedRows.length; i++) {
    if (updatedRows[i][2] === '未完了') {
      hasIncomplete = true;
      break;
    }
  }

  if (!hasIncomplete) {
    const helpMessage = '🎉 すべてのタスクが完了しました！\n\n以下のコマンドをお試しください:\n- 追加 タスク名\n- タスク\n- 完了\n- 日記\n- URL（URLの自動要約）';
    replyToLine(userId, helpMessage);
  }
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

  const updatedRows = getAllRows('タスク');
  let hasIncomplete = false;
  for (let i = 1; i < updatedRows.length; i++) {
    if (updatedRows[i][2] === '未完了') {
      hasIncomplete = true;
      break;
    }
  }

  if (!hasIncomplete) {
    const helpMessage = '🎉 すべてのタスクが完了しました！\n\n以下のコマンドをお試しください:\n- 追加 タスク名\n- タスク\n- 完了\n- 日記\n- URL（URLの自動要約）';
    replyToLine(userId, helpMessage);
  }
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
    message = 'おはようございます！☀️\nかった、今日のタスクはありません。';
  } else {
    message = 'おはようございます！☀️\n\n📋 今日のタスク (' + incompleteCount + '件)\n\n' + taskList;
  }

  pushToLine(LINE_USER_ID, message);
}
