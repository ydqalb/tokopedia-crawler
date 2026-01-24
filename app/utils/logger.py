class Logger:
    def info(self, msg): print(f"[INFO] {msg}")
    def ok(self, msg): print(f"[OK] {msg}")
    def warn(self, msg): print(f"[WARN] {msg}")
    def error(self, msg): print(f"[ERROR] {msg}")