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
import requests

# TransNetV2関連インポート
try:
    import torch
    import sys
    import os
    # transnetv2フォルダをパスに追加
    transnetv2_path = os.path.join(os.path.dirname(__file__), 'transnetv2')
    if transnetv2_path not in sys.path:
        sys.path.insert(0, transnetv2_path)
    from transnetv2_pytorch import TransNetV2
    TRANSNETV2_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ TransNetV2が利用できません ({e}) - OpenCVベースのシーン検出を使用します")
    TRANSNETV2_AVAILABLE = False

# 環境変数を.envから読み込み
load_dotenv()

# 設定ファイルを読み込み
def load_config():
    """config.yamlから設定を読み込み"""
    try:
        import yaml
    except ImportError:
        print("⚠️ PyYAMLがインストールされていません")
        print("  実行: pip install pyyaml")
        import sys
        sys.exit(1)
    
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"⚠️ config.yaml読み込みエラー: {e}")
        # デフォルト設定を返す
        return {
            "audio_extraction_enabled": False,
            "transcription_enabled": False,
            "scene_detection_enabled": True,
            "scene_detection_method": "transnetv2",
            "minutes_generation_enabled": False,
            "minutes_generation_method": "qwen3vl",
            "duplicate_removal_enabled": False,
            "image_saving_enabled": True,
            "transnetv2": {
                "detection_threshold": 0.5,
                "use_frame_similarity": True,
                "use_color_histograms": True
            }
        }

DEBUG_CONFIG = load_config()
print("🔧 デバッグ設定を読み込みました:")
for key, value in DEBUG_CONFIG.items():
    print(f"  {key}: {value}")

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
    if not DEBUG_CONFIG["audio_extraction_enabled"]:
        print("🚫 音声抽出: 無効化されています")
        return None

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
    if not DEBUG_CONFIG["transcription_enabled"]:
        print("🚫 文字起こし: 無効化されています - ダミーデータを使用")
        return {
            "text": "文字起こし機能が無効化されています。テスト用のダミーテキストです。",
            "segments": [
                {"start": 0.0, "end": 5.0, "text": "文字起こし機能が無効化されています。"},
                {"start": 5.0, "end": 10.0, "text": "テスト用のダミーテキストです。"}
            ]
        }

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


