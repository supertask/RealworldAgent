// アプリケーション状態
let appState = {
    selectedFile: null,
    videoId: null,
    currentMinutes: null,
    minutesMarkdown: null,
    transcriptMarkdown: null,
    downloadUrl: null,
    isProcessing: false,
    debugConfig: null
};

// DOM要素
const uploadArea = document.getElementById('upload-area');
const videoInput = document.getElementById('video-input');
const fileInfo = document.getElementById('file-info');
const processBtn = document.getElementById('process-btn');
const uploadSection = document.getElementById('upload-section');
const processingSection = document.getElementById('processing-section');
const resultSection = document.getElementById('result-section');
const historySection = document.getElementById('history-section');

// イベントリスナー設定
document.addEventListener('DOMContentLoaded', async () => {
    await loadDebugConfig();
    setupEventListeners();
    loadOutputsList();
});

// config.jsonからデバッグ設定を読み込み
async function loadDebugConfig() {
    try {
        // Flaskから設定を取得するAPIエンドポイントを追加する必要があります
        // 以下は仮のローカルストレージ取得
        console.log('🔧 デバッグ設定を読み込み中...');
        // 後でバックエンドから取得するように変更
    } catch (error) {
        console.error('❌ デバッグ設定の読み込みエラー:', error);
    }
}

function setupEventListeners() {
    // ファイルアップロード - シンプルな直接バインド
    const videoInput = document.getElementById('video-input');
    if (videoInput) {
        videoInput.addEventListener('change', function(e) {
            console.log('🔔 change イベント発火');
            handleFileSelect(e);
        }, false);
        console.log('✅ videoInput にイベントリスナー登録完了');
    } else {
        console.error('❌ video-input 要素が見つかりません');
    }

    // 処理ボタン
    const processBtn = document.getElementById('process-btn');
    if (processBtn) {
        processBtn.addEventListener('click', processVideo);
        console.log('✅ processBtn にイベントリスナー登録完了');
    }

    // タブ切り替え
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            switchTab(e.target.dataset.tab);
        });
    });

    // ダウンロードボタン
    const downloadBtn = document.getElementById('download-md-btn');
    const newVideoBtn = document.getElementById('new-video-btn');
    if (downloadBtn) downloadBtn.addEventListener('click', downloadMarkdown);
    if (newVideoBtn) newVideoBtn.addEventListener('click', resetForm);
}

function handleFileSelect(e) {
    console.group('📁 ファイル選択処理開始');
    console.log('イベント:', e);
    console.log('ファイル数:', e.target.files.length);
    
    if (e.target.files.length === 0) {
        console.warn('⚠️ ファイルが選択されていません');
        console.groupEnd();
        return;
    }

    const file = e.target.files[0];
    console.log('選択されたファイル:', file);
    
    handleFiles(file);
    console.groupEnd();
}

