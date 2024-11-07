import re

with open("README.md", "r") as file:
    content = file.read()

# Check if the pattern matches and display the current count
match = re.search(r"This workflow has run (\d+) times", content)
count = int(match.group(1)) if match else 0
print("Current count:", count)  # Debug print

# Increment the count
new_content = re.sub(
    r"This workflow has run (\d+) times",
    f"This workflow has run {count + 1} times",
    content,
)

# Display new content for debugging
print("New content:\n", new_content)  # Debug print

with open("README.md", "w") as file:
    file.write(new_content)
