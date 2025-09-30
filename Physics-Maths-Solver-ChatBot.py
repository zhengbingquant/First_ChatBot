# Physics & Maths Question Solver – An AI-powered chatbot for solving physics and math problems
# Copyright (C) 2025  zhengbingquant
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import streamlit as st
import google.generativeai as genai
import pyttsx3
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import tempfile
import os
import requests

# Configure the API
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
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

When a student asks a question, first understand what they're asking, then break down the solution into clear, logical steps.

If the user asks for diagrams or graphs, provide detailed descriptions of what should be plotted or drawn."""

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "model" not in st.session_state:
        # Use gemini-2.0-flash-exp (correct model name)
        st.session_state.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    if "vision_model" not in st.session_state:
        st.session_state.vision_model = genai.GenerativeModel('gemini-2.0-flash-exp')
    if "last_generated_image" not in st.session_state:
        st.session_state.last_generated_image = None
    if "last_generated_graph" not in st.session_state:
        st.session_state.last_generated_graph = None

def text_to_speech(text):
    """Convert text to speech with robust error handling"""
    try:
        # Remove markdown formatting for better speech
        clean_text = text.replace('**', '').replace('*', '').replace('#', '').replace('`', '')
        
        # Limit text length to avoid very long audio
        if len(clean_text) > 1000:
            clean_text = clean_text[:1000] + "... response truncated for audio."
        
        # Initialize pyttsx3 engine
        engine = pyttsx3.init()
        
        # Set much faster speed (2x faster)
        engine.setProperty('rate', 440)  # 2x speed (was 220)
        
        # Create a unique temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_filename = tmp_file.name
        
        # Generate speech
        engine.save_to_file(clean_text, tmp_filename)
        engine.runAndWait()
        engine.stop()
        
        # Wait a moment for file to be written
        import time
        time.sleep(0.1)
        
        # Read the file
        if os.path.exists(tmp_filename):
            with open(tmp_filename, 'rb') as audio_file:
                audio_bytes = audio_file.read()
            
            # Clean up
            try:
                os.unlink(tmp_filename)
            except:
                pass
            
            return audio_bytes
        else:
            raise Exception("Audio file was not created")
        
    except Exception as e:
        # Fallback to gTTS if pyttsx3 fails
        try:
            from gtts import gTTS
            clean_text = text.replace('**', '').replace('*', '').replace('#', '')
            if len(clean_text) > 1000:
                clean_text = clean_text[:1000]
            
            tts = gTTS(text=clean_text, lang='en', slow=False)
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer.getvalue()
        except Exception as e2:
            return None

def generate_image_with_api(prompt):
    """Generate images using multiple free APIs with fallback options"""
    try:
        # Clean the prompt
        clean_prompt = prompt.replace('\n', ' ').strip()
        
        # Try multiple APIs in order of quality
        apis = [
            {
                "name": "Hugging Face (Stable Diffusion XL)",
                "url": "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "data": {"inputs": clean_prompt}
            },
            {
                "name": "Hugging Face (Stable Diffusion 2.1)",
                "url": "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "data": {"inputs": clean_prompt}
            },
            {
                "name": "Segmind Stable Diffusion",
                "url": "https://api.segmind.com/v1/sd2.1-txt2img",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "data": {
                    "prompt": clean_prompt,
                    "negative_prompt": "blurry, low quality, distorted, ugly, bad anatomy",
                    "samples": 1,
                    "scheduler": "UniPC",
                    "num_inference_steps": 25,
                    "guidance_scale": 7.5,
                    "seed": -1,
                    "img_width": 768,
                    "img_height": 768,
                    "base64": False
                }
            },
            {
                "name": "Prodia AI (Realistic)",
                "url": f"https://image.prodia.ai/generate?prompt={requests.utils.quote(clean_prompt)}&model=realisticVisionV51_v51VAE.safetensors",
                "method": "GET"
            },
            {
                "name": "Pollinations AI (Flux)",
                "url": f"https://image.pollinations.ai/prompt/{requests.utils.quote(clean_prompt)}",
                "params": {
                    "width": 1024,
                    "height": 1024,
                    "model": "flux",
                    "nologo": "true",
                    "enhance": "true"
                },
                "method": "GET"
            }
        ]
        
        for api in apis:
            try:
                with st.spinner(f"🎨 Generating with {api['name']}..."):
                    if api["method"] == "GET":
                        # Build URL with parameters
                        url = api["url"]
                        if "params" in api:
                            params_str = "&".join([f"{k}={v}" for k, v in api["params"].items()])
                            url = f"{url}?{params_str}"
                        
                        response = requests.get(url, timeout=90)
                    else:
                        response = requests.post(
                            api["url"],
                            headers=api.get("headers", {}),
                            json=api.get("data", {}),
                            timeout=90
                        )
                    
                    if response.status_code == 200:
                        try:
                            image = Image.open(BytesIO(response.content))
                            st.success(f"✅ Image generated successfully using {api['name']}!")
                            return image
                        except:
                            st.warning(f"⚠️ {api['name']} returned invalid image, trying next option...")
                            continue
                    else:
                        st.warning(f"⚠️ {api['name']} returned status {response.status_code}, trying next option...")
            except requests.Timeout:
                st.warning(f"⚠️ {api['name']} timed out, trying next option...")
                continue
            except Exception as e:
                st.warning(f"⚠️ {api['name']} failed: {str(e)[:50]}... Trying next option...")
                continue
        
        st.error("❌ All image generation attempts failed. Please try again later or rephrase your prompt.")
        return None
        
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

def generate_graph_with_ai(user_prompt):
    """Use AI to generate Python code for creating graphs/diagrams"""
    try:
        code_prompt = f"""Generate Python code using matplotlib to create a diagram/graph for: {user_prompt}

