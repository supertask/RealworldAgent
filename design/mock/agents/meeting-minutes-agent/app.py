import os
import json
import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from collections import defaultdict
import subprocess
import tempfile
import base64
from dotenv import load_dotenv

# 環境変数を.envから読み込み
load_dotenv()

app = Flask(__name__)

# 設定
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'outputs')
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """ファイルが許可されているかチェック"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_audio_from_video(video_path):
    """動画から音声を抽出"""
    try:
        audio_path = os.path.join(tempfile.gettempdir(), 'audio_temp.wav')
        cmd = [
            'ffmpeg', '-i', video_path,
            '-ab', '160k',
            '-ac', '2',
            '-ar', '44100',
            '-vn',
            audio_path,
            '-y'
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return audio_path
    except Exception as e:
        print(f"音声抽出エラー: {str(e)}")
        return None


def transcribe_audio(audio_path, video_path):
    """Groq Whisper APIで音声をテキストに変換"""
    try:
        # Groq APIを使用
        import requests
        
        GROQ_API_KEY = os.getenv('GROQ_API_KEY')
        
        if not GROQ_API_KEY or not audio_path or not os.path.exists(audio_path):
            print("⚠️ Groq APIキーがないか音声ファイルが見つかりません - ダミーデータを使用")
            return {
                "text": "音声ファイルから会議の内容を確認しました。本日の議題について討議を行い、各項目について合意に達しました。次回までのアクションアイテムを確認し、担当者を決定しました。",
                "segments": [
                    {"start": 0.0, "end": 5.0, "text": "音声ファイルから会議の内容を確認しました。"},
                    {"start": 5.0, "end": 10.0, "text": "本日の議題について討議を行い、各項目について合意に達しました。"},
                    {"start": 10.0, "end": 15.0, "text": "次回までのアクションアイテムを確認し、担当者を決定しました。"}
                ]
            }
        
        print("🎤 Groq Whisper APIで文字起こし中...")
        
        # Groq Whisper API呼び出し
        with open(audio_path, 'rb') as audio_file:
            response = requests.post(
                'https://api.groq.com/openai/v1/audio/transcriptions',
                headers={'Authorization': f'Bearer {GROQ_API_KEY}'},
                files={'file': audio_file},
                data={
                    'model': 'whisper-large-v3-turbo',
                    'response_format': 'verbose_json',
                    'language': 'ja'
                }
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Groq Whisper API 成功: {len(result.get('segments', []))} セグメント")
            return {
                "text": result.get('text', ''),
                "segments": result.get('segments', [])
            }
        else:
            print(f"❌ Groq API エラー: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 文字起こしエラー: {str(e)}")
        # エラー時はダミーデータ
        return {
            "text": "音声ファイルから会議の内容を確認しました。本日の議題について討議を行い、各項目について合意に達しました。次回までのアクションアイテムを確認し、担当者を決定しました。",
            "segments": [
                {"start": 0.0, "end": 5.0, "text": "音声ファイルから会議の内容を確認しました。"},
                {"start": 5.0, "end": 10.0, "text": "本日の議題について討議を行い、各項目について合意に達しました。"},
                {"start": 10.0, "end": 15.0, "text": "次回までのアクションアイテムを確認し、担当者を決定しました。"}
            ]
        }


def detect_scene_changes(video_path, threshold=30.0):
    """シーン変化を検出してキーフレームを抽出
    
    Args:
        video_path: 動画ファイルのパス
        threshold: シーン変化と判定するヒストグラム差分の閾値
    
    Returns:
        キーフレームのリスト（タイムスタンプ、画像データ含む）
    
    Note:
        0.5秒以内に3回以上シーン変化がある場合はスキップ
    """
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if fps == 0:
            fps = 30  # デフォルト値
        
        print(f"📹 シーン検出開始: {total_frames}フレーム, {fps:.1f}fps")
        
        keyframes = []
        prev_frame = None
        prev_hist = None
        frame_count = 0
        
        # シーン変化履歴（0.5秒以内に3回以上変化を検出するため）
        scene_change_times = []
        N_SECONDS = 0.5  # この秒数以内に
        M_CHANGES = 3     # この回数以上変化したらスキップ
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            timestamp = frame_count / fps
            
            if prev_frame is not None:
                # ヒストグラム比較でシーン変化を検出
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                hist = cv2.calcHist([frame_gray], [0], None, [256], [0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                
                if prev_hist is not None:
                    # ヒストグラム差分を計算
                    diff = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                    
                    # 相関係数が低い（差が大きい）= シーン変化
                    if diff < (1.0 - threshold / 100.0):
                        # シーン変化を検出
                        scene_change_times.append(timestamp)
                        
                        # N_SECONDS以内の変化回数をカウント
                        recent_changes = [t for t in scene_change_times if timestamp - t <= N_SECONDS]
                        
                        if len(recent_changes) >= M_CHANGES:
                            # 頻繁にシーンが切り替わる → スキップ
                            print(f"⏭️  {timestamp:.1f}秒: 頻繁なシーン変化を検出 (スキップ)")
                            # 古い変化履歴を削除
                            scene_change_times = [t for t in scene_change_times if timestamp - t <= N_SECONDS]
                        else:
                            # キーフレームとして保存
                            frame_resized = cv2.resize(frame, (640, 360))
                            
                            # 画像をBase64エンコード
                            _, buffer = cv2.imencode('.jpg', frame_resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
                            frame_b64 = base64.b64encode(buffer).decode('utf-8')
                            
                            keyframes.append({
                                "timestamp": timestamp,
                                "frame_index": frame_count,
                                "image_base64": frame_b64,
                                "image": f"keyframe_{len(keyframes):04d}.jpg"
                            })
                            print(f"✅ {timestamp:.1f}秒: キーフレーム抽出 (#{len(keyframes)})")
                
                prev_hist = hist
            else:
                # 最初のフレームは必ず保存
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                prev_hist = cv2.calcHist([frame_gray], [0], None, [256], [0, 256])
                prev_hist = cv2.normalize(prev_hist, prev_hist).flatten()
                
                frame_resized = cv2.resize(frame, (640, 360))
                _, buffer = cv2.imencode('.jpg', frame_resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_b64 = base64.b64encode(buffer).decode('utf-8')
                
                keyframes.append({
                    "timestamp": timestamp,
                    "frame_index": frame_count,
                    "image_base64": frame_b64,
                    "image": f"keyframe_{len(keyframes):04d}.jpg"
                })
                print(f"✅ 0.0秒: 最初のキーフレーム抽出")
            
            prev_frame = frame
            frame_count += 1
        
        cap.release()
        print(f"🎬 シーン検出完了: {len(keyframes)}個のキーフレームを抽出")
        return keyframes
        
    except Exception as e:
        print(f"❌ キーフレーム抽出エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def extract_keyframes(video_path, interval=5):
    """動画からキーフレーム（画像）を抽出（後方互換用）
    
    シーン検出版を使用
    """
    return detect_scene_changes(video_path, threshold=30.0)


def remove_duplicate_keyframes(keyframes, similarity_threshold=0.95):
    """重複する画像を削除
    
    Args:
        keyframes: キーフレームリスト
        similarity_threshold: 類似度の閾値（これ以上で重複と判定）
    
    Returns:
        重複を削除したキーフレームリスト
    """
    if len(keyframes) <= 1:
        return keyframes
    
    print(f"🔍 画像重複チェック開始: {len(keyframes)}個")
    unique_keyframes = [keyframes[0]]  # 最初のフレームは必ず含める
    
    for i in range(1, len(keyframes)):
        current_img_b64 = keyframes[i].get('image_base64', '')
        if not current_img_b64:
            continue
        
        is_duplicate = False
        current_img_data = base64.b64decode(current_img_b64)
        current_img_array = np.frombuffer(current_img_data, dtype=np.uint8)
        current_img = cv2.imdecode(current_img_array, cv2.IMREAD_GRAYSCALE)
        
        if current_img is None:
            continue
        
        # 直前の数フレームと比較
        for prev_kf in unique_keyframes[-3:]:  # 直前3フレームのみチェック（効率化）
            prev_img_b64 = prev_kf.get('image_base64', '')
            if not prev_img_b64:
                continue
            
            prev_img_data = base64.b64decode(prev_img_b64)
            prev_img_array = np.frombuffer(prev_img_data, dtype=np.uint8)
            prev_img = cv2.imdecode(prev_img_array, cv2.IMREAD_GRAYSCALE)
            
            if prev_img is None:
                continue
            
            # ヒストグラム比較
            current_hist = cv2.calcHist([current_img], [0], None, [256], [0, 256])
            current_hist = cv2.normalize(current_hist, current_hist).flatten()
            
            prev_hist = cv2.calcHist([prev_img], [0], None, [256], [0, 256])
            prev_hist = cv2.normalize(prev_hist, prev_hist).flatten()
            
            similarity = cv2.compareHist(current_hist, prev_hist, cv2.HISTCMP_CORREL)
            
            if similarity > similarity_threshold:
                is_duplicate = True
                print(f"⏭️  {keyframes[i]['timestamp']:.1f}秒: 重複画像を検出 (類似度: {similarity:.3f})")
                break
        
        if not is_duplicate:
            unique_keyframes.append(keyframes[i])
    
    print(f"✅ 重複削除完了: {len(keyframes)} → {len(unique_keyframes)}個")
    return unique_keyframes


def generate_minutes_with_qwen3vl(transcript_data, keyframes):
    """Qwen3-VL (Modal) で画像つき議事録を生成
    
    Args:
        transcript_data: 音声文字起こしデータ（segments含む）
        keyframes: キーフレームリスト（画像base64含む）
    
    Returns:
        議事録データ
    """
    import requests
    
    try:
        MODAL_ENDPOINT = os.getenv('MODAL_QWEN3VL_ENDPOINT')
        
        if not MODAL_ENDPOINT:
            print("⚠️ MODAL_QWEN3VL_ENDPOINT が設定されていません - フォールバック処理")
            return generate_minutes_fallback(transcript_data, keyframes)
        
        segments = transcript_data.get("segments", []) if transcript_data else []
        
        # 重複画像を削除
        unique_keyframes = remove_duplicate_keyframes(keyframes)
        
        # 分割処理: セグメントとキーフレームを時間軸でマッチング
        chunks = []
        chunk_duration = 60  # 1チャンク = 60秒
        
        max_time = max(
            [s.get('end', 0) for s in segments] + [kf.get('timestamp', 0) for kf in unique_keyframes],
            default=0
        )
        
        num_chunks = int(max_time / chunk_duration) + 1
        
        print(f"📦 チャンク分割: {num_chunks}個 (各{chunk_duration}秒)")
        
        for i in range(num_chunks):
            start_time = i * chunk_duration
            end_time = (i + 1) * chunk_duration
            
            # この時間帯のセグメントを抽出
            chunk_segments = [
                s for s in segments 
                if s.get('start', 0) >= start_time and s.get('start', 0) < end_time
            ]
            
            # この時間帯のキーフレームを抽出
            chunk_keyframes = [
                kf for kf in unique_keyframes
                if kf.get('timestamp', 0) >= start_time and kf.get('timestamp', 0) < end_time
            ]
            
            if chunk_segments or chunk_keyframes:
                chunks.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    'segments': chunk_segments,
                    'keyframes': chunk_keyframes
                })
        
        print(f"📤 Modal Qwen3-VL に送信: {len(chunks)}チャンク")
        
        # 各チャンクをQwen3-VLで処理
        all_sections = []
        
        for idx, chunk in enumerate(chunks):
            print(f"🧠 チャンク {idx+1}/{len(chunks)} 処理中...")
            
            # テキスト部分を結合（タイムスタンプ付き）
            chunk_text_with_time = []
            for s in chunk['segments']:
                start_time = s.get('start', 0)
                end_time = s.get('end', 0)
                text = s.get('text', '')
                chunk_text_with_time.append(f"[{start_time:.1f}秒-{end_time:.1f}秒] {text}")
            chunk_text = "\n".join(chunk_text_with_time)
            
            # 画像データとタイムスタンプ情報を準備
            images_b64 = [kf.get('image_base64', '') for kf in chunk['keyframes']]
            images_timestamps = [f"画像{i}: {kf.get('timestamp', 0):.1f}秒時点" for i, kf in enumerate(chunk['keyframes'])]
            
            # Modal Qwen3-VL API呼び出し
            try:
                response = requests.post(
                    MODAL_ENDPOINT,
                    json={
                        'text': chunk_text,
                        'images': images_b64[:10],  # 最大10枚まで（制限）
                        'prompt': f"""以下の会議の一部（{chunk['start_time']:.0f}秒〜{chunk['end_time']:.0f}秒）について、
