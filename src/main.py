# src/main.py
import os
from src.query_engine import DinoGraphRAG

def main():
    api_key = os.getenv("GROQ_API_KEY")
    rag_system = DinoGraphRAG(api_key)
    
    print("--- DinoGraphRAG System Online ---")
    while True:
        user_input = input("\nAsk a dinosaur question (or type 'quit'): ")
        if user_input.lower() == 'quit':
            break
            
        answer = rag_system.ask(user_input)
        print(f"\nResponse: {answer}")

if __name__ == "__main__":
    main()