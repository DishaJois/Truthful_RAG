import json, sys

path = sys.argv[1]
qtype = input('type (answerable / unanswerable / tricky): ').strip()
question = input('question: ').strip()
gold = input('gold answer (empty for unanswerable): ').strip()
ids = [x.strip() for x in input('gold chunk ids, comma separated: ').split(',') if x.strip()]

with open(path, 'a', encoding='utf-8') as f:
    f.write(json.dumps({'qid': '', 'question': question, 'gold_answer': gold, 'gold_chunk_ids': ids, 'type': qtype}) + '\n')
print('saved')
