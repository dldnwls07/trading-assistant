import os
import glob
import shutil

src_dir = r"c:\Users\feca1\OneDrive\바탕 화면\Trading_asist\src"
agents_dir = os.path.join(src_dir, "agents")

mapping = {
    "core": ["analyst.py", "chartist.py", "profiler.py"],
    "analysis": ["ai_analyzer.py", "ml_predictor.py", "multi_timeframe.py", "pattern_detector.py", "portfolio_analyzer.py", "screener.py", "strategy_ensemble.py"],
    "calendar": ["calendar_fetchers.py", "event_calendar.py", "event_data.py"],
    "chat": ["chat_assistant.py"],
    "execution": ["auto_trader.py", "executor.py"]
}

# 1. Create subdirs and move files
for folder, files in mapping.items():
    folder_path = os.path.join(agents_dir, folder)
    os.makedirs(folder_path, exist_ok=True)
    
    # Create empty init file to make it a package
    with open(os.path.join(folder_path, "__init__.py"), "w", encoding="utf-8") as f:
        pass

    for file in files:
        src_file = os.path.join(agents_dir, file)
        dst_file = os.path.join(folder_path, file)
        if os.path.exists(src_file):
            shutil.move(src_file, dst_file)

# 2. Update imports in all python files
py_files = []
for root, _, files in os.walk(src_dir):
    for f in files:
        if f.endswith(".py"):
            py_files.append(os.path.join(root, f))

# Mapping from module name to new path
module_to_folder = {}
for folder, files in mapping.items():
    for f in files:
        mod_name = f.replace(".py", "")
        module_to_folder[mod_name] = folder

for py_file in py_files:
    with open(py_file, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = content
    for mod_name, folder in module_to_folder.items():
        # Look for the exact exact import
        old_import = f"from src.agents.{mod_name} import"
        new_import = f"from src.agents.{folder}.{mod_name} import"
        new_content = new_content.replace(old_import, new_import)

    if new_content != content:
        with open(py_file, "w", encoding="utf-8") as f:
            f.write(new_content)

print("Migration completed!")
