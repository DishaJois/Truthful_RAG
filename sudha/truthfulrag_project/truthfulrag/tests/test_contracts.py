from src.retrieval.retriever import retrieve
from src.kg.graph import kg_lookup

def test_retrieve_shape():
    r = retrieve('warfarin and aspirin', 5)
    assert len(r) <= 5
    assert all({'chunk_id', 'text', 'score', 'source'} <= set(x) for x in r)

def test_kg_shape():
    for e in kg_lookup(['warfarin']):
        assert {'subject', 'relation', 'object', 'chunk_id'} <= set(e)
