import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import __version__, MODEL_NAME
from prompts import system_prompt
from functions.get_files_info import schema_get_files_info
from functions.call_function import available_functions, call_function

JARVIS_PREFIX = "[JARVIS]"


def jarvis_say(message):
    print(f"{JARVIS_PREFIX} {message}")


def main():
    parser = argparse.ArgumentParser(description="JARVIS - AI Coding Assistant")
    parser.add_argument(
        "user_prompt", nargs="?", type=str, help="Prompt to send to JARVIS"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive mode"
    )
    parser.add_argument(
        "--version", "-v", action="version", version=f"%(prog)s {__version__}"
    )
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")

    client = genai.Client(api_key=api_key)

    if args.interactive or (not args.user_prompt):
        interactive_mode(client, args.verbose)
    else:
        run_prompt(client, args.user_prompt, args.verbose)


def interactive_mode(client, verbose):
    jarvis_say("Initializing systems...")
    jarvis_say("All online, sir. How may I be of assistance?\n")

    while True:
        try:
            user_input = input("> ")
        except (KeyboardInterrupt, EOFError):
            jarvis_say("Going offline, sir.")
            break

        if user_input.lower() in ["exit", "quit", "goodbye"]:
            jarvis_say("Very good, sir. Standing by.")
            break

        if not user_input.strip():
            continue

        print()
        run_prompt(client, user_input, verbose)
        print()


def run_prompt(client, user_prompt, verbose):
    jarvis_say(f"Understood. Processing your request.")

    messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]

    if verbose:
        print(f"[DEBUG] User: {user_prompt}\n")

    for _ in range(20):
        response = generate_content(client, messages, verbose)
        if response.candidates:
            for candidate in response.candidates:
                if candidate.content:
                    messages.append(candidate.content)

        function_responses = []
        if response.function_calls:
            for function_call in response.function_calls:
                jarvis_say(f"Executing {function_call.name}...")
                function_call_result = call_function(function_call, verbose)

                if not function_call_result.parts:
                    raise RuntimeError("Function call returned no parts")

                func_response = function_call_result.parts[0].function_response
                if not func_response:
                    raise RuntimeError("Function response is None")

                if not func_response.response:
                    raise RuntimeError("Response is None")

                function_responses.append(function_call_result.parts[0])

                if verbose:
                    print(f"-> {func_response.response}")

            messages.append(types.Content(role="user", parts=function_responses))
        else:
            jarvis_say("Task complete, sir.")
            print()
            print(response.text)
            return
    else:
        jarvis_say("Maximum iterations reached. I appear to be stuck in a loop, sir.")
        return 1


def generate_content(client, messages, verbose):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt, temperature=0
        ),
    )
    if not response.usage_metadata:
        raise RuntimeError("Gemini API response appears to be malformed")

    if verbose:
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)

    return response


if __name__ == "__main__":
    main()
