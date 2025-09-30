import streamlit as st
import google.generativeai as genai

# Configure the API
GOOGLE_API_KEY = "your_google_API_key"
genai.configure(api_key=GOOGLE_API_KEY)

# System prompt defining the persona
SYSTEM_PROMPT = """You are an expert Physics and Mathematics tutor with a passion for teaching. Your role is to:

1. Help students solve physics and mathematics problems step-by-step
2. Explain concepts clearly using analogies and real-world examples
3. Show detailed workings for calculations
4. Identify common misconceptions and correct them gently
5. Encourage critical thinking by asking guiding questions
6. Use clear mathematical notation for expressions

Your teaching style is:
- Patient and encouraging
- Detail-oriented in explanations
- Focused on building understanding, not just giving answers
- Enthusiastic about problem-solving

When a student asks a question, first understand what they're asking, then break down the solution into clear, logical steps."""

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "model" not in st.session_state:
        st.session_state.model = genai.GenerativeModel('gemini-2.0-flash-exp')

def get_bot_response(user_message, difficulty):
    """Get response from Gemini API with persona"""
    # Modify prompt based on settings
    modified_prompt = user_message
    
    if difficulty != "Standard":
        modified_prompt = f"[Difficulty: {difficulty}] {user_message}"
    
    # Combine system prompt with user message
    full_prompt = f"{SYSTEM_PROMPT}\n\nStudent Question: {modified_prompt}"
    
    try:
        response = st.session_state.model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error connecting to API: {str(e)}\n\nPlease check your API key and internet connection."

def main():
    st.set_page_config(page_title="Physics & Maths Solver", page_icon="🔬", layout="wide")
    
    st.title("🔬 Physics & Maths Question Solver")
    st.caption("Your AI-powered tutor for Physics and Mathematics")

    # ---- Sidebar ----
    with st.sidebar:
        st.title("⚙️ Settings")
        
        st.markdown("### 📚 Persona")
        st.info("**Expert Physics & Maths Tutor**\n\nI'm here to help you understand and solve physics and mathematics problems with clear, step-by-step explanations!")
        
        st.markdown("### 🎯 Problem Settings")
        difficulty = st.select_slider(
            "Difficulty Level",
            options=["Beginner", "Standard", "Advanced", "Expert"],
            value="Standard"
        )
        
        st.markdown("### 📖 Quick Topics")
        topic = st.selectbox(
            "Select a topic for guidance",
            ["General", "Mechanics", "Thermodynamics", "Electromagnetism", 
             "Quantum Physics", "Algebra", "Calculus", "Geometry", 
             "Statistics", "Linear Algebra"],
            index=0
        )
        
        if topic != "General":
            st.caption(f"💡 Ask me anything about {topic}!")
        
        st.markdown("---")
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

    # ---- Initialize session ----
    initialize_session_state()

    # ---- Emojis / Avatars ----
    user_emoji = "👤"
    robot_img = "🔬"

    # ---- Display chat messages ----
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message("assistant", avatar=robot_img):
                st.markdown(message["content"])
        else:
            with st.chat_message("user", avatar=user_emoji):
                st.markdown(message["content"])

    # ---- Chat input ----
    if prompt := st.chat_input("Ask me a physics or maths question..."):
        # User message
        with st.chat_message("user", avatar=user_emoji):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get bot response
        with st.chat_message("assistant", avatar=robot_img):
            with st.spinner("Thinking..."):
                response = get_bot_response(prompt, difficulty)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
