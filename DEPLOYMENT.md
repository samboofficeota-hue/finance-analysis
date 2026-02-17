# デプロイ手順書 🚀

このAPIは**Vercel**または**Railway**にデプロイできます。

## 📋 事前準備

### 必要なもの
- GitHub アカウント
- Vercel または Railway アカウント
- EDINET DB API キー

### プロジェクトをGitHubにプッシュ

```bash
# Git初期化
git init

# ファイルを追加
git add .

# コミット
git commit -m "Initial commit: EDINET DB API"

# GitHubリポジトリを作成してプッシュ
git remote add origin https://github.com/YOUR_USERNAME/edinet-api.git
git branch -M main
git push -u origin main
```

---

## 🔵 Vercel へのデプロイ（推奨）

### 手順

1. **Vercelにログイン**
   - https://vercel.com にアクセス
   - GitHubアカウントでログイン

2. **新規プロジェクトを作成**
   - "New Project" をクリック
   - GitHubリポジトリを選択してインポート

3. **環境変数を設定**
   - "Environment Variables" セクションで以下を追加：
     ```
     EDINET_API_KEY = edb_c0990ba3d64565a58dc8339c09c38099
     ```

4. **デプロイ**
   - "Deploy" ボタンをクリック
   - 数分でデプロイ完了

5. **APIにアクセス**
   - デプロイ完了後、URLが発行されます（例: `https://your-project.vercel.app`）
   - `https://your-project.vercel.app/` でAPIドキュメントを確認

### Vercel CLI を使ったデプロイ

```bash
# Vercel CLI インストール
npm i -g vercel

# プロジェクトディレクトリでデプロイ
vercel

# 本番環境にデプロイ
vercel --prod
```

### 注意点

- Vercelは無料プランでも十分使えます
- サーバーレス関数として動作するため、常時起動ではありません
- コールドスタートがあります（初回リクエストが少し遅い）

---

## 🚂 Railway へのデプロイ

### 手順

1. **Railwayにログイン**
   - https://railway.app にアクセス
   - GitHubアカウントでログイン

2. **新規プロジェクトを作成**
   - "New Project" をクリック
   - "Deploy from GitHub repo" を選択
   - リポジトリを選択

3. **環境変数を設定**
   - "Variables" タブで以下を追加：
     ```
     EDINET_API_KEY = edb_c0990ba3d64565a58dc8339c09c38099
     PORT = 8000
     ```

4. **デプロイ設定**
   - Railwayが自動的に設定を検出します
   - `railway.json` と `Procfile` が使用されます

5. **デプロイ**
   - 自動的にデプロイが開始されます
   - 数分でデプロイ完了

6. **ドメインを設定**
   - "Settings" → "Generate Domain" でパブリックURLを取得

### Railway CLI を使ったデプロイ

```bash
# Railway CLI インストール
npm i -g @railway/cli

# ログイン
railway login

# プロジェクトを初期化
railway init

# デプロイ
railway up
```

### 注意点

- Railwayは無料プランで月500時間まで利用可能
- 常時起動のサーバーとして動作（コールドスタートなし）
- より安定したパフォーマンス

---

## 📊 API エンドポイント

デプロイ後、以下のエンドポイントが利用可能になります：

### ドキュメント
- `GET /` - API情報
- `GET /docs` - Swagger UI（自動生成）
- `GET /redoc` - ReDoc（自動生成）

### 企業検索
```bash
GET /companies?query=任天堂&per_page=10
```

### 企業情報
```bash
GET /companies/E02367
```

### 財務データ
```bash
GET /companies/E02367/financials
```

### ランキング
```bash
GET /rankings/roe?limit=10
```

### 企業比較
```bash
GET /compare?codes=E02367,E01825,E02503
```

### 分析サマリー
```bash
GET /companies/E02367/analysis
```

---

## 🧪 デプロイ後のテスト

### curlでテスト

```bash
# APIルートを確認
curl https://your-project.vercel.app/

# 任天堂を検索
curl https://your-project.vercel.app/companies?query=任天堂

# 任天堂の財務データ
curl https://your-project.vercel.app/companies/E02367/financials

# ROEランキング
curl https://your-project.vercel.app/rankings/roe?limit=10
```

### ブラウザでテスト

デプロイしたURL + `/docs` にアクセスすると、インタラクティブなAPIドキュメントが表示されます。

例: `https://your-project.vercel.app/docs`

---

## 🔧 トラブルシューティング

### Vercel

**エラー: Module not found**
- `api/requirements.txt` が正しく配置されているか確認
- `vercel.json` の設定を確認

**エラー: API request failed**
- 環境変数 `EDINET_API_KEY` が設定されているか確認
- Vercelの "Settings" → "Environment Variables" で確認

### Railway

**エラー: Build failed**
- `Procfile` が正しく配置されているか確認
- 起動コマンドが正しいか確認

**エラー: Port binding**
- 環境変数 `PORT` が設定されているか確認（通常は自動設定）

---

## 📈 本番運用時の推奨設定

### 1. APIキーを環境変数で管理

コード内のハードコードされたAPIキーを削除し、必ず環境変数から読み込むようにしてください。

### 2. レート制限を設定

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.get("/companies")
@limiter.limit("10/minute")
async def search_companies(...):
    ...
```

### 3. キャッシュを導入

```python
from functools import lru_cache
from datetime import timedelta

@lru_cache(maxsize=128)
def cached_company_info(company_code: str):
    return client.get_company_info(company_code)
```

### 4. ログ監視

- Vercel: ダッシュボードの "Logs" タブ
- Railway: ダッシュボードの "Deployments" → "View Logs"

---

## 💰 料金について

### Vercel
- **無料プラン**: 月100GBの帯域幅、十分な実行時間
- **制限**: サーバーレス関数の実行時間10秒まで

### Railway
- **無料プラン**: 月500時間、512MBメモリ
- **制限**: クレジットカード登録で上限アップ

---

## 📚 参考リンク

- [Vercel ドキュメント](https://vercel.com/docs)
- [Railway ドキュメント](https://docs.railway.app/)
- [FastAPI ドキュメント](https://fastapi.tiangolo.com/)

---

**Happy Deploying! 🎉**
