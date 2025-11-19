import streamlit as st
import sys
import os

# Add backend to path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from pdf_parser import PDFParser
from question_generator import QuestionGenerator

# Page Config
st.set_page_config(
    page_title="Quiz Maker",
    page_icon="📚",
    layout="centered"
)

# Session State Initialization
if 'chapters' not in st.session_state:
    st.session_state.chapters = []
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'current_question_idx' not in st.session_state:
    st.session_state.current_question_idx = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {} # {question_id: {selected_idx, is_correct}}
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False
if 'score' not in st.session_state:
    st.session_state.score = 0

def reset_quiz():
    st.session_state.quiz_questions = []
    st.session_state.current_question_idx = 0
    st.session_state.user_answers = {}
    st.session_state.quiz_submitted = False
    st.session_state.score = 0

# --- Sidebar: Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # File Upload
    uploaded_file = st.file_uploader("Upload Textbook (PDF)", type="pdf")
    
    if uploaded_file is not None:
        # Check if we need to re-parse
        # We use a simple check: if chapters are empty or filename changed (not easily tracked here without more state, so just parse if chapters empty)
        if not st.session_state.chapters:
            with st.spinner("Parsing PDF..."):
                try:
                    parser = PDFParser()
                    st.session_state.chapters = parser.parse_pdf(uploaded_file)
                    st.success(f"Loaded {len(st.session_state.chapters)} chapters!")
                except Exception as e:
                    st.error(f"Error parsing PDF: {e}")

    # Exam Profile
    exam_profile = st.text_input("Exam Name", placeholder="e.g. NISM Series VII")
    
    # Mode Selection
    mode = st.radio("Quiz Mode", ["Practice", "Mock Exam"])
    
    # Chapter Selection (Only for Practice)
    selected_chapter_ids = []
    if mode == "Practice" and st.session_state.chapters:
        st.subheader("Select Chapters")
        for chapter in st.session_state.chapters:
            if st.checkbox(f"{chapter.title}", value=True, key=chapter.id):
                selected_chapter_ids.append(chapter.id)
    
    # Start Button
    if st.button("Start New Quiz", type="primary"):
        if not st.session_state.chapters:
            st.error("Please upload a PDF first.")
        elif mode == "Practice" and not selected_chapter_ids:
            st.error("Please select at least one chapter.")
        else:
            reset_quiz()
            
            # Gather text
            if mode == "Mock Exam":
                selected_chapters = st.session_state.chapters
                num_q = 50
            else:
                selected_chapters = [c for c in st.session_state.chapters if c.id in selected_chapter_ids]
                num_q = 10
            
            full_text = "\n".join([c.content for c in selected_chapters])
            
            with st.spinner("Generating Questions..."):
                generator = QuestionGenerator()
                questions = generator.generate_questions(full_text, num_questions=num_q)
                
                if not questions:
                    st.error("Could not generate questions. Text might be too short.")
                else:
                    st.session_state.quiz_questions = questions

# --- Main Area ---
st.title("📚 Quiz Maker")

if not st.session_state.quiz_questions:
    # Welcome Screen
    st.info("👈 Upload a PDF and click 'Start New Quiz' in the sidebar to begin.")
    
    if st.session_state.chapters:
        st.write("### Detected Chapters")
        for c in st.session_state.chapters:
            st.write(f"- **{c.title}** (Pages {c.start_page+1}-{c.end_page+1})")

else:
    # Quiz Interface
    if st.session_state.current_question_idx < len(st.session_state.quiz_questions):
        q = st.session_state.quiz_questions[st.session_state.current_question_idx]
        
        # Progress
        progress = (st.session_state.current_question_idx) / len(st.session_state.quiz_questions)
        st.progress(progress, text=f"Question {st.session_state.current_question_idx + 1} of {len(st.session_state.quiz_questions)}")
        
        # Question Card
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h3 style="margin:0;">{q.text}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Options
        # We use a form so we can submit the answer
        with st.form(key=f"q_form_{st.session_state.current_question_idx}"):
            choice = st.radio("Choose an answer:", q.options, index=None)
            submit_btn = st.form_submit_button("Submit Answer")
            
            if submit_btn and choice:
                # Check answer
                selected_idx = q.options.index(choice)
                is_correct = (selected_idx == q.correct_idx)
                
                st.session_state.user_answers[q.id] = {
                    "selected_idx": selected_idx,
                    "is_correct": is_correct,
                    "question": q
                }
                
                if is_correct:
                    st.success("✅ Correct!")
                    st.session_state.score += 1
                else:
                    st.error(f"❌ Incorrect. The correct answer was: **{q.options[q.correct_idx]}**")
                
                st.info(f"**Explanation:** {q.explanation}")
                
                # Next button (outside form to avoid auto-submit issues, but Streamlit flow is tricky)
                # Actually, in Streamlit, we usually just show the next button after submission
                
        if q.id in st.session_state.user_answers:
            if st.button("Next Question ➡️"):
                st.session_state.current_question_idx += 1
                st.rerun()
                
    else:
        # Results Screen
        st.balloons()
        st.header("🎉 Quiz Complete!")
        
        total = len(st.session_state.quiz_questions)
        score = st.session_state.score
        percentage = int((score / total) * 100)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Score", f"{percentage}%")
        with col2:
            st.metric("Correct Answers", f"{score}/{total}")
            
        st.subheader("Review")
        for q in st.session_state.quiz_questions:
            ans = st.session_state.user_answers.get(q.id)
            if ans:
                with st.expander(f"Q: {q.text} - {'✅' if ans['is_correct'] else '❌'}"):
                    st.write(f"**Your Answer:** {q.options[ans['selected_idx']]}")
                    if not ans['is_correct']:
                        st.write(f"**Correct Answer:** {q.options[q.correct_idx]}")
                    st.write(f"**Explanation:** {q.explanation}")
        
        if st.button("Start Another Quiz"):
            reset_quiz()
            st.rerun()
