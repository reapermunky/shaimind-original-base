import streamlit as st
from personality_manager import load_personality
from emotion_manager import update_emotional_state, apply_decision_heuristics
from main import generate_persona_response
import os

# Load available personalities
identities_folder = "identities"
personalities = {
    filename.replace(".json", ""): load_personality(os.path.join(identities_folder, filename))
    for filename in os.listdir(identities_folder) if filename.endswith(".json")
}

# Debugging step: Print loaded personalities
print("Loaded Personalities:", list(personalities.keys()))

# Streamlit UI Setup
st.set_page_config(page_title="ShaiMind AI", layout="centered")

st.title("🤖 ShaiMind - AI Personalities")
st.subheader("Talk to historical figures like Edgar Allan Poe and Nikola Tesla.")

# Ensure session state variables are initialized
if "selected_persona" not in st.session_state:
    st.session_state.selected_persona = list(personalities.keys())[0]  # Default to first personality

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [{"role": "system", "content": personalities[st.session_state.selected_persona].system_prompt}]

if "last_response" not in st.session_state:
    st.session_state.last_response = ""

# Dropdown for personality selection
selected_persona = st.selectbox("Choose a personality:", list(personalities.keys()), index=list(personalities.keys()).index(st.session_state.selected_persona))

# Reset conversation history when changing personality
if selected_persona != st.session_state.selected_persona:
    st.session_state.selected_persona = selected_persona
    st.session_state.conversation_history = [{"role": "system", "content": personalities[selected_persona].system_prompt}]
    st.session_state.last_response = ""

# Load selected personality
personality_state = personalities[selected_persona]

# Display Persona Info
st.markdown(f"**Talking to:** {personality_state.name}")
st.write(f"🧠 Traits: {personality_state.traits}")
st.write(f"💭 Current Mood: {personality_state.emotional_state} (Intensity: {personality_state.emotional_intensity})")

# Use an empty container to hold the latest AI response (so it updates without refreshing)
response_container = st.empty()

# Function to clean response output
def extract_final_response(raw_text):
    """
    Extract only the final response from AI output, removing internal thought processing.
    """
    if "RESPONSE:" in raw_text:
        return raw_text.split("RESPONSE:")[-1].strip()
    return raw_text.strip()

# Form to allow sending messages on Enter
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", key="user_input")
    submitted = st.form_submit_button("Send")  # Pressing Enter submits this form

if submitted and user_input:
    # Process emotion & decision heuristics
    heuristic_response = apply_decision_heuristics(personality_state, user_input)
    if heuristic_response:
        response_text = heuristic_response
    else:
        update_emotional_state(personality_state, user_input)  # Update emotion before response
        response_text = generate_persona_response(personality_state, user_input, st.session_state.conversation_history)
        response_text = extract_final_response(response_text)  # Strip internal thoughts


    # Store conversation history
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    st.session_state.conversation_history.append({"role": "assistant", "content": response_text})

    # Display the cleaned response
    response_text = extract_final_response(response_text)  # Fix thought process issue
    st.session_state.last_response = response_text
    response_container.success(f"💬 {personality_state.name}: {response_text}")

# Conversation History Section (Remains Below Input Box)
st.subheader("📜 Conversation History")
for message in st.session_state.conversation_history:
    if message["role"] == "user":
        st.write(f"**You:** {message['content']}")
    elif message["role"] == "assistant":
        st.write(f"**{personality_state.name}:** {message['content']}")
