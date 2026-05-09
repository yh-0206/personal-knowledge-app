"""Configuration for PersonalKnowledgeApp"""

# Google Sheets Configuration
SHEET_ID = "15Q77ftiz-yxtYAU3kOYxuRXLvdZdw6fW9TC-BuKMnvU"

# Sheet names
SHEET_DIARY = "日記"
SHEET_CONTENTS = "コンテンツ台帳"
SHEET_CLIPS = "情報クリップ"
SHEET_TODOS = "ToDo"

# Streamlit Configuration
APP_TITLE = "Personal Knowledge App"
APP_ICON = "📚"

# Columns for each sheet
DIARY_COLUMNS = ["日付", "曜日", "本文", "気分スコア", "記録日時"]
CONTENTS_COLUMNS = ["日付", "タイトル", "ジャンル", "メモ", "mdパス", "追記履歴", "記録日時"]
CLIPS_COLUMNS = ["保存日時", "URL", "タイトル", "要約", "コメント", "トピック"]
TODOS_COLUMNS = ["ID", "タスク名", "ステータス", "優先度", "期限日", "作成日時", "完了日時"]

# Content genres
CONTENT_GENRES = ["映画", "展覧会", "ライブ", "本", "配信"]

# Clip topics
CLIP_TOPICS = ["CX", "マーケ", "DS", "自動車", "その他"]

# Todo priority
TODO_PRIORITIES = ["高", "中", "低"]

# Mood score range
MOOD_SCORE_MIN = 1
MOOD_SCORE_MAX = 5