Requirements:
- Use matplotlib.pyplot as plt and numpy as np
- Create a clear, educational diagram
- Include labels, title, and legend where appropriate
- Use plt.figure(figsize=(10, 6))
- Don't use plt.show(), just create the figure
- Return only the Python code, no explanations
- The code should be executable as-is

Example format:
```python
import matplotlib.pyplot as plt
import numpy as np

plt.figure(figsize=(10, 6))
# your plotting code here
plt.title('Title')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.grid(True)
plt.legend()
```
"""
        
        response = st.session_state.model.generate_content(code_prompt)
        code = response.text
        
        # Extract code from markdown if present
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
        
        return code.strip()
    except Exception as e:
        st.error(f"Error generating graph code: {str(e)}")
        return None

def execute_graph_code(code):
    """Execute the AI-generated matplotlib code safely"""
    try:
        # Create a new figure
        fig = plt.figure(figsize=(10, 6))
        
        # Execute the code
        exec_globals = {'plt': plt, 'np': np, 'fig': fig}
        exec(code, exec_globals)
        
        # Save to buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        st.error(f"Error executing graph code: {str(e)}")
        plt.close()
        return None

def process_uploaded_image(uploaded_file):
    """Process uploaded image and analyze it"""
    try:
        image = Image.open(uploaded_file)
        
        # Use vision model to analyze the image
        response = st.session_state.vision_model.generate_content([
            "Analyze this image. If it contains a physics or mathematics problem, extract and describe it in detail. If it contains diagrams or graphs, describe what you see. Be specific about equations, numbers, and diagrams.",
            image
        ])
        
        return response.text, image
    except Exception as e:
        return f"Error processing image: {str(e)}", None

def get_bot_response(user_message, difficulty, uploaded_image=None):
    """Get response from Gemini API with persona"""
    # Modify prompt based on settings
    modified_prompt = user_message
    
    if difficulty != "Standard":
        modified_prompt = f"[Difficulty: {difficulty}] {user_message}"
    
    # Combine system prompt with user message
    full_prompt = f"{SYSTEM_PROMPT}\n\nStudent Question: {modified_prompt}"
    
    try:
        if uploaded_image:
            # Use vision model for image analysis
            response = st.session_state.vision_model.generate_content([full_prompt, uploaded_image])
        else:
            response = st.session_state.model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error connecting to API: {str(e)}\n\nPlease check your API key and internet connection."

def main():
    st.set_page_config(page_title="Physics & Maths Solver", page_icon="🔬", layout="wide")

    # ---- Sidebar ----
    with st.sidebar:
        st.title("🔬 Physics & Maths Question Solver")
        st.caption("Your AI-powered tutor for Physics and Mathematics")
        
        st.markdown("---")
        
        st.markdown("### 📚 Persona")
        st.info("**Expert Physics & Maths Tutor**\n\nI'm here to help you understand and solve physics and mathematics problems with clear, step-by-step explanations!")
        
        st.markdown("---")
        
        # Collapsible Settings Section
        with st.expander("⚙️ Settings", expanded=False):
            st.markdown("### 🎯 Problem Settings")
            difficulty = st.select_slider(
                "Difficulty Level",
                options=["Beginner", "Standard", "Advanced", "Expert"],
                value="Standard"
            )
            
            st.markdown("### 🎨 Image Generation")
            enable_image_gen = st.checkbox("Enable AI Image Generation", value=True)
            if enable_image_gen:
                st.caption("💡 Ask me to 'draw', 'create an image of', or 'show me a picture of...'")
            
            st.markdown("### 📊 Graph Generation")
            enable_graphs = st.checkbox("Enable Math/Physics Graphs", value=True)
            if enable_graphs:
                st.caption("💡 Ask me to 'plot', 'graph' mathematical functions!")
            
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
    
    # ---- FIXED CSS for bottom prompt bar with icons inline ----
    st.markdown("""
        <style>
        /* Ensure main content has padding at bottom for fixed input */
        .main .block-container {
            padding-bottom: 120px !important;
        }
        
        /* Make sure file uploader appears above the fixed container */
        .stFileUploader {
            margin-bottom: 0.5rem !important;
        }
        
        /* Fix the chat input at bottom */
        section[data-testid="stChatFloatingInputContainer"] {
            position: fixed !important;
            bottom: 0 !important;
            left: var(--sidebar-width, 21rem) !important;
            right: 0 !important;
            background: #1e1e1e !important;
            padding: 0.75rem 1rem !important;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.3) !important;
            z-index: 999999 !important;
            border-top: 1px solid #333 !important;
            margin: 0 !important;
        }
        
        /* Add left padding to chat input to make room for icons */
        section[data-testid="stChatFloatingInputContainer"] div[data-testid="stChatInput"] {
            margin-left: 120px !important;
        }
        
        /* Style the buttons to be more compact and match theme */
        div[data-testid="stHorizontalBlock"]:has(button) button {
            border-radius: 8px !important;
            height: 45px !important;
            font-size: 1.2rem !important;
        }
        
        /* Style the checkbox container */
        div[data-testid="stHorizontalBlock"]:has(.stCheckbox) .stCheckbox {
            margin: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        /* Position the icon container as overlay on the left of chat input */
        div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stHorizontalBlock"] button):not(:has(div[data-testid="stChatInput"])) {
            position: fixed !important;
            bottom: 10px !important;
            left: calc(var(--sidebar-width, 21rem) + 10px) !important;
            z-index: 9999999 !important;
            width: 110px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # ---- Add greeting message if chat is empty ----
    if len(st.session_state.messages) == 0:
        with st.chat_message("assistant", avatar=robot_img):
            st.markdown("### Hello! 👋 How may I help you today?\n\nI'm your Physics & Mathematics tutor. Feel free to ask me any questions about physics or math problems, or request visualizations and diagrams!")

    # ---- Display chat messages ----
    for idx, message in enumerate(st.session_state.messages):
        if message["role"] == "assistant":
            with st.chat_message("assistant", avatar=robot_img):
                st.markdown(message["content"])
        else:
            with st.chat_message("user", avatar=user_emoji):
                st.markdown(message["content"])
                if "image" in message and message["image"] is not None:
                    st.image(message["image"], width=200)

    # Show file uploader when button is clicked
    if "show_uploader" not in st.session_state:
        st.session_state.show_uploader = False
        
    uploaded_file = None
    if st.session_state.show_uploader:
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], key="image_upload")
        if uploaded_file:
            st.success("✓ Image attached - you can now ask questions about it!")

    # ---- Control icons in fixed position above the chat input ----
    icon_container = st.container()
    with icon_container:
        col1, col2, col3 = st.columns([0.06, 0.06, 0.88])
        
        with col1:
            if st.button("📎", help="Upload image", key="upload_trigger", use_container_width=True):
                st.session_state.show_uploader = not st.session_state.show_uploader
                st.rerun()
        
        with col2:
            enable_tts = st.checkbox("🔊", value=True, key="tts_toggle", 
                                    help="Text-to-Speech", label_visibility="collapsed")
    
    # CSS to position icon container next to chat input
    st.markdown("""
        <style>
        /* Position the icon container as overlay on the left of chat input */
        div[data-testid="stVerticalBlock"] > div:has(div[data-testid="stHorizontalBlock"] button):not(:has(div[data-testid="stChatInput"])) {
            position: fixed !important;
            bottom: 10px !important;
            left: calc(var(--sidebar-width, 21rem) + 10px) !important;
            z-index: 9999999 !important;
            width: auto !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # ---- Chat input (stays at bottom) ----
    prompt = st.chat_input("Ask me a physics or maths question...")
    
    if prompt:
        # Check if user wants graph generation (math/physics)
        wants_graph = enable_graphs and any(keyword in prompt.lower() for keyword in 
                                            ["plot", "graph", "chart", "diagram of function"])
        
        # Check if user wants AI image generation (creative images)
        wants_image = enable_image_gen and any(keyword in prompt.lower() for keyword in 
                                               ["draw", "create image", "generate image", "show me", "picture of", "image of", "visualize"])
        
        # User message
        with st.chat_message("user", avatar=user_emoji):
            st.markdown(prompt)
        
        user_msg = {"role": "user", "content": prompt, "image": None}
        if uploaded_file:
            user_msg["image"] = uploaded_file
        st.session_state.messages.append(user_msg)

        # Get bot response
        with st.chat_message("assistant", avatar=robot_img):
            # If user wants image generation, skip Gemini response and go straight to image generation
            if wants_image and not wants_graph:
                response = "🎨 Generating your image..."
                st.markdown(response)
                
                # Generate AI image immediately
                st.markdown("---")
                generated_image = generate_image_with_api(prompt)
                if generated_image:
                    # Store in session state to persist after download
                    st.session_state.last_generated_image = generated_image
                    st.image(generated_image, caption="AI Generated Image", use_column_width=True)
                    
                    # Add download button for AI generated image
                    img_buffer = BytesIO()
                    generated_image.save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    st.download_button(
                        label="⬇️ Download Image",
                        data=img_buffer,
                        file_name="ai_generated_image.png",
                        mime="image/png",
                        key=f"download_img_{len(st.session_state.messages)}"
                    )
                    response = "🎨 Image generated successfully!"
                else:
                    response = "❌ Failed to generate image. Please try again with a different prompt."
            else:
                with st.spinner("Thinking..."):
                    # Handle image input if present
                    img_for_analysis = None
                    if uploaded_file:
                        img_for_analysis = Image.open(uploaded_file)
                    
                    response = get_bot_response(prompt, difficulty, img_for_analysis)
                    st.markdown(response)
                
            # Generate graph if requested (for math/physics)
            if wants_graph:
                st.markdown("---")
                st.markdown("**📊 Generated Visualization:**")
                code = generate_graph_with_ai(prompt)
                if code:
                    graph_buf = execute_graph_code(code)
                    if graph_buf:
                        # Store in session state to persist after download
                        st.session_state.last_generated_graph = graph_buf
                        st.image(graph_buf, caption="Generated Graph", use_column_width=True)
                        
                        # Add download button for graph
                        graph_buf.seek(0)
                        st.download_button(
                            label="⬇️ Download Graph",
                            data=graph_buf,
                            file_name="graph.png",
                            mime="image/png",
                            key=f"download_graph_{len(st.session_state.messages)}"
                        )
                        
                        with st.expander("📝 View Python Code"):
                            st.code(code, language="python")
            
            # Generate audio if TTS is enabled (auto-play with hidden player) - only for non-image requests
            if enable_tts and not wants_image:
                audio_bytes = text_to_speech(response)
                if audio_bytes:
                    # Convert audio bytes to base64 for HTML embedding
                    import base64
                    audio_base64 = base64.b64encode(audio_bytes).decode()
                    
                    # Create hidden audio player that auto-plays
                    audio_html = f"""
                    <audio autoplay style="display: none;">
                        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                    </audio>
                    """
                    st.markdown(audio_html, unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
