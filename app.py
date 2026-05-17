"""Personal Knowledge App - Main Streamlit Application"""

import streamlit as st
from datetime import datetime
import pandas as pd
from shared_handler import SharedHandler
import config

# Page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'sheets_handler' not in st.session_state:
    st.session_state.sheets_handler = SharedHandler()

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "すべて"

sheets = st.session_state.sheets_handler

# ============================================================================
# TOP BAR
# ============================================================================
col1, col2 = st.columns([1, 1], gap="large")
with col1:
    st.title(f"{config.APP_ICON} {config.APP_TITLE}")
with col2:
    today = datetime.now().strftime("%Y年%m月%d日 (%A)")
    st.markdown(f"### {today}")

st.divider()

# ============================================================================
# QUICK INPUT SECTION
# ============================================================================
st.subheader("クイック入力")

input_type = st.radio(
    "入力種別を選択してください",
    options=["日記", "コンテンツ", "情報クリップ", "ToDo"],
    horizontal=True,
    key="input_type"
)

if input_type == "日記":
    col1, col2 = st.columns([4, 1])
    with col1:
        diary_text = st.text_area(
            "今日のできごとや気分を記録",
            placeholder="今日はどんな一日でしたか？",
            height=100,
            key="diary_input"
        )
    with col2:
        st.write("気分スコア")
        mood_score = st.slider(
            "1〜5で選択",
            min_value=1,
            max_value=5,
            value=3,
            key="mood_input",
            label_visibility="collapsed"
        )

    if st.button("保存", key="save_diary"):
        if diary_text.strip():
            if sheets.add_diary_entry(diary_text, mood_score):
                st.success("日記を記録しました")
                st.session_state.refresh_data = True
            else:
                st.error("保存に失敗しました")
        else:
            st.warning("テキストを入力してください")

elif input_type == "コンテンツ":
    mode = st.radio(
        "モードを選択",
        options=["新規作成", "既存に追記"],
        horizontal=True,
        key="content_mode"
    )

    if mode == "新規作成":
        col1, col2 = st.columns(2)
        with col1:
            content_title = st.text_input("作品名", key="content_title")
        with col2:
            content_genre = st.selectbox(
                "ジャンル",
                options=config.CONTENT_GENRES,
                key="content_genre"
            )

        content_memo = st.text_area(
            "感想・一言メモ",
            placeholder="この作品についての感想を入力",
            height=80,
            key="content_memo"
        )

        if st.button("保存", key="save_content"):
            if content_title.strip() and content_memo.strip():
                if sheets.add_content(content_title, content_genre, content_memo):
                    st.success("コンテンツを記録しました")
                    st.session_state.refresh_data = True
                else:
                    st.error("保存に失敗しました")
            else:
                st.warning("タイトルとメモを入力してください")

    else:
        # Existing content append mode (placeholder)
        st.info("既存コンテンツへの追記機能は次フェーズで実装します")

elif input_type == "情報クリップ":
    st.info("URL要約機能はPhase 4で実装します（Claude API連携）")

elif input_type == "ToDo":
    col1, col2, col3 = st.columns(3)
    with col1:
        todo_name = st.text_input("タスク名", key="todo_name")
    with col2:
        todo_priority = st.selectbox(
            "優先度",
            options=config.TODO_PRIORITIES,
            key="todo_priority"
        )
    with col3:
        todo_due = st.date_input("期限日（オプション）", value=None, key="todo_due")

    if st.button("追加", key="save_todo"):
        if todo_name.strip():
            due_date_str = todo_due.strftime("%Y-%m-%d") if todo_due else ""
            if sheets.add_todo(todo_name, todo_priority, due_date_str):
                st.success("ToDoを追加しました")
                st.session_state.refresh_data = True
            else:
                st.error("追加に失敗しました")
        else:
            st.warning("タスク名を入力してください")

st.divider()

# ============================================================================
# SUMMARY BAR
# ============================================================================
st.subheader("サマリー")

try:
    diary_df = sheets.get_diary_entries()
    contents_df = sheets.get_contents()
    clips_df = sheets.get_clips()
    todos_df = sheets.get_todos()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("日記", len(diary_df))
    with col2:
        st.metric("コンテンツ", len(contents_df))
    with col3:
        st.metric("情報クリップ", len(clips_df))
    with col4:
        todos_incomplete = len(todos_df[todos_df["ステータス"] == "未完了"]) if "ステータス" in todos_df.columns else 0
        st.metric("未完了ToDoタスク", todos_incomplete)
    with col5:
        if len(todos_df) > 0:
            todo_completion = (len(todos_df) - todos_incomplete) / len(todos_df) * 100
            st.metric("完了率", f"{todo_completion:.0f}%")
        else:
            st.metric("完了率", "0%")

except Exception as e:
    st.error(f"データ読み込みエラー: {e}")
    diary_df = pd.DataFrame()
    contents_df = pd.DataFrame()
    clips_df = pd.DataFrame()
    todos_df = pd.DataFrame()

st.divider()

# ============================================================================
# TABS & ENTRY LIST
# ============================================================================
st.subheader("エントリー一覧")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["すべて", "日記", "コンテンツ", "情報クリップ", "ToDo"])

with tab1:
    st.write("#### すべてのエントリー")
    if not diary_df.empty:
        st.write("**日記**")
        st.dataframe(diary_df, use_container_width=True)
    if not contents_df.empty:
        st.write("**コンテンツ**")
        st.dataframe(contents_df, use_container_width=True)
    if not clips_df.empty:
        st.write("**情報クリップ**")
        st.dataframe(clips_df, use_container_width=True)
    if not todos_df.empty:
        st.write("**ToDo**")
        st.dataframe(todos_df, use_container_width=True)

with tab2:
    st.write("#### 日記")
    if not diary_df.empty:
        st.dataframe(diary_df.iloc[::-1], use_container_width=True)  # Reverse order (newest first)
    else:
        st.info("日記がまだありません")

with tab3:
    st.write("#### コンテンツ")
    if not contents_df.empty:
        st.dataframe(contents_df.iloc[::-1], use_container_width=True)
    else:
        st.info("コンテンツがまだありません")

with tab4:
    st.write("#### 情報クリップ")
    if not clips_df.empty:
        st.dataframe(clips_df.iloc[::-1], use_container_width=True)
    else:
        st.info("情報クリップがまだありません")

with tab5:
    st.write("#### ToDo")
    if not todos_df.empty:
        # Show incomplete tasks first
        st.write("**未完了**")
        incomplete = todos_df[todos_df["ステータス"] == "未完了"] if "ステータス" in todos_df.columns else todos_df
        st.dataframe(incomplete, use_container_width=True)

        st.write("**完了**")
        complete = todos_df[todos_df["ステータス"] == "完了"] if "ステータス" in todos_df.columns else pd.DataFrame()
        if not complete.empty:
            st.dataframe(complete, use_container_width=True)
        else:
            st.info("完了したタスクはありません")
    else:
        st.info("ToDoがまだありません")

# Footer
st.divider()
st.caption("Personal Knowledge App © 2026 | Powered by Streamlit & Google Sheets & Claude API")