音声文字起こしと画像を元に議事録セクションを作成してください。

音声文字起こし（タイムスタンプ付き）:
{chunk_text}

画像情報:
{chr(10).join(images_timestamps)}

**重要**: 各画像のタイムスタンプと音声のタイムスタンプを照らし合わせて、
音声内容と**実際に関連がある画像のみ**をrelated_imagesに含めてください。

関連性の判断基準：
1. **時間的一致**: 画像のタイムスタンプが音声セグメントの時間範囲内またはその直後（±3秒程度）
2. **内容的一致**: 音声で言及されている内容が画像に映っている
3. **文脈的価値**: 画像が議論の文脈を理解するのに役立つ

除外すべき画像：
- 単なる話者の顔や会議室の風景
- 音声内容と時間的にも内容的にも関連がない
- ぼやけていたり、情報価値が低い

判断例：
- [12.3秒-18.5秒] 「このグラフを見てください」+ 画像1: 15.2秒時点 → グラフが映っていれば✅選択
- [25.0秒-30.2秒] 「次のステップは...」+ 画像2: 26.5秒時点 → 話者の顔だけなら❌除外
- [40.1秒-45.3秒] 「資料の3ページ目です」+ 画像3: 42.0秒時点 → 資料が映っていれば✅選択

以下の形式でJSON形式で返してください:
{{
  "section_title": "セクションタイトル",
  "content": "内容の要約",
  "key_points": ["ポイント1", "ポイント2"],
  "related_images": [0, 2]  // 音声内容と時間的・内容的に関連がある画像のインデックスのみ（関連画像がない場合は空配列[]）
}}"""
                    },
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    section = {
                        "time": f"{chunk['start_time']:.0f}秒 - {chunk['end_time']:.0f}秒",
                        "title": result.get('section_title', f"セクション {idx+1}"),
                        "content": result.get('content', chunk_text[:200]),
                        "key_points": result.get('key_points', []),
                        "keyframes": [chunk['keyframes'][i] for i in result.get('related_images', []) if i < len(chunk['keyframes'])]
                    }
                    all_sections.append(section)
                    print(f"✅ チャンク {idx+1} 処理完了")
                else:
                    print(f"⚠️ Modal API エラー (チャンク {idx+1}): {response.status_code}")
                    # エラー時はフォールバック
                    all_sections.append({
                        "time": f"{chunk['start_time']:.0f}秒 - {chunk['end_time']:.0f}秒",
                        "content": chunk_text[:200] if chunk_text else "内容なし",
                        "keyframes": chunk['keyframes'][:3]
                    })
            except Exception as e:
                print(f"⚠️ Modal API 呼び出しエラー (チャンク {idx+1}): {str(e)}")
                all_sections.append({
                    "time": f"{chunk['start_time']:.0f}秒 - {chunk['end_time']:.0f}秒",
                    "content": chunk_text[:200] if chunk_text else "内容なし",
                    "keyframes": chunk['keyframes'][:3]
                })
        
        # 全体のサマリーを生成
        all_text = "\n".join([s.get('text', '') for s in segments])
        
        print("📝 全体サマリー生成中...")
        try:
            summary_response = requests.post(
                MODAL_ENDPOINT,
                json={
                    'text': all_text,
                    'images': [kf.get('image_base64', '') for kf in unique_keyframes[:5]],  # 代表的な5枚
                    'prompt': f"""以下の会議全体の内容を300文字程度で要約してください:

