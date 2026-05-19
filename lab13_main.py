from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
import re
import cv2
import numpy as np
import duckdb
from fastapi.responses import Response

app = FastAPI()

PARQUET_PATH = "../data/wikipedia.parquet"

def init_duckdb():
    con = duckdb.connect()
    con.sql(f"CREATE VIEW pageviews AS SELECT * FROM read_parquet('{PARQUET_PATH}')")
    return con

class FetchRequest(BaseModel):
    url: str
    regex: Optional[str] = None

class BWImageRequest(BaseModel):
    url: str

@app.post("/fetch")
async def fetch(request: FetchRequest):
    resp = requests.get(request.url)
    headers = dict(resp.headers)
    text = resp.text
    lines = text.splitlines()
    matched = []
    if request.regex:
        pattern = re.compile(request.regex)
        for line in lines:
            if pattern.search(line):
                matched.append(line)
    return {"headers": headers, "matched_lines": matched[:100]}

@app.post("/bw-image")
async def bw_image(request: BWImageRequest):
    img_resp = requests.get(request.url)
    img_array = np.frombuffer(img_resp.content, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, encoded = cv2.imencode('.jpg', gray)
    return Response(content=encoded.tobytes(), media_type="image/jpeg")

@app.get("/stats/top")
async def top_articles(limit: int = 20):
    con = init_duckdb()
    result = con.sql(f"""
        SELECT article_title, view_count
        FROM pageviews
        WHERE wiki_code = 'en.wikipedia'
          AND article_title NOT LIKE 'Special:%'
          AND article_title NOT LIKE 'Wikipedia:%'
          AND article_title NOT LIKE 'Help:%'
          AND article_title NOT LIKE 'File:%'
          AND article_title NOT LIKE 'Category:%'
          AND article_title NOT LIKE 'Portal:%'
          AND article_title NOT LIKE 'Template:%'
          AND article_title != 'Main_Page'
          AND article_title != '-'
        ORDER BY view_count DESC
        LIMIT {limit}
    """).fetchall()
    return [{"title": row[0], "views": row[1]} for row in result]

@app.get("/stats/agents")
async def agent_breakdown():
    con = init_duckdb()
    result = con.sql("""
        SELECT agent_type, SUM(view_count) AS views
        FROM pageviews
        GROUP BY agent_type
        ORDER BY views DESC
    """).fetchall()
    return [{"agent": row[0], "views": row[1]} for row in result]

@app.get("/stats/hourly")
async def hourly_stats(hour: Optional[str] = None):
    con = init_duckdb()
    if hour:
        query = f"""
            SELECT STRPTIME(hourly_encoded, '%Y%m%d%H') AS hour, SUM(view_count) AS views
            FROM pageviews
            WHERE hourly_encoded = '{hour}'
              AND hourly_encoded ~ '^[0-9]{{10}}$'
            GROUP BY hour
        """
    else:
        query = """
            SELECT STRPTIME(hourly_encoded, '%Y%m%d%H') AS hour, SUM(view_count) AS views
            FROM pageviews
            WHERE hourly_encoded ~ '^[0-9]{10}$'
            GROUP BY hour
            ORDER BY hour
        """
    result = con.sql(query).fetchall()
    return [{"hour": row[0].isoformat() if row[0] else None, "views": row[1]} for row in result]
