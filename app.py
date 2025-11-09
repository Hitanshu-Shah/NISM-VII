# NISM Series-VII Interactive MCQ Game — Streamlit App (Fixed & Compact)
# ----------------------------------------------------------------------
# - Robust chapter detection (Chapter/Unit/Module)
# - Exactly 4 options per MCQ (trimmed & clean)
# - Readable question text (single line, ellipsized if too long)
# - Proper next-question flow (auto-advance after Submit)
# - Wrong-answer retry queue preserved
# - Negative marking & bookmarks available

import io, json, random, re
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import streamlit as st

try:
    import pdfplumber
    PDF_OK = True
except Exception:
    PDF_OK = False

APP_TITLE = "NISM Series-VII MCQ Game"
SUBTITLE = "Securities Operations & Risk Management — Interactive Study Tool"

MOTIVATION_LINES = [
    "🔥 That’s how pros think!", "🚀 Clean hit! Keep it up!",
    "💡 Sharp answer!", "🎯 On target!", "🏆 Textbook perfect!"
]
WRONG_TIPS = [
    "No stress — we’ll revisit this soon.",
    "Good attempt. The pattern will click.",
    "We’ll slot this back in the queue."
]

@dataclass
class MCQ:
    chapter: str
    question: str
    options: List[str]
    answer: str
    explanation: str = ""

    def to_dict(self):
        return asdict(self)

# ---- Session keys
KS_QBANK, KS_MODE, KS_STATS = "qbanks", "mode", "stats"
KS_QUEUE, KS_SEED = "queue", "seed"
KS_NEGATIVE, KS_BOOKMARKS = "negative", "bookmarks"
KS_POINTERS = "pointers"  # per-chapter index pointer

