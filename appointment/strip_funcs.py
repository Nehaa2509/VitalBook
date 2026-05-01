import os
with open("views.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
if "import random\n" not in "".join(lines[:20]):
    new_lines.extend(["import random\n", "import string\n"])

in_register = False
in_verify = False
in_resend = False

for line in lines:
    if line.startswith("def register(request):"):
        in_register = True
        continue
    elif line.startswith("def user_login(request):"):
        in_register = False
    
    if line.startswith("def verify_otp(request):"):
        in_verify = True
        continue
    elif line.startswith("def resend_otp(request):"):
        in_verify = False
        in_resend = True
        continue
    elif line.startswith("@login_required") and in_resend:
        in_resend = False

    if not in_register and not in_verify and not in_resend:
        new_lines.append(line)

with open("views_clean.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
