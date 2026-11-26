def _e(cid, text):
    return {'chunk_id': cid, 'text': text, 'score': 0.9, 'source': 'mock'}

MOCKS = [
    {'question': 'Can warfarin be taken with aspirin?',
     'evidence': [_e('m001', 'Concomitant use of warfarin and aspirin increases the risk of bleeding.')]},
    {'question': 'Does drug X interact with warfarin?', 'evidence': []},
    {'question': 'Is ibuprofen safe with warfarin?',
     'evidence': [_e('m002', 'NSAIDs such as ibuprofen can increase bleeding risk when used with warfarin.'),
                  _e('m003', 'No clinically significant interaction between ibuprofen and warfarin was observed.')]},
]
