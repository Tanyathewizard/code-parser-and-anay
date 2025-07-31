
from agent import create_agents
import sys
import os
import subprocess

def main():
    print("🔧 AutoGen Code Analyzer using Gemini")
    print("Supports Python, Java, C++, JavaScript...\n")

    # Ask for language
    language = input("Enter the programming language (or type 'exit' to quit): ").strip()
    if language.lower() == "exit":
        print(" Program exited by user.")
        sys.exit()

    if not language:
        print(" No language provided.")
        sys.exit()

    # Get user code
    print("Paste your code (type END to finish or EXIT to cancel):")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        elif line.strip().upper() == "EXIT":
            print(" Program exited by user.")
            sys.exit()
        lines.append(line)

    user_code = "\n".join(lines).strip()
    if not user_code:
        print("No code provided.")
        return

    # Choose save folder
    save_dir = input(" Enter folder path to save analysis (Press Enter for current folder): ").strip()
    if not save_dir:
        save_dir = os.getcwd()  # Default to current working directory

    os.makedirs(save_dir, exist_ok=True)  # Create folder if it doesn't exist

    # Create agents
    user_proxy, analyzer = create_agents()

    # Start chat
    print("\n Analyzing your code...\n")
    response = user_proxy.initiate_chat(
        recipient=analyzer,
        message=f"{language}||CODE||{user_code}",
        max_turns=1
    )

    # Extract result content safely
    content = ""
    if isinstance(response, dict) and "content" in response:
        content = response["content"]
    elif hasattr(response, "chat_history"):
        last_message = response.chat_history.get(analyzer.name, [])
        if last_message:
            content = last_message[-1].get("content", "")

    if content:
        file_path = os.path.join(save_dir, "analysis_result.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(" Analysis complete!")
        print(f" Saved to: {file_path}\n")
        print("------ ANALYSIS PREVIEW ------")
        print(content[:1000])  # show first 1000 chars in terminal

        # Automatically open file in Notepad
        try:
            subprocess.run(["notepad.exe", file_path])
        except Exception as e:
            print(f"Could not open file automatically: {e}")
    else:
        print(" No response received from analyzer.")

if __name__ == "__main__":
    main()



