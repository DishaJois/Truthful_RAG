from src.evaluation import metrics as M

def test_recall():
    assert M.recall_at_k(['a', 'b'], ['b']) == 1.0
    assert M.recall_at_k(['a', 'b'], ['z']) == 0.0

def test_keyword_match():
    assert M.keyword_match('It increases bleeding risk.', 'increases the risk of bleeding') == 1.0

def test_faithfulness_and_hallucination():
    cs = [{'state': 'SUPPORTED'}, {'state': 'UNSUPPORTED'}]
    assert M.faithfulness(cs) == 0.5
    assert M.hallucination_rate(cs) == 0.5

def test_abstention():
    p, r = M.abstention_scores([(True, 'unanswerable'), (True, 'answerable'), (False, 'unanswerable')])
    assert p == 0.5 and r == 0.5
