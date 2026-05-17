"""SQLite-based data handler for Streamlit Cloud environment"""

import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path


class SQLiteHandler:
    """Handle data persistence using SQLite database"""

    def __init__(self, db_path: str = "personal_data.db"):
        self.db_path = db_path
        self.conn = None
        self._init_db()

    def _init_db(self):
        """Initialize database and create tables if needed"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        # Create diary table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                weekday TEXT NOT NULL,
                text TEXT NOT NULL,
                mood_score INTEGER,
                timestamp TEXT NOT NULL
            )
        """)

        # Create contents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                title TEXT NOT NULL,
                genre TEXT,
                memo TEXT,
                md_path TEXT,
                history TEXT,
                timestamp TEXT NOT NULL
            )
        """)

        # Create clips table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                url TEXT NOT NULL,
                title TEXT,
                summary TEXT,
                comment TEXT,
                topic TEXT
            )
        """)

        # Create todos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY,
                task_name TEXT NOT NULL,
                status TEXT DEFAULT '未完了',
                priority TEXT,
                due_date TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)

        self.conn.commit()

    def read_sheet(self, sheet_name: str) -> pd.DataFrame:
        """Read data from a specific sheet (table)"""
        try:
            # Map sheet names to table names
            table_map = {
                "日記": "diary",
                "コンテンツ台帳": "contents",
                "情報クリップ": "clips",
                "ToDo": "todos"
            }

            table_name = table_map.get(sheet_name)
            if not table_name:
                return pd.DataFrame()

            # Read from database
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.conn)

            # Rename columns to match original sheet format
            if table_name == "diary":
                df = df[['date', 'weekday', 'text', 'mood_score', 'timestamp']]
                df.columns = ['日付', '曜日', '本文', '気分スコア', '記録日時']
            elif table_name == "contents":
                df = df[['date', 'title', 'genre', 'memo', 'md_path', 'history', 'timestamp']]
                df.columns = ['日付', 'タイトル', 'ジャンル', 'メモ', 'mdパス', '追記履歴', '記録日時']
            elif table_name == "clips":
                df = df[['timestamp', 'url', 'title', 'summary', 'comment', 'topic']]
                df.columns = ['保存日時', 'URL', 'タイトル', '要約', 'コメント', 'トピック']
            elif table_name == "todos":
                df = df[['id', 'task_name', 'status', 'priority', 'due_date', 'created_at', 'completed_at']]
                df.columns = ['ID', 'タスク名', 'ステータス', '優先度', '期限日', '作成日時', '完了日時']

            return df
        except Exception as e:
            print(f"Error reading sheet '{sheet_name}': {e}")
            return pd.DataFrame()

    def append_row(self, sheet_name: str, values: list) -> bool:
        """Append a row to a sheet"""
        try:
            cursor = self.conn.cursor()

            if sheet_name == "日記":
                # values: [date, weekday, text, mood_score, timestamp]
                cursor.execute("""
                    INSERT INTO diary (date, weekday, text, mood_score, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, values)
            elif sheet_name == "コンテンツ台帳":
                # values: [date, title, genre, memo, md_path, history, timestamp]
                cursor.execute("""
                    INSERT INTO contents (date, title, genre, memo, md_path, history, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, values)
            elif sheet_name == "情報クリップ":
                # values: [timestamp, url, title, summary, comment, topic]
                cursor.execute("""
                    INSERT INTO clips (timestamp, url, title, summary, comment, topic)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, values)
            elif sheet_name == "ToDo":
                # values: [id, task_name, status, priority, due_date, created_at, completed_at]
                cursor.execute("""
                    INSERT INTO todos (id, task_name, status, priority, due_date, created_at, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, values)
            else:
                return False

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error appending row to '{sheet_name}': {e}")
            return False

    def update_cell(self, sheet_name: str, row: int, col: int, value: str) -> bool:
        """Update a specific cell"""
        try:
            cursor = self.conn.cursor()

            # Map column numbers to field names
            col_map = {
                "日記": {1: "date", 2: "weekday", 3: "text", 4: "mood_score", 5: "timestamp"},
                "コンテンツ台帳": {1: "date", 2: "title", 3: "genre", 4: "memo", 5: "md_path", 6: "history", 7: "timestamp"},
                "情報クリップ": {1: "timestamp", 2: "url", 3: "title", 4: "summary", 5: "comment", 6: "topic"},
                "ToDo": {1: "id", 2: "task_name", 3: "status", 4: "priority", 5: "due_date", 6: "created_at", 7: "completed_at"}
            }

            if sheet_name not in col_map or col not in col_map[sheet_name]:
                return False

            table_map = {
                "日記": "diary",
                "コンテンツ台帳": "contents",
                "情報クリップ": "clips",
                "ToDo": "todos"
            }

            table_name = table_map[sheet_name]
            col_name = col_map[sheet_name][col]

            # row is 0-indexed in the dataframe but we use SQL row id
            cursor.execute(f"UPDATE {table_name} SET {col_name} = ? WHERE rowid = ?", (value, row))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating cell: {e}")
            return False

    def get_diary_entries(self) -> pd.DataFrame:
        """Get all diary entries"""
        return self.read_sheet("日記")

    def get_contents(self) -> pd.DataFrame:
        """Get all content records"""
        return self.read_sheet("コンテンツ台帳")

    def get_clips(self) -> pd.DataFrame:
        """Get all clips"""
        return self.read_sheet("情報クリップ")

    def get_todos(self) -> pd.DataFrame:
        """Get all todos"""
        return self.read_sheet("ToDo")

    def add_diary_entry(self, text: str, mood_score: int) -> bool:
        """Add a new diary entry"""
        today = datetime.now().strftime("%Y-%m-%d")
        weekday = datetime.now().strftime("%A")
        timestamp = datetime.now().isoformat()

        values = [today, weekday, text, mood_score, timestamp]
        return self.append_row("日記", values)

    def add_content(self, title: str, genre: str, memo: str) -> bool:
        """Add a new content record"""
        today = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().isoformat()

        values = [today, title, genre, memo, "", "", timestamp]
        return self.append_row("コンテンツ台帳", values)

    def add_clip(self, url: str, title: str, summary: str, comment: str = "", topic: str = "") -> bool:
        """Add a new clip"""
        timestamp = datetime.now().isoformat()
        values = [timestamp, url, title, summary, comment, topic]
        return self.append_row("情報クリップ", values)

    def add_todo(self, task_name: str, priority: str, due_date: str = "") -> bool:
        """Add a new todo"""
        todos_df = self.get_todos()
        next_id = len(todos_df) + 1
        timestamp = datetime.now().isoformat()

        values = [next_id, task_name, "未完了", priority, due_date, timestamp, ""]
        return self.append_row("ToDo", values)

    def update_todo_status(self, row: int, status: str) -> bool:
        """Update todo status"""
        timestamp = datetime.now().isoformat() if status == "完了" else ""

        # Status is in column 3 (1-indexed)
        self.update_cell("ToDo", row + 2, 3, status)  # +2 because row 1 is header
        if status == "完了":
            self.update_cell("ToDo", row + 2, 7, timestamp)

        return True

    def __del__(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