function handleFiles(file) {
    console.log('📄 handleFiles 呼び出し:', file.name);
    
    const fileExtension = file.name.split('.').pop().toLowerCase();
    const allowedExtensions = ['mp4', 'mov', 'avi', 'mkv', 'webm'];

    console.log('ファイル情報:', {
        name: file.name,
        type: file.type,
        size: `${(file.size / 1024 / 1024).toFixed(2)} MB`,
        extension: fileExtension
    });

    // 拡張子チェック
    if (!allowedExtensions.includes(fileExtension)) {
        console.error('❌ 形式エラー:', fileExtension);
        alert(`許可されていない形式です: .${fileExtension}\n対応形式: ${allowedExtensions.join(', ')}`);
        return;
    }

    // サイズチェック
    if (file.size > 500 * 1024 * 1024) {
        console.error('❌ サイズエラー:', file.size);
        alert('ファイルサイズは500MB以下である必要があります');
        return;
    }

    console.log('✅ ファイルが有効です');
    appState.selectedFile = file;

    // プレビュー表示
    const fileReader = new FileReader();
    fileReader.onload = function(e) {
        console.log('📹 プレビュー読み込み完了');
        document.getElementById('video-preview').src = e.target.result;
    };
    fileReader.onerror = function() {
        console.error('❌ ファイル読み込みエラー');
    };
    fileReader.readAsDataURL(file);

    // ファイル情報表示
    document.getElementById('file-name').textContent = file.name;
    document.getElementById('file-size').textContent = formatFileSize(file.size);
    document.getElementById('file-info').style.display = 'block';
    document.getElementById('process-btn').style.display = 'block';

    console.log('✅ UI 更新完了');
    updateProgressStep(1);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

async function processVideo() {
    console.group('🚀 動画処理開始');
    
    if (!appState.selectedFile) {
        console.error('❌ ファイルが選択されていません');
        console.groupEnd();
        alert('ファイルを選択してください');
        return;
    }

    console.log('📁 選択ファイル:', appState.selectedFile.name);

    appState.isProcessing = true;
    processBtn.disabled = true;

    try {
        // ファイルアップロード
        console.log('📤 ファイルをアップロード中...');
        const formData = new FormData();
        formData.append('video', appState.selectedFile);

        const uploadResponse = await fetch('/api/process-video', {
            method: 'POST',
            body: formData
        });

        console.log('📊 アップロードレスポンス:', uploadResponse.status);

        if (!uploadResponse.ok) {
            const errorData = await uploadResponse.json();
            console.error('❌ アップロード失敗:', errorData);
            throw new Error(errorData.error || 'ファイルのアップロードに失敗しました');
        }

        const uploadData = await uploadResponse.json();
        console.log('✅ アップロード成功:', uploadData);
        appState.videoId = uploadData.video_id;

        // UI更新
        uploadSection.style.display = 'none';
        processingSection.style.display = 'block';
        updateProgressStep(2);

        // シミュレート処理ステップ
        console.log('⏳ 処理ステップをシミュレート中...');
        await simulateProcessingSteps();

        // アノテーション進捗監視（有効な場合）
        if (appState.videoId) {
            startAnnotationProgressPolling(appState.videoId);
        }

        // 議事録生成
        console.log('🧠 議事録を生成中...');
        await generateMinutes();

        console.log('✅ 処理完了');

    } catch (error) {
        console.error('❌ エラーが発生しました:', error);
        alert('処理中にエラーが発生しました: ' + error.message);
        resetForm();
    } finally {
        appState.isProcessing = false;
        processBtn.disabled = false;
        console.groupEnd();
    }
}

async function simulateProcessingSteps() {
    try {
        // サーバーからconfig.jsonを取得
        const response = await fetch('/api/debug-config');
        const config = await response.json();
        
        const steps = [
            { id: 'step-audio', name: '音声抽出', enabled: config.audio_extraction_enabled },
            { id: 'step-transcribe', name: '文字起こし', enabled: config.transcription_enabled },
            { id: 'step-keyframes', name: 'キーフレーム抽出', enabled: config.scene_detection_enabled },
            { id: 'step-annotation', name: 'アノテーション', enabled: config.annotation_enabled },
            { id: 'step-generate', name: '議事録生成', enabled: config.minutes_generation_enabled }
        ];

        for (const step of steps) {
            const element = document.getElementById(step.id);
            
            if (!step.enabled) {
                // 無効な場合はスキップ表示
                element.style.opacity = '0.5';
                element.style.textDecoration = 'line-through';
                element.querySelector('.status-icon').textContent = '—';
                console.log(`⏭️  ${step.name}: スキップ (設定で無効化)`);
                continue;
            }
            
            await new Promise(resolve => setTimeout(resolve, 1500));
            element.classList.add('completed');
            element.querySelector('.status-icon').textContent = '✓';
            console.log(`✅ ${step.name}: 完了`);
        }
    } catch (error) {
        console.error('❌ デバッグ設定の取得に失敗:', error);
        // フォールバック：すべてのステップを表示
        const steps = [
            { id: 'step-audio', name: '音声抽出' },
            { id: 'step-transcribe', name: '文字起こし' },
            { id: 'step-keyframes', name: 'キーフレーム抽出' },
            { id: 'step-generate', name: '議事録生成' }
        ];
        
        for (const step of steps) {
            const element = document.getElementById(step.id);
            await new Promise(resolve => setTimeout(resolve, 1500));
            element.classList.add('completed');
            element.querySelector('.status-icon').textContent = '✓';
        }
    }
}

async function generateMinutes() {
    try {
        const response = await fetch(`/api/generate-minutes/${appState.videoId}`);

        if (!response.ok) {
            throw new Error('議事録の生成に失敗しました');
        }

        const data = await response.json();
        appState.currentMinutes = data.minutes;
        appState.minutesMarkdown = data.minutes_markdown;
        appState.transcriptMarkdown = data.transcript_markdown;
        appState.downloadUrl = data.download_url;

        // UI更新
        displayMinutes(data.minutes, data.minutes_markdown, data.transcript_markdown);
        processingSection.style.display = 'none';
        resultSection.style.display = 'block';
        updateProgressStep(3);

        // 出力一覧を更新
        loadOutputsList();

    } catch (error) {
        console.error('エラー:', error);
        alert('議事録の生成に失敗しました: ' + error.message);
    }
}

function displayMinutes(minutes, minutesMarkdown, transcriptMarkdown) {
    // プレビュータブ
    const preview = document.getElementById('minutes-preview');
    preview.innerHTML = renderMinutesPreview(minutes);

    // 議事録Markdownタブ
    document.getElementById('markdown-content').value = minutesMarkdown;
    
    // 文字起こしMarkdownタブ（新規追加）
    const transcriptTab = document.getElementById('transcript-content');
    if (transcriptTab) {
        transcriptTab.value = transcriptMarkdown;
    }

    // JSONタブ
    document.getElementById('json-content').value = JSON.stringify(minutes, null, 2);
}

function renderMinutesPreview(minutes) {
    let html = `
        <h3>📋 ${minutes.title}</h3>
        <p><strong>日時:</strong> ${minutes.date} ${minutes.time}</p>
        
        <h3>サマリー</h3>
        <p>${minutes.summary.replace(/\n/g, '<br>')}</p>
    `;

    if (minutes.sections && minutes.sections.length > 0) {
        html += '<h3>議事録内容</h3>';
        minutes.sections.forEach((section, index) => {
            html += `
                <div style="margin: 1rem 0; padding: 1rem; background: #f3f4f6; border-radius: 8px;">
                    <strong>[${section.time}]</strong>
                    <p>${section.content}</p>
                </div>
            `;
        });
    }

    if (minutes.action_items && minutes.action_items.length > 0) {
        html += '<h3>アクションアイテム</h3><ul>';
        minutes.action_items.forEach(item => {
            html += `<li>${item.description}</li>`;
        });
        html += '</ul>';
    }

    if (minutes.notes) {
        html += `<h3>備考</h3><p>${minutes.notes}</p>`;
    }

    return html;
}

function switchTab(tabName) {
    // タブボタンの更新
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // タブコンテンツの更新
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');
}

async function downloadMarkdown() {
    if (!appState.downloadUrl) {
        console.error('❌ ダウンロードURLがありません');
        alert('ダウンロードURLが見つかりません');
        return;
    }

    try {
        console.log('📥 ZIPダウンロード開始:', appState.downloadUrl);
        
        // ダウンロード実行（議事録・文字起こし・画像を含むZIPファイル）
        const link = document.createElement('a');
        link.href = appState.downloadUrl;
        link.download = `output_${appState.videoId.replace('.', '_')}.zip`;
        link.click();
        
        console.log('✅ ZIPダウンロード完了');
    } catch (error) {
        console.error('❌ ダウンロードエラー:', error);
        alert('ダウンロードに失敗しました: ' + error.message);
    }
}

function resetForm() {
    appState = {
        selectedFile: null,
        videoId: null,
        currentMinutes: null,
        minutesMarkdown: null,
        transcriptMarkdown: null,
        downloadUrl: null,
        isProcessing: false
    };

    // UI リセット
    uploadArea.classList.remove('dragover');
    videoInput.value = '';
    fileInfo.style.display = 'none';
    processBtn.style.display = 'none';
    processBtn.disabled = false;
    uploadSection.style.display = 'block';
    processingSection.style.display = 'none';
    resultSection.style.display = 'none';

    // ステップリセット
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active', 'completed');
    });
    document.getElementById('step-1').classList.add('active');

    // 処理ステップリセット
    document.querySelectorAll('.processing-step').forEach(step => {
        step.classList.remove('completed');
        const icon = step.querySelector('.status-icon');
        icon.textContent = '⏳';
    });
}

