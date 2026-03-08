from dotenv import load_dotenv
import os
from orchestrator import Orchestrator

def main():

    print("Initializing AI Customer Support System...")

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    orchestrator = Orchestrator(api_key)

    print("System Ready! (Type '/exit' to quit, '/stats' for system insights)")
    print("-" * 60)

    conversation_history = []

    while True:
        try:

            user_input = input("\nUser: ").strip()

            if not user_input:
                continue

            # Exit command
            if user_input.lower() == "/exit":
                print("Shutting down system. Goodbye!")
                break

            # Analytics command
            if user_input.lower() == "/stats":
                insights = orchestrator.get_system_insights()

                print("\n[System Insights]")
                for key, value in insights.items():
                    print(f"  {key}: {value}")

                continue

            # Process request
            result = orchestrator.process_request(
                user_input,
                conversation_history
            )

            response = result["response"]

            print("\n[AI System Response]")
            print(f"  Handled by: {result['agent']}")

            if "analysis" in result:
                print(
                    f"  Classification: "
                    f"{result['analysis']['category'].upper()} "
                    f"(Priority: {result['analysis']['priority'].upper()})"
                )
                print(f"  Explanation: {result['analysis']['explanation']}")

            print(f"  Response: {response['message']}")

            # Save history
            conversation_history.append(
                {"role": "user", "content": user_input}
            )

            conversation_history.append(
                {"role": "assistant", "content": response["message"]}
            )

        except KeyboardInterrupt:
            print("\nExiting...")
            break

        except Exception as e:
            print(f"\nSystem Error: {e}")


if __name__ == "__main__":
    main()