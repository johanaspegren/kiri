# modules/face_db.py
from __future__ import annotations
import numpy as np
from pathlib import Path
import json

class FaceDB:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "index.json"
        self.emb_dir = self.root / "embeds"
        self.emb_dir.mkdir(exist_ok=True)
        self.index = {}  # name -> [filenames]
        if self.index_path.exists():
            self.index = json.loads(self.index_path.read_text() or "{}")

    def _save_index(self):
        self.index_path.write_text(json.dumps(self.index, indent=2))

    def add(self, name: str, emb: np.ndarray):
        name = name.strip()
        fid = f"{name}_{len(self.index.get(name, []))}.npy"
        np.save(self.emb_dir / fid, emb.astype(np.float32))
        self.index.setdefault(name, []).append(fid)
        self._save_index()

    def all(self):
        """Yield (name, embedding) for all stored vectors."""
        for name, files in self.index.items():
            for f in files:
                path = self.emb_dir / f
                if path.exists():
                    yield name, np.load(path)

    def infer(self, emb: np.ndarray, thresh: float = 0.35):
        """Return (best_name, best_score) or (None, 0). Score is 1 - cosine distance."""
        best_name, best_score = None, 0.0
        # cosine similarity
        def cos(a,b): return float(np.dot(a, b) / (np.linalg.norm(a)*np.linalg.norm(b) + 1e-9))
        for name, ref in self.all():
            s = cos(emb, ref)
            if s > best_score:
                best_name, best_score = name, s
        if best_score >= (1.0 - thresh):  # thresh ~0.35 => require sim >= 0.65
            return best_name, best_score
        return None, best_score