async function loadOutputsList() {
    try {
        const response = await fetch('/api/list-outputs');
        const data = await response.json();

        const outputsList = document.getElementById('outputs-list');

        if (data.outputs.length === 0) {
            outputsList.innerHTML = '<p style="grid-column: 1/-1;">生成済み議事録がありません</p>';
            return;
        }

        outputsList.innerHTML = '';
        data.outputs.forEach(output => {
            const date = new Date(output.modified);
            const dateStr = date.toLocaleDateString('ja-JP');
            const timeStr = date.toLocaleTimeString('ja-JP');

            const item = document.createElement('div');
            item.className = 'output-item';
            item.innerHTML = `
                <div class="output-item-name">📄 ${output.filename}</div>
                <div class="output-item-meta">
                    <div>サイズ: ${formatFileSize(output.size)}</div>
                    <div>生成: ${dateStr} ${timeStr}</div>
                </div>
                <a href="${output.url}" class="output-item-link" download>
                    📥 ダウンロード
                </a>
            `;
            outputsList.appendChild(item);
        });
    } catch (error) {
        console.error('出力一覧取得エラー:', error);
    }
}

function updateProgressStep(stepNumber) {
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active', 'completed');
    });

    for (let i = 1; i < stepNumber; i++) {
        document.getElementById(`step-${i}`).classList.add('completed');
    }

    document.getElementById(`step-${stepNumber}`).classList.add('active');
}

