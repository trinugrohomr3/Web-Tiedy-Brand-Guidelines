"""
Sync products.json -> Firebase Firestore
Update img_c1 dan img_c2 untuk semua produk di Firestore
menggunakan Firestore REST API (tidak perlu Admin SDK)
"""
import json, urllib.request, urllib.error, sys, time

sys.stdout.reconfigure(encoding='utf-8')

# Firebase config (dari index.html)
PROJECT_ID = "web-tiedy-brand-guidelines"
API_KEY    = "AIzaSyDKGh1zwOtwSGFhmZwpsfyNAF2f5ZCZnAw"
BASE_URL   = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

def firestore_request(method, path, body=None):
    url = f"{BASE_URL}/{path}?key={API_KEY}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"  HTTP {e.code}: {err[:200]}")
        return None

def to_firestore_value(val):
    if val is None:
        return {"nullValue": None}
    if isinstance(val, str):
        return {"stringValue": val}
    if isinstance(val, bool):
        return {"booleanValue": val}
    if isinstance(val, int):
        return {"integerValue": str(val)}
    if isinstance(val, float):
        return {"doubleValue": val}
    return {"stringValue": str(val)}

# Load products.json
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"Loaded {len(products)} products from products.json")

# Check if Firestore already has data
print("\nChecking Firestore for existing products...")
result = firestore_request('GET', 'products?pageSize=5')
if result and 'documents' in result:
    existing_count = len(result.get('documents', []))
    print(f"  Firestore has {existing_count}+ documents")
    HAS_DATA = existing_count > 0
else:
    print("  Firestore appears empty or inaccessible")
    HAS_DATA = False

print(f"\nStrategy: {'UPDATE existing docs' if HAS_DATA else 'CREATE new docs'}")
print()

# Update/Create each product
ok = 0
fail = 0
for p in products:
    sku = p['sku']
    img_c1 = p.get('img_c1', '')
    img_c2 = p.get('img_c2', '')
    
    # Build Firestore document fields
    fields = {f: to_firestore_value(v) for f, v in p.items()}
    
    # Add images array field (for migration compatibility)
    imgs = [img for img in [img_c1, img_c2] if img]
    if imgs:
        fields['images'] = {
            "arrayValue": {
                "values": [{"stringValue": i} for i in imgs]
            }
        }
    
    body = {"fields": fields}
    
    # PATCH (create or update) the document
    # Using PATCH with document name creates or overwrites
    result = firestore_request('PATCH', f'products/{sku}', body)
    
    if result and 'name' in result:
        print(f"  [OK] {sku}: {img_c1[-30:] if img_c1 else 'NO IMG'}")
        ok += 1
    else:
        print(f"  [FAIL] {sku}")
        fail += 1
    
    time.sleep(0.05)  # rate limiting

print(f"\n=== DONE ===")
print(f"  Success: {ok}")
print(f"  Failed:  {fail}")
print(f"  Total:   {len(products)}")
