import sqlite3

def init_db():
    conn = sqlite3.connect('lab3_blockchain.db')
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS BLOCKS (
            hexString TEXT PRIMARY KEY,
            id INTEGER,
            view INTEGER,
            desc TEXT,
            img BLOB,
            votes INTEGER
        );

        CREATE TABLE IF NOT EXISTS SOURCES (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_addr TEXT,
            country_code TEXT
        );

        CREATE TABLE IF NOT EXISTS PERSONS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            addr TEXT
        );

        CREATE TABLE IF NOT EXISTS VOTES (
            block_id TEXT,
            voter_id INTEGER,
            timestamp DATETIME,
            source_id INTEGER,
            PRIMARY KEY (block_id, voter_id),
            FOREIGN KEY (block_id) REFERENCES BLOCKS(hexString) ON DELETE CASCADE,
            FOREIGN KEY (voter_id) REFERENCES PERSONS(id) ON DELETE CASCADE,
            FOREIGN KEY (source_id) REFERENCES SOURCES(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS event_stream (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            entity_id TEXT,
            processed BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()
    print("Database initialized")

if __name__ == "__main__":
    init_db()
