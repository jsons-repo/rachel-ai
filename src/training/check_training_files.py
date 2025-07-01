import os
from glob import glob

PARENT_DIR = "/DATA"
TARGET_FILES = glob(f"{PARENT_DIR}/**/training_hf.jsonl", recursive=True)

BAD_SUBSTRINGS = ["print(", "RETURN"]  # Add more if needed

def check_file_for_bad_strings(filepath):
    bad_lines = []
    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if any(bad in line for bad in BAD_SUBSTRINGS):
                bad_lines.append((i, line.strip()))
    return bad_lines

print(f"🔍 Scanning {len(TARGET_FILES)} files...")

any_issues = False
for file_path in TARGET_FILES:
    issues = check_file_for_bad_strings(file_path)
    if issues:
        any_issues = True
        print(f"\n🚨 Found suspicious lines in: {file_path}")
        for line_num, content in issues:
            print(f"  [Line {line_num}] {content}")

if not any_issues:
    print("✅ No bad strings found in any training_hf.jsonl files.")
