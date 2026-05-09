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
