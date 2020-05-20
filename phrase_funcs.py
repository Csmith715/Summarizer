import pandas as pd
import numpy as np
import difflib
from itertools import chain, groupby
from operator import itemgetter

import spacy
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
import pickle

with open('qterms.data', 'rb') as filehandle:
    qterms = pickle.load(filehandle)

with open('who_rules.data', 'rb') as filehandle:
    who_rules = pickle.load(filehandle)

with open('whatrules2.data', 'rb') as filehandle:
    what_rules2 = pickle.load(filehandle)

nlp = spacy.load('en_core_web_sm')
matcher = PhraseMatcher(nlp.vocab)
terms = qterms
patterns = [nlp.make_doc(text) for text in terms]
matcher.add("TerminologyList", None, *patterns)

exclude_rules = [['MONEY', 'DATE', 'DATE'], ['MONEY', 'DATE'], ['DATE'], ['MONEY', 'TIME'], ['TIME'], [], 
                 ['ORG'], ['MONEY', 'CARDINAL'], ['MONEY'], ['CARDINAL', 'CARDINAL', 'CARDINAL'], ['MONEY', 'ORG'],
                 ['GPE', 'CARDINAL']]

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


def extract_listed_about(text, rules):
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

    wlt = [get_qphrases_text(rules, s) for s in webinar_list_text]
    wlt = pd.unique(list(chain.from_iterable(wlt)))
    spacy_lt = [spacy_phrase_match(s) for s in webinar_list_text]
    spacy_lt = pd.unique(list(chain.from_iterable(spacy_lt)))
    if wlt.size > 1:
        list_max = np.argmax([find_sim(w, spacy_lt) for w in wlt])
        wlt = wlt[list_max]
    elif wlt.size != 0: 
        wlt = wlt[0]
    return wlt

def extract_sentence_about(text, listed_about, rules):
    if type(listed_about) == str:
        listed_about = listed_about.split('\n')
    ulist = text.split('\n')
    ulist = [u for u in ulist if u]
    if len(listed_about) == 0:  # Listed 'You will learn' doesn't exist
        nlt = [get_qphrases_text(rules, n) for n in ulist]
        nlt = pd.unique(list(chain.from_iterable(nlt)))
        sp_nlt = [a for a in nlt if spacy_phrase_match(a).size > 0]
    else:  # Listed 'You will learn' does exist 
        ss = symmetric_same(listed_about, ulist)
        sidxs = []
        for s in ss:
            sidxs.append(ulist.index(s))
        ulist = [u for i, u in enumerate(ulist) if i < min(sidxs)]
        nlt = [get_qphrases_text(rules, n) for n in ulist]
        nlt = pd.unique(list(chain.from_iterable(nlt)))
        sp_nlt = [a for a in nlt if spacy_phrase_match(a).size > 0]        
    return sp_nlt

def extract_introduction(text, listed_about, sentence_about):
    if type(listed_about) == str:
        listed_about = listed_about.split('\n')
    if type(sentence_about) == str:
        sentence_about = sentence_about.split('\n')
    ulist = text.split('\n')
    ulist = [u for u in ulist if u]
# Listed 'You will learn' does exist and Sentence does not
    if len(listed_about) != 0 and len(sentence_about) == 0:  
        ss = symmetric_same(listed_about, ulist)
        sidxs = []
        for s in ss:
            sidxs.append(ulist.index(s))
        ulist = [u for i, u in enumerate(ulist) if i < min(sidxs)]
        intro = [x for x in ulist if x[0] != '#']
        intro = [x for x in intro if x[:2] != '- ']
# Listed 'You will learn' does not exist and Sentence does         
    elif len(listed_about) == 0 and len(sentence_about) != 0: 
        ss = symmetric_same(sentence_about, ulist)
        sidxs = []
        for s in ss:
            sidxs.append(ulist.index(s))
        ulist = [u for i, u in enumerate(ulist) if i < min(sidxs)]
        intro = [x for x in ulist if x[0] != '#'] 
        intro = [x for x in intro if x[:2] != '- ']
# Both Listed and Sentence exist        
    elif len(listed_about) != 0 and len(sentence_about) != 0: 
        ss = symmetric_same(sentence_about, ulist)
        sidxs = []
        for s in ss:
            sidxs.append(ulist.index(s))
        ulist = [u for i, u in enumerate(ulist) if i < min(sidxs)]
        intro = [x for x in ulist if x[0] != '#']
        intro = [x for x in intro if x[:2] != '- ']
# Neither exist:
    elif len(listed_about) == 0 and len(sentence_about) == 0:
        intro = []
    intro = [i for i in intro if not detect_mech(i, exclude_rules)]
    
    return pd.unique(intro)

def find_speaker(useable_text, listed_about, sentence_about, intro, rules):
    if type(listed_about) == str:
        listed_about = listed_about.split('\n')
    if type(sentence_about) == str:
        sentence_about = sentence_about.split('\n')
    ulist = useable_text.split('\n')
    used_text = [*listed_about, *sentence_about, *intro]
    person_list  = [get_qphrases_text(rules, w) for w in ulist]
    person_list  = pd.unique(list(chain.from_iterable(person_list)))
    utext = useable_text.split('\n')
    available_text = symmetric_difference(utext, used_text)
    #speaker_chunk = symmetric_same(available_text, person_list)
    speaker_chunk = []
    for a in available_text:
        if any(str(p) in a for p in person_list):
            speaker_chunk.append(a)
    sp_idxs = [ulist.index(s) for s in speaker_chunk]
    sc = [x for _, x in sorted(zip(sp_idxs, person_list) )] 
    sc = [s for s in sc if not detect_mech(s, exclude_rules)]
    
    return sc

# Detect POS matches for lines of text that should be excluded, such as dates or mechanical page headers
def detect_mech(text, ex_rules):
    ddoc = nlp(text)
    ddoc_ents = [e.label_ for e in ddoc.ents]
    for r in ex_rules:
        if ddoc_ents == r:
            return True  

def extract_sections(text):
    ela = extract_listed_about(text, rules=what_rules2)
    est = extract_sentence_about(text, ela, rules=what_rules2)
    intro = extract_introduction(text, ela, est)
    spkr = find_speaker(text, ela, est, intro, who_rules)
    
    return intro, est, ela, spkr

def extract_relevant_chunk(about_text_sentences):
    ats = about_text_sentences.split('\n')
    refined_ats = [a for a in ats if spacy_phrase_match(a).size > 0]
    
    return '\n'.join(refined_ats)

def symmetric_difference(a, b):
    return list({*a} ^ {*b})

def symmetric_same(a,b):
    return list({*a} & {*b})

def find_sim(a, b):
    nlpa = nlp(str(a))
    nlpb = nlp(str(b))
    return(nlpa.similarity(nlpb))
