import json
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f'Total: {len(products)}')
print()
for p in products[:10]:
    img = p.get('img_c1', '')
    status = 'OK' if img and 'omo-oss-image' in img else 'MISSING'
    name = p['name'][:35]
    print(f'[{status}] {p["sku"]}: {name} | ...{img[-30:] if img else "EMPTY"}')
print('...')
for p in products[-5:]:
    img = p.get('img_c1', '')
    status = 'OK' if img and 'omo-oss-image' in img else 'MISSING'
    name = p['name'][:35]
    print(f'[{status}] {p["sku"]}: {name} | ...{img[-30:] if img else "EMPTY"}')
