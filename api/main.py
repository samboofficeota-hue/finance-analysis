"""
EDINET DB 財務分析 Web API
FastAPIを使用したREST API
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List, Optional, Dict, Any
import requests
import os

app = FastAPI(
    title="EDINET DB 財務分析 API",
    description="上場企業の財務情報を取得・分析するWeb API",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIキー（環境変数 EDINET_API_KEY で設定。.env.local または Vercel の環境変数に記載）
API_KEY = os.environ.get("EDINET_API_KEY")
if not API_KEY:
    raise RuntimeError("EDINET_API_KEY が設定されていません。.env.local または Vercel の環境変数を設定してください。")
BASE_URL = "https://edinetdb.jp/v1"


class EDINETClient:
    """EDINET DB APIクライアント"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key}

    def _request(self, endpoint: str, params: Dict = None) -> Dict:
        """APIリクエスト共通処理"""
        url = f"{BASE_URL}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="指定された企業コードはEDINETに存在しません。コードを確認するか、企業検索で有効なコードを取得してください。"
                )
            if response.status_code == 401:
                raise HTTPException(
                    status_code=503,
                    detail="EDINET APIの認証に失敗しました。EDINET_API_KEY（APIキー）を確認してください。"
                )
            if response.status_code == 403:
                raise HTTPException(
                    status_code=503,
                    detail="EDINET APIへのアクセスが拒否されました。APIキーの有効性または利用制限を確認してください。"
                )
            response.raise_for_status()
            return response.json()
        except HTTPException:
            raise
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")

    def search_companies(self, query: str = None, per_page: int = 10, page: int = 1):
        # EDINET DB API の企業検索は /search?q= を使用（/companies?query= は非対応）
        if query:
            data = self._request("search", {"q": query})
            # レスポンスは {"data": [{ name, sec_code, edinet_code, ... }]} 形式
            raw_list = data.get("data") or data.get("companies") or []
            companies = []
            for c in raw_list:
                companies.append({
                    "edinet_code": c.get("edinet_code") or c.get("code", ""),
                    "name": c.get("name", ""),
                    "securities_code": c.get("securities_code") or c.get("sec_code") or "",
                    "industry": c.get("industry") or c.get("sector") or "",
                })
            return {"companies": companies[:per_page]}
        # キーワードなしの場合は企業一覧
        params = {"per_page": per_page, "page": page}
        return self._request("companies", params)

    def get_company_info(self, company_code: str):
        return self._request(f"companies/{company_code}")

    def get_financials(self, company_code: str, years: Optional[int] = None):
        """財務時系列を取得。years 指定時は直近 N 期に絞る（APIは全期間返す想定）。"""
        data = self._request(f"companies/{company_code}/financials")
        # EDINET API は "data" または "financials" で配列を返す
        raw_list = data.get("data") or data.get("financials") or []
        if years is not None and years > 0:
            raw_list = raw_list[: int(years)]
        # レスポンス形式を統一（キー financials で返す）
        if "data" in data and "financials" not in data:
            data = {"financials": raw_list, **{k: v for k, v in data.items() if k != "data"}}
        else:
            data["financials"] = raw_list
        return data

    def get_ranking(self, metric: str, limit: int = 10, order: str = "desc"):
        params = {"limit": limit, "order": order}
        return self._request(f"rankings/{metric}", params)


# クライアントインスタンス
client = EDINETClient(API_KEY)


def _load_index_html() -> str:
    """トップページ用HTMLを index_template.html から読み込む"""
    from pathlib import Path
    path = Path(__file__).parent / "index_template.html"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "<!DOCTYPE html><html><body><h1>EDINET DB 財務分析</h1><p>index_template.html を配置してください。</p></body></html>"


@app.get("/", response_class=HTMLResponse)
async def root():
    """トップページ（HTML）— 各機能の入力・出力画面"""
    return _load_index_html()


@app.get("/api-info")
async def api_info():
    """API情報（JSON）"""
    return {
        "message": "EDINET DB 財務分析 API",
        "version": "1.0.0",
        "endpoints": {
            "GET /companies": "企業を検索",
            "GET /companies/{code}": "企業の詳細情報",
            "GET /companies/{code}/financials": "企業の財務データ",
            "GET /rankings/{metric}": "ランキング取得",
            "GET /compare": "複数企業を比較"
        }
    }


@app.get("/health")
async def health():
    """ヘルスチェック"""
    return {"status": "ok"}


@app.get("/api-status")
async def api_status():
    """
    EDINET API との接続状態を確認します。
    - status: サービス疎通
    - api_key_ok: APIキーで検索が成功するか
    """
    result = {"status": "unknown", "api_key_ok": None, "detail": ""}
    try:
        # 認証不要のステータス確認（edinetdb.jp の仕様）
        r = requests.get(f"{BASE_URL}/status", timeout=10)
        result["status"] = "ok" if r.status_code == 200 else f"http_{r.status_code}"
        if r.status_code == 200 and r.text:
            try:
                result["edinet_status"] = r.json()
            except Exception:
                pass
    except requests.exceptions.RequestException as e:
        result["status"] = "error"
        result["detail"] = str(e)
        return result

    # APIキーで検索を1回試行
    try:
        data = client.search_companies("トヨタ", per_page=1)
        result["api_key_ok"] = bool(data.get("companies"))
        if not result["api_key_ok"] and result["status"] == "ok":
            result["detail"] = "検索は成功しましたが0件でした。APIキーは有効な可能性があります。"
    except HTTPException as e:
        result["api_key_ok"] = False
        result["detail"] = e.detail if hasattr(e, "detail") else str(e)
    except Exception as e:
        result["api_key_ok"] = False
        result["detail"] = str(e)

    return result


