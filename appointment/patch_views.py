import os

with open("views.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

with open("replacements.py", "r", encoding="utf-8") as f:
    replacements_lines = f.readlines()

# Extract from replacements
reg_lines = []
ver_lines = []
res_lines = []

state = 0
for line in replacements_lines:
    if line.startswith("def register("): state = 1
    elif line.startswith("def verify_otp("): state = 2
    elif line.startswith("def resend_otp("): state = 3
    
    if state == 1: reg_lines.append(line)
    elif state == 2: ver_lines.append(line)
    elif state == 3: res_lines.append(line)

new_lines = []
if "import random\n" not in "".join(lines[:20]):
    new_lines.extend(["import random\n", "import string\n"])

in_register = False
in_verify = False
in_resend = False

i = 0
while i < len(lines):
    line = lines[i]
    if line.startswith("def register("):
        new_lines.extend(reg_lines)
        new_lines.append("\n")
        in_register = True
    elif line.startswith("def user_login("):
        in_register = False
    
    if line.startswith("def verify_otp("):
        new_lines.extend(ver_lines)
        new_lines.append("\n")
        new_lines.extend(res_lines)
        new_lines.append("\n")
        in_verify = True
    elif line.startswith("def resend_otp("):
        in_resend = True
    elif line.startswith("@login_required") and (in_resend or in_verify):
        in_verify = False
        in_resend = False

    if not in_register and not in_verify and not in_resend:
        new_lines.append(line)
    i += 1

with open("views.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Patch successful!")
