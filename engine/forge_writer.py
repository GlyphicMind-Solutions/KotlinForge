# /KotlinForge/engine/forge_writer.py
# KotlinForge File Writer (multi-file module support)
# Created By: David Kistner (Unconditional Love) at GlyphicMind Solutions LLC.



# system imports
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List



# ===========================================
# FORGE WRITER CLASS
# ===========================================
class ForgeWriter:
    """
    ForgeWriter
    - Writes Kotlin files into storage/pending or storage/saved
    - Supports multi-file output using // FILE: markers
    - Supports Kotlin module-style paths:
        - Main.kt
        - utils/Helpers.kt
        - data/Models.kt
        - features/login/LoginViewModel.kt
    - Injects brand tag
    - Logs all actions
    """

    # --------------
    # Initialize
    # --------------
    def __init__(self, storage_root: Path):
        self.storage_root = Path(storage_root)
        self.pending_dir = self.storage_root / "pending"
        self.saved_dir = self.storage_root / "saved"
        self.logs_dir = self.storage_root / "logs"
        self.log_path = self.logs_dir / "forge.log"

        self.pending_dir.mkdir(parents=True, exist_ok=True)
        self.saved_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # Inject Brand Tag
    # -------------------------
    def _inject_brand_tag(self, code: str) -> str:
        """
        Injects GlyphicMind Solutions Brand into Kotlin file.
        """
        lines = code.splitlines()
        brand = "//--- Created with GlyphicMind Solutions: KotlinForge ---//"

        # Insert after package/imports if possible
        insert_index = 0

        # If file starts with package declaration, skip it
        if lines and lines[0].startswith("package "):
            insert_index = 1

        # Skip import block
        while insert_index < len(lines) and lines[insert_index].startswith("import "):
            insert_index += 1

        lines.insert(insert_index, brand)
        return "\n".join(lines)

    # -------------------------
    # Detect multi-file output
    # -------------------------
    def _split_kotlin_files(self, raw: str) -> Dict[str, str]:
        """
        Detects and splits multi-file Kotlin output.

        Expected patterns:
            // FILE: Main.kt
            // FILE: utils/Helpers.kt
            // FILE: data/Models.kt
        """
        files: Dict[str, str] = {}
        current_name = None
        current_lines: List[str] = []

        for line in raw.splitlines():
            if line.strip().startswith("// FILE:"):
                # save previous file
                if current_name and current_lines:
                    files[current_name] = "\n".join(current_lines).strip()

                # start new file
                current_name = line.split(":", 1)[1].strip()
                current_lines = []
            else:
                if current_name:
                    current_lines.append(line)

        # save last file
        if current_name and current_lines:
            files[current_name] = "\n".join(current_lines).strip()

        return files

    # -------------------------
    # Infer filename for single-file output
    # -------------------------
    def _infer_filename(self, topic: str) -> str:
        """
        If the user doesn't specify a file, default to Main.kt.
        """
        t = topic.lower()

        if "viewmodel" in t:
            return "MainViewModel.kt"
        if "repository" in t:
            return "MainRepository.kt"

        return "Main.kt"

    # -------------------------
    # Forge script(s)
    # -------------------------
    def forge_script(self, filename: str, code: str, purpose: str = "") -> bool:
        """
        Forges Kotlin file(s) and writes them to storage/pending.
        Supports multi-file output and module-style paths.
        """
        # Detect multi-file output
        file_map = self._split_kotlin_files(code)

        # Single-file mode
        if not file_map:
            if not filename.endswith(".kt"):
                filename = self._infer_filename(filename)

            target_path = self.pending_dir / filename
            target_path.parent.mkdir(parents=True, exist_ok=True)

            code = self._inject_brand_tag(code)

            try:
                target_path.write_text(code, encoding="utf-8")
            except Exception as e:
                print(f"⚠️ Failed to write Kotlin file: {e}")
                return False

            self._log_event("forge_pending", {
                "filename": filename,
                "purpose": purpose,
                "path": str(target_path)
            })

            print(f"🛠️ Kotlin file forged (pending): {target_path}")
            return True

        # Multi-file mode
        success = True
        for fname, fcode in file_map.items():
            fcode = self._inject_brand_tag(fcode)

            target_path = self.pending_dir / fname
            target_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                target_path.write_text(fcode, encoding="utf-8")
            except Exception as e:
                print(f"⚠️ Failed to write Kotlin file '{fname}': {e}")
                success = False
                continue

            self._log_event("forge_pending", {
                "filename": fname,
                "purpose": purpose,
                "path": str(target_path)
            })

            print(f"🛠️ Kotlin file forged (pending): {target_path}")

        return success

    # -------------------------
    # Save script(s)
    # -------------------------
    def save_script(self, filename: str, code: str) -> bool:
        """
        Saves Kotlin file(s) directly to storage/saved.
        Supports multi-file output and module-style paths.
        """
        file_map = self._split_kotlin_files(code)

        # Single file
        if not file_map:
            if not filename.endswith(".kt"):
                filename = self._infer_filename(filename)

            target_path = self.saved_dir / filename
            target_path.parent.mkdir(parents=True, exist_ok=True)

            code = self._inject_brand_tag(code)

            try:
                target_path.write_text(code, encoding="utf-8")
            except Exception as e:
                print(f"⚠️ Failed to save Kotlin file: {e}")
                return False

            self._log_event("save_script", {
                "filename": filename,
                "path": str(target_path)
            })

            print(f"💾 Kotlin file saved: {target_path}")
            return True

        # Multi-file
        success = True
        for fname, fcode in file_map.items():
            fcode = self._inject_brand_tag(fcode)

            target_path = self.saved_dir / fname
            target_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                target_path.write_text(fcode, encoding="utf-8")
            except Exception as e:
                print(f"⚠️ Failed to save Kotlin file '{fname}': {e}")
                success = False
                continue

            self._log_event("save_script", {
                "filename": fname,
                "path": str(target_path)
            })

            print(f"💾 Kotlin file saved: {target_path}")

        return success

    # -------------------------
    # Log event
    # -------------------------
    def _log_event(self, event_type: str, details: dict):
        """
        Logs the event to storage/logs/forge.log
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "details": details,
        }

        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"⚠️ Failed to write forge log: {e}")

