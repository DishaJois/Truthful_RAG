import sys
sys.path.insert(0, '.')
import streamlit as st
from src.pipeline.pipeline import run_pipeline

NAMES = {'A': 'A: Baseline RAG', 'C': 'C: Verified RAG', 'B': 'B: RAG knowledge graph', 'D': 'D: Full TruthfulRAG'}
COLORS = {'SUPPORTED': 'green', 'PARTIALLY_SUPPORTED': 'orange', 'CONTRADICTED': 'red',
          'CONFLICTING_EVIDENCE': 'violet', 'INSUFFICIENT_EVIDENCE': 'gray', 'UNSUPPORTED': 'red',
          'OUT_OF_SCOPE': 'gray', 'AMBIGUOUS_QUERY': 'gray', 'UNSAFE_TO_ANSWER': 'red'}
EXAMPLES = ['What is the interaction between warfarin and aspirin?',
            'Can ibuprofen be taken with warfarin?',
            'Does clarithromycin interact with simvastatin?']

st.set_page_config(page_title='TruthfulRAG', layout='wide')
st.title('TruthfulRAG: drug-interaction question answering')
st.caption('Academic prototype. Not medical advice.')

cfg = st.sidebar.radio('Configuration', list(NAMES), format_func=lambda c: NAMES[c])
ex = st.sidebar.selectbox('Example questions', [''] + EXAMPLES)
question = st.text_input('Question', value=ex)

if st.button('Ask') and question.strip():
    try:
        with st.spinner('Retrieving and generating...'):
            res = run_pipeline(question, cfg)
    except Exception as e:
        st.error('Pipeline error. Details: ' + str(e))
        st.stop()
    if res['abstained']:
        st.warning(res['answer'])
    else:
        st.subheader('Answer')
        st.write(res['answer'])
        st.caption('Latency: ' + str(res['latency_s']) + 's')
        if res['claims']:
            st.subheader('Claim verification')
            for c in res['claims']:
                color = COLORS.get(c['state'], 'gray')
                st.markdown(':' + color + '[**' + c['state'] + '**] ' + c['claim'] + ' (confidence ' + str(round(c['confidence'], 2)) + ')')
    with st.expander('Evidence (' + str(len(res['evidence'])) + ' passages)'):
        for e in res['evidence']:
            st.markdown('**' + e['chunk_id'] + '** (' + str(e.get('source', '')) + ')')
            st.write(e['text'][:600])
