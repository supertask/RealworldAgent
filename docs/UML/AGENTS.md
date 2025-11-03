# エージェント

- エージェントは、画像とテキストのルールを参考に入出力を行う
- 入出力はエージェントによって変えられる


```mermaid
mindmap
  root((エージェント))
    共通エージェント
      PMエージェント
      議事録エージェント
      コーディングエージェント
        フロントエンドエージェント
        バックエンドエージェント
        IoTエージェント
      調査エージェント
      プロモーションエージェント
      3Dエージェント
        CADエージェント
    プロジェクト別拡張
      Project A
        ⤷ PMエージェントを拡張
        ⤷ CADエージェントを拡張
      Project B
        ⤷ 議事録エージェントを拡張

```




## 議事録エージェント

```mermaid
flowchart LR
    subgraph Input["入力"]
        SG[🎥 Smart Glass<br/>（スマートグラス）]
        IO[📎 ioデバイス<br/>（ペンダント）]
        GM[💻 Google Meet<br/>（オンライン会議）]
    end

    API[🤖 議事録エージェント<br/>（AI要約・動画解析）]

    subgraph Output["出力"]
        Storage[📂 議事録ストレージ<br/>（Drive / GitHub / Notion）]
    end

    %% 動作（矢印上に記載）
    SG -->|"映像・音声をリアルタイム送信"| API
    IO -->|"映像・音声をリアルタイム送信"| API
    GM -->|"録画データを送信"| API
    API -->|"画像つき議事録を生成・保存"| Storage
```

### 実現方法

**オンライン（Google Meet）**:
- Google Meet録画 → Google Drive保存 → Webhook検知
- 並列処理: Google Docs議事録取得 + 動画からスクリーンショット抽出
- スクリーンショット抽出: PySceneDetect（シーン検出） → DeepSeek OCR（テキスト抽出） → Vision API（図表検出） → LLM（重要度スコアリング）
- 統合: 議事録 + スクリーンショット → GitHub保存（`{TargetDir}/Docs/Doc-{MeetingID}-{DateTime}.md`）

**対面（Mentra Glass/ioデバイス）**:
- デバイス → Modal GPU Serverへリアルタイムストリーム送信（音声・映像）
- 並列リアルタイム処理: Whisper API（音声認識） + リアルタイムシーン検出 → DeepSeek OCR → Vision API → LLM
- 統合: 音声テキスト + 重要フレーム → GitHub保存（即座）

## PMエージェント

```mermaid
flowchart LR
    %% --- 入力 ---
    subgraph Input["入力"]
        G[📘 議事録ストレージ<br/>（Google Drive / Notion）]
        M[✉️ メール / Slack<br/>（依頼・報告メッセージ）]
    end

    %% --- 中央処理 ---
    MA[🤖 PMエージェント<br/>（タスク整理・要件定義・指示出し）]

    %% --- 出力 ---
    subgraph Output["出力"]
        TODO[📝 ToDoリスト<br/>（チームタスク管理）]
        SPEC[📄 仕様書ストレージ<br/>（Notion / Google Drive / GitHub）]
        MAIL[📨 メール / Slack<br/>（依頼・報告送信）]
    end

    %% --- 矢印上に動作を明記 ---
    G -->|"画像付き議事録を受信"| MA
    M -->|"依頼・報告メッセージを受信"| MA
    MA -->|"タスクリストを保存"| TODO
    MA -->|"画像付き仕様書を生成"| SPEC
    MA -->|"担当者へ依頼メール送信"| MAIL
```



## 調査エージェント


```mermaid

flowchart LR
    %% --- 入力 ---
    subgraph Input["入力"]
        WEB[🔗 Web / APIレスポンス<br/>（検索・スクレイピング結果）]
        PROMPT[🧠 調査プロンプト（PMエージェント）<br/>（タスクベースの調査指示）]
        INSIGHT[💡 気づき<br/>（議事録×調査プロンプトの関連情報）]
    end

    %% --- 中央処理 ---
    RA[🧠 調査エージェント<br/>（DeepResearch）]

    %% --- 出力 ---
    subgraph Output["出力"]
        NOTION[📘 Notion 知識ノート<br/>（長期保存・チーム共有）]
        SLACK[💬 Slack通知 / ToDo生成<br/>（アクション連携）]
        DRIVE[📂 Google Drive<br/>（PDF・Markdown出力）]
        SHEET[📊 Google Sheets / Excel<br/>（定量比較・表形式）]
        MD[🧾 Markdown / GitHub Wiki<br/>（技術・調査ドキュメント）]
        DASH[📈 ダッシュボード更新<br/>（PowerBI / Lookerなど）]
    end

    %% --- 矢印（動作） ---
    WEB -->|"Web検索情報を取得"| RA
    PROMPT -->|"調査テーマ・条件を受信"| RA
    INSIGHT -->|"関連キーワード・状況を追加反映"| RA

    RA -->|"知識を整理しNotionへ保存"| NOTION
    RA -->|"調査結果をSlack連携"| SLACK
    RA -->|"資料をDriveに出力"| DRIVE
    RA -->|"比較表をSheetsで生成"| SHEET
    RA -->|"Markdownレポートを作成"| MD
    RA -->|"可視化ツールを更新"| DASH

```