{all_text[:2000]}

提供された{min(5, len(unique_keyframes))}枚の画像は、会議中の重要なシーンです。
画像に資料やグラフ、重要な情報が映っていればそれも考慮してください。
ただし、単なる話者の顔だけの画像は無視して構いません。

音声内容を中心に、会議の全体像を簡潔にまとめてください。"""
                },
                timeout=60
            )
            
            if summary_response.status_code == 200:
                summary_result = summary_response.json()
                summary = summary_result.get('content', all_text[:300])
            else:
                summary = all_text[:300] + "..." if len(all_text) > 300 else all_text
        except Exception as e:
            print(f"⚠️ サマリー生成エラー: {str(e)}")
            summary = all_text[:300] + "..." if len(all_text) > 300 else all_text
        
        now = datetime.datetime.now()
        minutes = {
            "title": "会議議事録",
            "date": now.strftime("%Y年%m月%d日"),
            "time": now.strftime("%H:%M"),
            "summary": summary,
            "sections": all_sections,
            "keyframes_used": [kf.get('image', '') for kf in unique_keyframes]
        }
        
        return minutes
        
    except Exception as e:
        print(f"❌ Qwen3-VL 処理エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return generate_minutes_fallback(transcript_data, keyframes)


def generate_minutes_fallback(transcript_data, keyframes):
    """フォールバック: OpenAI GPT-4で議事録生成"""
    import requests
    
    try:
        now = datetime.datetime.now()
        
        # 文字起こしテキストを取得
        transcript_text = transcript_data.get("text", "") if transcript_data else ""
        segments = transcript_data.get("segments", []) if transcript_data else []
        
        # OpenAI APIで議事録生成
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        
        if OPENAI_API_KEY and transcript_text:
            print("🧠 OpenAI GPT-4で議事録生成中（フォールバック）...")
            try:
                response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {OPENAI_API_KEY}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'gpt-4',
                        'messages': [
                            {
                                'role': 'system',
                                'content': 'あなたは会議の議事録を作成する専門家です。音声文字起こしから、要点をまとめた議事録を作成してください。'
                            },
                            {
                                'role': 'user',
                                'content': f'以下の会議の音声文字起こしから、議事録のサマリーを300文字程度で作成してください:\n\n{transcript_text}'
                            }
                        ],
                        'temperature': 0.7
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    summary = result['choices'][0]['message']['content']
                    print("✅ OpenAI GPT-4で議事録生成成功")
                else:
                    print(f"⚠️ OpenAI API エラー: {response.status_code} - デフォルトサマリーを使用")
                    summary = transcript_text[:300] + "..." if len(transcript_text) > 300 else transcript_text
            except Exception as e:
                print(f"⚠️ OpenAI API エラー: {str(e)} - デフォルトサマリーを使用")
                summary = transcript_text[:300] + "..." if len(transcript_text) > 300 else transcript_text
        else:
            print("⚠️ OpenAI APIキーなし or テキストなし - デフォルトサマリーを使用")
            summary = transcript_text[:300] + "..." if len(transcript_text) > 300 else transcript_text
        
        minutes = {
            "title": "会議議事録",
            "date": now.strftime("%Y年%m月%d日"),
            "time": now.strftime("%H:%M"),
            "summary": summary,
            "sections": [],
            "keyframes_used": []
        }
        
        # トランスクリプトのセグメントを議事録セクションに変換
        if transcript_data and "segments" in transcript_data:
            for i, segment in enumerate(transcript_data["segments"]):
                section = {
                    "time": f"{int(segment.get('start', 0))}秒 - {int(segment.get('end', 0))}秒",
                    "timestamp_start": segment.get('start', 0),
                    "timestamp_end": segment.get('end', 0),
                    "content": segment.get("text", ""),
                    "keyframe": keyframes[i]["image"] if i < len(keyframes) else None
                }
                minutes["sections"].append(section)
                if section["keyframe"]:
                    minutes["keyframes_used"].append(section["keyframe"])
        else:
            # データがない場合はダミーセクションを作成
            minutes["sections"].append({
                "time": "0秒 - 30秒",
                "timestamp_start": 0,
                "timestamp_end": 30,
                "content": "これはプロトタイプの議事録です。実際の動画内容から自動生成されます。",
                "keyframe": keyframes[0]["image"] if keyframes else None
            })
        
        # アクションアイテムをLLMで抽出
        action_items = []
        if OPENAI_API_KEY and transcript_text:
            try:
                response = requests.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {OPENAI_API_KEY}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'gpt-4',
                        'messages': [
                            {
                                'role': 'system',
                                'content': 'あなたは会議のアクションアイテムを抽出する専門家です。'
                            },
                            {
                                'role': 'user',
                                'content': f'以下の会議内容から、アクションアイテムを3〜5個抽出してください。各アイテムは1行で簡潔に:\n\n{transcript_text}'
                            }
                        ],
                        'temperature': 0.5
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    actions_text = result['choices'][0]['message']['content']
                    action_items = [{"description": line.strip('- ').strip()} for line in actions_text.split('\n') if line.strip()]
                    print(f"✅ アクションアイテム抽出: {len(action_items)}個")
            except Exception as e:
                print(f"⚠️ アクションアイテム抽出エラー: {str(e)}")
        
        if not action_items:
            action_items = [{"description": "議事録の内容を確認"}]
        
        minutes["action_items"] = action_items
        minutes["notes"] = f"自動生成日時: {now.strftime('%Y年%m月%d日 %H:%M')}"
        
        return minutes
    except Exception as e:
        print(f"❌ 議事録生成エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def save_keyframes_to_disk(keyframes, video_id, output_folder):
    """キーフレーム画像をディスクに保存
    
    Args:
        keyframes: キーフレームリスト（image_base64含む）
        video_id: ビデオID（ファイル名）
        output_folder: 出力先フォルダ
    
    Returns:
        保存された画像ファイルのパスリスト
    """
    import base64
    import os
    
    saved_images = []
    video_prefix = video_id.replace('.', '_')
    
    for idx, kf in enumerate(keyframes):
        image_b64 = kf.get('image_base64', '')
        if not image_b64:
            continue
        
        try:
            # Base64デコード
            image_data = base64.b64decode(image_b64)
            
            # ファイル名を生成（video_id含む）
            image_filename = f"{video_prefix}_keyframe_{idx:04d}.jpg"
            image_path = os.path.join(output_folder, image_filename)
            
            # 画像を保存
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            # キーフレーム情報を更新
            kf['image'] = image_filename
            kf['saved_path'] = image_path
            saved_images.append(image_path)
            
            print(f"✅ 画像保存: {image_filename}")
        
        except Exception as e:
            print(f"❌ 画像保存エラー (idx={idx}): {str(e)}")
            continue
    
    print(f"📁 合計 {len(saved_images)} 枚の画像を保存")
    return saved_images


def transcript_to_markdown(transcript_data, keyframes, video_id):
    """文字起こしをMarkdown形式に変換（タイムスタンプ + 画像）
    
    Args:
        transcript_data: 音声文字起こしデータ（segments含む）
        keyframes: キーフレームリスト
        video_id: ビデオID
    
    Returns:
        Markdown形式の文字起こし
    """
    now = datetime.datetime.now()
    markdown = f"""# 文字起こし - {video_id}

