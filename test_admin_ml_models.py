#!/usr/bin/env python3
"""
Admin ML Models Smoke Test
- Auth via admin_key
- Load stocklist sheets to pick a category
- Run BTST and Stock Recommender
- List recent results and print the saved result IDs
"""
import requests
import json

def main():
    base = "http://127.0.0.1:80"
    s = requests.Session()

    print("Admin ML Models Smoke Test")
    print("=" * 40)

    # Authenticate as admin using admin_key shortcut
    r = s.get(f"{base}/admin_dashboard", params={"admin_key": "admin123"})
    print("Admin dashboard:", r.status_code)

    # Load available sheets/categories
    r = s.get(f"{base}/api/admin/stocklist_sheets")
    print("Stocklist sheets:", r.status_code)
    sheet = "NIFTY 50"
    try:
        j = r.json()
        if j.get("success") and j.get("sheets"):
            sheet = j["sheets"][0]["sheet_name"]
            print("Using sheet:", sheet)
        else:
            print("Sheets API returned no sheets, falling back to:", sheet)
    except Exception as e:
        print("Sheets JSON parse error:", e)

    # Run BTST Analyzer
    print("\nRunning BTST analyzer...")
    r = s.post(f"{base}/api/admin/ml_models/run_btst_analyzer", data={
        "stock_category": sheet,
        "min_confidence": "70",
        "btst_min_score": "75",
    })
    print("BTST status:", r.status_code)
    btst_result_id = None
    try:
        j = r.json()
        print("BTST success:", j.get("success"))
        if j.get("success"):
            btst_result_id = j["result"].get("id")
            print("BTST result id:", btst_result_id)
        else:
            print("BTST error:", j.get("error"))
    except Exception as e:
        print("BTST parse error:", e)
        print(r.text[:300])

    # Run Advanced Stock Recommender
    print("\nRunning Stock Recommender...")
    r = s.post(f"{base}/api/admin/ml_models/run_stock_recommender", data={
        "stock_category": sheet,
        "min_confidence": "70",
    })
    print("Recommender status:", r.status_code)
    rec_result_id = None
    try:
        j = r.json()
        print("Recommender success:", j.get("success"))
        if j.get("success"):
            rec_result_id = j["result"].get("id")
            print("Recommender result id:", rec_result_id)
        else:
            print("Recommender error:", j.get("error"))
    except Exception as e:
        print("Recommender parse error:", e)
        print(r.text[:300])

    # Run Sector ML Analyzer (all sectors)
    print("\nRunning Sector ML Analyzer...")
    r = s.post(f"{base}/api/admin/ml_models/run_sector_analyzer", data={
        "period": "6mo",
        "analysis_type": "all_sectors"
    })
    print("Sector analyzer status:", r.status_code)
    sector_result_id = None
    try:
        j = r.json()
        print("Sector analyzer success:", j.get("success"))
        if j.get("success"):
            sector_result_id = j["result"].get("id")
            print("Sector analyzer result id:", sector_result_id)
        else:
            print("Sector analyzer error:", j.get("error"))
    except Exception as e:
        print("Sector analyzer parse error:", e)
        print(r.text[:300])

    # Recent results
    print("\nRecent ML results:")
    r = s.get(f"{base}/api/admin/ml_results/recent")
    print("Recent status:", r.status_code)
    try:
        j = r.json()
        results = j.get("results", [])
        print("Count:", len(results))
        for it in results[:5]:
            print("-", it.get("id"), it.get("model_name"), it.get("stock_category"), it.get("created_at"))
    except Exception as e:
        print("Recent parse error:", e)
        print(r.text[:300])

    print("\nSummary:")
    print(" BTST result id:", btst_result_id)
    print(" Recommender result id:", rec_result_id)
    print(" Sector analyzer result id:", sector_result_id)

if __name__ == "__main__":
    main()
