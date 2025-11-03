# RealworldAgent システム図

## 最終ゴール

**「ミーティングするだけで、AIが全オフィス作業を自動実行する世界」**

RealworldAgentは、Google Meetなどのオンラインミーティングや対面での会話から**意思決定・タスク・要求を自動抽出**し、**AIエージェントが人間の作業を完全自動化**するシステムです。

### 対応デバイス
- 🖥️ **オンライン**: Google Meet（音声・画面共有）- 録画後処理
- 👓 **対面**: [Mentra Glass](https://mentraglass.com/)（GPU非搭載スマートグラス）- リアルタイム処理
- 📹 **対面**: ioデバイス（Jony Ive × OpenAIのカメラ・音声AIデバイス）- リアルタイム処理
- ☁️ **処理**: GPU搭載サーバー（Modal）でリアルタイム推論

### 自動化される作業例
- ✅ **ソフトウェア開発**: コード生成・レビュー・デプロイ
- ✅ **営業活動**: メール送信・提案資料作成・顧客対応
- ✅ **ドキュメント作成**: 仕様書・プレゼン資料・議事録
- ✅ **プロジェクト管理**: タスク割り当て・進捗管理・レポート作成
- ✅ **データ分析**: 分析・レポート・可視化

### システムフロー概要
```
オンラインミーティング（Google Meet）/ 対面ミーティング（Mentra Glass, ioデバイス）
    ↓
音声・映像を解析
  - オンライン: 録画後に一括処理（3-10分）
  - 対面: リアルタイムストリーム処理（即座）
    ↓
【誰が・何を要求・どう決定・期限は？】を自動抽出
    ↓
現場や会話から仕様書を自動生成
    ↓
AIエージェントが自動実行
    ↓
✅ コード生成完了（GitHub PR）
✅ メール送信完了
✅ 資料作成完了
✅ タスク管理完了
```

---

## 技術実装詳細（現バージョン）

**現在の実装**: 
- **オンライン**: Google Meet録画からコード生成までを自動化（録画後処理）
- **対面**: Mentra Glass/ioデバイスからコード生成までをリアルタイム自動化

**処理方式の違い**:
- **オンライン（Google Meet）**: 録画後に一括処理（3-10分）- 高精度な議事録・スクリーンショット抽出
- **対面（Mentra Glass/io）**: リアルタイムストリーム処理（即座）- GPU非搭載デバイス + Modal GPU Server連携

**将来の拡張**: メール送信・営業活動・タスク管理等の全オフィス作業へ展開

---

## 1. ユースケース図

```mermaid
graph TB
    subgraph GoogleServices["Google Services"]
        GoogleMeet["📹 Google Meet<br/>(オンライン)"]
        GoogleDrive["☁️ Google Drive"]
    end
    
    subgraph InPersonDevices["対面デバイス"]
        MentraGlass["👓 Mentra Glass"]
        IoDevice["📹 ioデバイス"]
    end
    
    subgraph RWA["RealworldAgent"]
        UC1["🆕 プロジェクト作成"]
        UC2["📝 ミーティング議事録<br/>確認"]
        ModalGPU["☁️ Modal GPU Server<br/>(リアルタイム処理)"]
    end
    
    subgraph GitHub["GitHub"]
        UC3["🔧 コード生成/更新"]
        UC4["📋 仕様書確認"]
    end
    
    UserOnline["👥 オンライン参加者"]
    UserInPerson["👥 対面参加者"]
    Engineer["👨‍💻 エンジニア"]
    
    UserOnline -->|"参加・録画"| GoogleMeet
    GoogleMeet -->|"録画保存"| GoogleDrive
    GoogleDrive -->|"自動検知"| RWA
    
    UserInPerson -->|"装着・録画"| MentraGlass
    UserInPerson -->|"設置・録画"| IoDevice
    MentraGlass -->|"リアルタイム<br/>ストリーム"| ModalGPU
    IoDevice -->|"リアルタイム<br/>ストリーム"| ModalGPU
    ModalGPU -->|"即座に処理"| RWA
    
    UserOnline -->|"実行"| UC1
    UserOnline -->|"確認"| UC2
    UserInPerson -->|"確認"| UC2
    
    Engineer -->|"確認"| UC4
    Engineer -->|"確認"| UC3
    
    RWA -->|"議事録生成"| GitHub
    GitHub -->|"Doc保存"| UC4
    UC4 -->|"差分検出"| UC3
```

---

## ユースケース図の説明

### アクター

| アクター | 説明 | 確認可能な情報 |
|---------|------|---------|
| **オンライン参加者** | Google Meetに参加し、後でGoogle Drive上のGoogle Docsでミーティング議事録を確認できる | Google Drive（議事録・Google Docs） |
| **対面参加者** | Mentra Glass/ioデバイスを使用して対面ミーティングを実施し、リアルタイムで議事録が生成される | RealworldAgent（リアルタイム議事録） |
| **エンジニア** | GitHub経由でコードや仕様書の情報を確認・管理 | GitHub（仕様書・コード） |

---

### ユースケース一覧

| # | ユースケース | 説明 | アクター | 場所 |
|----|------------|------|---------|------|
| 1 | **プロジェクト作成** | 新しいプロジェクトを作成 | オンライン/対面参加者 | RealworldAgent |
| 2 | **Google Meet録画（オンライン）** | Google Meetでミーティング実施・録画 | オンライン参加者 | Google Meet |
| 3 | **録画自動検知（オンライン）** | Google Driveに保存された録画を自動検知 | システム | Google Drive → RealworldAgent |
| 4 | **リアルタイム録画（対面）** | Mentra Glass/ioデバイスでミーティング実施・リアルタイムストリーム送信 | 対面参加者 | デバイス → Modal GPU Server |
| 5 | **議事録取得・要求抽出** | 議事録を取得し、「誰が・何を要求・どう決定」を抽出（将来実装） | システム | RealworldAgent |
| 6 | **コード生成/更新** | 仕様書をベースにコード生成（初回）または更新（既存） | システム | GitHub |
| 7 | **仕様書確認** | GitHub内で仕様書を確認 | エンジニア | GitHub |
| 8 | **ミーティング議事録確認** | 議事録を確認（オンライン: Google Docs、対面: RealworldAgent） | オンライン/対面参加者 | Google Drive / RealworldAgent |

---

### ユースケース間の関係

**ユースケース遷移（オンライン）**:
```
オンライン参加者
    ↓
[Google Meet録画]
    ↓
[Google Drive保存]
    ↓
[RealworldAgent自動検知]
    ↓
[録画後処理・議事録生成] → GitHub保存
    ↓
[仕様書確認] (エンジニア)
    ↓
[コード生成/更新] (Cursor Agent)
    
議事録確認 ← Google Drive
(オンライン参加者)
```

**ユースケース遷移（対面）**:
```
対面参加者
    ↓
[Mentra Glass/ioデバイス装着・設置]
    ↓
[リアルタイムストリーム送信]
    ↓
[Modal GPU Server - リアルタイム処理]
    ↓
[議事録生成（即座）] → GitHub保存
    ↓
[仕様書確認] (エンジニア)
    ↓
[コード生成/更新] (Cursor Agent)
    
議事録確認 ← RealworldAgent
(対面参加者)
```

**オンライン（Google Meet）**:
- **Google Meet録画**: オンライン参加者がGoogle Meetでミーティング実施・録画
- **Google Drive保存**: 録画が自動的にGoogle Driveに保存
- **録画自動検知**: RealworldAgentがGoogle Drive Webhookで録画を検知
- **録画後処理**: 音声・映像解析→議事録生成→GitHub保存（3-10分）
- **議事録確認**: オンライン参加者がGoogle Drive上のGoogle Docsで議事録を後で確認

**対面（Mentra Glass/io）**:
- **リアルタイム録画**: 対面参加者がデバイスを装着・設置してミーティング実施
- **ストリーム送信**: デバイスがModal GPU Serverにリアルタイムストリーム送信
- **リアルタイム処理**: Modal GPU Serverで音声・映像を即座に解析→議事録生成→GitHub保存
- **議事録確認**: 対面参加者がRealworldAgent上で議事録を確認

**共通**:
- **仕様書確認**: エンジニアが GitHub 内で確認（議事録 + スクリーンショット）
- **コード生成/更新**: 仕様書をベースに、初回はコード生成、2回目以降は差分を検出してコード更新

---

## 2. ステートマシン図（システムライフサイクル）

```mermaid
stateDiagram-v2
    [*] --> Idle: システム起動
    
    Idle --> WatchingDrive: Google Drive監視開始（オンライン）
    Idle --> WaitingStream: デバイス接続待機（対面）
    
    state "オンライン処理（録画後）" as OnlineFlow {
        WatchingDrive --> MinutesDocsDetected: 議事録Docs検出
        WatchingDrive --> RecordingDetected: 録画検出
        
        state ProcessingDocs {
            MinutesDocsDetected --> FetchingGoogleDocs: Google Docs取得
            FetchingGoogleDocs --> ParsingDocs: 議事録パース
            ParsingDocs --> DocsComplete: 議事録取得完了
        }
        
        state ProcessingVideo {
            RecordingDetected --> DownloadingVideo: 動画ダウンロード
            DownloadingVideo --> AudioExtraction: 音声トラック抽出
            AudioExtraction --> SceneDetection: PySceneDetectでシーン検出
            SceneDetection --> DeepSeekOCR: DeepSeek OCR処理
            DeepSeekOCR --> VisionAnalysis: Vision分析（図表・UI検出）
            VisionAnalysis --> ImportanceScoring: 重要度スコアリング
            ImportanceScoring --> ScreenshotsComplete: スクショ抽出完了
        }
        
        DocsComplete --> WaitingForScreenshots
        ScreenshotsComplete --> WaitingForDocs
        
        WaitingForScreenshots --> IntegratingContent: 両方完了
        WaitingForDocs --> IntegratingContent: 両方完了
    }
    
    state "対面処理（リアルタイム）" as InPersonFlow {
        WaitingStream --> StreamingDetected: ストリーム検出
        
        state RealtimeProcessing {
            StreamingDetected --> RealtimeAudio: リアルタイム音声認識<br/>(Whisper API)
            StreamingDetected --> RealtimeVision: リアルタイム映像解析<br/>(DeepSeek OCR + Vision)
            RealtimeAudio --> RealtimeIntegration: 音声テキスト生成
            RealtimeVision --> RealtimeIntegration: 重要フレーム抽出
            RealtimeIntegration --> StreamComplete: ストリーム処理完了
        }
    }
    
    IntegratingContent --> DeterminingTargetDir
    StreamComplete --> DeterminingTargetDir
    
    DeterminingTargetDir --> CommittingDoc: scope判定完了
    
    CommittingDoc --> UpdatingSource: GitHub保存完了
    
    state UpdatingSource <<choice>>
    UpdatingSource --> UpdatingGoogleDocs: オンライン
    UpdatingSource --> DetectingDiff: 対面
    
    UpdatingGoogleDocs --> DetectingDiff: Google Docs更新完了
    
    DetectingDiff --> FirstDoc: 初回Doc
    DetectingDiff --> SubsequentDoc: 2回目以降
    
    FirstDoc --> GeneratingCodeInitial: 新規コード生成
    SubsequentDoc --> GeneratingCodeUpdate: コード更新生成
    
    GeneratingCodeInitial --> CallingCursorAgent
    GeneratingCodeUpdate --> CallingCursorAgent
    
    CallingCursorAgent --> CreatingPR: コード生成完了
    
    CreatingPR --> WaitingReview: PR作成完了
    
    WaitingReview --> Idle: レビュー完了
```

---

## ステートマシン図の説明

### 状態遷移

| 状態 | 説明 | 遷移先 |
|------|------|--------|
| **Idle** | 待機状態 | WatchingDrive（オンライン）/ WaitingStream（対面） |
| **WatchingDrive** | Google Drive監視中（オンライン） | MinutesDocsDetected / RecordingDetected |
| **WaitingStream** | デバイス接続待機（対面） | StreamingDetected |
| **StreamingDetected** | リアルタイムストリーム検出（対面） | RealtimeAudio / RealtimeVision |
| **RealtimeAudio** | リアルタイム音声認識処理（対面） | RealtimeIntegration |
| **RealtimeVision** | リアルタイム映像解析処理（対面） | RealtimeIntegration |
| **RealtimeIntegration** | リアルタイム統合処理（対面） | StreamComplete |
| **StreamComplete** | ストリーム処理完了（対面） | DeterminingTargetDir |
| **MinutesDocsDetected** | 議事録Docs検出 | FetchingGoogleDocs |
| **FetchingGoogleDocs** | Google Docs取得中 | ParsingDocs |
| **ParsingDocs** | 議事録パース中 | DocsComplete |
| **DocsComplete** | 議事録取得完了 | WaitingForScreenshots |
| **RecordingDetected** | 録画検出 | DownloadingVideo |
| **DownloadingVideo** | 動画ダウンロード中 | AudioExtraction |
| **AudioExtraction** | 音声トラック抽出中 | SceneDetection |
| **SceneDetection** | PySceneDetectシーン検出中 | DeepSeekOCR |
| **DeepSeekOCR** | DeepSeek OCR処理中 | VisionAnalysis |
| **VisionAnalysis** | Vision分析中（図表・UI検出） | ImportanceScoring |
| **ImportanceScoring** | 重要度スコアリング中 | ScreenshotsComplete |
| **ScreenshotsComplete** | スクショ抽出完了 | WaitingForDocs |
| **WaitingForScreenshots** | スクショ待機中（Docs完了済み） | IntegratingContent |
| **WaitingForDocs** | Docs待機中（スクショ完了済み） | IntegratingContent |
| **IntegratingContent** | 議事録+スクショ統合中 | DeterminingTargetDir |
| **DeterminingTargetDir** | scope判定中（Meeting名パース） | CommittingDoc |
| **CommittingDoc** | GitHub保存中 | UpdatingSource |
| **UpdatingSource** | 更新先判定 | UpdatingGoogleDocs（オンライン）/ DetectingDiff（対面） |
| **UpdatingGoogleDocs** | Google Docs更新中（オンライン） | DetectingDiff |
| **DetectingDiff** | Doc差分検出・判定 | FirstDoc / SubsequentDoc |
| **FirstDoc** | 初回Doc判定 | GeneratingCodeInitial |
| **SubsequentDoc** | 2回目以降Doc判定 | GeneratingCodeUpdate |
| **GeneratingCodeInitial** | 新規コード生成準備 | CallingCursorAgent |
| **GeneratingCodeUpdate** | 更新コード生成準備 | CallingCursorAgent |
| **CallingCursorAgent** | Cursor Agent API実行中 | CreatingPR |
| **CreatingPR** | PR作成中 | WaitingReview |
| **WaitingReview** | レビュー待ち | Idle |

### 重要な分岐点

1. **オンライン/対面の分岐（Idle）**
   - オンライン: Google Drive監視開始
   - 対面: デバイス接続待機

2. **オンライン処理（録画後・並列処理）**
   - **並列検出（WatchingDrive）**
     - 議事録Docs検出: Google Docs取得フロー開始
     - 録画検出: スクリーンショット抽出フロー開始
   - **並列処理の同期**
     - ProcessingDocs: Google Docs → パース → 完了
     - ProcessingVideo: 
       - 動画DL → 音声トラック抽出（Whisper API）
       - PySceneDetectでシーン検出
       - DeepSeek OCRでテキスト抽出
       - Vision APIで図表・UI検出
       - 重要度スコアリング → 完了
     - 両方完了後にコンテンツ統合へ

3. **対面処理（リアルタイム・並列処理）**
   - **ストリーム検出（StreamingDetected）**
     - リアルタイム音声認識: Whisper APIで即座に文字起こし
     - リアルタイム映像解析: DeepSeek OCR + Vision APIで重要フレーム抽出
   - **リアルタイム統合**
     - 音声テキスト + 重要フレーム → 即座に統合 → GitHub保存

4. **更新先判定（UpdatingSource）**
   - オンライン: Google Docs更新 → Doc差分検出
   - 対面: 直接Doc差分検出（Google Docs更新なし）

5. **Doc判定**
   - 初回Doc: すべての内容でコード生成
   - 2回目以降: 差分検出後にコード更新

---

## 3. Google Meet議事録取得 → GitHub保存フロー（オンライン）

```mermaid
sequenceDiagram
    participant User as ミーティング参加者
    participant Meet as Google Meet
    participant Docs as Google Docs
    participant Drive as Google Drive
    participant Webhook as Webhook Handler
    participant API as API Server
    participant Storage as Storage Service
    participant GPU as Modal GPU Server
    participant GitHub as GitHub
    
    User->>Meet: ミーティング実施
    Note over Meet: 議事録機能有効
    
    par Google Meet議事録
        Meet->>Docs: 議事録自動生成
        Docs->>Drive: Google Docs保存
        Drive->>Webhook: Push Notification<br/>(新規Docs検出)
    and 録画保存
        Meet->>Drive: 録画保存（.mp4）
        Drive->>Webhook: Push Notification<br/>(新規動画検出)
    end
    
    Webhook->>API: 議事録・録画検出通知
    
    par 議事録取得
        API->>Docs: Google Docs内容取得<br/>(Google Docs API)
        Docs-->>API: 議事録テキスト
        API->>API: Meeting名からプロジェクト名抽出
    and スクリーンショット抽出
        API->>Drive: 動画ファイルダウンロード
        Drive-->>API: 動画ファイル（.mp4）
        API->>Storage: 動画保存
        API->>GPU: スクリーンショット抽出リクエスト
        Note over GPU: 次のシーケンス図参照
        GPU-->>API: スクリーンショット一覧
    end
    
    API->>API: 議事録 + スクショ統合
    API->>API: Meeting名からscopeとディレクトリ判定<br/>(<ProjectName>_<scope>_<title>)
    
    par GitHub保存
        API->>GitHub: コミット<br/>{TargetDir}/Docs/Doc-{MeetingID}-{YYYYMMDD_HHMMSS}.md
        API->>GitHub: コミット<br/>{TargetDir}/Docs/images/Doc-{MeetingID}-{YYYYMMDD_HHMMSS}/
    and Google Docs更新
        API->>Docs: GitHubリンク追記<br/>(Google Docs API)
    end
    
    GitHub-->>API: コミット完了
    API-->>User: 議事録保存完了通知
```

---

## 4. 動画からスクリーンショット自動抽出フロー（オンライン - 改善版）

```mermaid
sequenceDiagram
    participant API as API Server
    participant GPU as Modal GPU Server
    participant PyScene as PySceneDetect
    participant Whisper as Whisper API<br/>(音声認識)
    participant DeepSeek as DeepSeek OCR
    participant Vision as Vision API<br/>(Claude/GPT-4V)
    participant LLM as LLM Service
    
    API->>GPU: フレーム抽出リクエスト<br/>(video_url)
    
    par 音声処理
        GPU->>Whisper: 音声トラック抽出 + 文字起こし
        Note over Whisper: タイムスタンプ付きテキスト生成
        Whisper-->>GPU: 音声テキスト<br/>(timestamp + text)
    and シーン検出
        GPU->>PyScene: シーン変化検出
        Note over PyScene: 適応的閾値 + コンテンツ検出
        PyScene-->>GPU: シーンチェンジ候補<br/>(timestamp + confidence)
    end
    
    GPU->>GPU: 候補フレーム統合<br/>(PyScene結果でフィルタリング)
    
    loop 各候補フレーム
        GPU->>DeepSeek: OCR実行<br/>(高精度テキスト抽出)
        DeepSeek-->>GPU: 抽出テキスト + 座標
        
        GPU->>GPU: 時刻前後の音声テキスト取得<br/>(±30秒)
        
        GPU->>Vision: マルチモーダル分析<br/>(図表・コード・UI要素検出)
        Vision-->>GPU: 視覚要素分析結果
        
        GPU->>LLM: 重要度スコアリング<br/>(OCR + 音声 + Vision結果)
        Note over LLM: キーワード: "仕様", "要件",<br/>"画面", "API", "フロー"等
        LLM-->>GPU: 重要度スコア (0-1)
        
        alt スコア > 0.65
            GPU->>GPU: スクリーンショット保存<br/>(メタデータ付き)
            Note over GPU: 音声コンテキスト,<br/>OCRテキスト,<br/>検出要素を含む
        end
    end
    
    GPU->>GPU: 類似画像除去<br/>(pHash比較)
    
    GPU->>GPU: タイムスタンプ付きメタデータ生成
    Note over GPU: {timestamp, image_path,<br/>ocr_text, audio_context,<br/>vision_elements, importance_score}
    
    GPU-->>API: スクリーンショット一覧<br/>(画像 + タイムスタンプ + リッチメタデータ)
```

---

## 5. 議事録処理履歴管理 → Cursor Agent連携フロー

```mermaid
sequenceDiagram
    participant GitHub as GitHub
    participant Webhook as GitHub Webhook
    participant ProcessingEngine as 処理履歴エンジン
    participant DB as Database<br/>(処理履歴)
    participant CursorAPI as Cursor Agent API
    participant GitHubCode as GitHub<br/>(コード保存)
    
    GitHub->>Webhook: Doc更新通知<br/>({TargetDir}/Docs/Doc-{MeetingID}-{DateTime}.md)
    Webhook->>ProcessingEngine: 新規Doc検出
    
    ProcessingEngine->>ProcessingEngine: パスからscope判定<br/>(Meeting名パース)
    
    ProcessingEngine->>DB: プロジェクトの処理履歴確認
    DB-->>ProcessingEngine: 処理済み議事録リスト<br/>(Doc-20241027_140000.md 等)
    
    ProcessingEngine->>ProcessingEngine: 今回のDocが処理済みかチェック
    
    alt 既に処理済み
        ProcessingEngine-->>Webhook: スキップ（処理済み）
    else 未処理
        ProcessingEngine->>GitHub: 新規Doc取得<br/>({TargetDir}/Docs/Doc-{MeetingID}-{DateTime}.md)
        GitHub-->>ProcessingEngine: Doc内容（議事録+スクショ）
        
        ProcessingEngine->>GitHub: 対象ディレクトリのコンテキスト取得<br/>({TargetDir}の既存コード・README)
        GitHub-->>ProcessingEngine: プロジェクト情報
        
        ProcessingEngine->>CursorAPI: コード生成リクエスト<br/>(Doc内容 + コンテキスト + 対象ディレクトリ)
        Note over CursorAPI: 初回: 新規セッション作成<br/>2回目以降: 既存セッションで更新
        CursorAPI->>CursorAPI: Background Agent起動
        CursorAPI->>CursorAPI: コード生成/更新<br/>({TargetDir}配下)
        CursorAPI-->>ProcessingEngine: 生成コード<br/>(複数ファイル)
        
        ProcessingEngine->>GitHubCode: ブランチ作成<br/>{TargetDir}/feature/update-from-{MeetingID}
        ProcessingEngine->>GitHubCode: ファイルコミット
        ProcessingEngine->>GitHubCode: Pull Request作成
        GitHubCode-->>ProcessingEngine: PR URL
        
        ProcessingEngine->>DB: 処理済みとして記録<br/>(Doc-{MeetingID}-{DateTime}.md + TargetDir)
        DB-->>ProcessingEngine: 記録完了
        
        ProcessingEngine-->>Webhook: 処理完了通知
    end
```

---

## 6. エンジニアとミーティング参加者による確認フロー

```mermaid
sequenceDiagram
    participant Engineer as エンジニア
    participant GitHub as GitHub
    participant CursorIDE as Cursor IDE
    participant User as ミーティング参加者
    participant Drive as Google Drive
    participant Docs as Google Docs
    
    Note over Engineer,GitHub: エンジニア: コード確認
    Engineer->>GitHub: PR確認<br/>{TargetDir}/feature/update-from-{MeetingID}
    GitHub-->>Engineer: 生成コード + 差分表示
    
    Engineer->>GitHub: 仕様書確認<br/>{TargetDir}/Docs/Doc-{MeetingID}-{DateTime}.md
    GitHub-->>Engineer: 議事録 + スクリーンショット
    
    Engineer->>CursorIDE: Cursor Agent履歴確認
    CursorIDE-->>Engineer: セッション情報<br/>(生成プロセス・プロンプト)
    
    alt 修正が必要
        Engineer->>CursorIDE: コード修正
        Engineer->>GitHub: 修正コミット
    end
    
    Engineer->>GitHub: PR承認・マージ
    
    Note over User,Docs: ミーティング参加者: 議事録確認
    User->>Drive: Google Drive開く
    Drive-->>User: Meet Recordingsフォルダ表示
    User->>Docs: 議事録Google Docs開く
    Docs-->>User: 議事録内容表示<br/>(GitHubリンク付き)
    
    opt GitHubで詳細確認
        User->>GitHub: GitHubリンクをクリック
        GitHub-->>User: Doc + スクリーンショット表示
    end
```

---

## フロー説明

### シーケンス3: Google Meet議事録取得からGitHub保存までの全体フロー
**目的**: Google Meet議事録とスクリーンショットを自動取得してGitHub保存  
**主要ステップ**:
1. Google Meetミーティング実施（議事録機能有効）
2. 並列生成:
   - Google Meetが議事録を自動生成 → Google Docsとして保存
   - 録画も自動保存（スクリーンショット用）
3. Google DriveのWebhookで新規Docs・録画を検出
4. 並列処理:
   - Google Docs APIで議事録テキスト取得
   - 録画からスクリーンショット自動抽出
5. Meeting名からプロジェクト名とscopeを自動抽出（`<ProjectName>_<scope>_<title>`形式）
6. 議事録とスクリーンショットを統合
7. GitHub に保存: `{TargetDir}/Docs/Doc-{MeetingID}-{YYYYMMDD_HHMMSS}.md` + `images/Doc-{MeetingID}-{YYYYMMDD_HHMMSS}/`
8. Google DocsにGitHubリンクを追記

**所要時間**: 3-10分（録画の長さに依存）

**特徴**:
- Google Meet標準の議事録機能を活用（高精度）
- Google DocsとGitHubの両方に保存（バックアップ）
- スクリーンショットで視覚情報を補完

---

### シーケンス4: 動画解析とスクリーンショット自動抽出の詳細（改善版）
**目的**: 動画から仕様書に適したスクリーンショットを自動抽出し、音声コンテキストと紐付け  

**主要ステップ**:
1. **並列処理開始**:
   - **音声処理**: Whisper APIで音声トラックを文字起こし（タイムスタンプ付き）
   - **シーン検出**: PySceneDetectで適応的閾値によるシーン変化検出（固定間隔ではない）
2. **候補フレーム統合**: PySceneDetectの結果でフレームをフィルタリング（不要フレーム削減）
3. **マルチモーダル解析**（各候補フレームに対して）:
   - **DeepSeek OCR**: 高精度テキスト抽出（座標付き）
   - **音声コンテキスト取得**: フレーム時刻の前後±30秒の音声テキスト
   - **Vision API分析**: 図表・コード・UI要素・ホワイトボードの検出
4. **LLMによる重要度スコアリング**:
   - 入力: OCRテキスト + 音声コンテキスト + Vision分析結果
   - キーワード重み付け: "仕様", "要件", "画面", "API", "フロー", "設計" 等
   - スコア閾値: 0.65以上を保存
5. **類似画像除去**: pHash（知覚ハッシュ）で重複スクリーンショット削除
6. **リッチメタデータ付きで保存**:
   - 画像ファイル、タイムスタンプ、OCRテキスト、音声コンテキスト、検出要素リスト、重要度スコア

**技術選定の理由**:

**PySceneDetect vs OpenCV-CUDA ヒストグラム比較**:
- ✅ **推奨: PySceneDetect**
  - 適応的閾値で動画特性に自動対応
  - コンテンツベースの検出でより高精度
  - 会議動画に最適化した閾値設定が容易（threshold=27-30）
  - 候補フレーム数を大幅削減（1/3〜1/5）
- ❌ OpenCV-CUDA ヒストグラム比較
  - 固定閾値で調整が必要
  - シンプルなヒストグラム比較で誤検出が多い
  - ただし、GPU並列処理が必要な場合は選択肢

**フレーム抽出間隔**:
- ❌ **固定5秒間隔は非推奨**
  - 重要なシーンを見逃す可能性
  - 不要なフレームも大量に抽出
- ✅ **PySceneDetectの適応的検出を推奨**
  - シーン変化を自動検出（間隔は可変）
  - 会議動画では平均10-20秒に1回程度のシーン変化
  - 処理効率が大幅に向上

**特徴**:
- PySceneDetectで賢くフィルタリング（固定間隔より効率的）
- DeepSeek OCRで高精度テキスト抽出
- マルチモーダル（画像 + 音声 + テキスト）で高精度判定
- 音声コンテキストで文脈を保持

---

### シーケンス5: 議事録処理履歴管理からコード生成までの自動化フロー
**目的**: 議事録更新を検知し、**未処理の議事録のみ**を自動でコード生成  

**Meeting名形式**: `<ProjectName>_<scope>_<title>`
- 例: `ProjectAlpha_frontend_LoginUI`, `ProjectAlpha_backend_API`, `ProjectAlpha_all_Architecture`

**scopeと対象ディレクトリ**:
- `frontend`: フロントエンドミーティング → `frontend/` 配下のコード生成
- `backend`: バックエンドミーティング → `backend/` 配下のコード生成
- `test`: テストミーティング → `test/` 配下のコード生成
- `all`: 開発全体ミーティング → プロジェクト全体のコード生成
- `management`: マネージャーミーティング → ドキュメント生成のみ（コード生成なし）

**主要ステップ**:
1. GitHub WebhookでDoc更新を検知
2. **処理履歴チェック**: データベースで処理済み議事録リストを確認
   - 例: `Doc-20241027_140000.md`, `Doc-20241028_150000.md` が処理済み
3. **今回のDocが処理済みか判定**:
   - **処理済みの場合**: スキップ（Cursor Agent APIに送信しない）
   - **未処理の場合**: 以下の処理を実行
4. 新規Doc取得（議事録+スクリーンショット）
5. プロジェクトコンテキスト取得（既存コード・README）
6. **Cursor Agent Background APIでコード生成/更新**:
   - **初回**: 新規セッション作成 → Background Agent起動 → コード生成 → **セッションID保存**
   - **2回目以降**: 前回の**セッションID**を使用 → 既存セッション内でコード更新生成
   - セッション内でプロジェクトコンテキストを保持（効率的）
7. GitHubにブランチ作成・コミット・PR作成
8. **処理済みとしてDB記録**: `Doc-{MeetingID}-{DateTime}.md`を処理済みリストに追加

**処理履歴データ構造**:
```json
{
  "project_id": "project_abc123",
  "project_name": "ProjectA",
  "repository_url": "github.com/supertask/ProjectA",
  "cursor_session_id": "session_abc123xyz",
  "processed_documents": [
    {
      "doc_filename": "Doc-meet_abc123-20241027_140000.md",
      "meeting_name": "ProjectA_backend_API",
      "scope": "backend",
      "target_directory": "backend",
      "processed_at": "2024-10-27T14:05:00Z",
      "pr_url": "https://github.com/supertask/ProjectA/pull/123"
    },
    {
      "doc_filename": "Doc-meet_def456-20241028_150000.md",
      "meeting_name": "ProjectA_frontend_LoginUI",
      "scope": "frontend",
      "target_directory": "frontend",
      "processed_at": "2024-10-28T15:08:00Z",
      "pr_url": "https://github.com/supertask/ProjectA/pull/124"
    }
  ]
}
```

**特徴**:
- **処理済み議事録はスキップ**: 日時Aが処理済みなら、日時Bのみを処理
- **重複処理を防止**: 同じ議事録を複数回Cursor Agent APIに送信しない
- **処理履歴を永続化**: データベースで処理済みリストを管理
- **初回/2回目以降を自動判定**: 処理履歴の有無でセッション管理
- **セッションIDを再利用**: 前回のセッション内でコード更新を継続的に生成
- 自動でPR作成まで完了

---

### シーケンス6: エンジニアとミーティング参加者による確認フロー
**目的**: エンジニアとミーティング参加者がそれぞれの視点で確認  
**主要ステップ**:

**エンジニア側**:
1. GitHubでPR確認（生成コード + 差分）
2. 仕様書確認（議事録 + スクリーンショット）
3. Cursor IDEでAgent履歴確認（生成プロセス）
4. 必要に応じて修正
5. PR承認・マージ

**ミーティング参加者側**:
1. Google Driveで「Meet Recordings」フォルダを開く
2. 議事録Google Docsを開く
3. 議事録内容確認（GitHubリンク付き）
4. 必要に応じてGitHubリンクからスクリーンショット含む詳細版を確認

**特徴**:
- エンジニアはGitHub/Cursor経由（コード中心）
- ミーティング参加者はGoogle Drive経由（議事録中心）
- Google DocsにGitHubリンクがあり、詳細確認も可能
- 役割に応じた確認フロー

---

## システム全体の特徴

### 現バージョンの自動化範囲（v1.0）
**実装済み**: Google Meetミーティング → 議事録・スクショ抽出 → コード生成

### 自動化されたワークフロー
1. **Google Meet議事録機能活用**: 標準機能で高精度な議事録を自動生成
2. **Google Docs + GitHub二重保存**: Google DocsとGitHubの両方に保存してバックアップ
3. **並列処理**: 議事録取得とスクリーンショット抽出を同時処理して効率化
4. **スマートなスクリーンショット抽出**: Vision APIとOCRで重要なフレームのみを自動選別
5. **差分ベースのコード更新**: 変更箇所のみをCursor Agentに送信
6. **Google Docs自動更新**: GitHubリンクを議事録に追記して連携

### データフロー

**オンライン（Google Meet）- 録画後処理**:
```
Google Meet会議
  ├─ 議事録機能（Google Docs自動生成）
  └─ 録画保存
      ↓
Google Drive保存（Docs + 録画）
      ↓
RealworldAgent検知（Webhook）
      ↓
並列処理（録画後・3-10分）
  ├─ Google Docs取得
  └─ スクリーンショット抽出
      ├─ PySceneDetect（シーン検出）
      ├─ Whisper API（音声認識）
      ├─ DeepSeek OCR（テキスト抽出）
      ├─ Vision API（視覚分析）
      └─ マルチモーダルLLM（重要度判定）
      ↓
議事録 + スクショ統合 + scope判定
      ↓
GitHub保存（{TargetDir}/Docs/Doc-{MeetingID}-{DateTime}.md）
  ※Meeting名: <ProjectName>_<scope>_<title>
  + 画像保存（{TargetDir}/Docs/images/Doc-{MeetingID}-{DateTime}/）
  + Google Docs更新（GitHubリンク追記）
      ↓
Doc差分検出
      ↓
Cursor Agent（コード生成/更新、対象ディレクトリ内）
      ↓
GitHub PR作成（{TargetDir}/feature/update-from-{MeetingID}）
```

**対面（Mentra Glass/io）- リアルタイム処理**:
```
対面ミーティング（Mentra Glass/ioデバイス）
      ↓
リアルタイムストリーム送信
  ├─ 音声ストリーム → Modal GPU Server
  └─ 映像ストリーム → Modal GPU Server
      ↓
並列リアルタイム処理（即座）
  ├─ リアルタイム音声認識（Whisper API）
  └─ リアルタイム映像解析
      ├─ リアルタイムシーン検出
      ├─ DeepSeek OCR（重要シーンのみ）
      ├─ Vision API（視覚分析）
      └─ マルチモーダルLLM（重要度判定）
      ↓
リアルタイム統合 + scope判定
      ↓
GitHub保存（{TargetDir}/Docs/Doc-{MeetingID}-{DateTime}.md）
  ※Meeting名: <ProjectName>_<scope>_<title>
  + 画像保存（{TargetDir}/Docs/images/Doc-{MeetingID}-{DateTime}/）
  （Google Docs更新なし）
      ↓
Doc差分検出
      ↓
Cursor Agent（コード生成/更新、対象ディレクトリ内）
      ↓
GitHub PR作成（{TargetDir}/feature/update-from-{MeetingID}）
```

### 役割分担
- **オンライン参加者**: Google Meetでミーティング実施、後でGoogle Drive上のGoogle Docsで議事録確認
- **対面参加者**: Mentra Glass/ioデバイスを装着・設置してミーティング実施、RealworldAgentで議事録確認
- **エンジニア**: GitHub/Cursorでコード確認・仕様書確認、PR承認
- **システム**: 完全自動処理（議事録検知/ストリーム処理→GitHub保存→コード生成）

### Google連携の特徴（オンライン）
- **Google Meet議事録**: 標準機能で高精度、今後さらに精度向上
- **Google Docs**: 議事録の一次保存先、GitHubリンクで連携
- **Google Drive**: Webhook通知で即座に検知
- **双方向同期**: Google Docs ⇔ GitHub の相互参照可能

### 対面デバイスの特徴
- **GPU非搭載**: Mentra Glass/ioデバイスはGPU非搭載（軽量・低消費電力）
- **リアルタイムストリーム**: 音声・映像をModal GPU Serverにリアルタイム送信
- **即座処理**: ミーティング終了と同時に議事録生成完了
- **ネットワーク最適化**: H.264/H.265圧縮でストリーミング（録画ダウンロードより軽量）
- **Modal GPU Server連携**: すべての重い処理（OCR、Vision、LLM）をクラウドGPUで実行

---

## 将来の拡張計画（Full Version）

### フェーズ2: 意思決定・タスク抽出エンジン
**目的**: ミーティングから「誰が・何を要求・どう決定・期限」を自動抽出

**実装予定**:
1. **要求者識別**: 話者分離 + 発話内容から要求者を特定
2. **決定事項抽出**: 「〜することに決定」「〜で進めます」を検出
3. **期限推論**: 「来週まで」「月末まで」を具体的日付に変換
4. **作業分類**: 開発 / メール / 資料作成 / 管理業務 に自動分類

**抽出データ構造例**:
```json
{
  "meeting_id": "meet_abc123",
  "decisions": [
    {
      "time": "00:12:34",
      "requester": "田中さん (営業)",
      "content": "ログイン機能を来週までに実装してほしい",
      "decision": "承認 - エンジニアが対応",
      "deadline": "2024-11-03",
      "priority": "high",
      "task_type": "software_development"
    }
  ]
}
```

### フェーズ3: AIエージェント自動実行
**目的**: 抽出されたタスクをAIエージェントが自動実行

**実装予定エージェント**:

| エージェント | 役割 | 自動化される作業 |
|------------|------|----------------|
| **コード開発エージェント** | ソフトウェア開発 | コード生成・PR作成・テスト・デプロイ |
| **メールエージェント** | 営業・連絡 | メール文面生成・送信・フォローアップ |
| **ドキュメント作成エージェント** | 資料作成 | 仕様書・提案資料・プレゼン資料・レポート |
| **タスク管理エージェント** | プロジェクト管理 | タスク割り当て・進捗管理・リスク検出・レポート |

**実行フロー例**:
```
ミーティング終了
    ↓
タスク抽出完了（3分後）
    ↓
並列実行:
  ├─ CodeAgent: ログイン機能実装 → GitHub PR作成
  ├─ EmailAgent: A社へ報告メール送信
  ├─ DocAgent: API仕様書作成
  └─ TaskAgent: タスク管理・進捗レポート
    ↓
全作業完了（数時間後）
    ↓
Slack通知: 「全タスク完了しました🎉」
```

### フェーズ4: 完全自動化オフィス
**目標**: 人間は意思決定と承認のみ、実行はすべてAI

**実装予定機能**:
- 📧 **自動営業**: CRM連携・顧客分析・提案資料作成・商談スケジューリング
- 📊 **自動分析**: データ収集・分析・可視化・レポート作成
- 🤖 **マルチエージェント協調**: エージェント間の自動連携・最適スケジューリング
- ⚠️ **リスク検出**: 納期遅延・予算超過の自動警告・代替案提示
- 📝 **自動見積**: 要求から自動見積書・契約書作成

### ロードマップ
```
v1.0 (現在) ✅
  ├─ オンライン: Google Meet → 議事録・スクショ → コード生成（録画後処理）
  └─ 対面: Mentra Glass/io → 議事録・スクショ → コード生成（リアルタイム処理）

v2.0 (次期)
  └─ 意思決定・タスク抽出エンジン追加（オンライン・対面両対応）

v3.0
  └─ AIエージェント自動実行（メール・資料作成・タスク管理）

v4.0 (最終形)
  └─ 完全自動化オフィス（営業・分析・全業務自動化）
```

**最終ゴール達成時の世界**:
- エンジニアがコードを書く必要なし
- 営業がメールを書く必要なし
- PMがタスクを管理する必要なし
- **人間は意思決定と承認だけ、実行はすべてAI**

これがRealworldAgentの目指す未来です。

---

## 7. 対面ミーティング リアルタイム解析フロー

### 7-1. 対面ミーティング全体フロー

```mermaid
sequenceDiagram
    participant User as 対面参加者
    participant Device as Mentra Glass/<br/>ioデバイス
    participant API as API Server
    participant GPU as Modal GPU Server
    participant Whisper as Whisper API<br/>(リアルタイム音声認識)
    participant DeepSeek as DeepSeek OCR
    participant Vision as Vision API<br/>(Claude/GPT-4V)
    participant GitHub as GitHub
    
    User->>Device: デバイス装着・起動
    Device->>API: デバイス接続通知
    API->>GPU: リアルタイム処理セッション開始
    
    User->>Device: 対面ミーティング開始
    Note over Device: 音声・映像を<br/>リアルタイム録画
    
    par リアルタイム音声処理
        loop 音声ストリーム
            Device->>GPU: 音声ストリーム送信<br/>(継続的)
            GPU->>Whisper: リアルタイム文字起こし
            Whisper-->>GPU: タイムスタンプ付きテキスト
            GPU->>API: 音声テキスト保存<br/>(バッファリング)
        end
    and リアルタイム映像処理
        loop 映像ストリーム
            Device->>GPU: 映像ストリーム送信<br/>(継続的)
            GPU->>GPU: リアルタイムシーン検出<br/>(PySceneDetect相当)
            
            alt 重要シーン検出
                GPU->>DeepSeek: OCR実行<br/>(リアルタイム)
                DeepSeek-->>GPU: 抽出テキスト + 座標
                
                GPU->>Vision: マルチモーダル分析<br/>(図表・コード・UI検出)
                Vision-->>GPU: 視覚要素分析結果
                
                GPU->>GPU: 重要度スコアリング<br/>(OCR + 音声コンテキスト)
                
                alt スコア > 0.65
                    GPU->>API: 重要フレーム保存<br/>(メタデータ付き)
                end
            end
        end
    end
    
    User->>Device: ミーティング終了
    Device->>API: ストリーム終了通知
    
    API->>API: 音声テキスト + 重要フレーム統合
    API->>API: Meeting名からscopeとディレクトリ判定
    
    API->>GitHub: コミット<br/>{TargetDir}/Docs/Doc-{MeetingID}-{YYYYMMDD_HHMMSS}.md
    API->>GitHub: コミット<br/>{TargetDir}/Docs/images/Doc-{MeetingID}-{YYYYMMDD_HHMMSS}/
    
    GitHub-->>API: コミット完了
    API-->>User: 議事録生成完了通知<br/>(リアルタイム完了)
```

### 7-2. オンラインと対面の処理方式の違い

| 項目 | オンライン（Google Meet） | 対面（Mentra Glass/io） |
|------|------------------------|----------------------|
| **処理タイミング** | 録画後に一括処理 | リアルタイムストリーム処理 |
| **処理時間** | 3-10分（録画長に依存） | 即座（ストリーム終了時） |
| **音声認識** | 録音ファイル → Whisper API | リアルタイムストリーム → Whisper API |
| **シーン検出** | PySceneDetect（一括処理） | リアルタイムシーン検出 |
| **OCR処理** | 全フレーム候補を一括処理 | 重要シーンのみリアルタイム処理 |
| **重要度判定** | 全候補フレームを一括スコアリング | 検出シーンごとにリアルタイムスコアリング |
| **議事録保存先** | Google Docs + GitHub | GitHub（リアルタイム生成） |
| **デバイス要件** | GPU不要（ブラウザのみ） | GPU非搭載デバイス + Modal GPU Server |
| **ネットワーク** | 録画ダウンロード（大容量） | ストリーミング（継続的・軽量） |
| **精度** | 高精度（後処理で最適化） | 高精度（リアルタイムでも同等） |

### 7-3. リアルタイム処理の技術的特徴

**ストリーミング音声認識**:
- Whisper APIのストリーミングモード利用
- バッファリング: 音声を30秒単位でバッファリング → API送信
- タイムスタンプ同期: 映像フレームと音声テキストを時刻で同期

**リアルタイムシーン検出**:
- PySceneDetectアルゴリズムのリアルタイム実装
- 適応的閾値: 環境に応じてリアルタイムで閾値調整
- 候補フレーム即座判定: シーン変化を検出した瞬間にOCR・Vision処理へ

**リアルタイム重要度判定**:
- 音声コンテキスト: 前後30秒の音声テキストをバッファから取得
- マルチモーダルLLM: OCRテキスト + 音声 + Vision結果で即座にスコアリング
- 閾値判定: スコア > 0.65 で即座に保存

**GPU非搭載デバイス + Modal GPU Server連携**:
- デバイス側: 音声・映像の録画・ストリーム送信のみ
- Modal GPU Server: すべての重い処理（OCR、Vision、LLM）を実行
- 低レイテンシ: Modal GPU Serverの高速GPUで即座に処理

**ネットワーク最適化**:
- 映像圧縮: H.264/H.265でストリーム圧縮
- 音声圧縮: Opus/AACで低ビットレート
- バッファリング: ネットワーク遅延に対応

**処理完了タイミング**:
- オンライン: ミーティング終了 → 録画完了 → ダウンロード → 処理（3-10分後）
- 対面: ミーティング終了 → ストリーム終了通知 → 統合・保存（即座）

---

## 8. Webアプリケーション構成

### バックエンド構成

RealworldAgentのバックエンドは3つの主要サービスで構成されています。

```mermaid
graph TB
    subgraph Backend["Backend Services"]
        API["API Server<br/>(Node.js + Express)"]
        GPU["GPU Server<br/>(Modal + Python)"]
        DB[("PostgreSQL<br/>(Prisma ORM)")]
        Storage["File Storage<br/>(Local/Cloud)"]
    end
    
    subgraph ExternalServices["External Services"]
        Google["Google APIs<br/>(Drive, Docs, Meet)"]
        GitHub["GitHub API"]
        CursorAPI["Cursor Agent API"]
        Whisper["Whisper API<br/>(音声認識)"]
        DeepSeek["DeepSeek OCR"]
        Vision["Vision API<br/>(Claude/GPT-4V)"]
    end
    
    API --> DB
    API --> Storage
    API --> GPU
    API --> Google
    API --> GitHub
    API --> CursorAPI
    
    GPU --> Whisper
    GPU --> DeepSeek
    GPU --> Vision
    GPU --> Storage
```

**API Server** (`services/api-server/`):
- Express.js + TypeScript
- PostgreSQL (Prisma ORM)
- REST API エンドポイント提供
- Google Drive Webhook受信（オンライン）
- デバイスストリーム受信（対面）
- GitHub Webhook受信

**GPU Server** (`services/gpu-server/`):
- Modal.com でホスティング
- Python + PySceneDetect
- 動画処理・スクリーンショット抽出（オンライン - 録画後処理）
- リアルタイムストリーム処理（対面 - リアルタイム処理）
- マルチモーダルAI処理（Whisper API、DeepSeek OCR、Vision API）

**データベース** (PostgreSQL):
```prisma
model Project {
  id                String      @id @default(uuid())
  name              String
  description       String?
  cursorSessionId   String?     // Cursor Agent セッションID
  repositoryUrl     String      // github.com/supertask/<プロジェクト名>
  documents         Document[]
  processingHistory ProcessingHistory[]
  createdAt         DateTime    @default(now())
}

model Document {
  id                String               @id @default(uuid())
  projectId         String
  meetingId         String
  meetingName       String               // <ProjectName>_<scope>_<title>
  meetingType       String               // online/in_person
  scope             String               // frontend/backend/test/all/management
  targetDirectory   String               // frontend/backend/test など
  filename          String               // Doc-{MeetingID}-{DateTime}.md
  googleDriveUrl    String?              // Google Drive議事録URL（オンラインのみ）
  githubUrl         String               // GitHub Doc URL
  screenshotUrls    Json                 // スクリーンショットURL配列
  processingStatus  String               // pending/processing/processed/skipped
  createdAt         DateTime             @default(now())
  project           Project              @relation(fields: [projectId], references: [id])
  processingHistory ProcessingHistory[]
}

model ProcessingHistory {
  id          String   @id @default(uuid())
  projectId   String
  documentId  String
  status      String   // processed/skipped
  prUrl       String?  // GitHub PR URL (モノレポ内の該当ディレクトリ)
  processedAt DateTime @default(now())
  project     Project  @relation(fields: [projectId], references: [id])
  document    Document @relation(fields: [documentId], references: [id])
}
```

---

### フロントエンド構成（設計）

RealworldAgentのフロントエンドは、**Google Meetミーティング → 議事録・コード生成までの自動化フロー**を視覚化・管理する**最小限のインターフェース**です。

**設計方針**:
- 外部サービス（Google Drive、GitHub）で賄えるものは外部リンクのみ提供
- 自動化フローの**進捗状況・ステータス監視**に特化
- 設定・連携管理を簡潔に

```mermaid
graph TB
    subgraph Frontend["Web Client (apps/web-client/)"]
        Index["index.html<br/>🏠 ダッシュボード"]
        
        subgraph ProjectFlow["プロジェクトフロー"]
            ProjectCreate["プロジェクト作成画面<br/>📝 新規プロジェクト"]
            ProjectList["プロジェクト一覧<br/>📁 全プロジェクト表示"]
            ProjectDetail["プロジェクト詳細<br/>📊 進行状況・履歴"]
        end
        
        subgraph MeetingFlow["ミーティングフロー"]
            MeetingList["ミーティング一覧<br/>📹 プロジェクト内のミーティング"]
            VideoAnalysis["動画解析状況<br/>🎬 処理進捗・ログ"]
        end
        
        subgraph CodeGenFlow["コード生成フロー"]
            ProcessingStatus["処理状況画面<br/>🔍 議事録処理履歴"]
            CodeGenStatus["コード生成状況<br/>⚙️ Cursor Agent進捗"]
            PRView["PR確認画面<br/>✅ 生成PR・コード確認"]
        end
        
        subgraph SettingsFlow["設定・連携"]
            GoogleAuth["Google連携設定<br/>🔐 OAuth認証"]
            GitHubAuth["GitHub連携設定<br/>🔐 Token設定"]
            WebhookConfig["Webhook設定<br/>📡 通知エンドポイント"]
        end
    end
    
    Index --> ProjectList
    Index --> MeetingList
    
    ProjectList --> ProjectCreate
    ProjectList --> ProjectDetail
    
    ProjectDetail --> MeetingList
    ProjectDetail --> CodeGenStatus
    
    MeetingList --> VideoAnalysis
    MeetingList --> ProcessingStatus
    VideoAnalysis --> ProcessingStatus
    ProcessingStatus --> CodeGenStatus
    CodeGenStatus --> PRView
    
    Index --> GoogleAuth
    Index --> GitHubAuth
    Index --> WebhookConfig
```

---

### フロントエンドページ詳細（設計）

| ページ | 説明 | 主要機能 | 連携 |
|--------|------|---------|------|
| **ダッシュボード** | システム全体の概要表示 | ・最近のミーティング<br/>・進行中のコード生成<br/>・通知一覧 | API Server |
| **プロジェクト作成** | 新規プロジェクト登録 | ・プロジェクト名入力<br/>・GitHub Repository設定<br/>・初期設定 | GitHub API |
| **プロジェクト一覧** | 全プロジェクト管理 | ・プロジェクト検索<br/>・ステータス表示<br/>・削除・編集 | API Server |
| **プロジェクト詳細** | プロジェクト進行状況 | ・議事録履歴（オンライン: Google Driveリンク、対面: RealworldAgent）<br/>・生成コード履歴<br/>・Cursor Agentセッション情報 | API Server + GitHub |
| **ミーティング一覧** | プロジェクト内のミーティング一覧（オンライン・対面両方） | ・プロジェクトでフィルタリング済み<br/>・ミーティングタイプ表示（オンライン/対面）<br/>・処理ステータス<br/>・議事録リンク（オンライン: Drive、対面: RealworldAgent）<br/>・プロジェクト内のみ表示 | API Server + Google Drive API |
| **動画解析状況** | スクリーンショット抽出進捗 | ・オンライン: PySceneDetect進捗<br/>・対面: リアルタイム処理進捗<br/>・OCR処理状況<br/>・重要度スコア一覧<br/>・エラーログ | GPU Server |
| **処理状況画面** | 議事録処理履歴管理 | ・処理済み議事録一覧<br/>・未処理議事録一覧<br/>・処理日時・セッションID<br/>・スキップ/処理ボタン | API Server |
| **コード生成状況** | Cursor Agent実行進捗 | ・Background API進捗<br/>・リアルタイムログ<br/>・生成ファイル一覧 | Cursor Agent API |
| **PR確認画面** | 生成されたPRの確認 | ・GitHub PR表示<br/>・差分確認<br/>・承認・却下 | GitHub API |
| **Google連携設定** | Google OAuth設定（オンライン） | ・認証フロー<br/>・Drive Webhook設定<br/>・権限管理 | Google OAuth |
| **GitHub連携設定** | GitHub Token設定 | ・Personal Access Token<br/>・Repository選択<br/>・Webhook設定 | GitHub OAuth |
| **デバイス連携設定** | 対面デバイス設定 | ・Mentra Glass/ioデバイス登録<br/>・ストリーム接続設定<br/>・Modal GPU Server設定 | API Server |
| **Webhook設定** | 通知エンドポイント管理 | ・Google Drive Webhook URL（オンライン）<br/>・GitHub Webhook URL<br/>・デバイスストリームエンドポイント（対面）<br/>・Secret設定 | API Server |

---

### フロントエンド技術スタック

**開発環境**:
- Vite (ビルドツール)
- TypeScript
- HTML5 + CSS3

**主要ライブラリ**:
```json
{
  "dependencies": {
    "axios": "HTTP通信",
    "marked": "Markdown表示",
    "highlight.js": "シンタックスハイライト"
  }
}
```

**共通スタイル** (`styles.css`):
- モダンなダークテーマUI
- レスポンシブデザイン
- カード型レイアウト

**共通ロジック** (`app.ts`):
- API通信処理
- 認証・セッション管理
- エラーハンドリング

---

### フロントエンドユーザーフロー（設計）

**シナリオ1: 初回プロジェクトセットアップ**

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Dashboard as ダッシュボード
    participant GoogleAuth as Google連携設定
    participant GitHubAuth as GitHub連携設定
    participant DeviceAuth as デバイス連携設定
    participant ProjectCreate as プロジェクト作成
    participant ProjectDetail as プロジェクト詳細
    
    User->>Dashboard: 初回アクセス
    Dashboard-->>User: セットアップガイド表示
    
    alt オンライン設定
        User->>GoogleAuth: Google認証
        GoogleAuth->>GoogleAuth: OAuth認証フロー
        GoogleAuth-->>User: 認証完了・Webhook設定
    end
    
    alt 対面設定
        User->>DeviceAuth: デバイス連携設定
        DeviceAuth->>DeviceAuth: Mentra Glass/ioデバイス登録
        DeviceAuth-->>User: デバイス登録完了・ストリーム設定
    end
    
    User->>GitHubAuth: GitHub認証
    GitHubAuth->>GitHubAuth: Token設定
    GitHubAuth-->>User: Repository選択
    
    User->>ProjectCreate: 新規プロジェクト作成
    ProjectCreate-->>User: プロジェクト名・Repository入力
    User->>ProjectCreate: 作成実行
    ProjectCreate->>ProjectDetail: プロジェクト詳細へ遷移
    
    ProjectDetail-->>User: プロジェクト情報・ガイド表示<br/>「Google Meetでミーティングを開始するか、<br/>対面デバイスを装着してください」
```

**シナリオ2: ミーティング → コード生成までの自動フロー確認**

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Dashboard as ダッシュボード
    participant ProjectDetail as プロジェクト詳細
    participant MeetingList as ミーティング一覧<br/>（プロジェクト内）
    participant GoogleDrive as Google Drive<br/>(外部)
    participant VideoAnalysis as 動画解析状況
    participant ProcessingStatus as 処理状況画面
    participant CodeGenStatus as コード生成状況
    participant PRView as PR確認画面
    
    Note over User: ミーティング実施<br/>（オンライン: Google Meet / 対面: Mentra Glass/io）<br/>（バックグラウンドで自動処理）
    
    User->>Dashboard: ダッシュボード確認
    Dashboard-->>User: 「新規ミーティング検出」通知表示<br/>ProjectA: 新しいミーティング（オンライン/対面）
    
    User->>ProjectDetail: プロジェクト詳細へ
    ProjectDetail-->>User: プロジェクト情報・進行状況表示
    
    User->>MeetingList: 「ミーティング一覧」をクリック
    MeetingList-->>User: 処理中のミーティング表示<br/>【ProjectA内のみ】<br/>「オンライン: 録画検出 → 動画解析中」<br/>「対面: リアルタイム処理中」<br/>+ 議事録リンク（オンライン: Drive、対面: RealworldAgent）<br/>+ プロジェクト内のミーティングのみ表示
    
    opt 議事録確認（外部サービス）
        User->>GoogleDrive: 議事録Driveリンクをクリック
        GoogleDrive-->>User: Google Docs議事録表示
    end
    
    User->>VideoAnalysis: 解析状況確認
    VideoAnalysis-->>User: オンライン:<br/>・PySceneDetect進捗: 85%<br/>・OCR処理: 完了<br/>・重要度スコアリング: 進行中<br/><br/>対面:<br/>・リアルタイム処理: 進行中<br/>・ストリーム接続: 正常
    
    Note over VideoAnalysis: 処理完了後
    
    User->>ProcessingStatus: 処理状況画面へ
    ProcessingStatus-->>User: ・【ProjectA】の議事録一覧表示<br/>・Doc-20241027_140000: ✅処理済み<br/>・Doc-20241028_150000: ⏳未処理<br/>・Doc-20241029_160000: ⏳未処理
    
    Note over ProcessingStatus: システムは未処理の議事録のみを<br/>Cursor Agent APIに送信
    
    User->>CodeGenStatus: コード生成状況確認
    CodeGenStatus-->>User: ・【ProjectA】のCursor Agent進捗<br/>・リアルタイムログ<br/>・生成ファイル一覧
    
    Note over CodeGenStatus: コード生成完了後
    
    CodeGenStatus->>PRView: PR確認画面へ自動遷移
    PRView-->>User: ・GitHub PR表示<br/>・生成コード差分<br/>・承認ボタン
    
    User->>PRView: PR確認・承認
    PRView-->>User: 「マージ完了」通知
```

---

### デプロイ構成

**開発環境**:
```bash
# API Server
cd services/api-server
npm run dev  # http://localhost:3000

# Web Client
cd apps/web-client
npm run dev  # http://localhost:5173

# GPU Server (Modal)
cd services/gpu-server
modal serve modal_app.py
```

**本番環境**:
```
Frontend (Web Client)
  └─ Vercel / Netlify
      └─ Static Site Hosting

Backend (API Server)
  └─ Railway / Render
      └─ Node.js Server
      └─ PostgreSQL Database

GPU Server
  └─ Modal.com
      └─ Serverless Python Functions
```

---
