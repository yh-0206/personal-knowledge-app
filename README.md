# Personal Knowledge App

パーソナルナレッジアプリ - 日記・コンテンツ記録・情報蓄積・ToDoを一元管理するWebアプリケーション

## 📋 機能概要

### 4つのモジュール

| モジュール | 概要 | 主な用途 |
|-----------|------|--------|
| 📔 日記 | 毎日の出来事・気分を記録 | 振り返り・気分スコアのトレンド・週次AI要約 |
| 📺 コンテンツ | 展覧会・映画・ライブ・本・配信の記録 | 鑑賞ログ管理・mdファイルへの新規作成と追記 |
| 📰 情報クリップ | URLクリップ・トピック別情報整理 | CX・マーケ・DS・自動車の最新情報をAI要約 |
| ✅ ToDo | タスク管理 | 優先度・期限・習慣タスク・完了率の管理 |

## 🔧 技術スタック

| レイヤー | 技術 | 役割 | 費用 |
|--------|------|------|-----|
| **フロントエンド** | Streamlit (Python) | ブラウザ・スマホ対応のWebアプリ | 無料 |
| **ホスティング** | Streamlit Community Cloud | GitHubと連携・URLでどこからでもアクセス可 | 無料 |
| **コンテンツ保存** | ローカルmdファイル + GitHub | 考察テキストの本体・追記・バージョン管理 | 無料 |
| **動的データ** | Google スプレッドシート | 日記・ToDo・クリップ・コンテンツ台帳 | 無料 |
| **AI処理** | Claude API (Haiku) | URL要約・日記振り返り生成 | 月100〜300円程度 |

## 📁 プロジェクト構成

```
PersonalKnowledgeApp/
├── app.py                    # Streamlit メインアプリケーション
├── config.py                 # 設定値（Sheet ID等）
├── sheets_handler.py         # Google Sheets API ハンドラー
├── requirements.txt          # Python 依存パッケージ
├── README.md                 # このファイル
├── .gitignore               # Git除外設定
└── knowledge/
    └── contents/            # md形式の考察ファイル
        ├── exhibition/      # 展覧会
        ├── film/            # 映画
        ├── live/            # ライブ
        ├── book/            # 本
        └── streaming/       # 配信
```

## 🚀 セットアップ手順

### 1. 必須条件

- Python 3.9 以上
- pip

### 2. インストール

```bash
pip install -r requirements.txt
```

### 3. Google Sheets API 認証

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成
3. Google Sheets API を有効化
4. サービスアカウントを作成
5. JSON キーをダウンロード

### 4. Streamlit Secrets 設定

`~/.streamlit/secrets.toml` ファイルを作成：

```toml
[google_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "your-private-key"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

### 5. 実行

```bash
streamlit run app.py
```

## 📊 Google Sheets 設計

### シート1: 日記

| 列 | 内容 | 備考 |
|----|------|------|
| A | 日付 | YYYY-MM-DD |
| B | 曜日 | 自動付与 |
| C | 本文 | ユーザー入力テキスト |
| D | 気分スコア | 1〜5の整数 |
| E | 記録日時 | ISO8601形式 |

### シート2: コンテンツ台帳

| 列 | 内容 | 備考 |
|----|------|------|
| A | 日付 | YYYY-MM-DD |
| B | タイトル | 作品名 |
| C | ジャンル | 映画/展覧会/ライブ/本/配信 |
| D | メモ | 初回記録時の感想・一言メモ |
| E | mdパス | ローカルファイルパス。未作成は空欄 |
| F | 追記履歴 | 追記日時のログ（セミコロン区切り） |
| G | 記録日時 | ISO8601形式 |

### シート3: 情報クリップ

| 列 | 内容 | 備考 |
|----|------|------|
| A | 保存日時 | ISO8601形式 |
| B | URL | クリップ元URL |
| C | タイトル | ページタイトル（取得できれば） |
| D | 要約 | Claude APIによる3行要約 |
| E | トピック | CX/マーケ/DS/自動車/その他 |

### シート4: ToDo

| 列 | 内容 | 備考 |
|----|------|------|
| A | ID | 追加順の連番 |
| B | タスク名 | ユーザー入力テキスト |
| C | ステータス | 未完了/完了 |
| D | 優先度 | 高/中/低 |
| E | 期限日 | YYYY-MM-DD。未設定は空欄 |
| F | 作成日時 | ISO8601形式 |
| G | 完了日時 | 完了時のみ記録 |

## 📅 実装フェーズ

### Phase 1: 基本UI実装 ✅
- Streamlitアプリの基本構造
- トップバー、クイック入力エリア、タブシステム
- エントリーリスト表示とフィルタリング
- サマリーバー（カウント表示）

### Phase 2: Google Sheets 完全連携 ⏳
- Sheets API認証（Streamlit Secrets）
- 日記・コンテンツ・クリップ・ToDoの読み書き
- リアルタイム同期

### Phase 3: md管理とGit連携 ⏳
- mdファイルの新規作成・追記
- git commit の自動実行
- GitHub との同期

### Phase 4: Claude API連携 ⏳
- URL要約（情報クリップ）
- 日記振り返り生成
- トピック分類

### Phase 5: LINE連携（第2フェーズ） ⏳
- 既存LINE秘書Botとの統合
- GASスクリプト

## 🔗 参考資料

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Claude API Documentation](https://www.anthropic.com/claude/api)

## 📝 ライセンス

Private Project

## 👨‍💻 開発者

Yuya Hata (@yuyahata)
