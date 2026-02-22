import torch
import sys
import platform

print(f"Python version: {sys.version}")
print(f"OS: {platform.platform()}")
print(f"Torch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    print(f"CUDA version: {torch.version.cuda}")
else:
    print("CUDA is NOT available to Torch.")
