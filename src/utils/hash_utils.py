import hashlib

def file_hash(path: str, algo: str = "sha1", bufsize: int = 1024 * 1024) -> str:
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        while True:
            chunk = f.read(bufsize)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
