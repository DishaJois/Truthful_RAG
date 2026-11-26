from src.adjudication.adjudicator import adjudicate

def v(state, conf=0.8, risk='low'):
    return {
        'claim': 'warfarin increases bleeding with aspirin',
        'state': state,
        'confidence': conf,
        'evidence_ids': ['c1'],
        'reason': '',
        'risk_level': risk
    }

def state_of(res):
    return res['claim_states'][0]['state']

def test_out_of_scope():
    assert state_of(adjudicate([], question='What is the capital of France?', entities=[])) == 'OUT_OF_SCOPE'

def test_ambiguous_query():
    r = adjudicate([], question='Is it safe to take this medicine together?', entities=[])
    assert state_of(r) == 'AMBIGUOUS_QUERY'

def test_unsupported():
    assert state_of(adjudicate([v('UNSUPPORTED')])) == 'UNSUPPORTED'

def test_conflicting():
    assert state_of(adjudicate([v('CONFLICTING_EVIDENCE')])) == 'CONFLICTING_EVIDENCE'

def test_contradicted():
    assert state_of(adjudicate([v('CONTRADICTED')])) == 'CONTRADICTED'

def test_partial():
    assert state_of(adjudicate([v('PARTIALLY_SUPPORTED')])) == 'PARTIALLY_SUPPORTED'

def test_insufficient():
    assert state_of(adjudicate([v('INSUFFICIENT_EVIDENCE')])) == 'INSUFFICIENT_EVIDENCE'

def test_supported():
    assert state_of(adjudicate([v('SUPPORTED')])) == 'SUPPORTED'

def test_unsafe_to_answer():
    r = adjudicate([v('SUPPORTED', conf=0.4, risk='high')])
    assert state_of(r) == 'UNSAFE_TO_ANSWER'

def test_abstention_and_filtering():
    r = adjudicate([v('SUPPORTED'), v('UNSUPPORTED')], filter_claims=True, use_abstention=True)
    assert r['abstain'] is True
