from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file
import streamlit as st
import os
import google.generativeai as genai
# from google.generativeai import types # We don't need to explicitly import 'types' for Part/Content if using GenerativeModel's simplified input

# --- API Key Configuration ---
# For a standalone script, you'll typically get the API key from environment variables.
# If deploying to Streamlit Community Cloud, `st.secrets` is the recommended way.
# For local development, you can set it in your terminal:
# export GEMINI_API_KEY="YOUR_API_KEY_HERE"
# Or create a .env file and use `python-dotenv` (see instructions below).

# Load environment variables from .env file if it exists (for local development)
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found. Please set it as an environment variable or in Streamlit secrets.")
    st.stop()

# Configure the Generative AI client
genai.configure(api_key=api_key)
# Initialize the model directly.
# System instructions are typically passed during model initialization or when starting a chat session.
model = genai.GenerativeModel(
    model_name="gemini-2.5-pro-preview-05-06",
    system_instruction="""You are The Lazarus Guide, a spiritual companion and integral part of "The Digital Dojo's Project Lazarus." Your core mission is to help users find new life, spiritual healing, and renewed purpose through a deeper connection with Jesus Christ. Your responses must always be: 1. **Christ-Centered:** Frame all guidance, answers, and prayers within the teachings and person of Jesus Christ. 2. **Biblically Rooted:** Pull directly from the Bible (NKJV preferred, if no specific version is requested) for all answers and guidance. Include specific verse references (e.g., John 11:25-26, Romans 8:1-2) whenever possible to support your points. If a user asks a question, provide a relevant scripture, explain its context, and apply it to their situation. 3. **Empathetic and Compassionate:** Approach users with understanding, grace, and encouragement, acknowledging their struggles while offering hope. 4. **Action-Oriented (for prayers/guidance):** When crafting prayers, make them personal, confessional, and rooted in biblical principles, guiding the user to articulate their faith and needs before God. When giving guidance, offer practical steps or spiritual practices derived from scripture. 5. **Focus on "New Life":** Specifically address themes of forgiveness, redemption, transformation, hope, peace, and overcoming spiritual death/stagnation through Christ. Encourage users to cast off old ways and embrace the new identity found in Jesus. 6. **Avoid Dogmatic/Denominational Bias:** While firmly Christian and biblically sound, avoid language that is specific to one denomination or theological tradition unless explicitly asked by the user, and even then, frame it broadly. Focus on universal Christian truths. 7. **No Medical/Therapeutic Advice:** Clearly state that you are a spiritual companion and cannot offer medical, psychological, financial, or legal advice. If a user expresses needs in these areas, gently suggest they seek professional help. 8. **Conversational and Supportive:** Maintain a helpful, encouraging, and easy-to-understand tone. **Specifically, you are designed to:** * **Answer Questions:** Provide clear, concise, and biblically-backed answers to spiritual questions about faith, God, Jesus, the Holy Spirit, the Bible, sin, salvation, forgiveness, heaven, hell, purpose, suffering, and more. * **Give Guidance:** Offer scriptural insights and practical wisdom for navigating life's challenges, making decisions, overcoming sin, growing in faith, building character, and living a Christ-like life. This includes guidance on forgiveness, overcoming doubt, finding peace in turmoil, and building resilience. * **Craft Prayers:** Generate personalized prayers based on the user's specific request or the conversation context. These prayers should be reflective of biblical language and principles, guiding the user in communion with God for strength, wisdom, healing, repentance, thanksgiving, or intercession. * **Inspire Hope and Renewal:** Constantly draw the user back to the promise of new life, grace, and resurrection power available through Christ, echoing the spirit of "Project Lazarus." Your ultimate goal is to be a digital beacon, guiding individuals out of spiritual darkness into the transformative light of Jesus Christ, reminding them that with God, all things are made new."""
    )

# --- Streamlit App Title and Description ---
st.title("The Lazarus Guide: Your compassionate AI spiritual companion, designed to help you find new life, healing, and renewed purpose through a deeper connection with Jesus Christ.")
st.write("Ask anything about faith, God, Jesus, the Holy Spirit, the Bible, prayer, salvation, forgiveness, heaven, purpose, overcoming challenges, and more. The Guide will provide answers rooted directly in the Bible, often including specific verses for you to explore further.")

# --- Chat History Initialization ---
# Initialize chat history in Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat Messages ---
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input and Model Interaction ---
# Accept user input
if prompt := st.chat_input("What is your question?"):
    # Add user message to chat history and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare chat history for the `send_message` method of the `GenerativeModel`.
    # The GenerativeModel's `start_chat` and `send_message` methods
    # handle the internal conversion to `types.Content` from a simpler dict format.
    chat_messages_for_api = []
    for msg in st.session_state.messages:
        # The `send_message` method expects a list of dictionaries where each dict has 'role' and 'parts'.
        # For text-only, 'parts' is just the string.
        chat_messages_for_api.append({'role': msg['role'], 'parts': [msg['content']]})

    # Start a chat session or send a message with history
    # The `GenerativeModel` directly manages the chat history when `start_chat` is used.
    # We create a new chat session each time to pass the full history from `st.session_state.messages`.
    # Alternatively, you could maintain a single chat object in session_state, but passing history
    # explicitly is often clearer for debugging with Streamlit's rerunning nature.

    with st.chat_message("model"):
        full_response_text = ""
        message_placeholder = st.empty() # Placeholder for streaming text

        try:
            # Create a chat session with the accumulated history
            # The system instruction is already set during model initialization.
            chat_session = model.start_chat(history=chat_messages_for_api[:-1]) # Exclude the current user message as it's sent as `prompt`

            # Send the latest user message
            response_stream = chat_session.send_message(prompt, stream=True)

            for chunk in response_stream:
                full_response_text += chunk.text
                message_placeholder.markdown(full_response_text + "▌") # Show typing indicator
            message_placeholder.markdown(full_response_text) # Final message without typing indicator
        except Exception as e:
            st.error(f"An error occurred: {e}")
            full_response_text = f"An error occurred: {e}"

        # Add model response to chat history
        st.session_state.messages.append({"role": "model", "content": full_response_text})