def detect_scene_changes_transnetv2(video_path):
    """TransNetV2でシーン変化を検出してキーフレームを抽出

    Args:
        video_path: 動画ファイルのパス

    Returns:
        キーフレームのリスト（タイムスタンプ、画像データ含む）
    """
    try:
        if not TRANSNETV2_AVAILABLE:
            print("⚠️ TransNetV2が利用できないため、OpenCVベースの検出にフォールバックします")
            return detect_scene_changes_opencv(video_path)

        # TransNetV2モデルの初期化（初回のみ）
        if not hasattr(detect_scene_changes_transnetv2, '_model'):
            print("🔄 TransNetV2モデルを初期化中...")
            try:
                detect_scene_changes_transnetv2._model = TransNetV2()

                # トレーニング済み重みのロードを試行
                weights_path = os.path.join(os.path.dirname(__file__), 'transnetv2', 'transnetv2-pytorch-weights.pth')
                if os.path.exists(weights_path):
                    state_dict = torch.load(weights_path, map_location='cpu')
                    detect_scene_changes_transnetv2._model.load_state_dict(state_dict)
                    print("✅ トレーニング済み重みをロードしました")
                else:
                    print("⚠️ トレーニング済み重みが見つからないため、ランダム初期化を使用します")

                # Apple Silicon対応: MPS（Metal Performance Shaders）を使用
                if torch.backends.mps.is_available():
                    detect_scene_changes_transnetv2._model = detect_scene_changes_transnetv2._model.to('mps')
                    print("✅ MPS（Apple Silicon GPU）を使用")
                elif torch.cuda.is_available():
                    detect_scene_changes_transnetv2._model = detect_scene_changes_transnetv2._model.cuda()
                    print("✅ CUDA GPUを使用")
                else:
                    print("⚠️ GPUが利用できないためCPUを使用")

                detect_scene_changes_transnetv2._model.eval()
                print("✅ TransNetV2モデル初期化完了")

            except Exception as e:
                print(f"❌ TransNetV2モデル初期化エラー: {str(e)}")
                print("⚠️ OpenCVベースの検出にフォールバックします")
                return detect_scene_changes_opencv(video_path)

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if fps == 0:
            fps = 30  # デフォルト値

        print(f"🎬 TransNetV2シーン検出開始: {total_frames}フレーム, {fps:.1f}fps")

        # 動画からフレームを抽出
        # TransNetV2用：27x48サイズで予測
        # 保存用：元のサイズで保存
        frames_small = []  # TransNetV2用（27x48）
        frames_full = []   # 表示用（元のサイズ）
        timestamps = []

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # TransNetV2用にリサイズ（27x48, RGB）
            frame_resized = cv2.resize(frame, (48, 27))  # 幅x高さ
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            
            # 表示用：元サイズのRGB
            frame_full_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frames_small.append(frame_rgb)
            frames_full.append(frame_full_rgb)
            timestamps.append(frame_count / fps)
            frame_count += 1

        cap.release()

        if not frames_small:
            print("❌ フレーム抽出に失敗しました")
            return []

        frames_np = np.array(frames_small, dtype=np.uint8)  # [n_frames, 27, 48, 3]
        print(f"✅ フレーム抽出完了: {len(frames_small)}フレーム")

        # TransNetV2で予測
        print("🧠 TransNetV2でシーン境界を検出中...")
        with torch.no_grad():
            # デバイス設定
            device = next(detect_scene_changes_transnetv2._model.parameters()).device

            # フレームをテンソルに変換
            frames_tensor = torch.from_numpy(frames_np).unsqueeze(0)  # [1, n_frames, 27, 48, 3]
            frames_tensor = frames_tensor.to(device)

            # 予測実行
            single_frame_pred, all_frame_pred = detect_scene_changes_transnetv2._model(frames_tensor)

            # シグモイド適用
            single_frame_pred = torch.sigmoid(single_frame_pred).cpu().numpy().flatten()
            all_frame_pred = torch.sigmoid(all_frame_pred["many_hot"]).cpu().numpy().flatten()

        # シーン境界を検出（single_frame_predを使用）
        scene_boundaries = []
        # 設定からTransNetV2の検出閾値を取得
        threshold = DEBUG_CONFIG.get('transnetv2', {}).get('detection_threshold', 0.5)

        for i, pred in enumerate(single_frame_pred):
            if pred > threshold:
                scene_boundaries.append(i)

        print(f"✅ シーン境界検出完了: {len(scene_boundaries)}個の境界を検出")

        # シーン境界のフレームをキーフレームとして抽出
        keyframes = []

        # 最初のフレームは必ず含める
        if frames_full:
            frame_rgb = frames_full[0]
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            # 元のサイズを保持（リサイズしない、または最小限にする）
            frame_display = cv2.resize(frame_bgr, (640, 360)) if frame_bgr.shape[1] > 640 else frame_bgr

            _, buffer = cv2.imencode('.jpg', frame_display, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_b64 = base64.b64encode(buffer).decode('utf-8')

            keyframes.append({
                "timestamp": timestamps[0],
                "frame_index": 0,
                "image_base64": frame_b64,
                "image": f"keyframe_{len(keyframes):04d}.jpg"
            })
            print(f"✅ 0.0秒: 最初のキーフレーム抽出 ({frame_bgr.shape[1]}x{frame_bgr.shape[0]})")

        # シーン境界のフレームをキーフレームとして追加
        for boundary_idx in scene_boundaries:
            if boundary_idx < len(frames_full):
                frame_rgb = frames_full[boundary_idx]
                frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                # 元のサイズを保持
                frame_display = cv2.resize(frame_bgr, (640, 360)) if frame_bgr.shape[1] > 640 else frame_bgr

                _, buffer = cv2.imencode('.jpg', frame_display, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_b64 = base64.b64encode(buffer).decode('utf-8')

                keyframes.append({
                    "timestamp": timestamps[boundary_idx],
                    "frame_index": boundary_idx,
                    "image_base64": frame_b64,
                    "image": f"keyframe_{len(keyframes):04d}.jpg"
                })
                print(f"✅ {timestamps[boundary_idx]:.1f}秒: シーン境界キーフレーム抽出 (#{len(keyframes)}, サイズ: {frame_bgr.shape[1]}x{frame_bgr.shape[0]})")

        print(f"🎬 TransNetV2シーン検出完了: {len(keyframes)}個のキーフレームを抽出")
        return keyframes

    except Exception as e:
        print(f"❌ TransNetV2シーン検出エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        print("⚠️ OpenCVベースの検出にフォールバックします")
        return detect_scene_changes_opencv(video_path)


def detect_scene_changes_opencv(video_path, threshold=30.0):
    """OpenCVヒストグラム比較でシーン変化を検出（フォールバック用）

    Args:
        video_path: 動画ファイルのパス
        threshold: シーン変化と判定するヒストグラム差分の閾値

    Returns:
        キーフレームのリスト（タイムスタンプ、画像データ含む）
    """
    try:
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if fps == 0:
            fps = 30  # デフォルト値

        print(f"📹 OpenCVシーン検出開始: {total_frames}フレーム, {fps:.1f}fps")

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
        print(f"🎬 OpenCVシーン検出完了: {len(keyframes)}個のキーフレームを抽出")
        return keyframes

    except Exception as e:
        print(f"❌ OpenCVキーフレーム抽出エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


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
    """動画からキーフレーム（画像）を抽出

    config.jsonの設定に基づいてシーン検出方法を選択
    """
    if not DEBUG_CONFIG["scene_detection_enabled"]:
        print("🚫 シーン検出: 無効化されています")
        return []

    method = DEBUG_CONFIG["scene_detection_method"]

    if method == "transnetv2":
        return detect_scene_changes_transnetv2(video_path)
    elif method == "opencv":
        return detect_scene_changes_opencv(video_path)
    else:
        print(f"⚠️ 不明なシーン検出方法: {method} - TransNetV2を使用します")
        return detect_scene_changes_transnetv2(video_path)


def remove_duplicate_keyframes(keyframes, similarity_threshold=0.95):
    """重複する画像を削除
    
    Args:
        keyframes: キーフレームリスト
        similarity_threshold: 類似度の閾値（これ以上で重複と判定）
    
    Returns:
        重複を削除したキーフレームリスト
    """
    if not DEBUG_CONFIG["duplicate_removal_enabled"]:
        print("🚫 重複画像削除: 無効化されています")
        return keyframes

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
    if not DEBUG_CONFIG["minutes_generation_enabled"]:
        print("🚫 議事録生成: 無効化されています - ダミーデータを使用")
        return {
            "title": "会議議事録（ダミー）",
            "date": datetime.datetime.now().strftime("%Y年%m月%d日"),
            "time": datetime.datetime.now().strftime("%H:%M"),
            "summary": "議事録生成が無効化されています。テスト用のダミーデータです。",
            "sections": [],
            "keyframes_used": []
        }

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
        保存された画像ファイルのパスリスト、動画用サブフォルダパス
    """
    if not DEBUG_CONFIG["image_saving_enabled"]:
        print("🚫 画像保存: 無効化されています")
        return [], None

    import base64
    import os
    
    # 動画ごとのサブフォルダを作成
    video_prefix = video_id.replace('.', '_')
    video_subfolder = os.path.join(output_folder, video_prefix)
    os.makedirs(video_subfolder, exist_ok=True)
    
    saved_images = []
    
    for idx, kf in enumerate(keyframes):
        image_b64 = kf.get('image_base64', '')
        if not image_b64:
            continue
        
        try:
            # Base64デコード
            image_data = base64.b64decode(image_b64)
            
            # ファイル名を生成（シンプルに）
            image_filename = f"keyframe_{idx:04d}.jpg"
            image_path = os.path.join(video_subfolder, image_filename)
            
            # 画像を保存
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            # キーフレーム情報を更新
            kf['image'] = image_filename
            kf['saved_path'] = image_path
            saved_images.append(image_path)
            
            print(f"✅ 画像保存: {video_prefix}/{image_filename}")
        
        except Exception as e:
            print(f"❌ 画像保存エラー (idx={idx}): {str(e)}")
            continue
    
    print(f"📁 合計 {len(saved_images)} 枚の画像を保存（フォルダ: {video_prefix}/）")
    return saved_images, video_subfolder


def filter_keyframes_by_time_gap(keyframes, video_path, min_time_gap_seconds=0.5):
    """時間差が短すぎるフレームをフィルタリング
    
    Args:
        keyframes: キーフレームリスト（timestamp, frame_index含む）
        video_path: 動画ファイルパス（FPS取得用）
        min_time_gap_seconds: 最小時間差（秒）
    
    Returns:
        フィルタリング後のキーフレームリスト
    """
    if not keyframes or len(keyframes) == 0:
        return keyframes
    
    # FPSを取得
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    
    if fps == 0:
        fps = 30  # デフォルト値
    
    print(f"🔍 フレームフィルタリング開始: {len(keyframes)}フレーム, FPS={fps:.1f}, 最小時間差={min_time_gap_seconds}秒")
    
    filtered_keyframes = []
    last_included_frame = None
    removed_count = 0
    
    for frame in keyframes:
        if last_included_frame is None:
            # 最初のフレームは常に含める
            filtered_keyframes.append(frame)
            last_included_frame = frame
        else:
            # フレーム間の時間差を計算
            time_gap_seconds = abs(frame.get('timestamp', 0) - last_included_frame.get('timestamp', 0))
            
            if time_gap_seconds >= min_time_gap_seconds:
                filtered_keyframes.append(frame)
                last_included_frame = frame
            else:
                # 短すぎるフレームは除外
                removed_count += 1
                print(f"⏭️  フレーム除外: 時間差{time_gap_seconds:.3f}秒 < 最小{min_time_gap_seconds}秒 (フレーム#{frame.get('frame_index', '?')})")
    
    print(f"✅ フレームフィルタリング完了: {len(filtered_keyframes)}/{len(keyframes)}フレーム保持 ({removed_count}フレーム削除)")
    
    return filtered_keyframes


def generate_frame_metadata(keyframes, video_path, video_id, output_folder):
    """フレームメタデータJSONを生成
    
    Args:
        keyframes: キーフレームリスト（timestamp, frame_index, image含む）
        video_path: 動画ファイルパス
        video_id: ビデオID
        output_folder: 出力フォルダ
    
    Returns:
        メタデータファイルパス
    """
    # FPSと動画情報を取得
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_seconds = total_frames / fps if fps > 0 else 0
    cap.release()
    
    if fps == 0:
        fps = 30  # デフォルト値
    
    # 動画用サブフォルダを取得
    video_prefix = video_id.replace('.', '_')
    video_subfolder = os.path.join(output_folder, video_prefix)
    
    # メタデータ構造を構築
    metadata = {
        "video_info": {
            "filename": video_id,
            "duration_seconds": duration_seconds,
            "fps": fps,
            "total_frames": total_frames
        },
        "filtering_applied": {
            "enabled": True,
            "min_time_gap_seconds": DEBUG_CONFIG.get("filtering_min_time_gap_seconds", 0.5)
        },
        "keyframes": []
    }
    
    # キーフレーム情報を追加
    for idx, kf in enumerate(keyframes):
        frame_number = kf.get('frame_index', 0)
        image_path = kf.get('image', f'keyframe_{idx:04d}.jpg')
        scene_score = kf.get('scene_score', None)
        
        # keyframesにidを追加（まだない場合）
        if 'id' not in kf:
            kf['id'] = idx + 1
        
        frame_data = {
            "id": kf.get('id', idx + 1),
            "frame_number": frame_number,
            "image_path": image_path,
        }
        
        if scene_score is not None:
            frame_data["scene_score"] = scene_score
        
        metadata["keyframes"].append(frame_data)
    
    # JSONファイルに保存
    metadata_path = os.path.join(video_subfolder, 'frame_metadata.json')
    os.makedirs(video_subfolder, exist_ok=True)
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"✅ フレームメタデータ保存: {metadata_path}")
    
    return metadata_path


def generate_batch_plan(keyframes, video_subfolder, max_images_per_batch=6, overlap_frames=1):
    """バッチアノテーションプランを生成（オーバーラップ戦略）
    
    Args:
        keyframes: キーフレームリスト（frame_number, image含む）
        video_subfolder: 出力フォルダ
        max_images_per_batch: バッチあたり最大画像数
        overlap_frames: オーバーラップするフレーム数
    
    Returns:
        バッチプランファイルパス
    """
    if not keyframes or len(keyframes) == 0:
        print("⚠️ キーフレームがありません - バッチプランをスキップ")
        return None
    
    print(f"📦 バッチプラン生成開始: {len(keyframes)}フレーム, 最大{max_images_per_batch}枚/バッチ, オーバーラップ{overlap_frames}フレーム")
    
    # keyframesにidを追加（まだない場合）
    for idx, kf in enumerate(keyframes):
        if 'id' not in kf:
            kf['id'] = idx + 1
        if 'image_path' not in kf:
            kf['image_path'] = kf.get('image', f'keyframe_{idx:04d}.jpg')
    
    batches = []
    batch_id = 1
    i = 0
    
    while i < len(keyframes):
        # 現在のバッチに含めるフレームを決定
        batch_frames = []
        
        # 最初のバッチ以外は、前のバッチの最後のフレームをオーバーラップとして含める
        if batch_id > 1 and i > 0:
            # 前のバッチの最後のフレームを追加
            prev_last_frame = keyframes[i - 1]
            batch_frames.append(prev_last_frame)
        
        # 新しいフレームを追加（最大数まで）
        while len(batch_frames) < max_images_per_batch and i < len(keyframes):
            batch_frames.append(keyframes[i])
            i += 1
        
        if not batch_frames:
            break
        
        # バッチ情報を構築
        frame_ids = [f.get('id', idx + 1) for idx, f in enumerate(batch_frames)]
        image_paths = [f.get('image_path', f.get('image', f'keyframe_{idx:04d}.jpg')) for idx, f in enumerate(batch_frames)]
        
        # 時間範囲を計算
        timestamps = [f.get('timestamp', 0) for f in batch_frames if 'timestamp' in f]
        time_range_seconds = [min(timestamps), max(timestamps)] if timestamps else [0, 0]
        
        # フレーム範囲を計算
        frame_numbers = [f.get('frame_number', 0) for f in batch_frames]
        frame_range = [min(frame_numbers), max(frame_numbers)] if frame_numbers else [0, 0]
        
        batch = {
            "batch_id": batch_id,
            "frame_ids": frame_ids,
            "image_paths": image_paths,
            "time_range_seconds": time_range_seconds,
            "frame_range": frame_range,
            "processing_order": batch_id
        }
        
        batches.append(batch)
        batch_id += 1
    
    # バッチプラン構造を構築
    batch_plan = {
        "batching_config": {
            "strategy": "temporal_window_with_overlap",
            "overlap_frames": overlap_frames,
            "max_images_per_batch": max_images_per_batch,
            "lm_studio_config": {
                "endpoint": DEBUG_CONFIG.get("lm_studio_endpoint", "http://localhost:1234/v1/chat/completions"),
                "model": DEBUG_CONFIG.get("lm_studio_model", "unsloth/Qwen3-VL-8B-Instruct"),
                "max_tokens": 512,
                "temperature": 0.7
            }
        },
        "batches": batches
    }
    
    # JSONファイルに保存
    batch_plan_path = os.path.join(video_subfolder, 'batch_annotation_plan.json')
    
    with open(batch_plan_path, 'w', encoding='utf-8') as f:
        json.dump(batch_plan, f, ensure_ascii=False, indent=2)
    
    print(f"✅ バッチプラン保存: {batch_plan_path} ({len(batches)}バッチ)")
    
    return batch_plan_path


def annotate_images_with_lm_studio(image_paths, batch_id, video_subfolder):
    """LM Studio Qwen3-VL 8Bで画像をアノテーション
    
    Args:
        image_paths: 画像ファイルパスのリスト
        batch_id: バッチID
        video_subfolder: 出力フォルダ
    
    Returns:
        アノテーション結果のリスト
    """
    if not DEBUG_CONFIG.get("annotation_enabled", False):
        print("🚫 アノテーション: 無効化されています")
        return []
    
    endpoint = DEBUG_CONFIG.get("lm_studio_endpoint", "http://localhost:1234/v1/chat/completions")
    model = DEBUG_CONFIG.get("lm_studio_model", "unsloth/Qwen3-VL-8B-Instruct")
    
    print(f"🤖 LM Studioアノテーション開始: バッチ{batch_id}, {len(image_paths)}枚")
    
    # 接続確認（最初の1回だけ）
    print(f"🔍 LM Studio接続確認中: {endpoint}")
    try:
        # ヘルスチェック用の軽量リクエスト
        test_response = requests.get(endpoint.replace('/v1/chat/completions', '/health'), timeout=5)
        print(f"✅ LM Studio接続確認成功")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ LM Studio接続確認失敗: {str(e)}")
        print(f"💡 ヒント: LM Studioが起動しているか確認してください")
        print(f"   - エンドポイント: {endpoint}")
        print(f"   - モデル: {model}")
        # 接続エラーでも処理は続行（個別リクエストでリトライするため）
    
    results = []
    
    for idx, image_path in enumerate(image_paths):
        try:
            # 画像をBase64エンコード
            full_image_path = os.path.join(video_subfolder, image_path)
            if not os.path.exists(full_image_path):
                print(f"⚠️ 画像が見つかりません: {full_image_path}")
                results.append({
                    "status": "error",
                    "readable": False,
                    "reason": f"画像ファイルが見つかりません: {image_path}",
                    "content": None
                })
                continue
            
            with open(full_image_path, 'rb') as f:
                image_data = f.read()
                image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            # LM Studioに送信
            prompt = """この画像を詳細に説明してください。以下のJSON形式で返してください:
{
  "scene": "シーンの説明",
  "objects": ["検出されたオブジェクト1", "オブジェクト2"],
  "text": [
    {
      "content": "検出されたテキスト",
      "position": "center|upper_left|lower_center|etc",
      "type": "document|slide_title|slide_content|speech_bubble|etc"
    }
  ],
  "speaker_count": 人数,
  "visual_changes": ["前のフレームからの変化1", "変化2"]
}"""
            
            # リトライ処理（最大3回）
            max_retries = 3
            retry_delay = 2  # 秒
            response = None
            
            for retry_count in range(max_retries):
                try:
                    response = requests.post(
                        endpoint,
                        json={
                            "model": model,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{image_b64}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            "max_tokens": 512,
                            "temperature": 0.7
                        },
                        timeout=60
                    )
                    # 成功したらループを抜ける
                    break
                except requests.exceptions.ConnectionError as e:
                    if retry_count < max_retries - 1:
                        print(f"⚠️ 接続エラー (リトライ {retry_count + 1}/{max_retries}): {str(e)}")
                        import time
                        time.sleep(retry_delay)
                        continue
                    else:
                        # 最後のリトライでも失敗
                        raise
                except requests.exceptions.RequestException as e:
                    # 接続エラー以外は即座に再スロー
                    raise
            
            if response is None:
                raise requests.exceptions.RequestException("リトライ後も接続に失敗しました")
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                
                # JSON形式を抽出
                try:
                    if "{" in content and "}" in content:
                        json_start = content.find("{")
                        json_end = content.rfind("}") + 1
                        json_str = content[json_start:json_end]
                        annotation_data = json.loads(json_str)
                        
                        results.append({
                            "status": "success",
                            "readable": True,
                            "content": annotation_data,
                            "raw_response": content
                        })
                        print(f"✅ 画像{idx+1}/{len(image_paths)}: アノテーション成功")
                    else:
                        raise ValueError("JSON形式が見つかりません")
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON解析エラー: {str(e)}")
                    results.append({
                        "status": "partial_failure",
                        "readable": False,
                        "reason": f"JSON解析エラー: {str(e)}",
                        "raw_response": content,
                        "content": None
                    })
            else:
                print(f"❌ LM Studio APIエラー: {response.status_code}")
                results.append({
                    "status": "error",
                    "readable": False,
                    "reason": f"LM Studio APIエラー: {response.status_code}",
                    "content": None
                })
        
        except requests.exceptions.RequestException as e:
            print(f"❌ リクエストエラー: {str(e)}")
            results.append({
                "status": "error",
                "readable": False,
                "reason": f"リクエストエラー: {str(e)}",
                "content": None
            })
        except Exception as e:
            print(f"❌ 予期しないエラー: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append({
                "status": "error",
                "readable": False,
                "reason": f"予期しないエラー: {str(e)}",
                "content": None
            })
    
    print(f"✅ バッチ{batch_id}アノテーション完了: {len([r for r in results if r['status'] == 'success'])}/{len(results)}成功")
    
    return results


def generate_image_annotations(batch_plan_path, video_subfolder, keyframes):
    """アノテーション結果を統合してimage_annotations.jsonを生成
    
    Args:
        batch_plan_path: バッチプランファイルパス
        video_subfolder: 出力フォルダ
        keyframes: キーフレームリスト（メタデータ用）
    
    Returns:
        アノテーションファイルパス
    """
    if not os.path.exists(batch_plan_path):
        print("⚠️ バッチプランファイルが見つかりません")
        return None
    
    # バッチプランを読み込み
    with open(batch_plan_path, 'r', encoding='utf-8') as f:
        batch_plan = json.load(f)
    
    print(f"📝 アノテーション結果統合開始: {len(batch_plan['batches'])}バッチ")
    
    annotations = []
    frame_id_to_keyframe = {kf.get('id', idx+1): kf for idx, kf in enumerate(keyframes)}
    
    # 各バッチのアノテーション結果を読み込み
    for batch in batch_plan['batches']:
        batch_id = batch['batch_id']
        frame_ids = batch['frame_ids']
        image_paths = batch['image_paths']
        
        # バッチごとのアノテーション結果ファイルを読み込み（存在する場合）
        batch_result_path = os.path.join(video_subfolder, f'batch_{batch_id}_results.json')
        
        if os.path.exists(batch_result_path):
            with open(batch_result_path, 'r', encoding='utf-8') as f:
                batch_results = json.load(f)
        else:
            print(f"⚠️ バッチ{batch_id}の結果ファイルが見つかりません: {batch_result_path}")
            continue
        
        # 各フレームのアノテーションを構築
        for idx, frame_id in enumerate(frame_ids):
            if idx >= len(batch_results):
                continue
            
            result = batch_results[idx]
            keyframe = frame_id_to_keyframe.get(frame_id, {})
            
            annotation = {
                "id": frame_id,
                "frame_number": keyframe.get('frame_number', 0),
                "image_path": image_paths[idx] if idx < len(image_paths) else f'keyframe_{frame_id:04d}.jpg',
                "quality": {
                    "status": result.get("status", "unknown"),
                    "readable": result.get("readable", False)
                },
                "annotation": {}
            }
            
            # 品質情報を追加
            if result.get("reason"):
                annotation["quality"]["reason"] = result["reason"]
            
            # アノテーション内容を追加
            if result.get("status") == "success" and result.get("content"):
                content = result["content"]
                annotation["annotation"] = {
                    "scene": content.get("scene", ""),
                    "objects": content.get("objects", []),
                    "text": content.get("text", []),
                    "speaker_count": content.get("speaker_count"),
                    "visual_changes": content.get("visual_changes", [])
                }
            else:
                # エラー時は空のアノテーション
                annotation["annotation"] = {
                    "scene": "判定不可" if not result.get("readable") else "",
                    "objects": [],
                    "text": [],
                    "speaker_count": None,
                    "visual_changes": []
                }
            
            # 処理メタデータ
            annotation["processing_metadata"] = {
                "batch_id": batch_id,
                "skip_in_transcript": not result.get("readable", False)
            }
            
            annotations.append(annotation)
    
    # アノテーション結果構造を構築
    annotation_data = {
        "lm_studio_config": {
            "model": batch_plan["batching_config"]["lm_studio_config"]["model"],
            "endpoint": batch_plan["batching_config"]["lm_studio_config"]["endpoint"]
        },
        "annotations": annotations
    }
    
    # JSONファイルに保存
    annotation_path = os.path.join(video_subfolder, 'image_annotations.json')
    
    with open(annotation_path, 'w', encoding='utf-8') as f:
        json.dump(annotation_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ アノテーション結果保存: {annotation_path} ({len(annotations)}フレーム)")
    
    return annotation_path


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
        
        # フレームフィルタリング（時間差 < 0.5秒のフレーム削除）
        original_keyframe_count = len(keyframes)
        min_time_gap = DEBUG_CONFIG.get("filtering_min_time_gap_seconds", 0.5)
        filtering_enabled = DEBUG_CONFIG.get("filtering_enabled", True)
        
        if filtering_enabled:
            print(f"🔍 フレームフィルタリング中... (最小時間差: {min_time_gap}秒)")
            print(f"   フィルタリング前: {original_keyframe_count}フレーム")
            filtered_keyframes = filter_keyframes_by_time_gap(keyframes, video_path, min_time_gap)
            print(f"   フィルタリング後: {len(filtered_keyframes)}フレーム (削除: {original_keyframe_count - len(filtered_keyframes)}フレーム)")
            keyframes = filtered_keyframes
        else:
            print(f"🚫 フレームフィルタリング: 無効化されています ({original_keyframe_count}フレーム保持)")
        
        # キーフレーム画像を保存（ファイル名を更新）
        print("💾 キーフレーム画像を保存中...")
        _, video_subfolder = save_keyframes_to_disk(keyframes, video_id, app.config['OUTPUT_FOLDER'])
        print(f"✅ キーフレーム画像保存完了")
        
        # フレームメタデータ生成
        print("📋 フレームメタデータ生成中...")
        generate_frame_metadata(keyframes, video_path, video_id, app.config['OUTPUT_FOLDER'])
        
        # バッチプラン生成
        max_images_per_batch = DEBUG_CONFIG.get("batch_max_images", 6)
        print(f"📦 バッチプラン生成中... (最大{max_images_per_batch}枚/バッチ)")
        batch_plan_path = generate_batch_plan(keyframes, video_subfolder, max_images_per_batch, overlap_frames=1)
        
        # アノテーション処理（有効な場合）
        annotation_progress = {
            "status": "not_started",
            "current_batch": 0,
            "total_batches": 0,
            "completed_frames": 0,
            "total_frames": len(keyframes)
        }
        
        if DEBUG_CONFIG.get("annotation_enabled", False) and batch_plan_path:
            print("🤖 アノテーション処理開始...")
            annotation_progress["status"] = "in_progress"
            
            # バッチプランを読み込み
            with open(batch_plan_path, 'r', encoding='utf-8') as f:
                batch_plan = json.load(f)
            
            annotation_progress["total_batches"] = len(batch_plan['batches'])
            
            # 各バッチを処理
            for batch in batch_plan['batches']:
                batch_id = batch['batch_id']
                image_paths = batch['image_paths']
                annotation_progress["current_batch"] = batch_id
                
                print(f"📦 バッチ{batch_id}/{len(batch_plan['batches'])}処理中...")
                
                # アノテーション実行
                batch_results = annotate_images_with_lm_studio(image_paths, batch_id, video_subfolder)
                
                # バッチ結果を保存
                batch_result_path = os.path.join(video_subfolder, f'batch_{batch_id}_results.json')
                with open(batch_result_path, 'w', encoding='utf-8') as f:
                    json.dump(batch_results, f, ensure_ascii=False, indent=2)
                
                annotation_progress["completed_frames"] += len([r for r in batch_results if r.get("status") == "success"])
            
            # アノテーション結果を統合
            print("📝 アノテーション結果統合中...")
            generate_image_annotations(batch_plan_path, video_subfolder, keyframes)
            
            annotation_progress["status"] = "completed"
            print("✅ アノテーション処理完了")
        else:
            print("🚫 アノテーション: 無効化されています")
        
        # 進捗情報を保存（フロントエンド用）
        progress_path = os.path.join(video_subfolder, 'annotation_progress.json')
        with open(progress_path, 'w', encoding='utf-8') as f:
            json.dump(annotation_progress, f, ensure_ascii=False, indent=2)
        
        # 議事録生成（Qwen3-VL使用、エラー時はフォールバック）
        print("🧠 議事録を生成中...")
        minutes = generate_minutes_with_qwen3vl(transcript, keyframes)
        print(f"✅ 議事録生成完了")
        
        # 保存先フォルダ（サブフォルダがない場合はoutputs直下）
        save_folder = video_subfolder if video_subfolder else app.config['OUTPUT_FOLDER']
        
        # 1. 議事録Markdownを生成
        minutes_markdown = minutes_to_markdown(minutes)
        minutes_filename = "minutes.md"
        minutes_path = os.path.join(save_folder, minutes_filename)
        
        with open(minutes_path, 'w', encoding='utf-8') as f:
            f.write(minutes_markdown)
        print(f"✅ 議事録を保存: {minutes_filename}")
        
        # 2. 文字起こしMarkdownを生成
        transcript_markdown = transcript_to_markdown(transcript, keyframes, video_id)
        transcript_filename = "transcript.md"
        transcript_path = os.path.join(save_folder, transcript_filename)
        
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
        
        # 動画用サブフォルダを確認
        video_subfolder = os.path.join(app.config['OUTPUT_FOLDER'], video_prefix)
        
        # メモリ上にZIPファイルを作成
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # サブフォルダが存在する場合
            if os.path.exists(video_subfolder):
                # サブフォルダ内のすべてのファイルを追加
                for filename in os.listdir(video_subfolder):
                    file_path = os.path.join(video_subfolder, filename)
                    
                    if os.path.isfile(file_path):
                        # ファイル名を日本語に変更
                        if filename == "minutes.md":
                            arcname = f"議事録.md"
                        elif filename == "transcript.md":
                            arcname = f"文字起こし.md"
                        else:
                            arcname = filename
                        
                        zip_file.write(file_path, arcname=arcname)
                        print(f"✅ ZIP追加: {filename}")
            else:
                # レガシー形式：outputs直下のファイルを探す
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


@app.route('/api/debug-config', methods=['GET'])
def get_debug_config():
    """デバッグ設定をJSONで返す"""
    try:
        return jsonify(DEBUG_CONFIG)
    except Exception as e:
        print(f"❌ debug-config エラー: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/debug-info', methods=['GET'])
def get_debug_info():
    """デバッグ情報をJSONで返す"""
    try:
        debug_info = {
            "transnetv2_available": TRANSNETV2_AVAILABLE,
            "config": DEBUG_CONFIG,
            "model_status": "未初期化"
        }
        
        # TransNetV2モデルが初期化されているか確認
        if TRANSNETV2_AVAILABLE:
            if hasattr(detect_scene_changes_transnetv2, '_model'):
                model = detect_scene_changes_transnetv2._model
                weights_path = os.path.join(os.path.dirname(__file__), 'transnetv2', 'transnetv2-pytorch-weights.pth')
                
                debug_info["model_status"] = "初期化済み"
                debug_info["model_info"] = {
                    "device": str(next(model.parameters()).device),
                    "weights_file": weights_path,
                    "weights_exists": os.path.exists(weights_path),
                    "weights_size_mb": os.path.getsize(weights_path) / (1024*1024) if os.path.exists(weights_path) else 0
                }
            else:
                debug_info["model_status"] = "未初期化（初回実行時に初期化されます）"
        
        return jsonify(debug_info)
    except Exception as e:
        print(f"❌ debug-info エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/annotation-progress/<video_id>', methods=['GET'])
def get_annotation_progress(video_id):
    """アノテーション処理の進捗を取得"""
    try:
        video_prefix = video_id.replace('.', '_')
        video_subfolder = os.path.join(app.config['OUTPUT_FOLDER'], video_prefix)
        progress_path = os.path.join(video_subfolder, 'annotation_progress.json')
        
        if not os.path.exists(progress_path):
            return jsonify({
                "status": "not_started",
                "current_batch": 0,
                "total_batches": 0,
                "completed_frames": 0,
                "total_frames": 0,
                "percentage": 0
            })
        
        with open(progress_path, 'r', encoding='utf-8') as f:
            progress = json.load(f)
        
        # パーセンテージを計算
        if progress.get("total_frames", 0) > 0:
            percentage = int((progress.get("completed_frames", 0) / progress.get("total_frames", 1)) * 100)
        else:
            percentage = 0
        
        progress["percentage"] = percentage
        
        return jsonify(progress)
    
    except Exception as e:
        print(f"❌ 進捗取得エラー: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


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

