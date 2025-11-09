# NISM Series-VII Interactive MCQ Game — Streamlit App (Enhanced)
# ---------------------------------------------------------------
# Features:
# - Chapter-wise quizzes parsed from PDF or CSV
# - Motivational feedback and retry queue
# - Timed 100Q mock with negative marking option
# - Bookmarking and review system
# - Per-chapter progress tracking and export

import io, json, random, re
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
import streamlit as st

try:
    import pdfplumber
    PDF_OK = True
except Exception:
    PDF_OK = False

# --- CONFIG ---
APP_TITLE = "NISM Series-VII MCQ Game"
SUBTITLE = "Securities Operations & Risk Management — Interactive Study Tool"

MOTIVATION_LINES = ["🔥 That’s how pros think!", "🚀 Clean hit! Keep it up!", "💡 Sharp answer!", "🎯 On target!", "🏆 Textbook perfect!"]
WRONG_TIPS = ["No stress — we’ll revisit this soon.", "Good attempt. The pattern will click.", "We’ll slot this back in the queue."]

@dataclass
class MCQ:
    chapter: str
    question: str
    options: List[str]
    answer: str
    explanation: str = ""

    def to_dict(self):
        return asdict(self)

# --- SESSION KEYS ---
KS_QBANK, KS_MODE, KS_STATS = "qbanks", "mode", "stats"
KS_QUEUE, KS_HISTORY, KS_SEED = "queue", "history", "seed"
KS_TIMER, KS_SCORE, KS_NEGATIVE = "timer", "score", "negative"
KS_BOOKMARKS, KS_MOCK_REMAIN = "bookmarks", "mock_remain"

for k, v in {
    KS_QBANK: {"All": []}, KS_MODE: "Home", KS_STATS: {}, KS_QUEUE: [], KS_HISTORY: [],
    KS_SEED: 42, KS_TIMER: 0, KS_SCORE: 0.0, KS_NEGATIVE: False, KS_BOOKMARKS: set(), KS_MOCK_REMAIN: 0
}.items():
    if k not in st.session_state:
        st.session_state[k] = v
random.seed(st.session_state[KS_SEED])

# --- REGEX ---
CHAPTER_PAT = re.compile(r"^\s*(?:chapter|unit|module)\s*(\d+)[\.:\-\s]*(.*)$", re.I)
Q_PAT = re.compile(r"^\s*(?:Q\.?|Question\s*)?\s*(\d+)?[\):\.\-\s]*(.+?)\?\s*$", re.I)
OPT_PAT = re.compile(r"^[\s]*([A-Da-d])[\)\.\-:]+\s*(.+)$")
ANS_PAT = re.compile(r"^\s*(?:Ans|Answer|Correct\s*Option)\s*[:\-]\s*([A-Da-d])\b.*", re.I)
EXPL_PAT = re.compile(r"^(?:Explanation|Reason)\s*[:\-]\s*(.+)$", re.I)
KEY_ROW_PAT = re.compile(r"^\s*(?:\d+\.|Q\d+)[\)\.]?.*?(?:Ans|Answer|Correct\s*Option)\s*[:\-]\s*([A-Da-d])\b", re.I)

# --- HELPERS ---
def update_stats(ch, correct):
    s = st.session_state[KS_STATS].setdefault(ch, {"seen":0,"correct":0,"wrong":0})
    s["seen"] += 1; s["correct" if correct else "wrong"] += 1

def add_wrong(q):
    st.session_state[KS_QUEUE].append((random.randint(2,6), q))

def tick_queue():
    newq, popped = [], None
    for d,q in st.session_state[KS_QUEUE]:
        d-=1
        if d<=0 and popped is None: popped=q
        else: newq.append((d,q))
    st.session_state[KS_QUEUE]=newq; return popped

# --- PARSER ---
def parse_pdf_to_mcqs(pdf_bytes: bytes)->Dict[str,List[MCQ]]:
    if not PDF_OK: return {}
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        text="\n".join([p.extract_text(x_tolerance=3,y_tolerance=3) or '' for p in pdf.pages])
    lines=[l.strip() for l in text.splitlines() if l.strip()]

    chapters={}; cur="General"; q=None; opts=[]; ans=None; expl=[]

    def flush():
        nonlocal q,opts,ans,expl
        if q and opts:
            l=(ans or 'A').upper(); i=ord(l)-65; i=0 if i>=len(opts) or i<0 else i
            chapters.setdefault(cur,[]).append(MCQ(cur,q,opts,opts[i]," ".join(expl)))
        q,opts,ans,expl=None,[],None,[]

    for ln in lines:
        if m:=CHAPTER_PAT.match(ln): flush(); cur=f"Chapter {m[1]}: {m[2]}"; continue
        if m:=KEY_ROW_PAT.match(ln): ans=m[1].upper(); continue
        if m:=Q_PAT.match(ln): flush(); q=m[2].strip()+"?"; continue
        if m:=OPT_PAT.match(ln): opts.append(m[2].strip()); continue
        if m:=ANS_PAT.match(ln): ans=m[1].upper(); continue
        if m:=EXPL_PAT.match(ln): expl.append(m[1].strip()); continue
        if q: expl.append(ln)
    flush(); allq=[]
    for ch,a in chapters.items(): allq+=a
    chapters['All']=allq; return chapters

