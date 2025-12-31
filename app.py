import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="CareerForge AI", page_icon="🚀", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    .stButton>button {width: 100%; border-radius: 5px; height: 3em; background-color: #4285F4; color: white;}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR & API SETUP ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Google_Gemini_logo.svg/2560px-Google_Gemini_logo.svg.png", width=150)
    st.title("CareerForge AI 🚀")
    api_key_input = st.text_input("Gemini API Key", type="password")
    
    # CLEAN THE KEY (Removes accidental spaces)
    api_key = api_key_input.strip() if api_key_input else None

    if api_key:
        st.success("Key Accepted")
        genai.configure(api_key=api_key)
    else:
        st.warning("Enter API Key to start")

# --- HELPER FUNCTION TO HANDLE MODELS ---
def get_gemini_response(model_name, prompt, chat_history=None):
    try:
        model = genai.GenerativeModel(model_name)
        if chat_history:
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(prompt)
            return response.text, chat
        else:
            response = model.generate_content(prompt)
            return response.text, None
    except Exception as e:
        # If the specific model fails, try to list available ones to help debug
        st.error(f"Error with model '{model_name}': {e}")
        try:
            st.write("Trying to fetch available models for your key...")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    st.code(f"Available Model: {m.name}")
        except:
            st.error("Could not list models. Please check your API Key.")
        return None, None

# --- SESSION STATE ---
if "analysis_result" not in st.session_state: st.session_state.analysis_result = None
if "curriculum" not in st.session_state: st.session_state.curriculum = None
if "messages" not in st.session_state: st.session_state.messages = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- MAIN APP ---
st.title("Build the Future: CareerForge AI")
tab1, tab2, tab3 = st.tabs(["1️⃣ Skill Gap Analysis", "2️⃣ Curriculum Architect", "3️⃣ Interview Simulator"])

# --- TAB 1: ANALYST ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        current_role = st.text_area("Current Profile", height=150, placeholder="E.g., Marketing Manager...")
    with col2:
        target_role = st.text_input("Target Job", placeholder="E.g., Python Developer")
    
    if st.button("🚀 Run Gap Analysis") and api_key:
        prompt = f"""Act as a Career Analyst. User: {current_role}. Target: {target_role}. 
        Identify 3 transferable skills, 3 missing skills, and a match score (0-100%)."""
        
        # WE USE 'gemini-2.5-flash' AS IT IS MOST STABLE
        response, _ = get_gemini_response('gemini-2.5-flash', prompt)
        if response:
            st.session_state.analysis_result = response
            st.rerun()

    if st.session_state.analysis_result:
        st.markdown(st.session_state.analysis_result)

# --- TAB 2: ARCHITECT ---
with tab2:
    if st.button("Generate Learning Path") and st.session_state.analysis_result:
        prompt = f"""Based on: {st.session_state.analysis_result}. 
        Create a 4-Week Study Plan. Week 1: Basics. Week 2: Deep Dive. Week 3: Project. Week 4: Interview Prep."""
        
        response, _ = get_gemini_response('gemini-2.5-flash', prompt)
        if response:
            st.session_state.curriculum = response
            st.rerun()
            
    if st.session_state.curriculum:
        st.markdown(st.session_state.curriculum)

# --- TAB 3: SIMULATOR ---
with tab3:
    st.caption("AI Interviewer Active")
    
    # Initial Start
    if st.session_state.curriculum and len(st.session_state.messages) == 0:
        start_prompt = f"""You are a Recruiter. The candidate wants to be a {target_role}. 
        Ask one tough interview question based on this gap analysis: {st.session_state.analysis_result}."""
        
        response, chat_obj = get_gemini_response('gemini-2.5-flash', start_prompt, [])
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})
            # Save history format for Gemini
            st.session_state.chat_history.append({"role": "user", "parts": [start_prompt]})
            st.session_state.chat_history.append({"role": "model", "parts": [response]})

    # Chat Interface
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Your answer..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Prepare history for API
        current_history = st.session_state.chat_history
        
        response, _ = get_gemini_response('gemini-2.5-flash', prompt, current_history)
        
        if response:
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.chat_history.append({"role": "user", "parts": [prompt]})
            st.session_state.chat_history.append({"role": "model", "parts": [response]})