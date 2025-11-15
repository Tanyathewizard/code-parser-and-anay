# main.py
import os
import sys
import subprocess
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
from agent import create_agents

# ---------------------
# Helper Functions
# ---------------------

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


# ---------------------
# GUI Application
# ---------------------

class CodeAnalyzerGUI(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("system")        # light/dark
        ctk.set_default_color_theme("blue")      # theme

        self.title("AutoGen Code Analyzer (Gemini)")
        self.geometry("650x350")
        self.resizable(False, False)

        # Drag-drop file path
        self.file_path = None

        # UI Layout
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

        # Drag-Drop Frame
        self.drop_frame = ctk.CTkFrame(self, width=500, height=120, corner_radius=15)
        self.drop_frame.pack(pady=20)

        self.drop_label = ctk.CTkLabel(
            self.drop_frame,
            text="Drop file here",
            font=("Segoe UI", 14)
        )
        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")

        # Enable drag and drop
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind("<<Drop>>", self.on_file_drop)

        # Analyze Button
        self.analyze_btn = ctk.CTkButton(
            self,
            text="Analyze",
            width=180,
            height=40,
            command=self.run_analysis
        )
        self.analyze_btn.pack(pady=10)

    # ---------------------
    # Event Handlers
    # ---------------------

    def on_file_drop(self, event):
        path = event.data.strip("{}")
        if os.path.isfile(path):
            self.file_path = path
            self.drop_label.configure(text=f"Selected: {os.path.basename(path)}")
        else:
            self.drop_label.configure(text="Invalid file")

    # ---------------------
    # Analysis Logic
    # ---------------------

    def run_analysis(self):
        if not self.file_path:
            self.popup("Error", "Please drop a file first.")
            return

        # Read file
        try:
            code = read_file(self.file_path)
        except:
            self.popup("Error", "Could not read the file.")
            return

        language = detect_language_from_extension(self.file_path)

        # Load agents
        user_proxy, analyzer, semantic = create_agents()

        # ------------------ Analyzer ------------------
        response = user_proxy.initiate_chat(
            recipient=analyzer,
            message=f"{language}||CODE||{code}",
            max_turns=1
        )
        analyzer_output = response["content"] if isinstance(response, dict) else ""

        # ------------------ Semantic ------------------
        sem_response = user_proxy.initiate_chat(
            recipient=semantic,
            message=f"{language}||SEMANTICS||{code}",
            max_turns=1
        )
        semantic_output = sem_response["content"] if isinstance(sem_response, dict) else ""

        # Show results popup
        self.show_results(analyzer_output, semantic_output)

    # ---------------------
    # UI Popup Windows
    # ---------------------

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

        # Analyzer Output
        text1 = ctk.CTkTextbox(tab1, wrap="word")
        text1.pack(expand=True, fill="both", padx=10, pady=10)
        text1.insert("1.0", analyzer_output)

        # Semantic Output
        text2 = ctk.CTkTextbox(tab2, wrap="word")
        text2.pack(expand=True, fill="both", padx=10, pady=10)
        text2.insert("1.0", semantic_output)


# ---------------------
# Run App
# ---------------------
if __name__ == "__main__":
    app = CodeAnalyzerGUI()
    app.mainloop()
