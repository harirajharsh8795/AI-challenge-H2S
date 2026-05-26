"""
verify_install.py — Redrob Copilot environment checker
Run:  python verify_install.py
      python verify_install.py --offline    # skip Gemini API ping
"""
import sys, os, time, argparse

G="\033[92m"; R="\033[91m"; Y="\033[93m"; C="\033[96m"; B="\033[1m"; X="\033[0m"

results = []

def chk(label, fn, critical=True):
    try:
        info = fn()
        print(f"{G}  PASS{X}  {label:<42} {C}{info}{X}")
        results.append((label, True))
    except Exception as e:
        tag = f"{R}  FAIL{X}" if critical else f"{Y}  WARN{X}"
        print(f"{tag}  {label:<42} {R}{e}{X}")
        results.append((label, not critical))

# ── 1. Core packages ─────────────────────────────────────────
print(f"\n{B}[1/5] Core packages{X}")

def _numpy():
    import numpy as np
    v = tuple(int(x) for x in np.__version__.split(".")[:2])
    if v[0] >= 2: raise RuntimeError(f"v{np.__version__} — needs < 2.0!")
    return f"v{np.__version__} OK"

def _torch():
    import torch
    return f"v{torch.__version__} {'CUDA' if torch.cuda.is_available() else 'CPU'} OK"

chk("numpy < 2.0",    _numpy,                          critical=True)
chk("torch (CPU)",    _torch,                          critical=True)
chk("scipy",          lambda: __import__("scipy").__version__,  critical=True)
chk("pydantic v2",    lambda: __import__("pydantic").__version__, critical=True)
chk("pyyaml",         lambda: __import__("yaml").__version__,  critical=False)
chk("pandas",         lambda: __import__("pandas").__version__, critical=False)

# ── 2. NLP / Retrieval ───────────────────────────────────────
print(f"\n{B}[2/5] NLP & retrieval{X}")

def _st():
    import sentence_transformers as st
    return f"v{st.__version__}"

def _bm25():
    from rank_bm25 import BM25Okapi
    BM25Okapi([["hello","world"]]).get_scores(["hello"])
    return "functional OK"

chk("transformers",          lambda: __import__("transformers").__version__, critical=True)
chk("sentence-transformers", _st,                                            critical=True)
chk("rank-bm25",             _bm25,                                          critical=True)
chk("huggingface-hub",       lambda: __import__("huggingface_hub").__version__, critical=False)

# ── 3. Google Antigravity / Gemini SDK ───────────────────────
print(f"\n{B}[3/5] Google Antigravity SDK{X}")

chk("google-generativeai",   lambda: __import__("google.generativeai", fromlist=[""]).__version__, critical=True)
chk("google-cloud-aiplatform", lambda: __import__("google.cloud.aiplatform", fromlist=[""]).__version__, critical=True)
chk("google-auth",           lambda: __import__("google.auth", fromlist=[""]).__version__, critical=False)

# ── 4. Model load test ───────────────────────────────────────
print(f"\n{B}[4/5] Model load (offline){X}")

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

def _biencoder():
    from sentence_transformers import SentenceTransformer
    path = os.path.join(MODELS_DIR, "all-MiniLM-L6-v2")
    src = path if os.path.isdir(path) else "all-MiniLM-L6-v2"
    m = SentenceTransformer(src)
    v = m.encode(["test"], show_progress_bar=False)
    return f"dim={v.shape[1]} src={'local' if os.path.isdir(path) else 'HF cache'} OK"

def _crossencoder():
    from sentence_transformers import CrossEncoder
    path = os.path.join(MODELS_DIR, "ms-marco-MiniLM-L-6-v2")
    src = path if os.path.isdir(path) else "cross-encoder/ms-marco-MiniLM-L-6-v2"
    m = CrossEncoder(src)
    s = m.predict([("query","passage")])
    return f"score={s[0]:.3f} src={'local' if os.path.isdir(path) else 'HF cache'} OK"

chk("Bi-Encoder  (all-MiniLM-L6-v2)",          _biencoder,    critical=True)
chk("Cross-Encoder (ms-marco-MiniLM-L-6-v2)",  _crossencoder, critical=True)

# ── 5. Gemini API ping ───────────────────────────────────────
def _gemini_ping():
    print(f"\n{B}[5/5] Gemini API connectivity{X}")
    def _ping():
        import google.generativeai as genai
        key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not key: raise RuntimeError("GOOGLE_API_KEY env var not set")
        genai.configure(api_key=key)
        t0 = time.time()
        r = genai.GenerativeModel("gemini-1.5-flash").generate_content("Reply PONG only")
        ms = (time.time()-t0)*1000
        if "PONG" not in r.text.upper(): raise RuntimeError(f"Bad response: {r.text}")
        return f"latency={ms:.0f}ms OK"
    chk("Gemini 1.5-flash ping", _ping, critical=True)

# ── Summary ──────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    if not args.offline:
        _gemini_ping()
    else:
        print(f"\n{Y}[5/5] Gemini ping skipped (--offline){X}")

    passed = sum(ok for _, ok in results)
    total  = len(results)
    print(f"\n{B}{'-'*55}{X}")
    if passed == total:
        print(f"{G}{B}  OK {passed}/{total} — Environment ready!{X}")
        sys.exit(0)
    else:
        failed = [l for l,ok in results if not ok]
        print(f"{R}{B}  FAIL {passed}/{total} passed — Fix: {', '.join(failed)}{X}")
        sys.exit(1)
    print(f"{B}{'-'*55}{X}\n")

if __name__ == "__main__":
    main()
