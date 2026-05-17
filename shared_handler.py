"""Shared handler that detects environment and uses appropriate backend"""

import os
import pandas as pd
from pathlib import Path


class SharedHandler:
    """
    Automatically selects the appropriate handler based on environment:
    - Local: GoogleSheetsHandler
    - Streamlit Cloud: SQLiteHandler
    """

    def __init__(self):
        self.handler = self._init_handler()
        self.is_cloud = self._is_streamlit_cloud()

    def _is_streamlit_cloud(self) -> bool:
        """Detect if running on Streamlit Cloud"""
        # Check multiple indicators to be sure
        indicators = [
            os.path.exists("/.streamlit/"),  # Streamlit Cloud file structure
            "/mount/src/" in os.getcwd(),     # Cloud mounted source path
            os.environ.get("STREAMLIT_SERVER_RUNONSAVE") is not None,  # Cloud env var
        ]
        return any(indicators)

    def _init_handler(self):
        """Initialize appropriate handler based on environment"""
        if self._is_streamlit_cloud():
            # Use SQLite on Streamlit Cloud
            from sqlite_handler import SQLiteHandler
            return SQLiteHandler("personal_data.db")
        else:
            # Use Google Sheets locally
            from sheets_handler import SheetsHandler
            return SheetsHandler()

    # ========== Delegation Methods ==========

    def read_sheet(self, sheet_name: str) -> pd.DataFrame:
        """Read data from a specific sheet"""
        return self.handler.read_sheet(sheet_name)

    def append_row(self, sheet_name: str, values: list) -> bool:
        """Append a row to a sheet"""
        return self.handler.append_row(sheet_name, values)

    def update_cell(self, sheet_name: str, row: int, col: int, value: str) -> bool:
        """Update a specific cell"""
        return self.handler.update_cell(sheet_name, row, col, value)

    def get_diary_entries(self) -> pd.DataFrame:
        """Get all diary entries"""
        return self.handler.get_diary_entries()

    def get_contents(self) -> pd.DataFrame:
        """Get all content records"""
        return self.handler.get_contents()

    def get_clips(self) -> pd.DataFrame:
        """Get all clips"""
        return self.handler.get_clips()

    def get_todos(self) -> pd.DataFrame:
        """Get all todos"""
        return self.handler.get_todos()

    def add_diary_entry(self, text: str, mood_score: int) -> bool:
        """Add a new diary entry"""
        return self.handler.add_diary_entry(text, mood_score)

    def add_content(self, title: str, genre: str, memo: str) -> bool:
        """Add a new content record"""
        return self.handler.add_content(title, genre, memo)

    def add_clip(self, url: str, title: str, summary: str, comment: str = "", topic: str = "") -> bool:
        """Add a new clip"""
        return self.handler.add_clip(url, title, summary, comment, topic)

    def add_todo(self, task_name: str, priority: str, due_date: str = "") -> bool:
        """Add a new todo"""
        return self.handler.add_todo(task_name, priority, due_date)

    def update_todo_status(self, row: int, status: str) -> bool:
        """Update todo status"""
        return self.handler.update_todo_status(row, status)
