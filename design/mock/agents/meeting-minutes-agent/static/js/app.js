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
            const tabName = e.target.dataset.tab;
            // アクティブなタブボタンを更新
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            switchTab(tabName);
        });
    });

    // ダウンロードボタン
    const downloadBtn = document.getElementById('download-md-btn');
    const newVideoBtn = document.getElementById('new-video-btn');
    if (downloadBtn) downloadBtn.addEventListener('click', downloadMarkdown);
    if (newVideoBtn) newVideoBtn.addEventListener('click', resetForm);
    
    // モーダルのイベントリスナー
    const modal = document.getElementById('file-view-modal');
    const modalClose = document.getElementById('modal-close');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const modalTabBtns = document.querySelectorAll('.modal-tab-btn');
    
    if (modalClose) {
        modalClose.addEventListener('click', closeFileModal);
    }
    
    if (modalCloseBtn) {
        modalCloseBtn.addEventListener('click', closeFileModal);
    }
    
    // モーダル外をクリックで閉じる
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeFileModal();
            }
        });
    }
    
    // モーダルタブ切り替え（削除 - 新しい2段階タブ方式に置き換え）
    // モーダルファイルタイプタブ
    document.querySelectorAll('.modal-file-tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            switchModalFileTab(e.target.dataset.fileType);
        });
    });
    
    // モーダル表示形式タブ
    document.querySelectorAll('.modal-view-tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            switchModalViewTab(e.target.dataset.viewType);
        });
    });
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

        // 処理進捗監視を開始
        if (appState.videoId) {
            startProcessingProgressPolling(appState.videoId);
        }

        // 議事録生成（非同期で実行）
        console.log('🧠 議事録を生成中...');
        generateMinutes().catch(error => {
            console.error('❌ 議事録生成エラー:', error);
            alert('議事録の生成に失敗しました: ' + error.message);
        });

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

