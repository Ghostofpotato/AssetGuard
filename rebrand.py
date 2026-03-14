import os
import re

# ── Configuration ──────────────────────────────────────────────
ROOT_DIR = "."

REPLACEMENTS = [
    ("ASSETGUARD",  "ASSETGUARD"),
    ("AssetGuard",  "AssetGuard"),
    ("assetguard",  "assetguard"),
]

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}

TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".html", ".css", ".scss", ".less",
    ".yaml", ".yml", ".json", ".toml",
    ".conf", ".cfg", ".ini", ".env",
    ".md", ".rst", ".txt", ".sh",
    ".xml", ".gradle", ".cmake",
    ".Dockerfile", ".dockerignore",
    ".gitignore", ".gitattributes",
    "Makefile", "Dockerfile",
}

# ── Helpers ─────────────────────────────────────────────────────
def should_skip(path):
    parts = path.replace("\\", "/").split("/")
    return any(p in SKIP_DIRS for p in parts)

def replace_text(content):
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)
    return content

def rename_path(name):
    for old, new in REPLACEMENTS:
        name = name.replace(old, new)
    return name

# ── Step 1: Replace content inside files ────────────────────────
def rebrand_file_contents():
    changed = 0
    errors = 0
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR, topdown=True):
        # Skip unwanted dirs in-place
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            basename = os.path.basename(filename)

            if ext not in TEXT_EXTENSIONS and basename not in TEXT_EXTENSIONS:
                continue

            filepath = os.path.join(dirpath, filename)

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    original = f.read()

                updated = replace_text(original)

                if updated != original:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(updated)
                    print(f"  [CONTENT] {filepath}")
                    changed += 1

            except Exception as e:
                print(f"  [ERROR] {filepath} — {e}")
                errors += 1

    print(f"\n✅ Content rebranding done — {changed} files changed, {errors} errors")

# ── Step 2: Rename files and folders ────────────────────────────
def rebrand_file_names():
    renamed = 0
    # Walk bottom-up so we rename children before parents
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR, topdown=False):
        if should_skip(dirpath):
            continue

        # Rename files
        for filename in filenames:
            new_name = rename_path(filename)
            if new_name != filename:
                old = os.path.join(dirpath, filename)
                new = os.path.join(dirpath, new_name)
                os.rename(old, new)
                print(f"  [FILE]    {old} → {new}")
                renamed += 1

        # Rename the directory itself
        folder = os.path.basename(dirpath)
        new_folder = rename_path(folder)
        if new_folder != folder and dirpath != ROOT_DIR:
            parent = os.path.dirname(dirpath)
            old_dir = dirpath
            new_dir = os.path.join(parent, new_folder)
            os.rename(old_dir, new_dir)
            print(f"  [DIR]     {old_dir} → {new_dir}")
            renamed += 1

    print(f"\n✅ Rename rebranding done — {renamed} items renamed")

# ── Main ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Starting AssetGuard rebranding...\n")
    print("── Phase 1: Rebranding file contents ──")
    rebrand_file_contents()
    print("\n── Phase 2: Renaming files and folders ──")
    rebrand_file_names()
    print("\n🎉 Rebranding complete!")