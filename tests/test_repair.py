from src.repair import repair as R

EV = [{'chunk_id': 'c1', 'text': 'Warfarin increases bleeding risk with aspirin.'}]

def cs(state, claim='Warfarin has no effect with aspirin.'):
    return {'claim': claim, 'state': state, 'evidence_ids': ['c1'], 'risk_level': 'low'}

def test_keep_supported():
    assert R.repair_claim(cs('SUPPORTED'), EV)['action'] == 'keep'

def test_drop_unsupported():
    r = R.repair_claim(cs('UNSUPPORTED'), EV)
    assert r['action'] == 'drop' and r['repaired'] == ''

def test_hedge_insufficient():
    assert R.repair_claim(cs('INSUFFICIENT_EVIDENCE'), EV)['action'] == 'hedge'

def test_rewrite_contradicted(monkeypatch):
    monkeypatch.setattr(R, '_ask', lambda ins, claim, ev: 'Warfarin increases bleeding risk with aspirin.')
    monkeypatch.setattr(R, 'verify_claim', lambda c, ev: {'state': 'SUPPORTED'})
    assert R.repair_claim(cs('CONTRADICTED'), EV)['action'] == 'rewrite'

def test_failed_gate_drops_contradicted(monkeypatch):
    monkeypatch.setattr(R, '_ask', lambda ins, claim, ev: 'Some other sentence.')
    monkeypatch.setattr(R, 'verify_claim', lambda c, ev: {'state': 'INSUFFICIENT_EVIDENCE'})
    assert R.repair_claim(cs('CONTRADICTED'), EV)['action'] == 'drop'

def test_must_abstain_on_high_risk():
    assert R.must_abstain([{'state': 'UNSAFE_TO_ANSWER', 'risk_level': 'high'}])
    assert not R.must_abstain([{'state': 'CONTRADICTED', 'risk_level': 'low'}])
