# EDINET DB 財務分析 Web API 🌐

上場企業の財務情報を提供するREST API（FastAPI製）

## 🎯 2つの使い方

### 1. コマンドラインツール（CLI）
- **ファイル**: `edinet_analyzer.py`
- **用途**: ローカル環境でコマンド実行
- **詳細**: [README.md](README.md) または [QUICKSTART.md](QUICKSTART.md)

### 2. Web API
- **ファイル**: `api/main.py`
- **用途**: Webサービスとしてデプロイ、他のアプリから利用
- **詳細**: このドキュメント

---

## 🚀 Web API のデプロイ

### ✨ クイックデプロイ

**Vercel（推奨）**
```bash
# Vercel CLIをインストール
npm i -g vercel

# デプロイ
vercel
```

**Railway**
```bash
# Railway CLIをインストール
npm i -g @railway/cli

# ログイン
railway login

# デプロイ
railway up
```

**詳細な手順は [DEPLOYMENT.md](DEPLOYMENT.md) を参照**

---

## 📡 API エンドポイント

### 基本情報

```
GET /              - API情報
GET /health        - ヘルスチェック
GET /docs          - Swagger UI（インタラクティブなドキュメント）
GET /redoc         - ReDoc（美しいドキュメント）
```

### 企業検索

```bash
# 企業を検索
GET /companies?query=任天堂&per_page=10&page=1

# 例
curl "https://your-api.com/companies?query=トヨタ"
```

**レスポンス例:**
```json
{
  "companies": [
    {
      "edinet_code": "E01825",
      "name": "トヨタ自動車株式会社",
      "securities_code": "7203",
      "industry": "輸送用機器"
    }
  ]
}
```

### 企業情報

```bash
# 企業の詳細情報を取得
GET /companies/{company_code}

# 例
curl "https://your-api.com/companies/E02367"
```

### 財務データ

```bash
# 企業の財務データを取得
GET /companies/{company_code}/financials

# 例
curl "https://your-api.com/companies/E02367/financials"
```

**レスポンス例:**
```json
{
  "financials": [
    {
      "fiscal_period": "2024年3月期",
      "net_sales": 1671635000000,
      "operating_income": 528961000000,
      "net_income": 370466000000,
      "roe": 14.85,
      "roa": 12.35
    }
  ]
}
```

### ランキング

```bash
# ランキングを取得
GET /rankings/{metric}?limit=10&order=desc

# ROEランキング
curl "https://your-api.com/rankings/roe?limit=10"

# 利用可能な指標
# - roe (自己資本利益率)
# - roa (総資産利益率)
# - sales (売上高)
# - market_cap (時価総額)
# - operating_income (営業利益)
```

### 企業比較

```bash
# 複数企業を比較（カンマ区切り）
GET /compare?codes=E02367,E01825,E02503

# 例
curl "https://your-api.com/compare?codes=E02367,E01825"
```

### 分析サマリー（新機能！）

```bash
# 企業の財務分析サマリーを取得
GET /companies/{company_code}/analysis

# 例
curl "https://your-api.com/companies/E02367/analysis"
```

**レスポンス例:**
```json
{
  "company": {
    "code": "E02367",
    "name": "任天堂株式会社",
    "industry": "その他製品"
  },
  "indicators": {
    "roe": 14.85,
    "roa": 12.35,
    "equity_ratio": 82.65
  },
  "ratings": {
    "profitability": "良好",
    "efficiency": "優秀",
    "stability": "優秀"
  }
}
```

---

## 🧪 ローカルでテスト

### 1. FastAPIを起動

```bash
# 依存関係をインストール
pip install -r api/requirements.txt

# サーバーを起動
python -m uvicorn api.main:app --reload
```

サーバーが起動したら:
- API: http://localhost:8000
- ドキュメント: http://localhost:8000/docs

### 2. テストスクリプトを実行

```bash
# APIテストスクリプトを実行
python test_api.py http://localhost:8000
```

---

## 🌐 デプロイ後のテスト

```bash
# デプロイしたAPIをテスト
python test_api.py https://your-project.vercel.app
```

---

## 💻 フロントエンドからの利用例

### JavaScript (Fetch API)

```javascript
// 企業検索
async function searchCompany(query) {
  const response = await fetch(
    `https://your-api.com/companies?query=${query}`
  );
  const data = await response.json();
  return data.companies;
}

// 財務データ取得
async function getFinancials(code) {
  const response = await fetch(
    `https://your-api.com/companies/${code}/financials`
  );
  return await response.json();
}

// ROEランキング
async function getRoeRanking(limit = 10) {
  const response = await fetch(
    `https://your-api.com/rankings/roe?limit=${limit}`
  );
  const data = await response.json();
  return data.ranking;
}
```

### Python (requests)

```python
import requests

BASE_URL = "https://your-api.com"

# 企業検索
def search_company(query):
    response = requests.get(
        f"{BASE_URL}/companies",
        params={"query": query}
    )
    return response.json()["companies"]

# 財務データ取得
def get_financials(code):
    response = requests.get(f"{BASE_URL}/companies/{code}/financials")
    return response.json()

# 分析サマリー
def get_analysis(code):
    response = requests.get(f"{BASE_URL}/companies/{code}/analysis")
    return response.json()
```

---

## 📊 レスポンス形式

すべてのAPIはJSON形式でデータを返します。

### 成功レスポンス
```json
{
  "companies": [...],
  "financials": [...],
  "ranking": [...]
}
```

### エラーレスポンス
```json
{
  "detail": "Company not found"
}
```

---

## 🔐 環境変数

本番環境では、APIキーを環境変数で設定してください：

```bash
export EDINET_API_KEY="your_api_key_here"
```

デプロイ時は、プラットフォームの環境変数設定で追加：
- Vercel: Settings → Environment Variables
- Railway: Variables タブ

---

## 📈 パフォーマンス

- **Vercel**: サーバーレス、コールドスタートあり
- **Railway**: 常時起動、高速レスポンス

### レート制限（推奨）

本番環境では、レート制限の実装を推奨します（詳細は DEPLOYMENT.md）。

---

## 🛠️ カスタマイズ

### 新しいエンドポイントを追加

`api/main.py` に追加:

```python
@app.get("/custom-endpoint")
async def custom_endpoint():
    return {"message": "Hello World"}
```

### CORSの設定変更

必要に応じて `api/main.py` の CORS 設定を変更:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    ...
)
```

---

## 📚 参考リンク

- [FastAPI ドキュメント](https://fastapi.tiangolo.com/)
- [EDINET DB API](https://edinetdb.jp/)
- [Vercel Python ランタイム](https://vercel.com/docs/functions/runtimes/python)
- [Railway ドキュメント](https://docs.railway.app/)

---

## 🤝 活用例

### 1. 株式分析ダッシュボード
Next.js + このAPIで財務ダッシュボードを構築

### 2. Discord/Slack Bot
企業情報を自動で取得するBot

### 3. モバイルアプリ
React Native / Flutter でこのAPIを使用

### 4. データ分析
Jupyter NotebookからこのAPIを呼び出してデータ分析

---

**Happy API Building! 🎉**
