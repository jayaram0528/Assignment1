import csv
import io
import json

from eventlog.exporters import CSV_COLUMNS, to_csv, to_jsonl
from tests.helpers import make_event


def test_csv_has_header_and_rows():
    out = to_csv([make_event(1, payload={"k": "v"})])
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == CSV_COLUMNS
    assert rows[1][0] == "1"
    assert json.loads(rows[1][4]) == {"k": "v"}


def test_csv_escapes_commas_in_payload():
    out = to_csv([make_event(1, payload={"msg": "a,b"})])
    rows = list(csv.reader(io.StringIO(out)))
    assert json.loads(rows[1][4])["msg"] == "a,b"


def test_jsonl_one_line_per_event():
    out = to_jsonl([make_event(1), make_event(2)])
    lines = out.strip().split("\n")
    assert [json.loads(line)["id"] for line in lines] == [1, 2]


def test_jsonl_empty():
    assert to_jsonl([]) == ""
