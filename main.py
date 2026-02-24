import os
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from pytrends.request import TrendReq

# =========================================
# 기본 설정
# =========================================

KEYWORDS = [
    "홍콩여행",
    "홍콩디즈니랜드",
    "디즈니랜드",
    "디즈니랜드호텔"
]

today = datetime.today()
two_year_ago = today - timedelta(days=365*2)

# =========================================
# NAVER TREND
# =========================================

client_id = os.environ.get("NAVER_CLIENT_ID")
client_secret = os.environ.get("NAVER_CLIENT_SECRET")

naver_url = "https://openapi.naver.com/v1/datalab/search"

headers = {
    "X-Naver-Client-Id": client_id,
    "X-Naver-Client-Secret": client_secret,
    "Content-Type": "application/json"
}

keyword_groups = [
    {"groupName": kw, "keywords": [kw]}
    for kw in KEYWORDS
]

naver_data = {
    "startDate": two_year_ago.strftime("%Y-%m-%d"),
    "endDate": today.strftime("%Y-%m-%d"),
    "timeUnit": "week",
    "keywordGroups": keyword_groups
}

naver_response = requests.post(
    naver_url,
    headers=headers,
    data=json.dumps(naver_data)
)

# ✅ API 에러 체크
if naver_response.status_code != 200:
    print("❌ Naver API 오류:", naver_response.text)
    raise Exception("Naver API 호출 실패")

naver_json = naver_response.json()

naver_rows = []

for result in naver_json["results"]:
    keyword_name = result["title"]
    
    for item in result["data"]:
        naver_rows.append({
            "date": item["period"],
            "keyword": keyword_name,
            "naver_ratio": item["ratio"]
        })

naver_df = pd.DataFrame(naver_rows)

# 날짜 처리
naver_df['date'] = pd.to_datetime(naver_df['date'])
naver_df['year_week'] = naver_df["date"].dt.strftime("%Y-%U")

# -------------------------
# GOOGLE TRENDS
# -------------------------

pytrends = TrendReq(hl='ko-KR', tz=540)

pytrends.build_payload(
        KEYWORDS, 
        timeframe='today 2-y', 
        geo='KR'
)

google_df = pytrends.interest_over_time()

if google_df.empty:
    raise Exception("❌ Google Trends 데이터 없음")

google_df = google_df.reset_index()

# isPartial 제거
google_df = google_df.drop(columns=["isPartial"], errors="ignore")

# 날짜 처리
google_df["date"] = pd.to_datetime(google_df["date"])
google_df["year_week"] = google_df["date"].dt.strftime("%Y-%U")

# Wide → Long 변환
google_df = google_df.melt(
    id_vars=["date", "year_week"],
    value_vars=KEYWORDS,
    var_name="keyword",
    value_name="google_ratio"
)

# -------------------------
# MERGE
# -------------------------

final_df = pd.merge(
    google_df,
    naver_df[["year_week", "keyword", "naver_ratio"]],
    how="left",
    left_on=["year_week", "keyword"]
)

# 정렬
final_df = final_df.sort_values(["keyword", "date"])

final_df.to_csv(
    "trend_result.csv", 
    index=False, 
    encoding="utf-8-sig"
)

print("✅ trend_result.csv 저장 완료")
