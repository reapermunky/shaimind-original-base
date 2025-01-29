import os
import openai
from dotenv import load_dotenv
from personality_manager import load_personality
from emotion_manager import update_emotional_state, apply_decision_heuristics

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_persona_response(personality_state, user_input, conversation_history):
    """
    Generate a concise, personality-driven response based on reasoning style, emotional state, and conversation history.
    """
    try:
        internal_reasoning_prompt = f"""
        INTERNAL THOUGHT PROCESS (not shown to user):
        You are {personality_state.name}. Think as they would:
        - Interpret the user's message.
        - Reflect on your current mood: {personality_state.emotional_state} (Intensity: {personality_state.emotional_intensity}).
        - Anchor your response in: {', '.join(personality_state.anchors)}.
        - Keep responses **concise** while preserving your personality and depth.
        """
        user_prompt = f"""
        USER MESSAGE: {user_input}
        Respond in a way that reflects {personality_state.name}'s speech patterns and emotional tone.
        Keep responses **brief but impactful**.
        """
        messages = [{"role": "system", "content": internal_reasoning_prompt}] + conversation_history + [{"role": "user", "content": user_prompt}]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.75,
            max_tokens=150,  # Reduced from 300 for brevity
            top_p=0.9,
            frequency_penalty=0.3,
            presence_penalty=0.5
        )

        # Extract response and enforce an additional word cap
        ai_response = response["choices"][0]["message"]["content"]
        return ' '.join(ai_response.split()[:75])  # Final hard limit of ~75 words

    except Exception as e:
        return f"I seem to have encountered an error in my thoughts: {e}"

def main():
    identities_folder = "identities"
    personalities = {
        filename.replace(".json", ""): load_personality(os.path.join(identities_folder, filename))
        for filename in os.listdir(identities_folder) if filename.endswith(".json")
    }

    print("Welcome to ShaiMind!")
    print("Available personalities:")
    for i, personality_name in enumerate(personalities.keys(), 1):
        print(f"{i}. {personality_name}")

    choice = int(input("Select a personality by number: "))
    selected_personality = list(personalities.values())[choice - 1]

    print(f"\nYou have selected: {selected_personality.name}.")
    print("Enter your messages below (type 'exit' to quit).\n")

    conversation_history = [{"role": "system", "content": selected_personality.system_prompt}]

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            heuristic_response = apply_decision_heuristics(selected_personality, user_input)
            if heuristic_response:
                print(f"\n{selected_personality.name} AI:\n{heuristic_response}\n")
                continue

            conversation_history.append({"role": "user", "content": user_input})
            update_emotional_state(selected_personality, user_input)
            assistant_reply = generate_persona_response(selected_personality, user_input, conversation_history)
            conversation_history.append({"role": "assistant", "content": assistant_reply})

            print(f"\n{selected_personality.name} AI:\n{assistant_reply}\n")
        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    main()
