import pandas as pd
import numpy as np
import difflib
from itertools import chain, groupby
from operator import itemgetter

import spacy
import en_core_web_sm
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
import pickle

with open('qterms.data', 'rb') as filehandle:
    qterms = pickle.load(filehandle)

#nlp = spacy.load('en_core_web_sm')
nlp = en_core_web_sm.load()
matcher = PhraseMatcher(nlp.vocab)
terms = qterms
patterns = [nlp.make_doc(text) for text in terms]
matcher.add("TerminologyList", None, *patterns)

def spacy_phrase_match(text):
    doc = nlp(text)
    matches = matcher(doc)
    matching_sents = []
    for match_id, start, end in matches:
        sent_span = doc[start:end].sent
        matching_sents.append(sent_span.text)
    
    return np.unique(matching_sents)

def get_pattern_tupples(text):
    doc = nlp(text)
    pattern = [(t.pos_, t.tag_, t.dep_) for t in doc]
    term_idx = [str(t) for t in doc]
    
    return pattern, term_idx
def get_qphrases_text(rules, text):
    fnd = []
    pat, t = get_pattern_tupples(text)
    for w in rules:
        rm = rule_matches(pat, w)
        if rm:
            fnd.append(text)
    
    return(fnd)

def rule_matches(a, b):
    sm = difflib.SequenceMatcher(None, a, b).get_matching_blocks()
    seq_match = [[s[0],s[0]+s[2]] for s in sm if s[2] == len(b)]
    return(seq_match)

def split_text_and_extract_sents(text):
    ulist = text.split('\n')
    ulist = [u for u in ulist if u]
    list_idxs = []
    for i, x in enumerate(ulist):
        if x[:2] == '- ':
            list_idxs.append(i)

    list_groups = []
    for k, g in groupby(enumerate(list_idxs), lambda x: x[0]-x[1]):
         list_groups.append(list(map(itemgetter(1), g)))

    webinar_list_text = []
    new_list_idxs = []
    for g in list_groups:
        if g[0] != 0:
            a = min(g)-1
            list_text = '\n'.join(ulist[a:max(g)+1])
            list_idxs.append(a)
        else:
            list_text = ''
        webinar_list_text.append(list_text)
        new_list_idxs.append(g)
        
    non_list_text = [x for i, x in enumerate(ulist) if i not in list_idxs]
    
    wlt = [spacy_phrase_match(s) for s in webinar_list_text]
    wlt = pd.unique(list(chain.from_iterable(wlt)))

    nlt = [spacy_phrase_match(n) for n in non_list_text]
    nlt = pd.unique(list(chain.from_iterable(nlt)))
    nlt = '\n'.join(nlt)
    
    return wlt, nlt

def split_listed_text(text, rules):
    ulist = text.split('\n')
    ulist = [u for u in ulist if u]
    list_idxs = []
    for i, x in enumerate(ulist):
        if x[:2] == '- ':
            list_idxs.append(i)
    
    list_groups = []
    for k, g in groupby(enumerate(list_idxs), lambda x: x[0]-x[1]):
         list_groups.append(list(map(itemgetter(1), g)))

    webinar_list_text = []
    new_list_idxs = []
    for g in list_groups:
        if g[0] != 0:
            a = min(g)-1
            list_text = '\n'.join(ulist[a:max(g)+1])
            list_idxs.append(a)
        else:
            list_text = ''
        webinar_list_text.append(list_text)
        new_list_idxs.append(g)

    if new_list_idxs and (min(chain.from_iterable(new_list_idxs)) != 0):
        min_list_idx = min(chain.from_iterable(new_list_idxs))
    else:
        min_list_idx = len(ulist)
 
    non_list_text = [x for i, x in enumerate(ulist) if i not in list_idxs and i < min_list_idx]
    
    wlt = [get_qphrases_text(rules, s) for s in webinar_list_text]        
    nlt = [get_qphrases_text(rules, n) for n in non_list_text]
    nlt = pd.unique(list(chain.from_iterable(nlt)))
    nlt = '\n'.join(nlt)
    
    wlt = pd.unique(list(chain.from_iterable(wlt)))
    
    return wlt, nlt
