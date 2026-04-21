import pytest
from pydantic import ValidationError
from datetime import datetime
from lab6 import Block, Person, Source, Vote

def test_valid_block():
    b = Block(id="0x123abc", view=10, desc="Test")
    assert b.id == "0x123abc"
    assert b.view == 10

def test_invalid_block_negative_view():
    with pytest.raises(ValidationError):
        Block(id="0x123", view=-1)

def test_invalid_block_id_non_hex():
    with pytest.raises(ValidationError):
        Block(id="zzz", view=0)

def test_valid_source():
    s = Source(id=1, ip_addr="192.168.1.1", country_code="UA")
    assert s.country_code == "UA"

def test_invalid_source_ip():
    with pytest.raises(ValidationError):
        Source(id=1, ip_addr="999.999.999.999", country_code="UA")

def test_invalid_source_country_code():
    with pytest.raises(ValidationError):
        Source(id=1, ip_addr="1.1.1.1", country_code="UKR")

def test_valid_person():
    p = Person(id=1, name="John", addr="Kyiv")
    assert p.name == "John"

def test_invalid_person_empty_name():
    with pytest.raises(ValidationError):
        Person(id=1, name="", addr="")

def test_valid_vote():
    v = Vote(block_id="0x123", voter_id=1, timestamp=datetime.now(), source_id=1)
    assert v.block_id == "0x123"

def test_invalid_vote_negative_voter_id():
    with pytest.raises(ValidationError):
        Vote(block_id="0x123", voter_id=-1, timestamp=datetime.now(), source_id=1)

def test_1():
    with pytest.raises(ValidationError):
        Block(id=1, view=0)