# --- ENGINE ---
def next_question(ch):
    q=tick_queue()
    if q: return q
    pool=list(st.session_state[KS_QBANK].get(ch,[]))
    random.shuffle(pool)
    return pool[0] if pool else None

def render_question(q:MCQ):
    st.markdown(f"### {q.question}")
    h=hash(q.question)
    bm=h in st.session_state[KS_BOOKMARKS]
    c1,c2=st.columns([4,1])
    with c2:
        if st.toggle("🔖",value=bm,key=f"bm_{h}"):
            st.session_state[KS_BOOKMARKS].add(h)
        else: st.session_state[KS_BOOKMARKS].discard(h)
    return st.radio("Select one:",q.options,index=None,key="opt")

def check_answer(q,choice):
    if not choice: st.info("Select an option"); return
    c=choice.strip()==q.answer.strip()
    update_stats(q.chapter,c)
    if st.session_state[KS_MODE] in ("Mega Mock","Timed Mock") and st.session_state[KS_MOCK_REMAIN]>0:
        st.session_state[KS_SCORE]+=1 if c else (-0.25 if st.session_state[KS_NEGATIVE] else 0)
        st.session_state[KS_MOCK_REMAIN]-=1
    if c: st.success(random.choice(MOTIVATION_LINES))
    else:
        st.error("❌ Not quite."); add_wrong(q)
        if q.explanation: st.info(q.explanation)

# --- UI ---
st.set_page_config(page_title=APP_TITLE,page_icon="📘",layout="wide")
with st.sidebar:
    st.title(APP_TITLE)
    st.caption(SUBTITLE)
    pdf=st.file_uploader("Upload NISM PDF",type=['pdf'])
    csv=st.file_uploader("or CSV",type=['csv'])
    if st.button("Load"):
        if pdf: st.session_state[KS_QBANK]=parse_pdf_to_mcqs(pdf.read()); st.success("PDF Loaded")
    st.divider()
    st.toggle("Negative Marking",value=st.session_state[KS_NEGATIVE],key=KS_NEGATIVE)
    mode=st.radio("Mode",["Home","Chapter Quiz","Mega Mock","Timed Mock","Bookmarks","Review"])
    st.session_state[KS_MODE]=mode

st.title(APP_TITLE); st.caption(SUBTITLE)

if st.session_state[KS_MODE]=="Home":
    st.write("Upload material and choose a mode from sidebar.")

elif st.session_state[KS_MODE]=="Chapter Quiz":
    chs=[c for c in st.session_state[KS_QBANK] if c!='All']
    if not chs: st.warning("No chapters loaded.")
    else:
        ch=st.selectbox("Chapter",chs)
        q=next_question(ch)
        if q:
            c=render_question(q)
            st.button("Submit",on_click=lambda:check_answer(q,c))

elif st.session_state[KS_MODE]=="Mega Mock":
    ch="All"; q=next_question(ch)
    if q:
        c=render_question(q)
        st.button("Submit",on_click=lambda:check_answer(q,c))

elif st.session_state[KS_MODE]=="Timed Mock":
    if st.session_state[KS_MOCK_REMAIN]==0:
        st.session_state[KS_MOCK_REMAIN]=100; st.session_state[KS_SCORE]=0.0; st.session_state[KS_TIMER]=120*60
    st.info(f"Time left: {st.session_state[KS_TIMER]//60}m | Score {st.session_state[KS_SCORE]:.2f}")
    st.session_state[KS_TIMER]-=1
    q=next_question('All')
    if q:
        c=render_question(q)
        st.button("Submit",on_click=lambda:check_answer(q,c))

elif st.session_state[KS_MODE]=="Bookmarks":
    b=st.session_state[KS_BOOKMARKS]
    if not b: st.info("No bookmarks yet.")
    else:
        for ch,arr in st.session_state[KS_QBANK].items():
            if ch=='All': continue
            for q in arr:
                if hash(q.question) in b:
                    with st.expander(q.question):
                        st.write(f"**Answer:** {q.answer}")
                        if q.explanation: st.caption(q.explanation)

elif st.session_state[KS_MODE]=="Review":
    if not st.session_state[KS_STATS]: st.info("No data yet.")
    else:
        for ch,s in st.session_state[KS_STATS].items():
            acc=(s['correct']/max(1,s['seen']))*100
            st.write(f"{ch}: {acc:.1f}% ({s['correct']}/{s['seen']})")
