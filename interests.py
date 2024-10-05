import re

interests_file = 'interests.txt'
sessions_file = 'sessions.txt'
sessions_with_interests_file = 'sessions_with_interests.txt'

interests_list = {}
for line in open(interests_file):
    parts = line.rstrip('\n').split(",")
    if len(parts) > 1:
        line = parts[0]
        priority = parts[1]
    else:
        line = parts[0]
        priority = "1"
    interests_list[("".join(line.upper().rstrip('\n').split('-')))] = priority

sessions_list = [line.rstrip('\n') for line in open(sessions_file)]

for index, session in enumerate(sessions_list):
    serssion_id = session.split('|')[0]
    serssion_id = "".join(serssion_id.upper().rstrip('\n').split('-'))
    if serssion_id in interests_list:
        sessions_list[index] = re.sub(r"\|False\|\d*\||\|True\|\d*\|", f"|True|{interests_list[serssion_id]}|", sessions_list[index])  # session.replace("|False|", "|True|")
        del interests_list[serssion_id]

with open(sessions_with_interests_file, 'w') as file:
    for line in sessions_list:
        file.write(line + "\n")

print("Couldn't find:")
print(interests_list)