# ---- Init session
defaults = {
    KS_QBANK: {"All": []},
    KS_MODE: "Home",
    KS_STATS: {},
    KS_QUEUE: [],
    KS_SEED: 42,
    KS_NEGATIVE: False,
    KS_BOOKMARKS: set(),
    KS_POINTERS: {}
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
random.seed(st.session_state[KS_SEED])

# ---- Regex (tuned)
CHAPTER_PAT = re.compile(r"^\s*(?:chapter|unit|module)\s*(\d+)[\.\:\-\s]*(.*)$", re.I)
Q_PAT       = re.compile(r"^\s*(?:Q\.?|Question\s*)?\s*(\d+)?[\)\:\.\-\s]*(.+?)\?\s*$", re.I)
OPT_PAT     = re.compile(r"^[\s]*([A-Da-d])[\)\.\-:]+\s*(.+)$")
ANS_PAT     = re.compile(r"^\s*(?:Ans|Answer|Correct\s*Option)\s*[:\-]\s*([A-Da-d])\b.*", re.I)
EXPL_PAT    = re.compile(r"^(?:Explanation|Reason)\s*[:\-]\s*(.+)$", re.I)
KEY_ROW_PAT = re.compile(r"^\s*(?:\d+\.|Q\d+)[\)\.]?.*?(?:Ans|Answer|Correct\s*Option)\s*[:\-]\s*([A-Da-d])\b", re.I)

# ---- Helpers
def update_stats(ch: str, correct: bool):
    s = st.session_state[KS_STATS].setdefault(ch, {"seen":0,"correct":0,"wrong":0})
    s["seen"] += 1
    if correct: s["correct"] += 1
    else:       s["wrong"]   += 1

def add_wrong(q: MCQ):
    st.session_state[KS_QUEUE].append((random.randint(2,5), q))

def tick_queue() -> Optional[MCQ]:
    newq, popped = [], None
    for d, q in st.session_state[KS_QUEUE]:
        d -= 1
        if d <= 0 and popped is None:
            popped = q
        else:
            newq.append((d, q))
    st.session_state[KS_QUEUE] = newq
    return popped

def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

TRIM_Q = 160    # max chars for questions
TRIM_O = 100    # max chars for options

def _trim(s: str, N: int) -> str:
    s = _clean(s)
    return (s[:N-1] + "…") if len(s) > N else s

def _cap4(opts: List[str]) -> List[str]:
    picked = []
    for o in opts[:4]:
        picked.append(_trim(o, TRIM_O))
    while len(picked) < 4:
        picked.append("(Option)")
    return picked

# ---- PDF Parser (compact & strict)
def parse_pdf_to_mcqs(pdf_bytes: bytes) -> Dict[str, List[MCQ]]:
    if not PDF_OK:
        st.warning("pdfplumber not available here.")
        return {}

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        text = "\n".join([p.extract_text(x_tolerance=3, y_tolerance=3) or "" for p in pdf.pages])

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    chapters: Dict[str, List[MCQ]] = {}
    cur = "Chapter 1"
    q = None; opts: List[str] = []; ans = None; expl: List[str] = []

    def flush():
        nonlocal q, opts, ans, expl
        if q and opts:
            qtxt = _trim(q, TRIM_Q) + ("" if q.endswith("?") else "?")
            opts4 = _cap4(opts)
            letter = (ans or "A").upper()
            idx = max(0, min(3, ord(letter) - ord("A")))
            chapters.setdefault(cur, []).append(
                MCQ(cur, qtxt, opts4, opts4[idx], _clean(" ".join(expl)))
            )
        q, opts, ans, expl = None, [], None, []

    for ln in lines:
        if m := CHAPTER_PAT.match(ln):
            flush()
            num, title = m.group(1), (m.group(2) or "").strip()
            cur = f"Chapter {num}: {title}" if title else f"Chapter {num}"
            continue
        if m := KEY_ROW_PAT.match(ln):
            ans = m.group(1).upper(); continue
        if m := Q_PAT.match(ln):
            flush()
            q = m.group(2).strip() + "?"
            continue
        if m := OPT_PAT.match(ln):
            opts.append(m.group(2).strip()); continue
        if m := ANS_PAT.match(ln):
            ans = m.group(1).upper(); continue
        if m := EXPL_PAT.match(ln):
            expl.append(m.group(1).strip()); continue
        if q:
            # treat extra wrapped lines as explanation to avoid creating new options
            expl.append(ln)

    flush()

    # Build "All"
    allq = []
    for ch, arr in chapters.items():
        allq.extend(arr)
    chapters["All"] = allq
    return chapters

# ---- Engine with proper next-question flow
def _next_from_queue_or_pool(ch: str) -> Optional[MCQ]:
    # 1) retry queue
    q = tick_queue()
    if q: return q

    # 2) chapter pool with pointer
    ptrs = st.session_state[KS_POINTERS]
    pool = list(st.session_state[KS_QBANK].get(ch, []))
    if not pool: return None
    if ch not in ptrs: ptrs[ch] = 0
    idx = ptrs[ch]
    if idx >= len(pool): idx = 0
    q = pool[idx]
    ptrs[ch] = idx + 1
    return q

def render_q(q: MCQ):
    st.subheader(q.question)
    # bookmark
    h = hash(q.question)
    bm = h in st.session_state[KS_BOOKMARKS]
    _, col_bm = st.columns([6,1])
    with col_bm:
        if st.toggle("🔖", value=bm, key=f"bm_{h}", help="Bookmark"):
            st.session_state[KS_BOOKMARKS].add(h)
        else:
            st.session_state[KS_BOOKMARKS].discard(h)
    choice = st.radio("Select one:", q.options, index=None, key="opt_select")
    return choice

def check_and_feedback(q: MCQ, choice: Optional[str]) -> bool:
    if not choice:
        st.info("Select an option to proceed.")
        return False
    correct = (choice.strip() == q.answer.strip())
    update_stats(q.chapter, correct)
    if correct:
        st.success(random.choice(MOTIVATION_LINES))
    else:
        st.error("❌ Not quite. We’ll retry this later.")
        st.caption(random.choice(WRONG_TIPS))
        add_wrong(q)
    return True

# ---- UI
st.set_page_config(page_title=APP_TITLE, page_icon="📘", layout="wide")

with st.sidebar:
    st.title(APP_TITLE)
    st.caption(SUBTITLE)

    st.markdown("**Upload PDF**")
    pdf = st.file_uploader("PDF", type=["pdf"])
    st.markdown("or **CSV (chapter,question,options,answer,explanation)**")
    csv = st.file_uploader("CSV", type=["csv"])

    if st.button("Load ▶"):
        if pdf:
            st.session_state[KS_QBANK] = parse_pdf_to_mcqs(pdf.read())
            st.session_state[KS_POINTERS] = {}
            chapters = [k for k in st.session_state[KS_QBANK].keys() if k != "All"]
            st.success(f"Loaded {sum(len(v) for k,v in st.session_state[KS_QBANK].items() if k!='All')} questions across {len(chapters)} chapters.")
        elif csv:
            text = csv.read().decode("utf-8")
            lines = [ln for ln in text.splitlines() if ln.strip()]
            header = [h.strip().lower() for h in lines[0].split(",")]
            idx = {name:i for i,name in enumerate(header)}
            bank: Dict[str, List[MCQ]] = {}
            for row in lines[1:]:
                cols = [c.strip() for c in re.split(r",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", row)]
                ch = cols[idx.get("chapter", 0)]
                q = cols[idx.get("question", 1)].strip('"')
                opts = cols[idx.get("options", 2)].strip('"').split("|")
                ans = cols[idx.get("answer", 3)].strip('"')
                ex  = cols[idx.get("explanation", 4)].strip('"') if len(cols) > 4 else ""
                opts = _cap4(opts)
                if ans not in opts:  # fallback to first if provided answer isn't in 4 options
                    ans = opts[0]
                bank.setdefault(ch, []).append(MCQ(ch, _trim(q, TRIM_Q), opts, ans, ex))
            allq = []; [allq.extend(v) for k,v in bank.items()]
            bank["All"] = allq
            st.session_state[KS_QBANK] = bank
            st.session_state[KS_POINTERS] = {}
            chapters = [k for k in bank.keys() if k != "All"]
            st.success(f"Loaded {sum(len(v) for k,v in bank.items() if k!='All')} questions across {len(chapters)} chapters.")
        else:
            st.warning("Upload a PDF or a CSV to load questions.")

    st.divider()
    st.toggle("Negative Marking (-0.25 on wrong in mocks)", value=st.session_state[KS_NEGATIVE], key=KS_NEGATIVE)

    mode = st.radio("Mode", ["Home", "Chapter Quiz", "Mega Mock", "Bookmarks", "Review"], index=["Home","Chapter Quiz","Mega Mock","Bookmarks","Review"].index(st.session_state[KS_MODE]) if st.session_state[KS_MODE] in ["Home","Chapter Quiz","Mega Mock","Bookmarks","Review"] else 0)
    st.session_state[KS_MODE] = mode

st.title(APP_TITLE)
st.caption(SUBTITLE)

if st.session_state[KS_MODE] == "Home":
    st.write("Upload your PDF/CSV on the left, then choose a mode. Each question has **only 4 options** and the app **auto-advances** after Submit.")

elif st.session_state[KS_MODE] == "Chapter Quiz":
    chapters = [c for c in st.session_state[KS_QBANK].keys() if c != "All"]
    if not chapters:
        st.warning("No chapters detected. If your PDF only shows a 'Sample Questions' section, try Mega Mock.")
    else:
        ch = st.selectbox("Chapter", chapters)
        q = _next_from_queue_or_pool(ch)
        if q:
            choice = render_q(q)
            if st.button("Submit"):
                ok = check_and_feedback(q, choice)
                if ok: st.experimental_rerun()

elif st.session_state[KS_MODE] == "Mega Mock":
    ch = "All"
    q = _next_from_queue_or_pool(ch)
    if q:
        choice = render_q(q)
        if st.button("Submit"):
            ok = check_and_feedback(q, choice)
            if ok: st.experimental_rerun()

elif st.session_state[KS_MODE] == "Bookmarks":
    bms = st.session_state[KS_BOOKMARKS]
    if not bms:
        st.info("No bookmarks yet.")
    else:
        for ch, arr in st.session_state[KS_QBANK].items():
            if ch == "All": continue
            for q in arr:
                if hash(q.question) in bms:
                    with st.expander(q.question):
                        for o in q.options: st.write("- ", o)
                        st.write(f"**Answer:** {q.answer}")
                        if q.explanation: st.caption(q.explanation)

elif st.session_state[KS_MODE] == "Review":
    stats = st.session_state[KS_STATS]
    if not stats:
        st.info("No attempts yet.")
    else:
        for ch, s in stats.items():
            seen = max(1, s["seen"])
            acc = round((s["correct"] / seen) * 100, 1)
            st.write(f"**{ch}** — Seen {s['seen']} | ✅ {s['correct']} | ❌ {s['wrong']} | Accuracy: {acc}%")
