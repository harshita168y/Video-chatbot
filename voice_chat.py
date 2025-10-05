from modules.speech import stt, tts
from modules.nlp.assistant import assistant  # your existing assistant class

def main():
    print("=== Voice Chatbot ===")
    print("Say 'exit' to quit.")

    while True:
        # Listen to user
        print("Listening...")
        user_text = stt.listen()  # returns recognized text
        if not user_text:
            continue

        print(f"You said: {user_text}")

        if user_text.lower() in ["exit", "quit"]:
            break

        # Send text to your model via assistant.py
        reply = assistant.chat(user_text)  # use your existing assistant.chat() method
        print(f"Model: {reply}")

        # Speak the response
        tts.speak(reply)


if __name__ == "__main__":
    main()
