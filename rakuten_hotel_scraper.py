#!/usr/bin/env python3
"""
楽天トラベルAPIを使って日本全国の宿泊施設情報を取得し、
OTAコンサル営業リスト（客室数5〜50室）をCSV出力するスクリプト

事前準備:
  1. 楽天デベロッパー (https://developers.rakuten.com/) に登録
  2. アプリを作成して「アプリID」(applicationId) を取得
  3. このスクリプトの APPLICATION_ID に設定するか、環境変数 RAKUTEN_APP_ID に設定

使い方:
  python rakuten_hotel_scraper.py
"""

import csv
import json
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

import requests

# ── 設定 ─────────────────────────────────────────────
APPLICATION_ID = os.environ.get("RAKUTEN_APP_ID", "YOUR_APPLICATION_ID_HERE")
BASE_URL = "https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426"
HITS_PER_PAGE = 30  # 最大30（API制限）
REQUEST_INTERVAL = 1.0  # 秒（レート制限回避）
OUTPUT_FILE = "ota_sales_list_rakuten.csv"

# 全国47都道府県の中分類コード
MIDDLE_CLASS_CODES = {
    "北海道": "hokkaido",
    "青森県": "aomori",
    "岩手県": "iwate",
    "宮城県": "miyagi",
    "秋田県": "akita",
    "山形県": "yamagata",
    "福島県": "fukushima",
    "茨城県": "ibaraki",
    "栃木県": "tochigi",
    "群馬県": "gunma",
    "埼玉県": "saitama",
    "千葉県": "chiba",
    "東京都": "tokyo",
    "神奈川県": "kanagawa",
    "新潟県": "niigata",
    "富山県": "toyama",
    "石川県": "ishikawa",
    "福井県": "fukui",
    "山梨県": "yamanashi",
    "長野県": "nagano",
    "岐阜県": "gifu",
    "静岡県": "shizuoka",
    "愛知県": "aichi",
    "三重県": "mie",
    "滋賀県": "shiga",
    "京都府": "kyoto",
    "大阪府": "osaka",
    "兵庫県": "hyogo",
    "奈良県": "nara",
    "和歌山県": "wakayama",
    "鳥取県": "tottori",
    "島根県": "shimane",
    "岡山県": "okayama",
    "広島県": "hiroshima",
    "山口県": "yamaguchi",
    "徳島県": "tokushima",
    "香川県": "kagawa",
    "愛媛県": "ehime",
    "高知県": "kochi",
    "福岡県": "fukuoka",
    "佐賀県": "saga",
    "長崎県": "nagasaki",
    "熊本県": "kumamoto",
    "大分県": "oita",
    "宮崎県": "miyazaki",
    "鹿児島県": "kagoshima",
    "沖縄県": "okinawa",
}


@dataclass
class Hotel:
    hotel_name: str = ""
    prefecture: str = ""
    address: str = ""
    phone: str = ""
    website: str = ""
    room_count_str: str = ""
    hotel_type: str = ""
    hotel_no: str = ""


def search_hotels_by_area(middle_code: str, page: int = 1) -> Optional[dict]:
    """指定したエリアのホテルを検索"""
    params = {
        "applicationId": APPLICATION_ID,
        "format": "json",
        "largeClassCode": "japan",
        "middleClassCode": middle_code,
        "hits": HITS_PER_PAGE,
        "page": page,
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] API request failed: {e}", file=sys.stderr)
        return None


