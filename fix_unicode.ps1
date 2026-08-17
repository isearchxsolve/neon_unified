import re
with open(r"D:\neon_unified\sdlc_wrapper_full.py", "r", encoding="utf-8") as f:
    content = f.read()

replacements = {
    "\u2192": "->", "\u2713": "[OK]", "\u2717": "[FAIL]",
    "\u2014": "--", "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2022": "*", "\u25cf": "*", "\u25a1": "[]", "\u2500": "=", "\u2502": "|",
    "\u250c": "+", "\u2510": "+", "\u2514": "+", "\u2518": "+", "\u251c": "+",
    "\u2524": "+", "\u252c": "+", "\u2534": "+", "\u253c": "+"
}
for k, v in replacements.items():
    content = content.replace(k, v)

with open(r"D:\neon_unified\sdlc_wrapper_full.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
