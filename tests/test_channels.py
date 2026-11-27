from src.adjudication.channels import apply_channels

EDGE = [{'subject': 'warfarin', 'relation': 'increases_bleeding_risk_with', 'object': 'aspirin', 'chunk_id': 'c1'}]

def vv(claim, state='SUPPORTED'):
    return {'claim': claim, 'state': state, 'confidence': 0.7, 'evidence_ids': ['c1'],
            'reason': '', 'risk_level': 'low'}

def test_disagreement_becomes_conflicting():
    s = apply_channels(vv('Aspirin decreases the effect of warfarin.'), EDGE, {'c1'})
    assert s['state'] == 'CONFLICTING_EVIDENCE' and s['channel'] == 'disagree'

def test_agreement_boosts_confidence():
    s = apply_channels(vv('Warfarin increases bleeding when taken with aspirin.'), EDGE, {'c1'})
    assert s['state'] == 'SUPPORTED' and s['confidence'] > 0.7

def test_no_edges_is_unchanged():
    s = vv('Warfarin increases bleeding.')
    assert apply_channels(s, [], set()) == s
