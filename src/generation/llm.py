import hashlib, os, sqlite3
import ollama

MODEL = os.environ.get('TRUTHFULRAG_MODEL', 'llama3.2:3b')
os.makedirs('results', exist_ok=True)
_db = sqlite3.connect('results/llm_cache.sqlite', check_same_thread=False)
_db.execute('CREATE TABLE IF NOT EXISTS cache (k TEXT PRIMARY KEY, v TEXT)')

def chat(prompt, system=None, temperature=0.0):
    key = hashlib.sha256(f'{MODEL}|{system}|{temperature}|{prompt}'.encode()).hexdigest()
    row = _db.execute('SELECT v FROM cache WHERE k=?', (key,)).fetchone()
    if row:
        return row[0]
    messages = []
    if system:
        messages.append({'role': 'system', 'content': system})
    messages.append({'role': 'user', 'content': prompt})
    out = ollama.chat(model=MODEL, messages=messages, options={'temperature': temperature})['message']['content']
    _db.execute('INSERT OR REPLACE INTO cache VALUES (?,?)', (key, out))
    _db.commit()
    return out