@app.get("/companies")
async def search_companies(
    query: Optional[str] = Query(None, description="検索キーワード（企業名）"),
    per_page: int = Query(10, ge=1, le=100, description="1ページあたりの件数"),
    page: int = Query(1, ge=1, description="ページ番号")
):
    """
    企業を検索

    - **query**: 検索キーワード（企業名）
    - **per_page**: 1ページあたりの件数（1-100）
    - **page**: ページ番号
    """
    return client.search_companies(query, per_page, page)


@app.get("/companies/{company_code}")
async def get_company_info(company_code: str):
    """
    企業の詳細情報を取得

    - **company_code**: 企業コード（例: E02367）
    """
    try:
        return client.get_company_info(company_code)
    except HTTPException:
        raise


@app.get("/companies/{company_code}/financials")
async def get_financials(
    company_code: str,
    years: Optional[int] = Query(None, description="表示する直近の期数（例: 5 → 直近5期）。省略時はAPIの全期間"),
):
    """
    企業の財務データを取得

    - **company_code**: 企業コード（例: E02367）
    - **years**: 対象範囲（直近何期分か）。指定しない場合はAPIが返す全期間
    """
    try:
        return client.get_financials(company_code, years=years)
    except HTTPException:
        raise


@app.get("/rankings/{metric}")
async def get_ranking(
    metric: str,
    limit: int = Query(10, ge=1, le=100, description="取得件数"),
    order: str = Query("desc", regex="^(asc|desc)$", description="並び順")
):
    """
    ランキングを取得

    - **metric**: 指標名（roe, roa, sales, market_cap, operating_income）
    - **limit**: 取得件数（1-100）
    - **order**: 並び順（asc: 昇順, desc: 降順）
    """
    valid_metrics = ["roe", "roa", "sales", "market_cap", "operating_income"]
    if metric not in valid_metrics:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric. Valid options: {', '.join(valid_metrics)}"
        )

    return client.get_ranking(metric, limit, order)


@app.get("/compare")
async def compare_companies(
    codes: str = Query(..., description="企業コード（カンマ区切り、例: E02367,E01825,E02503）"),
    years: Optional[int] = Query(None, description="対象範囲（直近何期）。省略時はAPIの全期間"),
):
    """
    複数企業の財務データを比較

    - **codes**: 企業コード（カンマ区切り、例: E02367,E01825,E02503）
    - **years**: 対象範囲（直近何期）
    """
    company_codes = [code.strip() for code in codes.split(",")]

    if len(company_codes) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 company codes are required"
        )

    if len(company_codes) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 companies can be compared at once"
        )

    results = []
    errors = []

    for code in company_codes:
        try:
            info = client.get_company_info(code)
            financials = client.get_financials(code, years=years)
            results.append({
                "code": code,
                "name": info.get("name"),
                "info": info,
                "financials": financials
            })
        except Exception as e:
            errors.append({
                "code": code,
                "error": str(e)
            })

    return {
        "success": results,
        "errors": errors
    }


@app.get("/companies/{company_code}/analysis")
async def get_company_analysis(
    company_code: str,
    years: Optional[int] = Query(None, description="対象範囲（直近何期）。省略時はAPIの全期間から直近を使用"),
):
    """
    企業の財務分析サマリー

    - **company_code**: 企業コード（例: E02367）
    - **years**: 対象範囲（直近何期）。指定時はその範囲の直近1期で分析
    """
    try:
        info = client.get_company_info(company_code)
        financials = client.get_financials(company_code, years=years)

        if not financials.get("financials"):
            raise HTTPException(status_code=404, detail="No financial data available")

        latest = financials["financials"][0]

        # 簡易分析
        analysis = {
            "company": {
                "code": company_code,
                "name": info.get("name"),
                "industry": info.get("industry"),
                "securities_code": info.get("securities_code")
            },
            "latest_period": {
                "fiscal_period": latest.get("fiscal_period"),
                "fiscal_year_end_date": latest.get("fiscal_year_end_date")
            },
            "performance": {
                "net_sales": latest.get("net_sales"),
                "operating_income": latest.get("operating_income"),
                "ordinary_income": latest.get("ordinary_income"),
                "net_income": latest.get("net_income")
            },
            "balance": {
                "total_assets": latest.get("total_assets"),
                "net_assets": latest.get("net_assets"),
                "equity": latest.get("equity")
            },
            "indicators": {
                "roe": latest.get("roe"),
                "roa": latest.get("roa"),
                "equity_ratio": latest.get("equity_ratio"),
                "operating_margin": latest.get("operating_margin")
            },
            "ratings": {
                "profitability": rate_profitability(latest.get("roe")),
                "efficiency": rate_efficiency(latest.get("roa")),
                "stability": rate_stability(latest.get("equity_ratio"))
            }
        }

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def rate_profitability(roe: float) -> str:
    """収益性評価"""
    if roe is None:
        return "N/A"
    if roe >= 15:
        return "優秀"
    elif roe >= 10:
        return "良好"
    elif roe >= 5:
        return "普通"
    else:
        return "要改善"


def rate_efficiency(roa: float) -> str:
    """効率性評価"""
    if roa is None:
        return "N/A"
    if roa >= 10:
        return "優秀"
    elif roa >= 5:
        return "良好"
    elif roa >= 2:
        return "普通"
    else:
        return "要改善"


def rate_stability(equity_ratio: float) -> str:
    """安全性評価"""
    if equity_ratio is None:
        return "N/A"
    if equity_ratio >= 50:
        return "優秀"
    elif equity_ratio >= 30:
        return "良好"
    elif equity_ratio >= 20:
        return "普通"
    else:
        return "要改善"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
