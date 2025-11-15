import os
import sys
import subprocess
import json
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
from agent import create_agents
def detect_language_from_extension(filename):
    ext = filename.split(".")[-1].lower()
    mapping = {
        "py": "Python",
        "cpp": "C++",
        "cc": "C++",
        "cxx": "C++",
        "js": "JavaScript",
        "ts": "TypeScript",
        "java": "Java",
        "rb": "Ruby",
        "go": "Go",
        "cs": "C#",
    }
    return mapping.get(ext, "Unknown")
def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
def extract_output(result):
    # result is ChatResult
    # 1. prefer summary if present
    if hasattr(result, "summary") and result.summary:
        return result.summary

    # 2. fallback: last message content
    try:
        return result.chat_history[-1].get("content", "")
    except:
        pass

    # last fallback: string
    return str(result)
def summarize_semantic_json(json_text):
    """
    Converts semantic JSON output into a formatted human-readable summary.
    """

    # Try to parse JSON
    try:
        data = json.loads(json_text)
    except Exception:
        return json_text  # Not JSON, return raw

    name = data.get("name", "Unknown")
    desc = data.get("description", "No description available.")
    inputs = data.get("inputs", [])
    outputs = data.get("outputs", [])
    complexity = data.get("complexity_estimate", "N/A")

    # Build human-readable summary
    summary = []
    summary.append(f"### {name}\n")
    summary.append(f"**Description:** {desc}\n")

    # Inputs
    if inputs:
        summary.append("\n#### Inputs:")
        for inp in inputs:
            summary.append(f"- **{inp.get('name')}** (*{inp.get('type')}*)")

    # Outputs
    if outputs:
        summary.append("\n#### Outputs:")
        for out in outputs:
            summary.append(f"- **{out.get('name')}** (*{out.get('type')}*)")

    # Complexity
    summary.append(f"\n#### Complexity Estimate: {complexity}")

    # Join everything
    return "\n".join(summary)
class CodeAnalyzerGUI(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("system")     
        ctk.set_default_color_theme("blue")  
        self.title("AutoGen Code Analyzer (Gemini)")
        self.geometry("650x350")
        self.resizable(False, False)
        self.file_path = None
        self.build_ui()
    def build_ui(self):
        title = ctk.CTkLabel(self, text="AutoGen Code Analyzer", font=("Segoe UI", 26, "bold"))
        title.pack(pady=20)
        subtitle = ctk.CTkLabel(
            self, 
            text="Drag & drop a code file below",
            font=("Segoe UI", 15)
        )
        subtitle.pack()
        self.drop_frame = ctk.CTkFrame(self, width=500, height=120, corner_radius=15)
        self.drop_frame.pack(pady=20)
        self.drop_label = ctk.CTkLabel(
            self.drop_frame,
            text="Drop file here",
            font=("Segoe UI", 14)
        )
        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind("<<Drop>>", self.on_file_drop)
        self.analyze_btn = ctk.CTkButton(
            self,
            text="Analyze",
            width=180,
            height=40,
            command=self.run_analysis
        )
        self.analyze_btn.pack(pady=10)
    def on_file_drop(self, event):
        path = event.data.strip("{}")
        if os.path.isfile(path):
            self.file_path = path
            self.drop_label.configure(text=f"Selected: {os.path.basename(path)}")
        else:
            self.drop_label.configure(text="Invalid file")
    def run_analysis(self):
        if not self.file_path:
            self.popup("Error", "Please drop a file first.")
            return
        try:
            code = read_file(self.file_path)
        except:
            self.popup("Error", "Could not read the file.")
            return
        language = detect_language_from_extension(self.file_path)
        user_proxy, analyzer, semantic = create_agents()
        # Analyzer output
        response = user_proxy.initiate_chat(
            recipient=analyzer,
            message=f"{language}||CODE||{code}",
            max_turns=1
        )
        analyzer_output = extract_output(response)

        # Semantic output
        sem_response = user_proxy.initiate_chat(
            recipient=semantic,
            message=f"{language}||SEMANTICS||{code}",
            max_turns=1
        )
        semantic_output = extract_output(sem_response)

        self.show_results(analyzer_output, semantic_output)
    def popup(self, title, msg):
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.geometry("350x200")
        label = ctk.CTkLabel(win, text=msg, font=("Segoe UI", 15))
        label.pack(pady=40)
        ctk.CTkButton(win, text="OK", command=win.destroy).pack()
    def show_results(self, analyzer_output, semantic_output):
        win = ctk.CTkToplevel(self)
        win.title("Analysis Results")
        win.geometry("900x600")
        tabs = ctk.CTkTabview(win, width=880, height=560)
        tabs.pack(padx=10, pady=10)
        tab1 = tabs.add("Analyzer Result")
        tab2 = tabs.add("Semantic Result")
        analyzer_output_str = str(analyzer_output)
        semantic_output_str = str(semantic_output)
        text1 = ctk.CTkTextbox(tab1, wrap="word")
        text1.pack(expand=True, fill="both", padx=10, pady=10)
        text1.insert("1.0", analyzer_output_str)
        text2 = ctk.CTkTextbox(tab2, wrap="word")
        text2.pack(expand=True, fill="both", padx=10, pady=10)
        semantic_output_clean = summarize_semantic_json(semantic_output_str)
        text2.insert("1.0", semantic_output_clean)

if __name__ == "__main__":
    app = CodeAnalyzerGUI()
    app.mainloop()