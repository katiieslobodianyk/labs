import socket
import json
import duckdb

PARQUET_PATH = "../data/wikipedia.parquet"

def init_duckdb():
    con = duckdb.connect()
    con.sql(f"CREATE VIEW pageviews AS SELECT * FROM read_parquet('{PARQUET_PATH}')")
    return con

def get_top_articles(limit=20):
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

def get_agent_breakdown():
    con = init_duckdb()
    result = con.sql("""
        SELECT agent_type, SUM(view_count) AS views
        FROM pageviews
        GROUP BY agent_type
        ORDER BY views DESC
    """).fetchall()
    return [{"agent": row[0], "views": row[1]} for row in result]

def get_hourly_stats(hour_str=None):
    con = init_duckdb()
    if hour_str:
        query = f"""
            SELECT
                STRPTIME(hourly_encoded, '%Y%m%d%H') AS hour,
                SUM(view_count) AS views
            FROM pageviews
            WHERE hourly_encoded = '{hour_str}'
            GROUP BY hour
        """
    else:
        query = """
            SELECT
                STRPTIME(hourly_encoded, '%Y%m%d%H') AS hour,
                SUM(view_count) AS views
            FROM pageviews
            GROUP BY hour
            ORDER BY hour
        """
    result = con.sql(query).fetchall()
    return [{"hour": row[0].isoformat() if row[0] else None, "views": row[1]} for row in result]

def handle_client(conn):
    data = conn.recv(8192).decode()
    if not data:
        return
    req = json.loads(data)
    action = req.get('action')
    if action == 'wiki_stats':
        query_type = req.get('query_type')
        if query_type == 'top_articles':
            limit = req.get('limit', 20)
            result = get_top_articles(limit)
        elif query_type == 'agent_breakdown':
            result = get_agent_breakdown()
        elif query_type == 'hourly_stats':
            hour = req.get('hour')
            result = get_hourly_stats(hour)
        else:
            result = {"error": "Unknown query_type"}
        conn.sendall(json.dumps(result).encode())
    else:
        conn.sendall(json.dumps({"error": "Unknown action"}).encode())
    conn.close()

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 25002))
    sock.listen(5)
    print("Wiki server listening on port 25002")
    while True:
        conn, addr = sock.accept()
        handle_client(conn)

if __name__ == "__main__":
    main()
