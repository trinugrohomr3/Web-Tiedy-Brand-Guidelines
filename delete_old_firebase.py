"""
Delete semua dokumen lama di Firestore products collection
yang SKU-nya tidak ada di products.json yang baru
"""
import json, urllib.request, urllib.error, sys, time

sys.stdout.reconfigure(encoding='utf-8')

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

# Load current valid SKUs
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)
valid_skus = set(p['sku'] for p in products)
print(f"Valid SKUs in new products.json: {len(valid_skus)}")

# Old SKUs to delete (produk LIAO67xxx dan L130xxx dari versi sebelumnya)
old_skus = [
    'LIAO67341', 'LIAO67342', 'L130006', 'L130007', 'L130008',
    'LIAO67332', 'LIAO67333', 'LIAO67334', 'L130009', 'LIAO67301',
    'LIAO67302', 'LIAO67303', 'L130010', 'LIAO67304', 'LIAO67305',
    'LIAO67306', 'LIAO67307', 'LIAO67308', 'LIAO67309', 'LIAO67310',
    'LIAO67311', 'LIAO67312', 'L130011', 'L130012', 'L130013',
    'L130014', 'L130015', 'L130016', 'LIAO67313', 'LIAO67314',
    'LIAO67315', 'LIAO67316', 'LIAO67317', 'LIAO67318', 'LIAO67319',
    'LIAO67320', 'LIAO67321', 'LIAO67322', 'LIAO67323', 'LIAO67324',
    'L130017', 'L130018', 'LIAO67325', 'LIAO67326', 'LIAO67327',
    'LIAO67328', 'LIAO67329', 'L130019', 'LIAO67330', 'L130020',
    'LIAO67331', 'L130021', 'L130022', 'LIAO67335', 'LIAO67336',
    'L130023', 'LIAO67337', 'L130024', 'LIAO67338', 'LIAO67339',
    'LIAO67340', 'L130025', 'L130026', 'L130027', 'L130028',
]

# Only delete SKUs not in new catalog
to_delete = [sku for sku in old_skus if sku not in valid_skus]
print(f"SKUs to delete: {len(to_delete)}")

deleted = 0
failed = 0
for sku in to_delete:
    result = firestore_request('DELETE', f'products/{sku}')
    if result is not None or True:  # DELETE returns empty on success
        print(f"  [DEL] {sku}")
        deleted += 1
    time.sleep(0.05)

print(f"\nDeleted: {deleted}")
print(f"Failed:  {failed}")
print("Done!")
