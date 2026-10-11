from eventlog.cli import main


def test_record_then_list(tmp_path, capsys):
    db = str(tmp_path / "db.json")
    assert main(["--db", db, "record", "login", "web", "--payload", '{"u": 1}']) == 0
    capsys.readouterr()
    assert main(["--db", db, "list"]) == 0
    assert "login" in capsys.readouterr().out


def test_record_rejects_bad_json(tmp_path):
    db = str(tmp_path / "db.json")
    assert main(["--db", db, "record", "a", "b", "--payload", "{nope"]) == 2


def test_record_rejects_non_object_payload(tmp_path):
    db = str(tmp_path / "db.json")
    assert main(["--db", db, "record", "a", "b", "--payload", "[1]"]) == 2


def test_export_jsonl(tmp_path, capsys):
    db = str(tmp_path / "db.json")
    main(["--db", db, "record", "a", "b"])
    capsys.readouterr()
    main(["--db", db, "export", "--format", "jsonl"])
    assert '"kind": "a"' in capsys.readouterr().out
