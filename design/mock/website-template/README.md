# RealworldAgent Mock Frontend (Flask + Jinja2)

Flask + Jinja2テンプレートエンジンを使用したRealworldAgentのモックフロントエンドです。

## 特徴

- **共通コンポーネントの一元管理**: App Bar、ハンバーガーメニューなどを1箇所で管理
- **テンプレート継承**: Jinja2のテンプレート継承機能でDRY原則を実現
- **自動リロード**: デバッグモード有効時、変更が即座に反映される
- **Pythonでデータ管理**: モックデータをPythonの辞書/リストで型安全に管理

## ディレクトリ構造

```
website-template/
├── app.py                    # Flask アプリケーション
├── requirements.txt          # Python依存関係
├── templates/                # Jinja2 テンプレート
│   ├── base.html            # ベーステンプレート
│   ├── components/          # 共通コンポーネント
│   │   ├── app_bar.html     # App Bar
│   │   └── hamburger_menu.html  # ハンバーガーメニュー
│   ├── dashboard.html       # ダッシュボード
│   ├── projects.html        # プロジェクト一覧
│   ├── project_detail.html  # プロジェクト詳細
│   ├── meetings.html        # ミーティング一覧
│   ├── meeting_detail.html  # ミーティング詳細
│   ├── code_generation.html # コード生成状況
│   └── settings.html        # 設定
├── static/                  # 静的ファイル
│   ├── css/
│   │   └── styles.css       # スタイルシート
│   └── js/
│       └── common.js        # 共通JavaScript
└── data/                    # モックデータ
    ├── __init__.py
    └── mock_data.py         # モックデータとヘルパー関数
```

## セットアップ

### 1. 仮想環境の作成（推奨）

```bash
cd docs/design/mock/website-template
python -m venv venv
```

### 2. 仮想環境の有効化

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. 開発サーバーの起動

```bash
python app.py
```

ブラウザで `http://localhost:5001` にアクセス

## 使い方

### テンプレートの編集

テンプレートファイルを編集すると、デバッグモードで即座に反映されます（ブラウザでリフレッシュするだけ）。

#### 例：App Barの修正

```html
<!-- templates/components/app_bar.html を編集 -->
<header class="app-bar">
  <!-- 変更内容 -->
</header>
```

保存後、ブラウザをリフレッシュすると変更が反映されます。

### 新しいページの追加

#### 1. ルートを追加（app.py）

```python
@app.route('/new-page')
def new_page():
    return render_template(
        'new_page.html',
        active_page='new_page',
        notifications=mock_notifications,
        unread_count=len(MockDataHelpers.get_unread_notifications())
    )
```

#### 2. テンプレートを作成（templates/new_page.html）

```html
{% extends "base.html" %}

{% block title %}新しいページ - RealworldAgent{% endblock %}

{% block content %}
<main class="main-content">
  <div class="page-header">
    <h1 class="page-title">新しいページ</h1>
  </div>
  <!-- コンテンツ -->
</main>
{% endblock %}
```

### モックデータの編集

`data/mock_data.py` を編集してモックデータを追加・変更できます。

```python
# 新しいプロジェクトを追加
mock_projects.append({
    'id': 'project-delta-004',
    'name': 'ProjectDelta',
    'description': '新しいプロジェクト',
    # ...
})
```

## Jinja2 カスタムフィルター

### 日時フォーマット

```html
{{ meeting.date|format_datetime }}
<!-- 出力例: 2024年10月27日 14:00 -->

{{ meeting.date|format_relative_time }}
<!-- 出力例: 2時間前 -->
```

### scopeバッジ

```html
{{ meeting.scope|render_scope_badge }}
<!-- 出力例: <span class="scope-badge scope-badge-frontend">フロントエンド</span> -->
```

### scope表示名

```html
{{ meeting.scope|scope_display_name }}
<!-- 出力例: フロントエンド -->
```

## 開発のヒント

### 変更が反映されない場合

1. ブラウザのキャッシュをクリア（Ctrl+Shift+R / Cmd+Shift+R）
2. サーバーを再起動（Ctrl+Cで停止後、再度 `python app.py`）

### Python構文エラー

サーバー起動時にエラーが表示されます。エラーメッセージを確認して修正してください。

### CSSの変更

`static/css/styles.css` を編集してスタイルを変更できます。

### JavaScriptの変更

`static/js/common.js` を編集してインタラクションを変更できます。

## 既存HTMLとの違い

| 項目 | 既存HTML | Flask + Jinja2 |
|------|----------|----------------|
| 共通部分 | 各ファイルにコピー | テンプレート継承で1箇所管理 |
| データ | JavaScript (mock-data.js) | Python (mock_data.py) |
| 変更反映 | 手動で全ファイル編集 | 1箇所の変更で全体に反映 |
| リロード | 手動リフレッシュ | 自動リロード（デバッグモード） |

## 本番環境への移行

このモックは実際のAPIサーバーと置き換え可能です：

1. `mock_data.py` のデータをAPIエンドポイントに置き換え
2. `app.py` でAPIリクエストを実装
3. 認証機能を追加
4. Gunicornなどのプロダクションサーバーで起動

## トラブルシューティング

### ポート5001が使用中

別のポートで起動する場合：

```python
# app.py の最後の行を変更
app.run(host='0.0.0.0', port=8000, debug=True)
```

### 仮想環境が有効化されない

Windowsの場合、PowerShellで以下を実行：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## ライセンス

このプロジェクトのライセンスに従います。

