import os
import sys
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types 
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file
from functions.call_function import call_function

def main():
    load_dotenv()

    verbose = "--verbose" in sys.argv
    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python3 main.py <"prompt"> [--verbose]')
        print('Example: python main.py "How do I fix the calculator?"')
        sys.exit(1)
    
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    Always use tools to inspect files before answering. Do not ask the user to provide files
    """
    prompt = " ".join(args)

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,

        ]   
    )
    
    if verbose:
        print(f"User prompt: {prompt}\n")

    messages =[
        types.Content(role="user", parts=[types.Part(text=prompt)])
    ]

    iterations = 0 
    max_iterations = 20
    while True:
        iterations +=1
        if iterations > max_iterations:
            print( f"Maximum iterations ({max_iterations}) reached")
            sys.exit(1)
        
        try:
            final_response = generate_content(client, messages, available_functions, system_prompt,  verbose)
            if final_response:
                print("Final response:")
                print(final_response)
                break

            time.sleep(0.4)
        except Exception as e:
            print(f"Error in generate_content: {e}")
            time.sleep(1.0)
    

def generate_content(client, messages, tools, system_instruction, verbose=False):
    
    for m in messages:
        if m.role not in ("user", "model"):
            raise ValueError(f"Invalid role found: {m.role}")

    response = client.models.generate_content(
        model="gemini-2.0-flash-001", 
        contents = messages,
        config=types.GenerateContentConfig(
            tools=[tools], 
            system_instruction=system_instruction)
    )       

    if verbose:
        
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    if response.candidates:
        for candidate in response.candidates:
            messages.append(
                types.Content(
                    role="model",
                    parts=candidate.content.parts
                )
            )
    if not response.function_calls:
        return response.text
    
    function_responses = []
    for function_call_part in response.function_calls:
        result_content = call_function(function_call_part, verbose=verbose)

        parts = result_content.parts

        if (
            not parts
            or not getattr(parts[0], "function_response", None)
            or parts[0].function_response.response is None
        ):
            raise RuntimeError("Missing function_response.response")

        if verbose:
            print(f"-> {parts[0].function_response.response}")
        function_responses.append(result_content.parts[0])
    if not function_responses:
        raise Exception("no function responses generated, exiting.")
    
    messages.append(types.Content(
        role="user",
        parts=function_responses
    ))

    return None

if __name__ == "__main__":
    main()