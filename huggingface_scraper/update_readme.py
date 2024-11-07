import re

with open("README.md", "r") as file:
    content = file.read()

match = re.search(r"This workflow has run (\d+) times", content)
count = int(match.group(1)) if match else 0

new_content = re.sub(
    r"This workflow has run (\d+) times",
    f"This workflow has run {count + 1} times",
    content,
)

with open("README.md", "w") as file:
    file.write(new_content)