### 定期的に調査

- 「figure03, 1x, tesla optimusのような人型ロボットをゼロから作りたいので、figure03, 1x, tesla optimusから出ている情報から必要なハードウェアやソフトウェアのコンポーネントを見つけてきて。」
    - この目的を達成するために、気づきを議事録（Smartglasses, web会議）から引っ張ってきてもらい、それを検索プロンプトに自動で入れられるように、かつそのプロンプトを管理サイトなどで可視化できるようにする
    - 1) Google Meetで「Optimusの関節トルク推定が不安定」と報告。 
      - → 調査観点に「関節トルク推定方式」「アクチュエータ制御方式」を追加。
    - 2) Smart Glass現場メモで「重心制御が難しい」と記録。
      - → 調査観点に「二足歩行時の重心制御」「ZMP制御」「足裏センサ」を追加。


### 一時的に調査

- PMエージェントから出てきたタスクリストに応じて、調査をする


## コーディングエージェント

```mermaid
flowchart LR
    %% --- 入力 ---
    subgraph Input["入力"]
        SPEC[📄 仕様書 / 要件定義書<br/>（Notion / Google Drive / GitHub）]
        ISSUE[🧾 チケット / ToDoリスト<br/>（PMエージェントからの指示）]
    end

    %% --- 中央処理 ---
    CA[💻 コーディングエージェント<br/>（Cursor）]

    %% --- 出力 ---
    subgraph Output["出力"]
        CODE[🧠 ソースコード<br/>（GitHubリポジトリ）]
        PR[🔀 プルリクエスト<br/>（自動レビュー / 修正提案）]
        TEST[🧪 テスト結果<br/>（CI / Cursor内検証）]
        DOCS[📄 技術ドキュメント<br/>（README / Wiki / API Docs）]
        REPORT[📊 進捗レポート<br/>（PMエージェント / Slack通知）]
    end

    %% --- 矢印（動作） ---
    SPEC -->|"仕様を読み取り実装計画を生成"| CA
    ISSUE -->|"タスク内容を解析"| CA

    CA -->|"コードを自動生成・更新"| CODE
    CA -->|"PRを作成・レビュー依頼"| PR
    CA -->|"テストを実行・結果を出力"| TEST
    CA -->|"技術ドキュメントを生成"| DOCS
    CA -->|"進捗レポートを通知"| REPORT
```

### 実現方法

- GitHub Webhookで議事録更新検知 → 処理履歴DB確認（未処理のみ処理）
- **Cursor Agent Background API**でコード生成/更新
  - 初回: 新規セッション作成 → コード生成 → セッションID保存
  - 2回目以降: セッションID再利用 → 既存コード更新（連続的に改善）
- scope別制御（`frontend/`、`backend/`、`test/`）→ GitHub PR自動作成


## フロントエンド・デザインエージェント


```mermaid
flowchart LR
    %% 入力
    subgraph Input["入力"]
        SPEC[仕様書 / 要件定義書]
        ISSUE[チケット / ToDoリスト]
        DSYS[既存のデザイン・コンポーネント]
        REFDESIGN[参考デザイン]
        STORY[絵コンテ / スケッチ / ユーザーストーリー]
    end

    %% 中央処理
    DA[フロントエンド・デザインエージェント]

    %% 出力
    subgraph Output["出力"]
        FIG[Figmaファイル<br/>ワイヤー / UIフロー / モック / プロトタイプ]
        ASSET[アセット書き出し<br/>画像 / アイコン / ロッティ]
        DOCS[ガイドライン / コンポーネント辞書]
    end

    %% 矢印（処理内容）
    DSYS -->|"既存ルール/コンポーネント参照"| DA
    SPEC -->|"仕様を読み取り設計方針作成"| DA
    ISSUE -->|"タスク内容を分解・分析"| DA
    REFDESIGN -->|"参考デザインを反映"| DA
    STORY -->|"ユーザーシナリオに基づき構成"| DA

    DA -->|"ワイヤー / UIフロー / プロトタイプ生成"| FIG
    DA -->|"アセットを最適化・書き出し"| ASSET
    DA -->|"デザインルールを文書化"| DOCS
```

デザインをきっちり決める必要がある社外に展開するWEBサイト・CMS・ECサイトなどは、こちらのデザインエージェントを使う。


## エージェントの共通実装




