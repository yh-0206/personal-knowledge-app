"""Google Sheets API handler"""

import streamlit as st
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime
import config

class SheetsHandler:
    def __init__(self):
        self.credentials = self._get_credentials()
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.sheet_id = config.SHEET_ID

    def _get_credentials(self):
        """Get credentials from JSON file or Streamlit Secrets"""
        import os
        import json

        try:
            # Try Streamlit Secrets first
            try:
                creds_dict = st.secrets.get("google_service_account", {})
                if creds_dict:
                    creds = Credentials.from_service_account_info(
                        creds_dict,
                        scopes=['https://www.googleapis.com/auth/spreadsheets']
                    )
                    return creds
            except Exception:
                pass

            # Fall back to JSON file in project directory
            json_file = "personalknowledgeapp-0123180f35bc.json"

            if os.path.exists(json_file):
                creds = Credentials.from_service_account_file(
                    json_file,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                st.success(f"✅ Credentials loaded from {json_file}")
                return creds

            st.error("Google Sheets credentials not found. Please add personal-knowledge-app-*.json file")
            return None
        except Exception as e:
            st.error(f"Error loading credentials: {e}")
            return None

    def read_sheet(self, sheet_name: str) -> pd.DataFrame:
        """Read data from a specific sheet"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=f"{sheet_name}!A:Z"
            ).execute()

            values = result.get('values', [])
            if not values:
                return pd.DataFrame()

            # First row is header
            headers = values[0]
            data = values[1:]

            # Pad rows to match header length
            padded_data = [row + [''] * (len(headers) - len(row)) for row in data]

            return pd.DataFrame(padded_data, columns=headers)
        except Exception as e:
            st.error(f"Error reading sheet '{sheet_name}': {e}")
            return pd.DataFrame()

    def append_row(self, sheet_name: str, values: list) -> bool:
        """Append a row to a sheet"""
        try:
            # Get the last row number
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=f"{sheet_name}!A:A"
            ).execute()

            last_row = len(result.get('values', [])) + 1

            # Append the new row
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=f"{sheet_name}!A{last_row}",
                valueInputOption='USER_ENTERED',
                body={'values': [values]}
            ).execute()

            return True
        except Exception as e:
            st.error(f"Error appending to sheet '{sheet_name}': {e}")
            return False

    def update_cell(self, sheet_name: str, row: int, col: int, value: str) -> bool:
        """Update a specific cell"""
        try:
            col_letter = chr(64 + col)  # Convert column number to letter
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=f"{sheet_name}!{col_letter}{row}",
                valueInputOption='USER_ENTERED',
                body={'values': [[value]]}
            ).execute()
            return True
        except Exception as e:
            st.error(f"Error updating cell: {e}")
            return False

    def get_diary_entries(self) -> pd.DataFrame:
        """Get diary entries"""
        return self.read_sheet(config.SHEET_DIARY)

    def get_contents(self) -> pd.DataFrame:
        """Get content records"""
        return self.read_sheet(config.SHEET_CONTENTS)

    def get_clips(self) -> pd.DataFrame:
        """Get information clips"""
        return self.read_sheet(config.SHEET_CLIPS)

    def get_todos(self) -> pd.DataFrame:
        """Get todos"""
        return self.read_sheet(config.SHEET_TODOS)

    def add_diary_entry(self, text: str, mood_score: int) -> bool:
        """Add a new diary entry"""
        today = datetime.now().strftime("%Y-%m-%d")
        weekday = datetime.now().strftime("%A")
        timestamp = datetime.now().isoformat()

        values = [today, weekday, text, mood_score, timestamp]
        return self.append_row(config.SHEET_DIARY, values)

    def add_content(self, title: str, genre: str, memo: str) -> bool:
        """Add a new content record"""
        today = datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.now().isoformat()

        values = [today, title, genre, memo, "", "", timestamp]
        return self.append_row(config.SHEET_CONTENTS, values)

    def add_clip(self, url: str, title: str, summary: str, comment: str = "", topic: str = "") -> bool:
        """Add a new clip"""
        timestamp = datetime.now().isoformat()
        values = [timestamp, url, title, summary, comment, topic]
        return self.append_row(config.SHEET_CLIPS, values)

    def add_todo(self, task_name: str, priority: str, due_date: str = "") -> bool:
        """Add a new todo"""
        todos_df = self.get_todos()
        next_id = len(todos_df) + 1
        timestamp = datetime.now().isoformat()

        values = [next_id, task_name, "未完了", priority, due_date, timestamp, ""]
        return self.append_row(config.SHEET_TODOS, values)

    def update_todo_status(self, row: int, status: str) -> bool:
        """Update todo status"""
        timestamp = datetime.now().isoformat() if status == "完了" else ""

        # Status is in column C (3), completed time in column G (7)
        self.update_cell(config.SHEET_TODOS, row + 2, 3, status)  # +2 because row 1 is header
        if status == "完了":
            self.update_cell(config.SHEET_TODOS, row + 2, 7, timestamp)

        return True