**生成日時**: {now.strftime('%Y年%m月%d日 %H:%M')}

---

"""
    
    segments = transcript_data.get("segments", []) if transcript_data else []
    
    # セグメントごとに処理
    for segment in segments:
        start_time = segment.get('start', 0)
        end_time = segment.get('end', 0)
        text = segment.get('text', '')
        
        # タイムスタンプ付きテキスト
        markdown += f"**[{start_time:.1f}秒 - {end_time:.1f}秒]**\n\n"
        markdown += f"{text}\n\n"
        
        # このセグメントに対応する画像を検索（±3秒以内）
        related_keyframes = [
            kf for kf in keyframes
            if abs(kf.get('timestamp', 0) - start_time) <= 3.0
        ]
        
        # 画像を埋め込み
        for kf in related_keyframes[:2]:  # 最大2枚まで
            image_name = kf.get('image', '')
            timestamp = kf.get('timestamp', 0)
            if image_name:
                markdown += f"![{image_name}]({image_name})\n"
                markdown += f"*画像タイムスタンプ: {timestamp:.1f}秒*\n\n"
        
        markdown += "---\n\n"
    
    markdown += f"\n*文字起こしは自動生成されました。生成日時: {now.strftime('%Y-%m-%d %H:%M:%S')}*"
    
    return markdown


def minutes_to_markdown(minutes):
    """議事録をMarkdown形式に変換"""
    markdown = f"""# {minutes.get('title', '会議議事録')}

