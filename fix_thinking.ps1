import re
with open(r"D:\neon_unified\neon_architect.py", "r", encoding="utf-8") as f:
    content = f.read()

# Update thinking_effort to high and allow medium/high thinking
content = content.replace('"thinking_effort": "low"', '"thinking_effort": "high"')
content = content.replace('"allow_medium_high_thinking": False', '"allow_medium_high_thinking": True')

with open(r"D:\neon_unified\neon_architect.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
