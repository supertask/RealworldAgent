"""
Modal Qwen3-VL API for Meeting Minutes Generation

このファイルをModalにデプロイして、画像付き議事録を生成します。

デプロイコマンド:
    modal deploy modal_qwen3vl.py

デプロイ後、表示されるURLを.envの MODAL_QWEN3VL_ENDPOINT に設定してください。
"""

import modal
import base64
import json
import io

app = modal.App("qwen3vl-meeting-minutes")

# イメージ定義
image = modal.Image.debian_slim().pip_install(
    "transformers>=4.37.0",
    "torch>=2.1.0",
    "torchvision>=0.16.0",
    "pillow>=10.0.0",
    "qwen-vl-utils>=0.0.2",
    "accelerate>=0.25.0",
    "fastapi>=0.115.0"
)

@app.cls(
    image=image,
    gpu="A100",  # Qwen3-VL 7Bには最低でもA100が必要
    timeout=300,
    memory=32768,  # 32GB RAM
    container_idle_timeout=300,  # 5分間モデルをキャッシュ
)
class Qwen3VLModel:
    def __init__(self):
        """モデルを初期化（コンテナ起動時に1回だけ実行）"""
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        import torch
        
        print("🔄 モデル初期化中...")
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            "Qwen/Qwen2-VL-7B-Instruct",
            dtype=torch.float16,
            device_map="auto"
        )
        self.processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-7B-Instruct")
        print("✅ モデル初期化完了")
    
    @modal.method()
    def generate(self, text: str, images: list[str], prompt: str):
        """Qwen3-VLで議事録セクションを生成
        
        Args:
            text: 音声文字起こしテキスト
            images: Base64エンコードされた画像リスト
            prompt: LLMへのプロンプト
        
        Returns:
            dict: 議事録セクション（JSON形式）
        """
        from qwen_vl_utils import process_vision_info
        from PIL import Image
        import torch
        
        print(f"📥 リクエスト受信: テキスト長={len(text)}, 画像数={len(images)}")
        
        # 画像をデコード
        pil_images = []
        for idx, img_b64 in enumerate(images):
            try:
                img_data = base64.b64decode(img_b64)
                img = Image.open(io.BytesIO(img_data))
                pil_images.append(img)
                print(f"✅ 画像 {idx+1}/{len(images)} デコード成功: {img.size}")
            except Exception as e:
                print(f"❌ 画像 {idx+1} デコードエラー: {str(e)}")
                continue
        
        if not pil_images:
            print("⚠️ 有効な画像がありません - テキストのみで処理")
            # 画像なしでテキストのみ処理
            return {
                "section_title": "セクション",
                "content": text[:500] if text else "内容なし",
                "key_points": [],
                "related_images": []
            }
        
        # メッセージ構築
        content_items = [{"type": "text", "text": prompt}]
        content_items.extend([{"type": "image", "image": img} for img in pil_images])
        
        messages = [
            {
                "role": "user",
                "content": content_items
            }
        ]
        
        print(f"🧠 Qwen3-VL 推論開始...")
        
        try:
            # チャットテンプレート適用
            text_input = self.processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # 画像処理
            image_inputs, video_inputs = process_vision_info(messages)
            
            # 入力準備
            inputs = self.processor(
                text=[text_input],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt"
            )
            inputs = inputs.to("cuda")
            
            # 推論実行
            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.7,
                    do_sample=True
                )
            
            # デコード
            result_text = self.processor.batch_decode(
                output,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )[0]
            
            print(f"✅ 推論完了: {len(result_text)} 文字")
            
            # JSON形式でパース試行
            try:
                # プロンプトで指定したJSON形式を抽出
                if "{" in result_text and "}" in result_text:
                    json_start = result_text.find("{")
                    json_end = result_text.rfind("}") + 1
                    json_str = result_text[json_start:json_end]
                    result_json = json.loads(json_str)
                    print(f"✅ JSON パース成功")
                    return result_json
                else:
                    raise ValueError("JSON形式が見つかりません")
            except Exception as e:
                print(f"⚠️ JSON パースエラー: {str(e)} - フォールバック形式で返却")
                # JSON形式でない場合はフォールバック
                return {
                    "section_title": "会議内容",
                    "content": result_text[:500],
                    "key_points": [line.strip() for line in result_text.split('\n') if line.strip()][:5],
                    "related_images": list(range(min(len(pil_images), 3)))  # 最初の3枚
                }
        
        except Exception as e:
            print(f"❌ 推論エラー: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # エラー時のフォールバック
            return {
                "section_title": "セクション（エラー発生）",
                "content": text[:300] if text else "処理中にエラーが発生しました",
                "key_points": [],
                "related_images": []
            }


@app.function(image=image)
@modal.asgi_app()
def fastapi_app():
    """FastAPI アプリケーション"""
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    
    web_app = FastAPI()
    model_instance = Qwen3VLModel()
    
    @web_app.post("/")
    async def endpoint(request: Request):
        """REST API エンドポイント
        
        POST リクエスト例:
        {
            "text": "音声文字起こしテキスト",
            "images": ["base64_encoded_image1", "base64_encoded_image2"],
            "prompt": "LLMへのプロンプト"
        }
        
        レスポンス例:
        {
            "section_title": "セクションタイトル",
            "content": "内容の要約",
            "key_points": ["ポイント1", "ポイント2"],
            "related_images": [0, 1]
        }
        """
        try:
            data = await request.json()
            text = data.get("text", "")
            images = data.get("images", [])
            prompt = data.get("prompt", "")
            
            print(f"🌐 Web エンドポイント呼び出し")
            
            result = model_instance.generate.remote(text, images, prompt)
            
            return JSONResponse({
                "status": "success",
                **result
            })
        
        except Exception as e:
            print(f"❌ エンドポイントエラー: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return JSONResponse({
                "status": "error",
                "error": str(e),
                "section_title": "エラー",
                "content": "処理中にエラーが発生しました",
                "key_points": [],
                "related_images": []
            }, status_code=500)
    
    return web_app

