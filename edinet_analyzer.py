#!/usr/bin/env python3
"""
EDINET DB 財務分析ツール
上場企業の財務情報を取得・分析するコマンドラインツール
"""

import requests
import argparse
import json
import sys
from typing import Dict, List, Optional
from datetime import datetime
import csv

class EDINETAnalyzer:
    """EDINET DB APIクライアント"""

    BASE_URL = "https://edinetdb.jp/v1"

    def __init__(self, api_key: str):
        """
        Args:
            api_key: EDINET DB APIキー
        """
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key}

    def _request(self, endpoint: str, params: Dict = None) -> Dict:
        """APIリクエスト共通処理"""
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ APIリクエストエラー: {e}", file=sys.stderr)
            sys.exit(1)

    def search_companies(self, query: str = None, per_page: int = 10, page: int = 1) -> List[Dict]:
        """
        企業を検索

        Args:
            query: 検索キーワード（企業名）
            per_page: 1ページあたりの件数
            page: ページ番号

        Returns:
            企業情報のリスト
        """
        params = {"per_page": per_page, "page": page}
        if query:
            params["query"] = query

        data = self._request("companies", params)
        return data.get("companies", [])

    def get_company_info(self, company_code: str) -> Dict:
        """
        企業の基本情報を取得

        Args:
            company_code: 企業コード（例: E02367）

        Returns:
            企業の詳細情報
        """
        return self._request(f"companies/{company_code}")

    def get_financials(self, company_code: str) -> Dict:
        """
        企業の財務データを取得

        Args:
            company_code: 企業コード

        Returns:
            財務データ
        """
        return self._request(f"companies/{company_code}/financials")

    def get_ranking(self, metric: str, limit: int = 10, order: str = "desc") -> List[Dict]:
        """
        ランキングを取得

        Args:
            metric: 指標名 (roe, roa, sales, market_cap等)
            limit: 取得件数
            order: 並び順 (desc: 降順, asc: 昇順)

        Returns:
            ランキングデータ
        """
        params = {"limit": limit, "order": order}
        data = self._request(f"rankings/{metric}", params)
        return data.get("ranking", [])

    def compare_companies(self, company_codes: List[str]) -> List[Dict]:
        """
        複数企業の財務データを比較

        Args:
            company_codes: 企業コードのリスト

        Returns:
            各企業の財務データリスト
        """
        results = []
        for code in company_codes:
            try:
                info = self.get_company_info(code)
                financials = self.get_financials(code)
                results.append({
                    "code": code,
                    "name": info.get("name"),
                    "info": info,
                    "financials": financials
                })
            except Exception as e:
                print(f"⚠️  {code} のデータ取得に失敗: {e}", file=sys.stderr)

        return results


def print_company_list(companies: List[Dict]):
    """企業リストを見やすく表示"""
    print("\n" + "="*80)
    print("企業一覧")
    print("="*80)

    for i, company in enumerate(companies, 1):
        code = company.get("edinet_code", "N/A")
        name = company.get("name", "N/A")
        securities_code = company.get("securities_code", "N/A")

        print(f"\n{i}. {name}")
        print(f"   EDINETコード: {code}")
        print(f"   証券コード: {securities_code}")


def print_company_detail(company: Dict):
    """企業詳細を表示"""
    print("\n" + "="*80)
    print(f"企業情報: {company.get('name', 'N/A')}")
    print("="*80)

    print(f"\nEDINETコード: {company.get('edinet_code', 'N/A')}")
    print(f"証券コード: {company.get('securities_code', 'N/A')}")
    print(f"業種: {company.get('industry', 'N/A')}")
    print(f"所在地: {company.get('address', 'N/A')}")
    print(f"設立年月日: {company.get('established_date', 'N/A')}")


def print_financials(company_name: str, financials: Dict):
    """財務情報を表示"""
    print("\n" + "="*80)
    print(f"財務情報: {company_name}")
    print("="*80)

    if "financials" in financials and financials["financials"]:
        latest = financials["financials"][0]  # 最新の財務データ

        print(f"\n決算期: {latest.get('fiscal_period', 'N/A')}")
        print(f"決算日: {latest.get('fiscal_year_end_date', 'N/A')}")

        print("\n【損益計算書】")
        print(f"  売上高: {format_number(latest.get('net_sales'))} 円")
        print(f"  営業利益: {format_number(latest.get('operating_income'))} 円")
        print(f"  経常利益: {format_number(latest.get('ordinary_income'))} 円")
        print(f"  当期純利益: {format_number(latest.get('net_income'))} 円")

        print("\n【貸借対照表】")
        print(f"  総資産: {format_number(latest.get('total_assets'))} 円")
        print(f"  純資産: {format_number(latest.get('net_assets'))} 円")
        print(f"  自己資本: {format_number(latest.get('equity'))} 円")

        print("\n【財務指標】")
        print(f"  ROE (自己資本利益率): {format_percent(latest.get('roe'))} %")
        print(f"  ROA (総資産利益率): {format_percent(latest.get('roa'))} %")
        print(f"  自己資本比率: {format_percent(latest.get('equity_ratio'))} %")
        print(f"  営業利益率: {format_percent(latest.get('operating_margin'))} %")
    else:
        print("\n財務データが見つかりません")


def print_ranking(metric: str, ranking: List[Dict]):
    """ランキングを表示"""
    metric_names = {
        "roe": "ROE (自己資本利益率)",
        "roa": "ROA (総資産利益率)",
        "sales": "売上高",
        "market_cap": "時価総額",
        "operating_income": "営業利益"
    }

    print("\n" + "="*80)
    print(f"{metric_names.get(metric, metric)} ランキング")
    print("="*80)

    for i, item in enumerate(ranking, 1):
        name = item.get("name", "N/A")
        value = item.get("value")
        code = item.get("edinet_code", "N/A")

        if metric in ["roe", "roa"]:
            value_str = f"{format_percent(value)} %"
        else:
            value_str = f"{format_number(value)} 円"

        print(f"{i:2d}. {name:30s} {value_str:>20s} ({code})")


