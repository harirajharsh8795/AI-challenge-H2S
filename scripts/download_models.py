import os
import sys

# Ensure parent directory is on sys.path to import src.patch_env
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import src.patch_env


# ==============================================================================
# MODEL DOWNLOAD LOGIC
# ==============================================================================
from sentence_transformers import SentenceTransformer, CrossEncoder

print("Initializing local model download...")

# Ensure target directory exists
os.makedirs("./models/all-MiniLM-L6-v2", exist_ok=True)
os.makedirs("./models/ms-marco-MiniLM-L-6-v2", exist_ok=True)

# 1. Download and save Bi-Encoder (all-MiniLM-L6-v2)
print("Downloading Bi-Encoder 'all-MiniLM-L6-v2'...")
bi_model = SentenceTransformer('all-MiniLM-L6-v2')
bi_model.save('./models/all-MiniLM-L6-v2')
print("Bi-Encoder successfully saved to './models/all-MiniLM-L6-v2'.")

# 2. Download and save Cross-Encoder (ms-marco-MiniLM-L-6-v2)
print("Downloading Cross-Encoder 'ms-marco-MiniLM-L-6-v2'...")
cross_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
cross_model.save('./models/ms-marco-MiniLM-L-6-v2')
print("Cross-Encoder successfully saved to './models/ms-marco-MiniLM-L-6-v2'.")

print("All models successfully pre-downloaded for offline execution!")
