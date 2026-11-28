import json
from collections import Counter


def test_ganavi_question_contribution_has_expected_types():
    with open("data/eval/q_ganavi.jsonl", encoding="utf-8-sig") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]

    assert len({row["qid"] for row in rows}) == len(rows)
    assert Counter(row["type"] for row in rows) == {
        "answerable": 13,
        "unanswerable": 7,
        "tricky": 7,
    }
    for row in rows:
        assert row["question"].strip()
        assert isinstance(row["gold_chunk_ids"], list)
        if row["type"] == "unanswerable":
            assert row["gold_answer"] == ""
            assert row["gold_chunk_ids"] == []
        else:
            assert row["gold_answer"].strip()
            assert row["gold_chunk_ids"]
