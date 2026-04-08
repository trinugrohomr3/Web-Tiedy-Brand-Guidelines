import os, json, time, hashlib, urllib.request, binascii

# CREDENTIALS
CLOUD_NAME = "dlqvrnjgn"
API_KEY = "312767855484481"
API_SECRET = "IA00hIR4rEjEDScFz45VMPglTJo"
BASE_DIR = r"f:/BackUp/Web Tiedy Brand Guidelines/assets/produk merah"
JSON_PATH = r"f:/BackUp/Web Tiedy Brand Guidelines/assets/products.json"

def get_signature(params, secret):
    s = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    return hashlib.sha1(f"{s}{secret}".encode()).hexdigest()

def upload(fp, pid):
    ts = int(time.time())
    p = {"folder": "tiedy/products", "public_id": pid, "timestamp": ts}
    sig = get_signature(p, API_SECRET)
    url = f"https://api.cloudinary.com/v1_1/{CLOUD_NAME}/image/upload"
    
    with open(fp, "rb") as f: data = f.read()
    b = binascii.hexlify(os.urandom(16)).decode()
    body = []
    for k, v in p.items():
        body.extend([f"--{b}".encode(), f'Content-Disposition: form-data; name="{k}"'.encode(), b"", str(v).encode()])
    body.extend([f"--{b}".encode(), b'Content-Disposition: form-data; name="api_key"', b"", API_KEY.encode()])
    body.extend([f"--{b}".encode(), b'Content-Disposition: form-data; name="signature"', b"", sig.encode()])
    body.extend([f"--{b}".encode(), f'Content-Disposition: form-data; name="file"; filename="a.png"'.encode(), b"Content-Type: image/png", b"", data])
    body.append(f"--{b}--".encode())
    
    req = urllib.request.Request(url, data=b"\r\n".join(body))
    req.add_header("Content-Type", f"multipart/form-data; boundary={b}")
    return urllib.request.urlopen(req).read()

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f: products = json.load(f)
    print(f"Total products: {len(products)}")
    for i, p in enumerate(products):
        sku = p["sku"]
        for suffix, offset in [("_c1", 1), ("_c2", 2)]:
            img_idx = (i * 2) + offset
            fp = os.path.join(BASE_DIR, f"image{img_idx:03}.png")
            if os.path.exists(fp):
                print(f"Uploading {sku}{suffix}...", end=" ", flush=True)
                try: 
                    upload(fp, f"{sku}{suffix}")
                    print("OK")
                except Exception as e: print(f"FAIL: {e}")
    print("DONE!")

if __name__ == "__main__": main()