// アノテーション進捗のポーリング
let annotationProgressInterval = null;

function startAnnotationProgressPolling(videoId) {
    console.log('📊 アノテーション進捗監視開始:', videoId);
    
    const annotationStep = document.getElementById('step-annotation');
    const progressContainer = document.getElementById('annotation-progress');
    const progressBar = document.getElementById('progress-bar-fill');
    const progressText = document.getElementById('progress-text');
    const detailsList = document.getElementById('progress-details-list');
    
    if (!annotationStep || !progressContainer) {
        console.warn('⚠️ アノテーション進捗要素が見つかりません');
        return;
    }
    
    // 進捗表示を有効化
    progressContainer.style.display = 'block';
    annotationStep.classList.add('active');
    
    // ポーリング開始
    annotationProgressInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/annotation-progress/${videoId}`);
            const progress = await response.json();
            
            if (progress.status === 'in_progress' || progress.status === 'completed') {
                // 進捗バー更新
                const percentage = progress.percentage || 0;
                progressBar.style.width = percentage + '%';
                
                // テキスト更新
                progressText.textContent = 
                    `バッチ ${progress.current_batch} / ${progress.total_batches} 処理中 (${progress.completed_frames}/${progress.total_frames}フレーム完了)`;
                
                // ステップアイコン更新
                if (progress.status === 'completed') {
                    annotationStep.classList.add('completed');
                    annotationStep.querySelector('.status-icon').textContent = '✓';
                    clearInterval(annotationProgressInterval);
                    annotationProgressInterval = null;
                    console.log('✅ アノテーション完了');
                } else {
                    annotationStep.querySelector('.status-icon').textContent = '⏳';
                }
            } else if (progress.status === 'not_started') {
                // まだ開始していない
                progressText.textContent = 'アノテーション待機中...';
            }
        } catch (error) {
            console.error('❌ 進捗取得エラー:', error);
        }
    }, 1000); // 1秒ごとにポーリング
}

// 定期的に出力一覧を更新
setInterval(() => {
    if (!appState.isProcessing) {
        loadOutputsList();
    }
}, 5000);

