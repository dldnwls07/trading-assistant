import os

# Define paths relative to the project root
# Using absolute paths based on the current environment would be safer if running from arbitrary cwd, 
# but assuming we run from project root or handle relative paths correctly.
# Let's use relative paths from where the script is likely run (project root) or absolute paths.

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(PROJECT_ROOT, "skills")
WORKFLOWS_DIR = os.path.join(PROJECT_ROOT, ".agent", "workflows")

def generate_workflows():
    if not os.path.exists(SKILLS_DIR):
        print(f"Skills directory not found: {SKILLS_DIR}")
        return

    # Ensure workflows directory exists
    os.makedirs(WORKFLOWS_DIR, exist_ok=True)
    print(f"Checking skills in: {SKILLS_DIR}")
    print(f"Generating workflows in: {WORKFLOWS_DIR}")

    count = 0
    # Iterate through skills
    for skill_name in os.listdir(SKILLS_DIR):
        skill_dir = os.path.join(SKILLS_DIR, skill_name)
        skill_file = os.path.join(skill_dir, "SKILL.md")
        
        if os.path.isdir(skill_dir) and os.path.exists(skill_file):
            workflow_filename = f"{skill_name}.md"
            workflow_path = os.path.join(WORKFLOWS_DIR, workflow_filename)
            
            # Create a simple wrapper workflow
            # We use forward slashes for cross-platform compatibility in the markdown link
            relative_skill_path = f"skills/{skill_name}/SKILL.md"
            
            content = f"""---
description: Activate the {skill_name} skill
---
1. Read the skill instructions by viewing the file `{relative_skill_path}`.
2. Strictly follow the instructions and persona defined in that file.
"""
            with open(workflow_path, "w", encoding="utf-8") as f:
                f.write(content.strip())
            
            print(f"Created/Updated: {workflow_filename}")
            count += 1
            
    print(f"Successfully generated {count} skill workflows.")

if __name__ == "__main__":
    generate_workflows()
