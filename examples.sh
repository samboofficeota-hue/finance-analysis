#!/bin/bash
# EDINET DB 財務分析ツール - 実行例

echo "================================"
echo "EDINET DB 財務分析ツール - 実行例"
echo "================================"
echo ""

# 1. 企業検索
echo "1. 企業検索（任天堂を検索）"
echo "$ python3 edinet_analyzer.py search \"任天堂\""
echo ""

# 2. 企業の基本情報
echo "2. 企業の基本情報（任天堂）"
echo "$ python3 edinet_analyzer.py info E02367"
echo ""

# 3. 財務データ表示
echo "3. 財務データ（任天堂）"
echo "$ python3 edinet_analyzer.py financials E02367"
echo ""

# 4. ROEランキング
echo "4. ROEランキング TOP10"
echo "$ python3 edinet_analyzer.py ranking roe --limit 10"
echo ""

# 5. 企業比較
echo "5. 企業比較（任天堂、ソニー、トヨタ）"
echo "$ python3 edinet_analyzer.py compare E02367 E02503 E01825"
echo ""

# 6. CSV出力
echo "6. ランキングをCSV出力"
echo "$ python3 edinet_analyzer.py ranking roe --limit 30 --export roe_ranking.csv"
echo ""

echo "================================"
echo "上記コマンドを実行してお試しください！"
echo "================================"
