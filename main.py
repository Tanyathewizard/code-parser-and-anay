# main.py
import os
import sys
import subprocess
from agent import create_agents   # this will return: user_proxy, analyzer, semantic


def main():
    print("\n🔧 AutoGen Code Analyzer using Gemini\n")

    language = input("Enter programming language (or 'exit'): ").strip()
    if language.lower() == "exit":
        sys.exit("👋 Program exited.")

    print("\nPaste your code (type END to finish):")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)

    user_code = "\n".join(lines).strip()
    if not user_code:
        print("⚠️ No code entered.")
        return

    save_dir = input("\nEnter save folder (Enter = current): ").strip() or os.getcwd()
    os.makedirs(save_dir, exist_ok=True)

    # -----------------------------
    # Load all agents
    # -----------------------------
    user_proxy, analyzer, semantic = create_agents()

    # -----------------------------
    # 1️⃣ PARSER + ANALYZER RUN
    # -----------------------------
    print("\n🧠 Analyzing code (Parser + Analyzer)…")

    response = user_proxy.initiate_chat(
        recipient=analyzer,
        message=f"{language}||CODE||{user_code}",
        max_turns=1
    )

    analyzer_output = ""
    if isinstance(response, dict):
        analyzer_output = response.get("content", "")

    analyzer_file = os.path.join(save_dir, "analysis_result.txt")
    with open(analyzer_file, "w", encoding="utf-8") as f:
        f.write(analyzer_output)

    print(f"✅ Analyzer output saved to {analyzer_file}")

    # -----------------------------
    # 2️⃣ SEMANTIC EXTRACTOR RUN
    # -----------------------------
    print("\n🧩 Running Semantic Extractor…")

    semantic_response = user_proxy.initiate_chat(
        recipient=semantic,
        message=f"{language}||SEMANTICS||{user_code}",
        max_turns=1
    )

    semantic_output = ""
    if isinstance(semantic_response, dict):
        semantic_output = semantic_response.get("content", "")

    semantic_file = os.path.join(save_dir, "semantic_result.txt")
    with open(semantic_file, "w", encoding="utf-8") as f:
        f.write(semantic_output)

    print(f"✅ Semantic output saved to {semantic_file}")

    # -----------------------------
    # AUTO OPEN BOTH
    # -----------------------------
    try:
        subprocess.run(["notepad.exe", analyzer_file])
        subprocess.run(["notepad.exe", semantic_file])
    except:
        print("ℹ️ Could not auto-open Notepad.")

    print("\n🎉 All tasks completed successfully!")


if __name__ == "__main__":
    main()
