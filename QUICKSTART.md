# クイックスタートガイド 🚀

## 10秒で始める

### 1. インストール

```bash
pip install requests
```

### 2. すぐに試せるコマンド

```bash
# 任天堂を検索
python3 edinet_analyzer.py search "任天堂"

# 任天堂の財務データを表示
python3 edinet_analyzer.py financials E02367

# ROEランキング TOP10
python3 edinet_analyzer.py ranking roe --limit 10
```

## 主要コマンド早見表

| コマンド | 説明 | 例 |
|---------|------|-----|
| `search` | 企業を検索 | `search "トヨタ"` |
| `info` | 基本情報を表示 | `info E01825` |
| `financials` | 財務データを表示 | `financials E02367` |
| `ranking` | ランキング表示 | `ranking roe --limit 10` |
| `compare` | 複数企業を比較 | `compare E02367 E01825` |

## 主要企業のコード一覧

| 企業名 | EDINETコード |
|--------|--------------|
| 任天堂 | E02367 |
| トヨタ自動車 | E01825 |
| ソニーグループ | E02503 |
| ソフトバンクグループ | E04425 |
| キーエンス | E01967 |
| ファーストリテイリング | E03516 |

## ヘルプ表示

```bash
# 全体のヘルプ
python3 edinet_analyzer.py --help

# 各コマンドのヘルプ
python3 edinet_analyzer.py search --help
python3 edinet_analyzer.py ranking --help
```

## よくある使い方

### 業界の上位企業を分析

```bash
# 1. 業界キーワードで検索
python3 edinet_analyzer.py search "製薬"

# 2. 気になる企業のコードをメモ

# 3. 比較
python3 edinet_analyzer.py compare E00000 E00001 E00002
```

### 高収益企業を探す

```bash
# ROEランキングをCSV出力
python3 edinet_analyzer.py ranking roe --limit 50 --export high_roe.csv

# Excelで開いて分析
```

---

詳しい使い方は [README.md](README.md) をご覧ください。
