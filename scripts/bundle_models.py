import os
import sys

def download_models():
    # Define paths relative to the script location
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    bi_encoder_path = os.path.join(models_dir, "all-MiniLM-L6-v2")
    cross_encoder_path = os.path.join(models_dir, "ms-marco-MiniLM-L-6-v2")
    
    print("="*60)
    print("                 OFFLINE MODEL BUNDLING SETUP                 ")
    print("="*60)
    
    try:
        from sentence_transformers import SentenceTransformer, CrossEncoder
    except ImportError as e:
        print(f"[ERROR] Failed to import sentence-transformers: {e}")
        print("Please run 'pip install -r requirements.txt' first.")
        sys.exit(1)
        
    # 1. Download and save Bi-Encoder model
    print("Downloading Bi-Encoder model 'all-MiniLM-L6-v2'...")
    try:
        bi_model = SentenceTransformer("all-MiniLM-L6-v2")
        print(f"Saving Bi-Encoder to {bi_encoder_path}...")
        bi_model.save(bi_encoder_path)
        print("[SUCCESS] Bi-Encoder model packaged.")
    except Exception as e:
        print(f"[ERROR] Failed to bundle Bi-Encoder model: {e}")
        sys.exit(1)
        
    print("-"*60)
    
    # 2. Download and save Cross-Encoder model
    print("Downloading Cross-Encoder model 'cross-encoder/ms-marco-MiniLM-L-6-v2'...")
    try:
        cross_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        print(f"Saving Cross-Encoder to {cross_encoder_path}...")
        cross_model.save(cross_encoder_path)
        print("[SUCCESS] Cross-Encoder model packaged.")
    except Exception as e:
        print(f"[ERROR] Failed to bundle Cross-Encoder model: {e}")
        sys.exit(1)
        
    print("="*60)
    print("Model bundling complete! Pipeline is now configured to run 100% offline.")
    
if __name__ == "__main__":
    download_models()