def print_comparison(companies_data: List[Dict]):
    """複数企業の比較表を表示"""
    print("\n" + "="*100)
    print("企業比較")
    print("="*100)

    # ヘッダー
    print(f"\n{'項目':<20s}", end="")
    for company in companies_data:
        name = company["name"][:12] if company["name"] else "N/A"
        print(f"{name:>20s}", end="")
    print()
    print("-" * 100)

    # 各指標を比較
    metrics = [
        ("売上高", "net_sales", lambda x: format_number(x)),
        ("営業利益", "operating_income", lambda x: format_number(x)),
        ("当期純利益", "net_income", lambda x: format_number(x)),
        ("総資産", "total_assets", lambda x: format_number(x)),
        ("純資産", "net_assets", lambda x: format_number(x)),
        ("ROE", "roe", lambda x: format_percent(x)),
        ("ROA", "roa", lambda x: format_percent(x)),
        ("自己資本比率", "equity_ratio", lambda x: format_percent(x)),
    ]

    for label, key, formatter in metrics:
        print(f"{label:<20s}", end="")
        for company in companies_data:
            if "financials" in company and company["financials"].get("financials"):
                value = company["financials"]["financials"][0].get(key)
                value_str = formatter(value) if value is not None else "N/A"
            else:
                value_str = "N/A"
            print(f"{value_str:>20s}", end="")
        print()


def format_number(value: Optional[float]) -> str:
    """数値をフォーマット"""
    if value is None:
        return "N/A"
    if abs(value) >= 1_000_000_000_000:  # 1兆以上
        return f"{value/1_000_000_000_000:,.2f}兆"
    elif abs(value) >= 100_000_000:  # 1億以上
        return f"{value/100_000_000:,.2f}億"
    elif abs(value) >= 10_000:  # 1万以上
        return f"{value/10_000:,.2f}万"
    else:
        return f"{value:,.0f}"


def format_percent(value: Optional[float]) -> str:
    """パーセント値をフォーマット"""
    if value is None:
        return "N/A"
    return f"{value:.2f}"


def export_to_csv(data: List[Dict], filename: str):
    """データをCSVにエクスポート"""
    if not data:
        print("エクスポートするデータがありません")
        return

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        # 最初のレコードからキーを取得
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(data)

    print(f"\n✓ データを {filename} にエクスポートしました")


def main():
    parser = argparse.ArgumentParser(
        description="EDINET DB 財務分析ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 企業を検索
  %(prog)s search "任天堂"

  # 企業の詳細情報を表示
  %(prog)s info E02367

  # 企業の財務データを表示
  %(prog)s financials E02367

  # ROEランキングを表示
  %(prog)s ranking roe --limit 20

  # 複数企業を比較
  %(prog)s compare E02367 E01825 E02503
        """
    )

    parser.add_argument(
        "--api-key",
        default="edb_c0990ba3d64565a58dc8339c09c38099",
        help="EDINET DB APIキー (デフォルト: 環境変数またはハードコード値)"
    )

    subparsers = parser.add_subparsers(dest="command", help="コマンド")

    # search コマンド
    search_parser = subparsers.add_parser("search", help="企業を検索")
    search_parser.add_argument("query", nargs="?", help="検索キーワード（企業名）")
    search_parser.add_argument("--per-page", type=int, default=10, help="表示件数")
    search_parser.add_argument("--page", type=int, default=1, help="ページ番号")
    search_parser.add_argument("--export", help="CSVファイルにエクスポート")

    # info コマンド
    info_parser = subparsers.add_parser("info", help="企業の詳細情報を表示")
    info_parser.add_argument("company_code", help="企業コード (例: E02367)")

    # financials コマンド
    fin_parser = subparsers.add_parser("financials", help="企業の財務データを表示")
    fin_parser.add_argument("company_code", help="企業コード (例: E02367)")

    # ranking コマンド
    rank_parser = subparsers.add_parser("ranking", help="ランキングを表示")
    rank_parser.add_argument(
        "metric",
        choices=["roe", "roa", "sales", "market_cap", "operating_income"],
        help="指標"
    )
    rank_parser.add_argument("--limit", type=int, default=10, help="表示件数")
    rank_parser.add_argument("--export", help="CSVファイルにエクスポート")

    # compare コマンド
    comp_parser = subparsers.add_parser("compare", help="複数企業を比較")
    comp_parser.add_argument("company_codes", nargs="+", help="企業コード (例: E02367 E01825)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # APIクライアント初期化
    analyzer = EDINETAnalyzer(args.api_key)

    # コマンド実行
    if args.command == "search":
        companies = analyzer.search_companies(
            query=args.query,
            per_page=args.per_page,
            page=args.page
        )
        print_company_list(companies)

        if args.export:
            export_to_csv(companies, args.export)

    elif args.command == "info":
        company = analyzer.get_company_info(args.company_code)
        print_company_detail(company)

    elif args.command == "financials":
        company = analyzer.get_company_info(args.company_code)
        financials = analyzer.get_financials(args.company_code)
        print_financials(company.get("name"), financials)

    elif args.command == "ranking":
        ranking = analyzer.get_ranking(args.metric, limit=args.limit)
        print_ranking(args.metric, ranking)

        if args.export:
            export_to_csv(ranking, args.export)

    elif args.command == "compare":
        companies_data = analyzer.compare_companies(args.company_codes)
        print_comparison(companies_data)


if __name__ == "__main__":
    main()
