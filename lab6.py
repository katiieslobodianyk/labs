import sqlite3
from datetime import datetime
from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Optional

DB_PATH = 'lab3_blockchain.db'

def get_conn():
    return sqlite3.connect(DB_PATH)

class BlockModel(BaseModel):
    id: str = Field(pattern=r"^[0-9a-fA-FxX]+$")
    view: int = Field(ge=0)
    desc: str = ""
    img: Optional[bytes] = None

class PersonModel(BaseModel):
    id: int = Field(ge=1)
    name: str = Field(min_length=1)
    addr: str = ""

class SourceModel(BaseModel):
    id: int = Field(ge=1)
    ip_addr: IPvAnyAddress
    country_code: str = Field(pattern=r"^[A-Z]{2}$")

class VoteModel(BaseModel):
    block_id: str = Field(pattern=r"^[0-9a-fA-FxX]+$")
    voter_id: int = Field(ge=1)
    timestamp: datetime
    source_id: int = Field(ge=1)

class Block:
    def __init__(self, id, view, desc="", img=None):
        v = BlockModel(id=id, view=view, desc=desc, img=img)
        self.id = v.id
        self.view = v.view
        self.desc = v.desc
        self.img = v.img

    @staticmethod
    def get_all():
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, view, desc, img FROM BLOCKS")
        rows = cur.fetchall()
        conn.close()
        return [Block(r[0], r[1], r[2], r[3]) for r in rows]

    @staticmethod
    def get_by_id(block_id):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, view, desc, img FROM BLOCKS WHERE id = ?", (block_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return Block(row[0], row[1], row[2], row[3])
        return None

    def __str__(self):
        return f"Block({self.id}, {self.view}, {self.desc})"

class Source:
    def __init__(self, id, ip_addr, country_code):
        v = SourceModel(id=id, ip_addr=ip_addr, country_code=country_code)
        self.id = v.id
        self.ip_addr = str(v.ip_addr)
        self.country_code = v.country_code

    @staticmethod
    def get_all():
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, ip_addr, country_code FROM SOURCES")
        rows = cur.fetchall()
        conn.close()
        return [Source(r[0], r[1], r[2]) for r in rows]

    @staticmethod
    def get_by_id(source_id):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, ip_addr, country_code FROM SOURCES WHERE id = ?", (source_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return Source(row[0], row[1], row[2])
        return None

    def __str__(self):
        return f"Source({self.id}, {self.ip_addr}, {self.country_code})"

class Person:
    def __init__(self, id, name, addr=""):
        v = PersonModel(id=id, name=name, addr=addr)
        self.id = v.id
        self.name = v.name
        self.addr = v.addr

    @staticmethod
    def get_all():
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, addr FROM PERSONS")
        rows = cur.fetchall()
        conn.close()
        return [Person(r[0], r[1], r[2]) for r in rows]

    @staticmethod
    def get_by_id(person_id):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, addr FROM PERSONS WHERE id = ?", (person_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return Person(row[0], row[1], row[2])
        return None

    def __str__(self):
        return f"Person({self.id}, {self.name})"

class Vote:
    def __init__(self, block_id, voter_id, timestamp, source_id):
        v = VoteModel(block_id=block_id, voter_id=voter_id, timestamp=timestamp, source_id=source_id)
        self.block_id = v.block_id
        self.voter_id = v.voter_id
        self.timestamp = v.timestamp
        self.source_id = v.source_id

    @staticmethod
    def get_all():
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT block_id, voter_id, timestamp, source_id FROM VOTES")
        rows = cur.fetchall()
        conn.close()
        return [Vote(r[0], r[1], r[2], r[3]) for r in rows]

    def get_details(self):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT v.block_id, v.voter_id, v.timestamp, v.source_id,
                   b.view, b.desc,
                   p.name, p.addr,
                   s.ip_addr, s.country_code
            FROM VOTES v
            LEFT JOIN BLOCKS b ON v.block_id = b.id
            LEFT JOIN PERSONS p ON v.voter_id = p.id
            LEFT JOIN SOURCES s ON v.source_id = s.id
            WHERE v.block_id = ? AND v.voter_id = ?
        """, (self.block_id, self.voter_id))
        row = cur.fetchone()
        conn.close()
        if row:
            return {
                'block_id': row[0],
                'voter_id': row[1],
                'timestamp': row[2],
                'source_id': row[3],
                'block_view': row[4],
                'block_desc': row[5],
                'voter_name': row[6],
                'voter_addr': row[7],
                'source_ip': row[8],
                'source_country': row[9]
            }
        return {}

    def __str__(self):
        return f"Vote({self.block_id}, {self.voter_id}, {self.timestamp})"
