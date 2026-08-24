"""Walk a tree once and record what can be measured. No deletes, ever."""
import os, hashlib, time
from dataclasses import dataclass

@dataclass(frozen=True)
class F:
    path: str
    rel: str
    size: int
    mtime: float
    sha: str
    lines: tuple

    @property
    def stem(self):
        b = os.path.basename(self.rel).rsplit(".", 1)[0].lower()
        for suf in ("_final", "-final", "_v2", "_v1", " copy", "_copy", "(1)", "_new"):
            if b.endswith(suf):
                b = b[: -len(suf)]
        return b.strip()

def walk(root: str):
    out = []
    for dirpath, _, names in os.walk(root):
        for n in sorted(names):
            p = os.path.join(dirpath, n)
            with open(p, "rb") as fh:
                raw = fh.read()
            st = os.stat(p)
            try:
                lines = tuple(l.strip() for l in raw.decode("utf-8").splitlines() if l.strip())
            except UnicodeDecodeError:
                lines = ()
            out.append(F(p, os.path.relpath(p, root), st.st_size, st.st_mtime,
                         hashlib.sha256(raw).hexdigest(), lines))
    return sorted(out, key=lambda f: f.rel)
