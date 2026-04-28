# /KotlinForge/kotlinforge.py



#system imports
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication

#folder imports
from gui.kotlinforge_window import KotlinForgeWindow
from engine.llm_engine import LLMEngine



# --------------------
# Main
# --------------------
def main():
    app = QApplication(sys.argv)

    # Storage root
    storage_root = Path(__file__).parent / "storage"

    # Manifest path (required by LLMEngine)
    manifest_path = Path(__file__).parent / "models" / "manifest.yaml"

    # Initialize LLM engine with manifest
    llm = LLMEngine(manifest_path=manifest_path)

    # Launch window
    window = KotlinForgeWindow(llm_engine=llm, storage_root=storage_root)
    window.show()

    sys.exit(app.exec_())

# ---------------------------
# if name = main for window 
# ---------------------------
if __name__ == "__main__":
    main()

