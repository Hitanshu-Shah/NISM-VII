import streamlit as st
import random
import json
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="NISM Series-VII MCQ Game",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        font-size: 1.2rem;
        margin: 20px 0;
        animation: slideIn 0.5s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .error-box {
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        text-align: center;
        font-size: 1.2rem;
        margin: 20px 0;
        animation: slideIn 0.5s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .question-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #1f77b4;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .timer-box {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        color: white;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .stats-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        margin: 10px 0;
        border: 2px solid #e0e0e0;
    }
    @keyframes slideIn {
        from {
            transform: translateY(-20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    .chapter-badge {
        display: inline-block;
        padding: 5px 15px;
        background: #1f77b4;
        color: white;
        border-radius: 20px;
        font-size: 0.9rem;
        margin: 5px 0;
    }
    .progress-bar {
        background: #e0e0e0;
        border-radius: 10px;
        height: 20px;
        overflow: hidden;
    }
    .progress-fill {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 100%;
        transition: width 0.3s ease;
    }
    .option-button {
        background: white;
        border: 2px solid #e0e0e0;
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s;
    }
    .option-button:hover {
        border-color: #1f77b4;
        background: #f0f8ff;
    }
</style>
""", unsafe_allow_html=True)

# Chapter 1: Introduction to Securities Market - 20 Questions
CHAPTER_1_QUESTIONS = [
    {
        "id": "c1q1",
        "question": "What is the primary function of the securities market?",
        "options": [
            "To facilitate price discovery and liquidity",
            "To provide banking services",
            "To regulate currency exchange",
            "To manage government debt"
        ],
        "correct": 0,
        "explanation": "Securities markets primarily facilitate price discovery through supply-demand dynamics and provide liquidity, enabling investors to buy and sell securities efficiently."
    },
    {
        "id": "c1q2",
        "question": "Which regulatory body oversees the securities market in India?",
        "options": [
            "Reserve Bank of India",
            "Securities and Exchange Board of India (SEBI)",
            "Ministry of Finance",
            "Insurance Regulatory and Development Authority"
        ],
        "correct": 1,
        "explanation": "SEBI, established in 1992, is the primary regulatory authority for securities markets in India, protecting investor interests and promoting market development."
    },
    {
        "id": "c1q3",
        "question": "What distinguishes the primary market from the secondary market?",
        "options": [
            "Primary market involves new securities issuance; secondary market involves trading of existing securities",
            "Primary market is for bonds only",
            "Secondary market is unregulated",
            "Primary market operates only on weekends"
        ],
        "correct": 0,
        "explanation": "The primary market is where new securities are issued for the first time (IPOs, FPOs), while the secondary market facilitates trading of already-issued securities."
    },
    {
        "id": "c1q4",
        "question": "What does IPO stand for in securities markets?",
        "options": [
            "Internal Purchase Order",
            "Initial Public Offering",
            "International Portfolio Organization",
            "Investment Protection Obligation"
        ],
        "correct": 1,
        "explanation": "IPO stands for Initial Public Offering, which is the first time a company offers its shares to the public for subscription."
    },
    {
        "id": "c1q5",
        "question": "Which of the following is NOT a participant in the securities market?",
        "options": [
            "Stock brokers",
            "Depositories",
            "Retail grocery stores",
            "Clearing corporations"
        ],
        "correct": 2,
        "explanation": "Retail grocery stores are not participants in securities markets. Key participants include brokers, depositories, clearing corporations, custodians, and investors."
    },
    {
        "id": "c1q6",
        "question": "What is the role of a depository in the securities market?",
        "options": [
            "To provide loans to investors",
            "To hold securities in electronic form",
            "To set market prices",
            "To approve company listings"
        ],
        "correct": 1,
        "explanation": "Depositories hold securities in electronic (dematerialized) form and facilitate their transfer. NSDL and CDSL are the two depositories in India."
    },
    {
        "id": "c1q7",
        "question": "What does 'Dematerialization' mean in the context of securities?",
        "options": [
            "Conversion of physical certificates into electronic form",
            "Selling securities at market price",
            "Borrowing against securities",
            "Cancellation of securities"
        ],
        "correct": 0,
        "explanation": "Dematerialization (Demat) is the process of converting physical share certificates into electronic form, making them easier to trade and hold."
    },
    {
        "id": "c1q8",
        "question": "Which year was SEBI given statutory powers?",
        "options": [
            "1988",
            "1992",
            "1995",
            "2000"
        ],
        "correct": 1,
        "explanation": "SEBI was established in 1988 as a non-statutory body and was given statutory powers in 1992 through the SEBI Act."
    },
    {
        "id": "c1q9",
        "question": "What is the main objective of SEBI?",
        "options": [
            "To maximize government revenue",
            "To protect investor interests and promote market development",
            "To control inflation",
            "To manage foreign exchange"
        ],
        "correct": 1,
        "explanation": "SEBI's primary objectives are to protect investor interests, promote the development of securities markets, and regulate market activities."
    },
    {
        "id": "c1q10",
        "question": "What is a stock exchange?",
        "options": [
            "A place where currencies are traded",
            "An organized marketplace for buying and selling securities",
            "A government bank",
            "A commodity trading platform"
        ],
        "correct": 1,
        "explanation": "A stock exchange is an organized marketplace where securities like stocks and bonds are bought and sold under regulatory supervision."
    },
    {
        "id": "c1q11",
        "question": "Which of these is NOT a type of security?",
        "options": [
            "Equity shares",
            "Debentures",
            "Real estate properties",
            "Government bonds"
        ],
        "correct": 2,
        "explanation": "Securities are financial instruments like shares, bonds, and debentures. Real estate properties are physical assets, not securities."
    },
    {
        "id": "c1q12",
        "question": "What does NSE stand for?",
        "options": [
            "National Securities Exchange",
            "National Stock Exchange",
            "New Securities Entity",
            "National Savings Exchange"
        ],
        "correct": 1,
        "explanation": "NSE stands for National Stock Exchange of India, established in 1992 as the first electronic stock exchange in India."
    },
    {
        "id": "c1q13",
        "question": "What is the purpose of a clearing corporation?",
        "options": [
            "To trade securities on behalf of investors",
            "To ensure settlement of trades and manage counterparty risk",
            "To issue new securities",
            "To provide investment advice"
        ],
        "correct": 1,
        "explanation": "Clearing corporations act as intermediaries between buyers and sellers, ensuring smooth settlement of trades and managing counterparty risk through guarantees."
    },
    {
        "id": "c1q14",
        "question": "What is 'T+1' settlement cycle?",
        "options": [
            "Trade is settled 1 hour after execution",
            "Trade is settled 1 day after the trade date",
            "Trade is settled on the 1st of every month",
            "Trade requires 1 broker"
        ],
        "correct": 1,
        "explanation": "T+1 settlement means that the final settlement of securities and funds occurs 1 business day after the trade date (T). Currently, all securities traded in equity segment follow T+1 settlement."
    },
    {
        "id": "c1q15",
        "question": "Which document is required to open a Demat account?",
        "options": [
            "Passport only",
            "KYC documents including PAN, address proof, and bank details",
            "Driving license only",
            "No documents required"
        ],
        "correct": 1,
        "explanation": "Opening a Demat account requires KYC (Know Your Customer) documents including PAN card, address proof, identity proof, and bank account details."
    },
    {
        "id": "c1q16",
        "question": "What does FPO stand for?",
        "options": [
            "First Public Offering",
            "Follow-on Public Offering",
            "Financial Portfolio Organization",
            "Foreign Portfolio Offering"
        ],
        "correct": 1,
        "explanation": "FPO stands for Follow-on Public Offering, which is when an already listed company issues additional shares to the public."
    },
    {
        "id": "c1q17",
        "question": "Which term best describes 'sovereign debt'?",
        "options": [
            "Corporate bonds",
            "Government Securities",
            "Equity shares",
            "Mutual fund units"
        ],
        "correct": 1,
        "explanation": "Government Securities are also known as 'sovereign debt' and are issued by central and state governments."
    },
    {
        "id": "c1q18",
        "question": "What is an ETF?",
        "options": [
            "Electronic Trading Facility",
            "Exchange Traded Fund",
            "Equity Transaction Fee",
            "Electronic Transfer Form"
        ],
        "correct": 1,
        "explanation": "An ETF (Exchange Traded Fund) is a marketable security that tracks an index, commodity, bonds, or basket of assets and trades like a common stock on an exchange."
    },
    {
        "id": "c1q19",
        "question": "What is the settlement cycle for T+0?",
        "options": [
            "Settlement on the same day as the trade",
            "Settlement 10 days after trade",
            "No settlement required",
            "Settlement after one month"
        ],
        "correct": 0,
        "explanation": "T+0 settlement means trades are settled on the same day they are executed. SEBI introduced beta version of optional T+0 settlement for select scrips."
    },
    {
        "id": "c1q20",
        "question": "What is the role of a Depository Participant (DP)?",
        "options": [
            "To provide loans to companies",
            "To act as an agent of depository and provide services to investors",
            "To regulate stock exchanges",
            "To issue new securities"
        ],
        "correct": 1,
        "explanation": "A Depository Participant acts as an agent of the depository (NSDL/CDSL) and provides depository services to investors, including opening and maintaining demat accounts."
    }
]

# Chapter 2: Market Participants - 20 Questions
CHAPTER_2_QUESTIONS = [
    {
        "id": "c2q1",
        "question": "Who are Retail Individual Investors?",
        "options": [
            "Investors who invest more than Rs. 10 lakhs",
            "Individual investors who apply for securities worth not more than Rs. 2 lakhs",
            "Only institutional investors",
            "Foreign investors"
        ],
        "correct": 1,
        "explanation": "Retail Individual Investors are individual investors (Resident Indians, NRIs, HUF) who apply or bid for securities for a value of not more than Rs. 2 lakhs."
    },
    {
        "id": "c2q2",
        "question": "What does FPI stand for?",
        "options": [
            "Foreign Portfolio Investor",
            "Financial Product Institution",
            "Future Portfolio Investment",
            "Fixed Portfolio Income"
        ],
        "correct": 0,
        "explanation": "FPI stands for Foreign Portfolio Investor, which is an entity established or incorporated outside India that proposes to make investments in India."
    },
    {
        "id": "c2q3",
        "question": "Which of the following is a Category I FPI?",
        "options": [
            "Individual investors",
            "Government and government-related investors",
            "Family offices",
            "Corporate bodies"
        ],
        "correct": 1,
        "explanation": "Category I FPIs include government and government-related investors such as central banks, sovereign wealth funds, pension funds, and appropriately regulated entities."
    },
    {
        "id": "c2q4",
        "question": "What is the minimum net worth requirement for accredited investors (individuals)?",
        "options": [
            "Rs. 5 crores",
            "Rs. 7.5 crores (with at least Rs. 3.75 crores in financial assets)",
            "Rs. 10 crores",
            "Rs. 1 crore"
        ],
        "correct": 1,
        "explanation": "For individuals to be accredited investors, they need a net worth of at least Rs. 7.5 crores, out of which at least Rs. 3.75 crores should be in the form of financial assets."
    },
    {
        "id": "c2q5",
        "question": "What is the main role of a market maker?",
        "options": [
            "To provide investment advice",
            "To provide two-way quotes to ensure liquidity",
            "To audit company accounts",
            "To issue securities"
        ],
        "correct": 1,
        "explanation": "Market makers provide liquidity by offering two-way (buy and sell) quotes on a continuous basis with reasonable bid-ask spreads."
    },
    {
        "id": "c2q6",
        "question": "What are GDRs?",
        "options": [
            "Government Debt Receipts",
            "Global Depository Receipts",
            "General Dividend Returns",
            "Guaranteed Deposit Rates"
        ],
        "correct": 1,
        "explanation": "Global Depository Receipts (GDRs) are negotiable instruments issued by a foreign depository bank representing shares of a foreign company's stock, generally traded on European exchanges."
    },
    {
        "id": "c2q7",
        "question": "Which regulation governs the issuance of capital by companies?",
        "options": [
            "SEBI (Stock Brokers) Regulations, 1992",
            "SEBI (Issue of Capital and Disclosure Requirements) Regulations, 2018",
            "Companies Act, 1956",
            "SCRA, 1956"
        ],
        "correct": 1,
        "explanation": "SEBI (ICDR) Regulations, 2018 lays down conditions for capital market issuances including public and rights issues, preferential issues, and QIPs."
    },
    {
        "id": "c2q8",
        "question": "What is novation in the context of clearing corporations?",
        "options": [
            "Creating new securities",
            "The act of clearing corporation becoming counterparty to both sides of every trade",
            "Cancelling trades",
            "Matching orders"
        ],
        "correct": 1,
        "explanation": "Novation is the process where the clearing corporation interposes itself between both parties of every trade, becoming the legal counterparty to both buyer and seller."
    },
    {
        "id": "c2q9",
        "question": "Which of these is NOT a function of stock exchanges?",
        "options": [
            "Providing trading platform",
            "Listing of securities",
            "Granting loans to companies",
            "Investor education"
        ],
        "correct": 2,
        "explanation": "Stock exchanges provide trading platforms, listing services, investor education, and surveillance, but they do not grant loans to companies."
    },
    {
        "id": "c2q10",
        "question": "What is a Professional Clearing Member (PCM)?",
        "options": [
            "A member with only trading rights",
            "A member with only clearing rights",
            "A member with both trading and clearing rights",
            "A member who provides loans"
        ],
        "correct": 1,
        "explanation": "Professional Clearing Members have only clearing rights and do not have trading rights. They clear and settle trades executed by trading members."
    },
    {
        "id": "c2q11",
        "question": "What is the minimum age requirement for individual trading membership?",
        "options": [
            "18 years",
            "21 years",
            "25 years",
            "30 years"
        ],
        "correct": 1,
        "explanation": "The minimum age requirement for individual trading membership is 21 years as per Securities Contracts (Regulation) Rules, 1957."
    },
    {
        "id": "c2q12",
        "question": "What is an Authorized Person in the context of stock broking?",
        "options": [
            "A member of stock exchange",
            "A person appointed by stock broker to provide access to trading platform",
            "A SEBI official",
            "A clearing member"
        ],
        "correct": 1,
        "explanation": "An Authorized Person is appointed by a stock broker and provides access to the trading platform of a stock exchange as an agent of the stock broker."
    },
    {
        "id": "c2q13",
        "question": "What is the primary function of a custodian?",
        "options": [
            "To execute trades",
            "To safeguard securities and maintain client accounts",
            "To provide market data",
            "To issue securities"
        ],
        "correct": 1,
        "explanation": "A custodian is responsible for safeguarding securities, maintaining clients' securities accounts, and keeping track of corporate actions on behalf of clients."
    },
    {
        "id": "c2q14",
        "question": "Which Act defines 'Securities' in India?",
        "options": [
            "SEBI Act, 1992",
            "Securities Contract Regulation Act (SCRA), 1956",
            "Companies Act, 2013",
            "Depositories Act, 1996"
        ],
        "correct": 1,
        "explanation": "The Securities Contract Regulation Act (SCRA), 1956 defines 'Securities' and includes shares, bonds, debentures, derivatives, and other instruments."
    },
    {
        "id": "c2q15",
        "question": "What does 'fit and proper person' criteria consider?",
        "options": [
            "Only financial capability",
            "Integrity, reputation, competence, and absence of convictions",
            "Only educational qualifications",
            "Only work experience"
        ],
        "correct": 1,
        "explanation": "'Fit and proper person' criteria considers integrity, reputation, character, competence including financial solvency, and absence of convictions and categorization as wilful defaulter."
    },
    {
        "id": "c2q16",
        "question": "What is insider trading?",
        "options": [
            "Trading by company employees",
            "Trading based on unpublished price sensitive information",
            "Trading in large volumes",
            "Trading after market hours"
        ],
        "correct": 1,
        "explanation": "Insider trading is dealing in securities based on unpublished price sensitive information (UPSI) that is not available to the public, which is prohibited by SEBI regulations."
    },
    {
        "id": "c2q17",
        "question": "What is the purpose of the Prevention of Money Laundering Act (PMLA), 2002?",
        "options": [
            "To regulate stock exchanges",
            "To prevent money laundering and provide for confiscation of property",
            "To control inflation",
            "To manage foreign exchange"
        ],
        "correct": 1,
        "explanation": "PMLA, 2002 aims to prevent money laundering, provide for confiscation of property derived from money laundering, and deal with matters connected thereto."
    },
    {
        "id": "c2q18",
        "question": "How long must reporting entities maintain records under PMLA?",
        "options": [
            "2 years",
            "5 years",
            "7 years",
            "10 years"
        ],
        "correct": 1,
        "explanation": "Under PMLA, reporting entities must maintain records for a period of 5 years from the date of transaction or from the end of business relationship, whichever is later."
    },
    {
        "id": "c2q19",
        "question": "What is 'front running'?",
        "options": [
            "Running a race",
            "Using non-public information to trade ahead of substantial orders",
            "Trading in the morning session",
            "Leading market trends"
        ],
        "correct": 1,
        "explanation": "Front running is the illegal practice of using non-public information to buy or sell securities ahead of a substantial order, anticipating price changes when the information becomes public."
    },
    {
        "id": "c2q20",
        "question": "What is 'dabba trading'?",
        "options": [
            "Trading in boxes",
            "Illegal trading in securities outside stock exchange mechanism",
            "Trading in large quantities",
            "Online trading"
        ],
        "correct": 1,
        "explanation": "Dabba trading refers to illegal trading in securities carried out outside the stock exchange mechanism by unregistered persons, typically settled by paying/receiving differences without actual delivery."
    }
]

# Initialize session state
if 'current_chapter' not in st.session_state:
    st.session_state.current_chapter = None
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'attempted' not in st.session_state:
    st.session_state.attempted = 0
if 'wrong_questions' not in st.session_state:
    st.session_state.wrong_questions = []
if 'shuffled_questions' not in st.session_state:
    st.session_state.shuffled_questions = []
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'selected_answer' not in st.session_state:
    st.session_state.selected_answer = None
if 'show_explanation' not in st.session_state:
    st.session_state.show_explanation = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'negative_marking' not in st.session_state:
    st.session_state.negative_marking = False
if 'test_mode' not in st.session_state:
    st.session_state.test_mode = None

# Motivational messages
CORRECT_MESSAGES = [
    "🎉 Excellent! You're mastering this!",
    "💪 Outstanding! Keep it up!",
    "🌟 Perfect! You're on fire!",
    "🚀 Brilliant! You got it right!",
    "⭐ Superb! You're doing great!"
]

WRONG_MESSAGES = [
    "📚 Don't worry! We'll revisit this.",
    "💡 Good try! Let's learn from this.",
    "🎯 Close! You'll get it next time.",
    "📖 Keep going! Practice makes perfect.",
    "🔄 We'll see this again soon!"
]

# Sidebar
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🎯 NISM Series-VII</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Securities Operations & Risk Management</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Negative marking option
    st.session_state.negative_marking = st.checkbox("Enable Negative Marking (-0.25)", value=st.session_state.negative_marking)
    
    st.markdown("---")
    st.subheader("📊 Your Progress")
    if st.session_state.current_chapter:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Score", f"{st.session_state.score}")
        with col2:
            st.metric("Attempted", f"{st.session_state.attempted}")
        
        if st.session_state.attempted > 0:
            accuracy = (st.session_state.score / st.session_state.attempted) * 100
            st.metric("Accuracy", f"{accuracy:.1f}%")

# Main content
st.markdown("<h1 class='main-header'>NISM Series-VII MCQ Practice</h1>", unsafe_allow_html=True)

# Home page - Chapter selection
if st.session_state.current_chapter is None:
    st.markdown("### Welcome! Choose a chapter to begin your preparation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📘 Chapter 1: Introduction to Securities Market", use_container_width=True):
            st.session_state.current_chapter = 1
            st.session_state.shuffled_questions = random.sample(CHAPTER_1_QUESTIONS, len(CHAPTER_1_QUESTIONS))
            st.session_state.current_question_index = 0
            st.session_state.score = 0
            st.session_state.attempted = 0
            st.session_state.wrong_questions = []
            st.session_state.start_time = datetime.now()
            st.rerun()
    
    with col2:
        if st.button("👥 Chapter 2: Market Participants", use_container_width=True):
            st.session_state.current_chapter = 2
            st.session_state.shuffled_questions = random.sample(CHAPTER_2_QUESTIONS, len(CHAPTER_2_QUESTIONS))
            st.session_state.current_question_index = 0
            st.session_state.score = 0
            st.session_state.attempted = 0
            st.session_state.wrong_questions = []
            st.session_state.start_time = datetime.now()
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎓 Features")
    st.markdown("""
    - ✅ 20 questions per chapter
    - 🔄 Wrong questions appear again for revision
    - 📊 Real-time progress tracking
    - ⏱️ Time tracking
    - 💯 Detailed explanations
    - 🎯 Optional negative marking
    """)

# Question display and handling
elif st.session_state.current_chapter is not None:
    # Check if we need to add wrong questions back
    if st.session_state.current_question_index >= len(st.session_state.shuffled_questions) and st.session_state.wrong_questions:
        # Add wrong questions back randomly
        for q in st.session_state.wrong_questions:
            insert_pos = random.randint(st.session_state.current_question_index, 
                                       st.session_state.current_question_index + 3)
            st.session_state.shuffled_questions.insert(min(insert_pos, len(st.session_state.shuffled_questions)), q)
        st.session_state.wrong_questions = []
    
    # Check if quiz is complete
    if st.session_state.current_question_index >= len(st.session_state.shuffled_questions):
        st.balloons()
        st.markdown("## 🎊 Chapter Complete!")
        
        elapsed_time = datetime.now() - st.session_state.start_time
        minutes = int(elapsed_time.total_seconds() // 60)
        seconds = int(elapsed_time.total_seconds() % 60)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Final Score", f"{st.session_state.score}/{st.session_state.attempted}")
        with col2:
            accuracy = (st.session_state.score / st.session_state.attempted * 100) if st.session_state.attempted > 0 else 0
            st.metric("Accuracy", f"{accuracy:.1f}%")
        with col3:
            st.metric("Time Taken", f"{minutes}m {seconds}s")
        
        if accuracy >= 80:
            st.success("🌟 Excellent Performance! You're ready for the next chapter!")
        elif accuracy >= 60:
            st.info("👍 Good job! Review the concepts and try again for better score.")
        else:
            st.warning("📚 Keep practicing! Review the chapter material before attempting again.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retry This Chapter", use_container_width=True):
                st.session_state.current_chapter = st.session_state.current_chapter
                questions = CHAPTER_1_QUESTIONS if st.session_state.current_chapter == 1 else CHAPTER_2_QUESTIONS
                st.session_state.shuffled_questions = random.sample(questions, len(questions))
                st.session_state.current_question_index = 0
                st.session_state.score = 0
                st.session_state.attempted = 0
                st.session_state.wrong_questions = []
                st.session_state.answered = False
                st.session_state.show_explanation = False
                st.session_state.start_time = datetime.now()
                st.rerun()
        
        with col2:
            if st.button("🏠 Back to Home", use_container_width=True):
                st.session_state.current_chapter = None
                st.session_state.current_question_index = 0
                st.session_state.score = 0
                st.session_state.attempted = 0
                st.session_state.wrong_questions = []
                st.session_state.shuffled_questions = []
                st.session_state.answered = False
                st.session_state.show_explanation = False
                st.rerun()
    else:
        # Display current question
        current_q = st.session_state.shuffled_questions[st.session_state.current_question_index]
        
        # Timer display
        if st.session_state.start_time:
            elapsed_time = datetime.now() - st.session_state.start_time
            minutes = int(elapsed_time.total_seconds() // 60)
            seconds = int(elapsed_time.total_seconds() % 60)
            st.markdown(f"<div class='timer-box'>⏱️ Time: {minutes:02d}:{seconds:02d}</div>", unsafe_allow_html=True)
        
        # Progress bar
        progress = (st.session_state.current_question_index) / len(st.session_state.shuffled_questions)
        st.progress(progress)
        st.markdown(f"**Question {st.session_state.current_question_index + 1} of {len(st.session_state.shuffled_questions)}**")
        
        # Chapter badge
        chapter_name = "Introduction to Securities Market" if st.session_state.current_chapter == 1 else "Market Participants"
        st.markdown(f"<span class='chapter-badge'>Chapter {st.session_state.current_chapter}: {chapter_name}</span>", unsafe_allow_html=True)
        
        # Question
        st.markdown(f"<div class='question-box'><h3>{current_q['question']}</h3></div>", unsafe_allow_html=True)
        
        # Options
        if not st.session_state.answered:
            selected_option = st.radio(
                "Select your answer:",
                options=range(len(current_q['options'])),
                format_func=lambda x: current_q['options'][x],
                key=f"q_{current_q['id']}"
            )
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("✅ Submit Answer", use_container_width=True):
                    st.session_state.selected_answer = selected_option
                    st.session_state.answered = True
                    st.session_state.attempted += 1
                    
                    if selected_option == current_q['correct']:
                        st.session_state.score += 1
                        st.session_state.show_explanation = True
                    else:
                        if st.session_state.negative_marking:
                            st.session_state.score -= 0.25
                        # Add to wrong questions for retry
                        st.session_state.wrong_questions.append(current_q)
                        st.session_state.show_explanation = True
                    st.rerun()
            
            with col2:
                if st.button("⏭️ Skip", use_container_width=True):
                    st.session_state.current_question_index += 1
                    st.session_state.answered = False
                    st.session_state.show_explanation = False
                    st.rerun()
        else:
            # Show result
            if st.session_state.selected_answer == current_q['correct']:
                st.markdown(f"<div class='success-box'>{random.choice(CORRECT_MESSAGES)}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='error-box'>{random.choice(WRONG_MESSAGES)}</div>", unsafe_allow_html=True)
            
            # Show options with correct/incorrect marking
            for idx, option in enumerate(current_q['options']):
                if idx == current_q['correct']:
                    st.success(f"✅ {option} (Correct Answer)")
                elif idx == st.session_state.selected_answer and idx != current_q['correct']:
                    st.error(f"❌ {option} (Your Answer)")
                else:
                    st.info(f"• {option}")
            
            # Show explanation
            if st.session_state.show_explanation:
                with st.expander("📖 Explanation", expanded=True):
                    st.write(current_q['explanation'])
            
            # Next button
            if st.button("➡️ Next Question", use_container_width=True, type="primary"):
                st.session_state.current_question_index += 1
                st.session_state.answered = False
                st.session_state.show_explanation = False
                st.session_state.selected_answer = None
                st.rerun()
        
        # Back to home button
        st.markdown("---")
        if st.button("🏠 Exit to Home"):
            if st.confirm("Are you sure you want to exit? Your progress will be lost."):
                st.session_state.current_chapter = None
                st.session_state.current_question_index = 0
                st.session_state.score = 0
                st.session_state.attempted = 0
                st.session_state.wrong_questions = []
                st.session_state.shuffled_questions = []
                st.session_state.answered = False
                st.session_state.show_explanation = False
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>📚 NISM Series-VII: Securities Operations and Risk Management</p>
    <p>Practice thoroughly • Review concepts • Master the exam</p>
    <p style='font-size: 0.8rem;'>Based on official NISM workbook - June 2025 version</p>
</div>
""", unsafe_allow_html=True)
