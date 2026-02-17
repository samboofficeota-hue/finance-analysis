#!/usr/bin/env python3
"""
API テストスクリプト
デプロイ後のAPIをテストするためのスクリプト
"""

import requests
import sys
from typing import Optional

def test_api(base_url: str):
    """APIをテスト"""

    print(f"\n🧪 APIテスト開始: {base_url}\n")
    print("=" * 80)

    # 1. ルートエンドポイント
    print("\n1️⃣ ルートエンドポイントをテスト")
    try:
        response = requests.get(f"{base_url}/")
        response.raise_for_status()
        print("✅ ルートエンドポイント: OK")
        print(f"   レスポンス: {response.json()}")
    except Exception as e:
        print(f"❌ エラー: {e}")

    # 2. ヘルスチェック
    print("\n2️⃣ ヘルスチェックをテスト")
    try:
        response = requests.get(f"{base_url}/health")
        response.raise_for_status()
        print("✅ ヘルスチェック: OK")
        print(f"   レスポンス: {response.json()}")
    except Exception as e:
        print(f"❌ エラー: {e}")

    # 3. 企業検索
    print("\n3️⃣ 企業検索をテスト（任天堂）")
    try:
        response = requests.get(f"{base_url}/companies", params={"query": "任天堂"})
        response.raise_for_status()
        data = response.json()
        print("✅ 企業検索: OK")
        if "companies" in data and data["companies"]:
            company = data["companies"][0]
            print(f"   企業名: {company.get('name')}")
            print(f"   EDINETコード: {company.get('edinet_code')}")
    except Exception as e:
        print(f"❌ エラー: {e}")

    # 4. 企業情報取得
    print("\n4️⃣ 企業情報を取得（任天堂: E02367）")
    try:
        response = requests.get(f"{base_url}/companies/E02367")
        response.raise_for_status()
        data = response.json()
        print("✅ 企業情報取得: OK")
        print(f"   企業名: {data.get('name')}")
        print(f"   業種: {data.get('industry')}")
        print(f"   証券コード: {data.get('securities_code')}")
    except Exception as e:
        print(f"❌ エラー: {e}")

    # 5. 財務データ取得
    print("\n5️⃣ 財務データを取得（任天堂: E02367）")
    try:
        response = requests.get(f"{base_url}/companies/E02367/financials")
        response.raise_for_status()
        data = response.json()
        print("✅ 財務データ取得: OK")
        if "financials" in data and data["financials"]:
            latest = data["financials"][0]
            print(f"   決算期: {latest.get('fiscal_period')}")
            print(f"   売上高: {latest.get('net_sales'):,} 円")
            print(f"   ROE: {latest.get('roe')}%")
    except Exception as e:
        print(f"❌ エラー: {e}")

    # 6. ランキング取得
    print("\n6️⃣ ROEランキングを取得")
    try:
        response = requests.get(f"{base_url}/rankings/roe", params={"limit": 5})
        response.raise_for_status()
        data = response.json()
        print("✅ ランキング取得: OK")
        if "ranking" in data:
            print("   TOP 5:")
            for i, item in enumerate(data["ranking"], 1):
                print(f"   {i}. {item.get('name')} - ROE: {item.get('value')}%")
    except Exception as e:
        print(f"❌ エラー: {e}")

    # 7. 企業比較
    print("\n7️⃣ 企業比較をテスト（任天堂、トヨタ）")
    try:
        response = requests.get(
            f"{base_url}/compare",
            params={"codes": "E02367,E01825"}
        )
        response.raise_for_status()
        data = response.json()
        print("✅ 企業比較: OK")
        print(f"   成功: {len(data.get('success', []))} 社")
        print(f"   エラー: {len(data.get('errors', []))} 件")
    except Exception as e:
        print(f"❌ エラー: {e}")

    # 8. 分析サマリー
    print("\n8️⃣ 分析サマリーを取得（任天堂）")
    try:
        response = requests.get(f"{base_url}/companies/E02367/analysis")
        response.raise_for_status()
        data = response.json()
        print("✅ 分析サマリー: OK")
        if "indicators" in data and "ratings" in data:
            print(f"   ROE: {data['indicators'].get('roe')}%")
            print(f"   収益性評価: {data['ratings'].get('profitability')}")
            print(f"   効率性評価: {data['ratings'].get('efficiency')}")
            print(f"   安全性評価: {data['ratings'].get('stability')}")
    except Exception as e:
        print(f"❌ エラー: {e}")

    print("\n" + "=" * 80)
    print("🎉 テスト完了!\n")
    print(f"📖 APIドキュメント: {base_url}/docs")
    print(f"📄 ReDoc: {base_url}/redoc")


def main():
    if len(sys.argv) < 2:
        print("使い方: python test_api.py <BASE_URL>")
        print("\n例:")
        print("  python test_api.py http://localhost:8000")
        print("  python test_api.py https://your-project.vercel.app")
        print("  python test_api.py https://your-project.up.railway.app")
        sys.exit(1)

    base_url = sys.argv[1].rstrip('/')
    test_api(base_url)


if __name__ == "__main__":
    main()
