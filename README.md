# ⭐ KotlinForge — Kotlin Code Forge
- Created By: David Kistner (Unconditional Love)  
- GlyphicMind Solutions LLC

## Overview
KotlinForge is a standalone Forge‑Suite tool designed to generate, refactor, analyze, and manage Kotlin code using an AI‑assisted workflow.
It follows the same tabbed IDE layout and workflow conventions as PythonForge, GoForge, RustForge, JavaForge, and the rest of the Forge ecosystem.

KotlinForge supports:
- Idiomatic Kotlin generation
- Multi‑file output using // FILE: markers
- Package‑structured Kotlin modules
- Deep Analysis v2 (chunk → summarize → meta‑summarize → reconstruct)
- Full GUI workflow with topic, corrections, raw output, extracted code, master code, and logs
- Pending/saved file management with brand‑tag injection
- Model‑family‑aware prompt building (GPT, Mistral, Qwen, DeepSeek, Phi, Llama)

---

## 🚀 Features
### 🔥 Local‑First LLM Execution
KotlinForge loads `.gguf` models defined in:
```
models/manifest.yaml

```

Supports:
- GPT‑OSS  
- Mistral  
- Llama  
- Qwen  
- DeepSeek  
- Phi  
- Any LocalAI‑compatible `.gguf` model  

---

### 🧠 Deep Analysis v2
KotlinForge includes the upgraded Deep Analysis engine:

- Splits large codebases into chunks  
- Summarizes each chunk  
- Produces a meta‑summary  
- Reconstructs/refactors the entire project  
- Logs every step in the Deep Analysis Log tab  

---

### 🧩 Multi‑File Go Module Output
KotlinForge automatically detects and writes multiple files when the model outputs:
```
// FILE: Main.kt
// FILE: utils/Helpers.kt
// FILE: data/Models.kt

```

---

### 📦 Go Module‑Aware Path Support
If the model outputs module‑structured paths, GoForge writes files exactly where they belong:
```
storage/pending/main.go
storage/pending/pkg/service.go
storage/pending/cmd/app/main.go
```

---

### 🖥️ Full GUI (PyQt5)

- Tabbed IDE layout:
   1. Topic / Corrections
   2. Raw LLM Output
   3. Extracted Code
   4. Master Code
   5. Deep Analysis Log

- Global controls:
   1. Generate
   2. Re‑run with Corrections
   3. Deep Analysis
   4. Open File
   5. Save File
   6. Forge → Pending
   7. Clear Session

---

### 🗂️ Storage System

JavaForge organizes output into:

```
storage/
    pending/   ← forged files awaiting review
    saved/     ← user‑saved files
    logs/      ← forge.log + deep analysis logs
```

---

## ⭐ Installation

1. Create a virtual environment

```
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies
```
pip install -r requirements.txt
```

3. Add your .gguf models
Place them in:
```
models/
```
Then update:
```
models/manifest.yaml
```

---

## ⭐ Running GoForge

In your terminal, or Command Prompt type in your directory:
```
python3 kotlinforge.py
```

---

### ⭐ Model Manifest Example
```
models:
  mistral_default:
    path: ./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf <--- you can change this to the directory of your model
    n_ctx: 32768
    template: mistral
```

---

# ⭐ Part of the GlyphicMind Forge Suite

JavaForge is one of many Forge tools:

1. ✅️ PythonForge

2. ✅️ JavaScriptForge

3. ✅️ CSharpForge

4. ✅️ CppForge

5. ✅️ JavaForge

6. ✅️ RustForge

7. ✅️ GoForge

8. ✅️ KotlinForge

9. HTML/CSS Forge

10. SQLForge

--All tools follow the same architecture, branding, and workflow.

---

### ⭐License

This project is part of the GlyphicMind Solutions ecosystem.
All rights reserved.