**日時**: {minutes.get('date', '')} {minutes.get('time', '')}

## サマリー

{minutes.get('summary', '')}

## 議事録内容

"""
    
    for section in minutes.get("sections", []):
        # セクションタイトル（時間帯 + タイトル）
        section_title = section.get('title', 'タイムスタンプ')
        time_range = section.get('time', '')
        markdown += f"### [{time_range}] {section_title}\n\n"
        
        # 内容
        markdown += f"{section.get('content', '')}\n\n"
        
        # キーフレーム画像を埋め込み
        if section.get('keyframes'):
            for idx, keyframe in enumerate(section['keyframes']):
                image_name = keyframe.get('image', f'keyframe_{idx:04d}.jpg')
                timestamp = keyframe.get('timestamp', 0)
                markdown += f"**画像** ({timestamp:.1f}秒時点):\n\n"
                markdown += f"![{image_name}]({image_name})\n\n"
        
        # キーポイント
        if section.get('key_points'):
            markdown += "**主なポイント**:\n\n"
            for point in section['key_points']:
                markdown += f"- {point}\n"
            markdown += "\n"
    
    if minutes.get('action_items'):
        markdown += "## アクションアイテム\n\n"
        for i, action in enumerate(minutes['action_items'], 1):
            markdown += f"{i}. {action.get('description', '')}\n"
        markdown += "\n"
    
    if minutes.get('notes'):
        markdown += f"## 備考\n\n{minutes.get('notes', '')}\n"
    
    markdown += f"\n---\n*議事録は自動生成されました。生成日時: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    
    return markdown


@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')


@app.route('/api/process-video', methods=['POST'])
def process_video():
    """動画を処理して議事録を生成"""
    print("\n" + "="*50)
    print("🔄 /api/process-video 呼び出し")
    print("="*50)
    
    try:
        # リクエスト情報をログ
        print(f"📊 Content-Type: {request.content_type}")
        print(f"📊 Files: {list(request.files.keys())}")
        print(f"📊 Form: {list(request.form.keys())}")
        
        # ファイルのチェック
        if 'video' not in request.files:
            print("❌ 'video' キーが request.files にありません")
            print(f"   利用可能なキー: {list(request.files.keys())}")
            return jsonify({'error': 'ビデオファイルが見つかりません'}), 400
        
        file = request.files['video']
        print(f"📁 ファイルオブジェクト取得: {file}")
        print(f"📁 ファイル名: {file.filename}")
        
        if not file or file.filename == '':
            print("❌ ファイルが選択されていません")
            return jsonify({'error': 'ファイルが選択されていません'}), 400
        
        # ファイル形式チェック
        if not allowed_file(file.filename):
            print(f"❌ 許可されていないファイル形式: {file.filename}")
            return jsonify({'error': f'許可されていないファイル形式です: {file.filename}'}), 400
        
        # ファイルサイズ取得
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        print(f"📏 ファイルサイズ: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
        
        if file_size > MAX_FILE_SIZE:
            print(f"❌ ファイルサイズが大きすぎます: {file_size} bytes")
            return jsonify({'error': 'ファイルサイズが大きすぎます (最大 500MB)'}), 413
        
        # ファイルを保存
        filename = secure_filename(file.filename)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_")
        safe_filename = timestamp + filename
        
        # uploads フォルダが存在することを確認
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        print(f"💾 保存先: {video_path}")
        
        file.save(video_path)
        
        # 保存確認
        if os.path.exists(video_path):
            actual_size = os.path.getsize(video_path)
            print(f"✅ ファイル保存成功")
            print(f"   パス: {video_path}")
            print(f"   サイズ: {actual_size} bytes")
        else:
            print(f"❌ ファイル保存に失敗しました")
            return jsonify({'error': 'ファイル保存に失敗しました'}), 500
        
        response_data = {
            'status': 'success',
            'video_id': safe_filename,
            'video_path': video_path,
            'file_size': file_size,
            'message': 'ファイルが正常にアップロードされました'
        }
        print(f"✅ レスポンス: {response_data}")
        print("="*50 + "\n")
        
        return jsonify(response_data), 200
    
    except Exception as e:
        print(f"❌ process_video エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*50 + "\n")
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-minutes/<video_id>', methods=['GET'])
def generate_minutes_endpoint(video_id):
    """議事録を生成"""
    try:
        print(f"\n🔄 議事録生成開始: {video_id}")
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_id)
        
        if not os.path.exists(video_path):
            print(f"❌ ビデオファイルが見つかりません: {video_path}")
            return jsonify({'error': 'ビデオファイルが見つかりません'}), 404
        
        print(f"✅ ビデオファイルを確認: {video_path}")
        
        # 音声抽出
        print("🎵 音声抽出中...")
        audio_path = extract_audio_from_video(video_path)
        if audio_path:
            print(f"✅ 音声抽出完了: {audio_path}")
        
        # 文字起こし
        print("📝 文字起こし中...")
        transcript = transcribe_audio(audio_path, video_path)
        if transcript:
            print(f"✅ 文字起こし完了: {len(transcript.get('segments', []))} セグメント")
        
        # キーフレーム抽出
        print("🎬 キーフレーム抽出中...")
        keyframes = extract_keyframes(video_path, interval=5)
        print(f"✅ キーフレーム抽出完了: {len(keyframes)} フレーム")
        
        # 出力フォルダを作成
        os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
        
        # キーフレーム画像を保存（ファイル名を更新）
        print("💾 キーフレーム画像を保存中...")
        save_keyframes_to_disk(keyframes, video_id, app.config['OUTPUT_FOLDER'])
        print(f"✅ キーフレーム画像保存完了")
        
        # 議事録生成（Qwen3-VL使用、エラー時はフォールバック）
        print("🧠 議事録を生成中...")
        minutes = generate_minutes_with_qwen3vl(transcript, keyframes)
        print(f"✅ 議事録生成完了")
        
        # 1. 議事録Markdownを生成
        minutes_markdown = minutes_to_markdown(minutes)
        minutes_filename = f"minutes_{video_id.replace('.', '_')}.md"
        minutes_path = os.path.join(app.config['OUTPUT_FOLDER'], minutes_filename)
        
        with open(minutes_path, 'w', encoding='utf-8') as f:
            f.write(minutes_markdown)
        print(f"✅ 議事録を保存: {minutes_filename}")
        
        # 2. 文字起こしMarkdownを生成
        transcript_markdown = transcript_to_markdown(transcript, keyframes, video_id)
        transcript_filename = f"transcript_{video_id.replace('.', '_')}.md"
        transcript_path = os.path.join(app.config['OUTPUT_FOLDER'], transcript_filename)
        
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(transcript_markdown)
        print(f"✅ 文字起こしを保存: {transcript_filename}")
        
        # ZIPファイル名を生成
        zip_filename = f"output_{video_id.replace('.', '_')}.zip"
        
        return jsonify({
            'status': 'success',
            'minutes': minutes,
            'minutes_markdown': minutes_markdown,
            'transcript_markdown': transcript_markdown,
            'download_url': f'/api/download-output/{zip_filename}'
        })
    
    except Exception as e:
        print(f"❌ generate_minutes_endpoint エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/download-output/<zip_filename>', methods=['GET'])
def download_output(zip_filename):
    """議事録・文字起こし・画像をZIPでダウンロード"""
    import zipfile
    import io
    
    try:
        # ZIPファイル名からvideo_idを抽出
        video_id = zip_filename.replace('output_', '').replace('.zip', '').replace('_', '.')
        video_prefix = video_id.replace('.', '_')
        
        # メモリ上にZIPファイルを作成
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 1. 議事録Markdownを追加
            minutes_filename = f"minutes_{video_prefix}.md"
            minutes_path = os.path.join(app.config['OUTPUT_FOLDER'], minutes_filename)
            if os.path.exists(minutes_path):
                zip_file.write(minutes_path, arcname=f"議事録_{video_prefix}.md")
                print(f"✅ ZIP追加: {minutes_filename}")
            
            # 2. 文字起こしMarkdownを追加
            transcript_filename = f"transcript_{video_prefix}.md"
            transcript_path = os.path.join(app.config['OUTPUT_FOLDER'], transcript_filename)
            if os.path.exists(transcript_path):
                zip_file.write(transcript_path, arcname=f"文字起こし_{video_prefix}.md")
                print(f"✅ ZIP追加: {transcript_filename}")
            
            # 3. 画像を追加
            image_count = 0
            for filename in os.listdir(app.config['OUTPUT_FOLDER']):
                # このvideo_idの画像のみ
                if filename.startswith(video_prefix) and filename.endswith('.jpg'):
                    image_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                    zip_file.write(image_path, arcname=filename)
                    image_count += 1
            
            print(f"✅ ZIP追加: {image_count}枚の画像")
        
        # ZIPファイルをクライアントに送信
        zip_buffer.seek(0)
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"output_{video_prefix}.zip"
        )
    
    except Exception as e:
        print(f"❌ ZIPダウンロードエラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/download-minutes/<filename>', methods=['GET'])
def download_minutes(filename):
    """議事録をダウンロード（個別ファイル用・後方互換性のため残す）"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'ファイルが見つかりません'}), 404
        
        return send_file(file_path, as_attachment=True, mimetype='text/markdown')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/list-outputs', methods=['GET'])
def list_outputs():
    """生成済み議事録の一覧"""
    try:
        outputs = []
        # OUTPUT_FOLDER が存在することを確認
        os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
        
        if os.path.exists(app.config['OUTPUT_FOLDER']):
            try:
                for filename in os.listdir(app.config['OUTPUT_FOLDER']):
                    if filename.endswith('.md'):
                        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
                        try:
                            file_size = os.path.getsize(file_path)
                            mod_time = os.path.getmtime(file_path)
                            outputs.append({
                                'filename': filename,
                                'size': file_size,
                                'modified': datetime.datetime.fromtimestamp(mod_time).isoformat(),
                                'url': f'/api/download-minutes/{filename}'
                            })
                        except (OSError, IOError) as fe:
                            print(f"ファイル読み込みエラー {filename}: {str(fe)}")
                            continue
            except (OSError, IOError) as de:
                print(f"ディレクトリ読み込みエラー: {str(de)}")
        
        return jsonify({'outputs': outputs})
    except Exception as e:
        print(f"list_outputs エラー: {str(e)}")
        return jsonify({'error': str(e), 'outputs': []}), 200  # エラー時も出力を返す


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')

