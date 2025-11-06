#!/bin/bash

# 議事録エージェント クイックセットアップスクリプト

set -e  # エラーで停止

echo "======================================"
echo "  議事録エージェント セットアップ"
echo "======================================"
echo ""

# 現在のディレクトリを確認
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📂 作業ディレクトリ: $SCRIPT_DIR"
echo ""

# Step 1: 仮想環境のチェック
if [ ! -d "venv" ]; then
    echo "🐍 仮想環境を作成中..."
    python3 -m venv venv
    echo "✅ 仮想環境を作成しました"
else
    echo "✅ 仮想環境は既に存在します"
fi
echo ""

# Step 2: 仮想環境をアクティブ化
echo "🔄 仮想環境をアクティブ化中..."
source venv/bin/activate
echo "✅ 仮想環境をアクティブ化しました"
echo ""

# Step 3: パッケージインストール
echo "📦 パッケージをインストール中..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ パッケージをインストールしました"
echo ""

# Step 4: .envファイルのチェック
if [ ! -f ".env" ]; then
    echo "⚠️  .env ファイルが見つかりません"
    echo ""
    echo "以下の情報を入力してください:"
    echo ""
    
    # Groq API Key
    read -p "Groq API Key (gsk_...): " GROQ_KEY
    
    # Modal Endpoint (オプション)
    read -p "Modal Endpoint URL (Enter でスキップ): " MODAL_ENDPOINT
    
    # OpenAI API Key (オプション)
    read -p "OpenAI API Key (Enter でスキップ): " OPENAI_KEY
    
    # .envファイルを作成
    cat > .env << EOF
# Groq API Key (必須)
GROQ_API_KEY=$GROQ_KEY

# Modal Qwen3-VL Endpoint (オプション)
MODAL_QWEN3VL_ENDPOINT=$MODAL_ENDPOINT

# OpenAI API Key (オプション)
OPENAI_API_KEY=$OPENAI_KEY
EOF
    
    echo ""
    echo "✅ .env ファイルを作成しました"
else
    echo "✅ .env ファイルは既に存在します"
fi
echo ""

# Step 5: Modalのチェック（オプション）
echo "🔍 Modal のチェック..."
if command -v modal &> /dev/null; then
    echo "✅ Modal はインストール済みです"
    
    # Modal認証のチェック
    if modal token verify &> /dev/null; then
        echo "✅ Modal 認証済みです"
    else
        echo "⚠️  Modal 認証が必要です"
        echo ""
        echo "以下のコマンドを実行してください:"
        echo "  modal setup"
        echo ""
    fi
else
    echo "⚠️  Modal がインストールされていません"
    echo ""
    echo "Modal を使用する場合は以下を実行してください:"
    echo "  pip install modal"
    echo "  modal setup"
    echo "  modal deploy modal_qwen3vl.py"
    echo ""
fi
echo ""

# Step 6: 必要なディレクトリを作成
echo "📁 必要なディレクトリを作成中..."
mkdir -p uploads outputs
echo "✅ ディレクトリを作成しました"
echo ""

# Step 7: サーバー起動確認
echo "======================================"
echo "  セットアップ完了！"
echo "======================================"
echo ""
echo "サーバーを起動するには:"
echo "  python app.py"
echo ""
echo "ブラウザで以下にアクセス:"
echo "  http://localhost:5001"
echo ""
echo "======================================"
echo ""

# オプション: サーバーを起動するか確認
read -p "今すぐサーバーを起動しますか？ (y/N): " START_SERVER

if [ "$START_SERVER" = "y" ] || [ "$START_SERVER" = "Y" ]; then
    echo ""
    echo "🚀 サーバーを起動中..."
    echo ""
    python app.py
else
    echo ""
    echo "後で 'python app.py' を実行してサーバーを起動してください。"
    echo ""
fi

