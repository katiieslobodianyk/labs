import duckdb
import bz2
import shutil
import os

def ingest(bz2_path: str, parquet_path: str):
    csv_path = bz2_path.replace('.bz2', '.csv')
    with bz2.open(bz2_path, 'rb') as f_in, open(csv_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    con = duckdb.connect()
    con.sql(f"""
        COPY (
            SELECT
                wiki_code,
                article_title,
                TRY_CAST(page_id AS INTEGER) AS page_id,
                agent_type,
                view_count,
                hourly_encoded
            FROM read_csv(
                '{csv_path}',
                delim=' ',
                header=false,
                columns={{
                    'wiki_code': 'VARCHAR',
                    'article_title': 'VARCHAR',
                    'page_id': 'VARCHAR',
                    'agent_type': 'VARCHAR',
                    'view_count': 'INTEGER',
                    'hourly_encoded': 'VARCHAR'
                }},
                ignore_errors=true
            )
            WHERE wiki_code IN ('en.wikipedia', 'en.wikipedia.m')
              AND article_title NOT LIKE 'Special:%'
              AND article_title != 'Main_Page'
              AND article_title != '_'
        ) TO '{parquet_path}' (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 100000)
    """)
    os.remove(csv_path)
    print(f"Converted {bz2_path} -> {parquet_path}")

if __name__ == "__main__":
    bz2_file = "../data/pageviews-20250901-user.bz2"
    parquet_file = "../data/wikipedia.parquet"
    ingest(bz2_file, parquet_file)