def parse_hotel_data(data: dict, prefecture: str) -> list[Hotel]:
    """API応答からホテル情報を抽出"""
    hotels = []
    if "hotels" not in data:
        return hotels

    for item in data["hotels"]:
        try:
            hotel_info = item.get("hotel", [{}])[0]
            basic_info = hotel_info.get("hotelBasicInfo", {})

            hotel = Hotel(
                hotel_name=basic_info.get("hotelName", ""),
                prefecture=prefecture,
                address=f"{basic_info.get('address1', '')} {basic_info.get('address2', '')}".strip(),
                phone=basic_info.get("telephoneNo", ""),
                website=basic_info.get("hotelInformationUrl", ""),
                room_count_str=basic_info.get("roomCount", ""),
                hotel_type=basic_info.get("hotelType", ""),
                hotel_no=basic_info.get("hotelNo", ""),
            )
            hotels.append(hotel)
        except (IndexError, KeyError, TypeError) as e:
            continue
    return hotels


def is_target_room_count(room_count_str: str) -> bool:
    """客室数が5〜50室の条件に合うか判定"""
    try:
        count = int(room_count_str)
        return 5 <= count <= 50
    except (ValueError, TypeError):
        return True  # 不明な場合は対象に含める（後で手動確認）


def main():
    if APPLICATION_ID == "YOUR_APPLICATION_ID_HERE":
        print("=" * 60)
        print("【設定が必要です】")
        print("楽天デベロッパー (https://developers.rakuten.com/) で無料登録し、")
        print("アプリIDを取得後、以下のいずれかの方法で設定してください:")
        print("")
        print("  方法1: 環境変数に設定")
        print("    export RAKUTEN_APP_ID='取得したアプリID'")
        print("    python rakuten_hotel_scraper.py")
        print("")
        print("  方法2: スクリプト内の APPLICATION_ID を直接書き換え")
        print("=" * 60)
        sys.exit(1)

    all_hotels: list[Hotel] = []
    total_prefs = len(MIDDLE_CLASS_CODES)
    total_api_calls = 0

    print(f"全国{total_prefs}都道府県の宿泊施設を取得開始...")
    print(f"出力ファイル: {OUTPUT_FILE}")
    print("-" * 60)

    for idx, (pref_name, middle_code) in enumerate(MIDDLE_CLASS_CODES.items(), 1):
        print(f"[{idx}/{total_prefs}] {pref_name} (code: {middle_code})")

        page = 1
        pref_hotels = 0

        while True:
            data = search_hotels_by_area(middle_code, page)
            total_api_calls += 1

            if data is None:
                print(f"  → {page}ページ目でエラー、次に進みます")
                break

            hotels = parse_hotel_data(data, pref_name)
            if not hotels:
                break

            for h in hotels:
                if is_target_room_count(h.room_count_str):
                    all_hotels.append(h)

            pref_hotels += len(hotels)
            page += 1

            # 最終ページ判定
            page_count = data.get("pageCount", 1)
            if page > page_count:
                break

            time.sleep(REQUEST_INTERVAL)

        print(f"  → {pref_hotels}件取得（うち対象: {len([h for h in all_hotels if h.prefecture == pref_name])}件）")

    # ── CSV出力 ──
    fieldnames = [
        "施設名",
        "都道府県",
        "住所",
        "電話番号",
        "WEBサイト",
        "客室数",
        "施設タイプ",
        "楽天ホテルNo",
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for h in all_hotels:
            writer.writerow({
                "施設名": h.hotel_name,
                "都道府県": h.prefecture,
                "住所": h.address,
                "電話番号": h.phone,
                "WEBサイト": h.website,
                "客室数": h.room_count_str,
                "施設タイプ": h.hotel_type,
                "楽天ホテルNo": h.hotel_no,
            })

    print("-" * 60)
    print(f"完了! 全API呼び出し: {total_api_calls}回")
    print(f"取得した宿泊施設: {len(all_hotels)}件")
    print(f"CSV出力: {OUTPUT_FILE}")
    print("")
    print("【注意】")
    print("・楽天APIの仕様上、客室数が正確に取得できない場合があります")
    print("・5〜50室以外の施設も含まれている場合は手動でフィルタしてください")
    print("・APIの呼び出し制限（1秒1回推奨）に従っています")


if __name__ == "__main__":
    main()
