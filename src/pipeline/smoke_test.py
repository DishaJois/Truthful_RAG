from src.pipeline.pipeline import run_pipeline
Q = 'What is the interaction between warfarin and aspirin?'
for cfg in 'ABCD':
    r = run_pipeline(Q, cfg)
    assert {'question', 'config', 'answer', 'abstained', 'evidence', 'claims', 'latency_s'} <= set(r)
    print(cfg, r['latency_s'], 's', r['answer'][:100])
print('smoke test passed')
if __name__ == '__main__':
    pass
