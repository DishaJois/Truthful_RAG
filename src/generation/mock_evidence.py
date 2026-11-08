def _e(cid, text):
    return {'chunk_id': cid, 'text': text, 'score': 0.9, 'source': 'mock'}

MOCKS = [
    {
        'question': 'Can warfarin be taken with aspirin?',
        'evidence': [_e('m001', 'Concomitant use of warfarin and aspirin increases the risk of bleeding.')]
    },
    {
        'question': 'Does drug X interact with warfarin?',
        'evidence': []
    },
    {
        'question': 'Is ibuprofen safe with warfarin?',
        'evidence': [
            _e('m002', 'NSAIDs such as ibuprofen can increase bleeding risk when used with warfarin.'),
            _e('m003', 'No clinically significant interaction between ibuprofen and warfarin was observed.')
        ]
    },
    {
        'question': 'Does metformin interact with lisinopril?',
        'evidence': [_e('m004', 'Metformin and lisinopril do not show significant adverse metabolic interactions.')]
    },
    {
        'question': 'Can atorvastatin be taken with grapefruit juice?',
        'evidence': [_e('m005', 'Grapefruit juice significantly increases the plasma concentration of atorvastatin, risking myopathy.')]
    },
    {
        'question': 'Is acetaminophen safe with ibuprofen?',
        'evidence': [_e('m006', 'Alternating or co-administering acetaminophen and ibuprofen is commonly tolerated for acute fever.')]
    },
    {
        'question': 'Does ciprofloxacin interact with theophylline?',
        'evidence': [_e('m007', 'Ciprofloxacin inhibits CYP1A2, elevating theophylline serum levels to potentially toxic thresholds.')]
    },
    {
        'question': 'Can levothyroxine be taken with calcium carbonate?',
        'evidence': [_e('m008', 'Calcium carbonate reduces the absorption of levothyroxine when taken simultaneously.')]
    },
    {
        'question': 'Does simvastatin interact with clarithromycin?',
        'evidence': [_e('m009', 'Concomitant administration of clarithromycin and simvastatin is contraindicated due to rhabdomyolysis risk.')]
    },
    {
        'question': 'Is amoxicillin safe with oral contraceptives?',
        'evidence': [
            _e('m010', 'Amoxicillin does not substantially diminish the contraceptive efficacy of oral ethinyl estradiol.'),
            _e('m011', 'Some studies caution that gut flora alterations from amoxicillin might transiently alter steroid reabsorption.')
        ]
    }
]
