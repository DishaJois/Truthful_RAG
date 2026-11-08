from src.generation.llm import chat

SYSTEM = (
    'You are a careful drug-interaction assistant. Answer ONLY using the evidence provided.\n'
    'Cite chunk ids in square brackets, like [c0001].\n'
    'If the evidence does not contain the answer, reply exactly: The evidence does not say.'
)

def format_evidence(evidence, max_chunks=8, max_words=1200):
    lines, used = [], 0
    for e in evidence[:max_chunks]:
        words = e['text'].split()[: max(0, max_words - used)]
        if not words:
            break
        lines.append('[' + e['chunk_id'] + '] ' + ' '.join(words))
        used += len(words)
    return '\n\n'.join(lines)

def generate(question, evidence):
    if not evidence:
        return 'The evidence does not say.'
    prompt = (
        'Evidence:\n' + format_evidence(evidence) +
        '\n\nQuestion: ' + question +
        '\n\nAnswer in 2 to 4 sentences, citing chunk ids.'
    )
    return chat(prompt, system=SYSTEM).strip()