function startProcessingProgressPolling(videoId) {
    // アノテーション進捗監視も開始（詳細な進捗表示用）
    startAnnotationProgressPolling(videoId);
    console.log('📊 処理進捗監視開始:', videoId);
    
    const stepMapping = {
        'audio_extraction': 'step-audio',
        'transcription': 'step-transcribe',
        'keyframe_extraction': 'step-keyframes',
        'annotation': 'step-annotation',
        'minutes_generation': 'step-generate'
    };
    
    // ポーリング開始
    processingProgressInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/processing-progress/${videoId}`);
            const progress = await response.json();
            
            // 各ステップの状態を更新
            for (const [key, stepId] of Object.entries(stepMapping)) {
                const stepInfo = progress[key];
                const element = document.getElementById(stepId);
                
                if (!element) continue;
                
                if (!stepInfo || !stepInfo.enabled) {
                    // 無効な場合はスキップ表示
                    element.style.opacity = '0.5';
                    element.style.textDecoration = 'line-through';
                    const icon = element.querySelector('.status-icon');
                    if (icon) icon.textContent = '—';
                    continue;
                }
                
                // ステータスに応じてアイコンを更新
                const icon = element.querySelector('.status-icon');
                if (!icon) continue;
                
                if (stepInfo.status === 'completed') {
                    element.classList.add('completed');
                    icon.textContent = '✓';
                } else if (stepInfo.status === 'in_progress') {
                    element.classList.remove('completed');
                    icon.textContent = '⏳';
                } else if (stepInfo.status === 'skipped') {
                    element.style.opacity = '0.5';
                    icon.textContent = '—';
                } else {
                    // not_started
                    element.classList.remove('completed');
                    icon.textContent = '⏳';
                }
            }
            
            // すべてのステップが完了したらポーリングを停止
            const allCompleted = Object.entries(stepMapping).every(([key, stepId]) => {
                const stepInfo = progress[key];
                const element = document.getElementById(stepId);
                
                // 無効化されているステップは完了とみなす
                if (!stepInfo || !stepInfo.enabled) {
                    return true;
                }
                
                // ステップが完了しているかチェック
                return element && element.classList.contains('completed');
            });
            
            if (allCompleted && processingProgressInterval) {
                clearInterval(processingProgressInterval);
                processingProgressInterval = null;
                console.log('✅ すべての処理が完了しました');
            }
        } catch (error) {
            console.error('❌ 進捗取得エラー:', error);
        }
    }, 500); // 0.5秒ごとにポーリング
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
        appState.enhancedTranscriptMarkdown = data.enhanced_transcript_markdown;
        appState.transcriptMarkdown = data.transcript_markdown;
        appState.downloadUrl = data.download_url;

        // 進捗ポーリングを停止
        if (processingProgressInterval) {
            clearInterval(processingProgressInterval);
            processingProgressInterval = null;
        }
        if (annotationProgressInterval) {
            clearInterval(annotationProgressInterval);
            annotationProgressInterval = null;
        }

        // UI更新（モーダル表示）
        displayMinutes(data.minutes, data.minutes_markdown, data.enhanced_transcript_markdown, data.transcript_markdown);
        processingSection.style.display = 'none';
        
        // 生成完了後、モーダルで表示
        showGeneratedMinutesModal(appState.videoId, data.enhanced_transcript_markdown, data.minutes_markdown);
        
        updateProgressStep(3);

        // 出力一覧を更新
        loadOutputsList();

    } catch (error) {
        console.error('エラー:', error);
        alert('議事録の生成に失敗しました: ' + error.message);
        
        // エラー時もポーリングを停止
        if (processingProgressInterval) {
            clearInterval(processingProgressInterval);
            processingProgressInterval = null;
        }
        if (annotationProgressInterval) {
            clearInterval(annotationProgressInterval);
            annotationProgressInterval = null;
        }
    }
}

function displayMinutes(minutes, minutesMarkdown, enhancedTranscriptMarkdown, transcriptMarkdown) {
    // 画像付き文字起こしのマークダウン
    const enhancedTranscriptMd = document.getElementById('enhanced-transcript-md-content');
    if (enhancedTranscriptMd && enhancedTranscriptMarkdown) {
        enhancedTranscriptMd.value = enhancedTranscriptMarkdown;
    }
    
    // 画像付き文字起こしのプレビュー
    if (enhancedTranscriptMarkdown) {
        renderMarkdown(enhancedTranscriptMarkdown, 'enhanced-transcript-preview');
    }
    
    // 議事録のマークダウン
    const minutesMd = document.getElementById('minutes-md-content');
    if (minutesMd && minutesMarkdown) {
        minutesMd.value = minutesMarkdown;
    }
    
    // 議事録のプレビュー
    if (minutesMarkdown) {
        renderMarkdown(minutesMarkdown, 'minutes-preview');
    }
    
    // JSON
    const jsonContent = document.getElementById('json-content');
    if (jsonContent) {
        jsonContent.value = JSON.stringify(minutes, null, 2);
    }
}

function renderMarkdown(markdown, containerId, videoId = null) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // videoIdが指定されていない場合は、appStateから取得を試みる
    const finalVideoId = videoId || appState.videoId;
    
    // marked.jsでMarkdownをHTMLに変換
    if (typeof marked !== 'undefined') {
        const html = marked.parse(markdown);
        // DOMPurifyでサニタイズ
        if (typeof DOMPurify !== 'undefined') {
            container.innerHTML = DOMPurify.sanitize(html);
        } else {
            container.innerHTML = html;
        }
        
        // 画像パスを修正（相対パスをAPI経由に）
        const images = container.querySelectorAll('img');
        images.forEach(img => {
            const src = img.getAttribute('src');
            if (src && !src.startsWith('http') && !src.startsWith('/api/')) {
                // 画像パスをAPI経由に変換
                if (finalVideoId) {
                    img.setAttribute('src', `/api/get-image/${finalVideoId}/${src}`);
                }
            }
        });
    } else {
        container.innerHTML = '<pre>' + escapeHtml(markdown) + '</pre>';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function switchTab(tabName) {
    // タブボタンの更新
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    if (event && event.target) {
        event.target.classList.add('active');
    }

    // タブコンテンツの更新
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    const targetTab = document.getElementById(`tab-${tabName}`);
    if (targetTab) {
        targetTab.classList.add('active');
    }
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
        enhancedTranscriptMarkdown: null,
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
            outputsList.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-secondary); font-size: 1.1rem;">📭 生成済み議事録がありません<br><span style="font-size: 0.9rem; margin-top: 0.5rem; display: block;">動画をアップロードして議事録を生成してください</span></p>';
            return;
        }

        outputsList.innerHTML = '';
        data.outputs.forEach(output => {
            const date = new Date(output.modified);
            const dateStr = date.toLocaleDateString('ja-JP');
            const timeStr = date.toLocaleTimeString('ja-JP');

            // ファイルタイプの日本語名マッピング
            const fileTypeNames = {
                'minutes': '議事録',
                'enhanced_transcript': '文字&シーン起こし',
                'transcript': '文字起こし',
                'legacy': 'ファイル'
            };

            const item = document.createElement('div');
            item.className = 'output-item';
            
            // 利用可能なファイルタイプのリストを作成
            const fileTypesList = Object.keys(output.available_files || {}).map(fileType => {
                const fileInfo = output.available_files[fileType];
                const typeName = fileTypeNames[fileType] || fileType;
                const viewUrl = output.video_id 
                    ? `/api/view-file/${output.video_id}/${fileType}`
                    : `/api/view-file/${fileInfo.filename || fileType}`;
                return `<a href="#" class="file-type-link" data-view-url="${viewUrl}" data-download-url="${fileInfo.url}">${typeName}</a>`;
            }).join(' | ');

            item.innerHTML = `
                <div class="output-item-name">📋 ${output.display_name || output.video_id || '不明'}</div>
                <div class="output-item-meta">
                    <div><strong>サイズ:</strong> ${formatFileSize(output.size)}</div>
                    <div><strong>日時:</strong> ${dateStr} ${timeStr}</div>
                    <div class="file-types">
                        ${fileTypesList}
                    </div>
                </div>
                <div class="output-item-actions">
                    <a href="${output.default_url}" class="btn btn-primary output-item-link" download>
                        📥 ダウンロード
                    </a>
                </div>
            `;
            outputsList.appendChild(item);
            
            // ファイルタイプリンクにクリックイベントを追加
            item.querySelectorAll('.file-type-link').forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const viewUrl = link.getAttribute('data-view-url');
                    const downloadUrl = link.getAttribute('data-download-url');
                    showFileModal(viewUrl, downloadUrl, link.textContent.trim());
                });
            });
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

// 処理進捗のポーリング（メイン）
let processingProgressInterval = null;

// アノテーション進捗のポーリング（詳細な進捗表示用）
let annotationProgressInterval = null;

function startAnnotationProgressPolling(videoId) {
    console.log('📊 アノテーション詳細進捗監視開始:', videoId);
    
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
                if (progressBar) progressBar.style.width = percentage + '%';
                
                // テキスト更新
                if (progressText) {
                    progressText.textContent = 
                        `バッチ ${progress.current_batch} / ${progress.total_batches} 処理中 (${progress.completed_frames}/${progress.total_frames}フレーム完了)`;
                }
                
                // ステップアイコン更新
                if (progress.status === 'completed') {
                    if (annotationStep) {
                        annotationStep.classList.add('completed');
                        const icon = annotationStep.querySelector('.status-icon');
                        if (icon) icon.textContent = '✓';
                    }
                    if (annotationProgressInterval) {
                        clearInterval(annotationProgressInterval);
                        annotationProgressInterval = null;
                    }
                    console.log('✅ アノテーション完了');
                } else {
                    const icon = annotationStep?.querySelector('.status-icon');
                    if (icon) icon.textContent = '⏳';
                }
            } else if (progress.status === 'not_started') {
                // まだ開始していない
                if (progressText) progressText.textContent = 'アノテーション待機中...';
            }
        } catch (error) {
            console.error('❌ 進捗取得エラー:', error);
        }
    }, 1000); // 1秒ごとにポーリング
}

// ファイル表示モーダル関連（2段階タブ対応）
let currentModalData = {
    videoId: null,
    enhanced_transcript: { markdown: '', downloadUrl: '' },
    minutes: { markdown: '', downloadUrl: '' }
};

async function showFileModal(viewUrl, downloadUrl, title) {
    const modal = document.getElementById('file-view-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalPreview = document.getElementById('modal-preview-content');
    const modalMarkdown = document.getElementById('modal-markdown-content');
    const modalDownloadBtn = document.getElementById('modal-download-btn');
    
    if (!modal) {
        console.error('モーダル要素が見つかりません');
        return;
    }
    
    // タイトルを設定（動画IDのみ）
    const videoIdMatch = viewUrl.match(/\/api\/view-file\/([^/]+)\//);
    const videoId = videoIdMatch ? videoIdMatch[1] : null;
    modalTitle.textContent = videoId || 'ファイル表示';
    
    // モーダルを表示
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    
    // ローディング表示
    modalPreview.innerHTML = '<div style="text-align: center; padding: 2rem;"><div class="spinner" style="margin: 0 auto;"></div><p style="margin-top: 1rem; color: var(--text-secondary);">読み込み中...</p></div>';
    modalMarkdown.value = '';
    
    try {
        // 文字&シーン起こしと議事録の両方を取得
        const enhancedTranscriptUrl = videoId ? `/api/view-file/${videoId}/enhanced_transcript` : null;
        const minutesUrl = videoId ? `/api/view-file/${videoId}/minutes` : null;
        
        currentModalData.videoId = videoId;
        
        // 文字&シーン起こしを取得
        if (enhancedTranscriptUrl) {
            try {
                const response = await fetch(enhancedTranscriptUrl);
                if (response.ok) {
                    const data = await response.json();
                    currentModalData.enhanced_transcript.markdown = data.markdown || '';
                    currentModalData.enhanced_transcript.downloadUrl = `/api/download-minutes/${videoId}/enhanced_transcript`;
                }
            } catch (e) {
                console.warn('文字&シーン起こし取得失敗:', e);
            }
        }
        
        // 議事録を取得
        if (minutesUrl) {
            try {
                const response = await fetch(minutesUrl);
                if (response.ok) {
                    const data = await response.json();
                    currentModalData.minutes.markdown = data.markdown || '';
                    currentModalData.minutes.downloadUrl = `/api/download-minutes/${videoId}/minutes`;
                }
            } catch (e) {
                console.warn('議事録取得失敗:', e);
            }
        }
        
        // 最初は文字&シーン起こしを表示
        switchModalFileTab('enhanced_transcript');
        switchModalViewTab('preview');
        
    } catch (error) {
        console.error('ファイル表示エラー:', error);
        modalPreview.innerHTML = `<div style="padding: 2rem; text-align: center;"><p style="color: var(--error-color); font-weight: 600;">エラーが発生しました</p><p style="color: var(--text-secondary); margin-top: 0.5rem;">${error.message}</p></div>`;
    }
}

function closeFileModal() {
    const modal = document.getElementById('file-view-modal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = ''; // 背景のスクロールを有効化
    }
    currentDownloadUrl = null;
}

// モーダルのファイルタイプタブを切り替え
function switchModalFileTab(fileType) {
    // ボタンの更新
    document.querySelectorAll('.modal-file-tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.fileType === fileType);
    });
    
    // コンテンツを更新
    const modalPreview = document.getElementById('modal-preview-content');
    const modalMarkdown = document.getElementById('modal-markdown-content');
    const modalDownloadBtn = document.getElementById('modal-download-btn');
    
    const fileData = currentModalData[fileType];
    if (fileData && fileData.markdown) {
        modalMarkdown.value = fileData.markdown;
        renderMarkdown(fileData.markdown, 'modal-preview-content', currentModalData.videoId);
        
        if (modalDownloadBtn) {
            modalDownloadBtn.href = fileData.downloadUrl;
        }
    } else {
        modalPreview.innerHTML = '<p style="padding: 2rem; text-align: center; color: var(--text-secondary);">データが見つかりません</p>';
        modalMarkdown.value = '';
    }
}

// モーダルの表示形式タブを切り替え
function switchModalViewTab(viewType) {
    // ボタンの更新
    document.querySelectorAll('.modal-view-tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.viewType === viewType);
    });
    
    // コンテンツの表示切り替え
    const modalPreview = document.getElementById('modal-preview-content');
    const modalMarkdown = document.getElementById('modal-markdown-content');
    
    if (viewType === 'preview') {
        modalPreview.classList.add('active');
        modalMarkdown.classList.remove('active');
    } else {
        modalPreview.classList.remove('active');
        modalMarkdown.classList.add('active');
    }
}

// 生成完了後にモーダルを表示する関数
function showGeneratedMinutesModal(videoId, enhancedTranscriptMarkdown, minutesMarkdown) {
    const modal = document.getElementById('file-view-modal');
    const modalTitle = document.getElementById('modal-title');
    
    if (!modal) {
        console.error('モーダル要素が見つかりません');
        return;
    }
    
    // video_idからサブフォルダ名を取得
    const videoPrefix = videoId.replace(/\./g, '_');
    
    // モーダルデータを設定
    currentModalData.videoId = videoId;
    currentModalData.enhanced_transcript.markdown = enhancedTranscriptMarkdown;
    currentModalData.enhanced_transcript.downloadUrl = `/api/download-minutes/${videoPrefix}/enhanced_transcript`;
    currentModalData.minutes.markdown = minutesMarkdown;
    currentModalData.minutes.downloadUrl = `/api/download-minutes/${videoPrefix}/minutes`;
    
    // タイトル設定
    modalTitle.textContent = videoId || '生成された議事録';
    
    // 最初は文字&シーン起こしを表示
    switchModalFileTab('enhanced_transcript');
    switchModalViewTab('preview');
    
    // モーダルを表示
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

// 定期的に出力一覧を更新
setInterval(() => {
    if (!appState.isProcessing) {
        loadOutputsList();
    }
}, 5000);

