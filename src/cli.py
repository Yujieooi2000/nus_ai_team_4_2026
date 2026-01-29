import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from orchestrator import Orchestrator

def main():
    print("Initializing AI Customer Support System...")
    orchestrator = Orchestrator()
    print("System Ready! (Type '/exit' to quit, '/stats' for system insights)")
    print("-" * 50)

    while True:
        try:
            user_input = input("\nUser: ").strip()
            
            if not user_input:
                continue

            if user_input.lower() == '/exit':
                print("Shutting down system. Goodbye!")
                break
            
            if user_input.lower() == '/stats':
                insights = orchestrator.get_system_insights()
                print("\n[System Insights]")
                for key, value in insights.items():
                    print(f"  {key}: {value}")
                continue

            # Process the Request
            result = orchestrator.process_request(user_input)
            
            # Display Output
            print("\n[AI System Response]")
            print(f"  Handled by: {result['agent']}")
            print(f"  Classification: {result['analysis']['category'].upper()} (Priority: {result['analysis']['priority'].upper()})")
            print(f"  Explanation: {result['analysis']['explanation']}")
            print(f"  Response: {result['response']['message']}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
