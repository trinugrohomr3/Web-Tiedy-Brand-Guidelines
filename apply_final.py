"""
Final mapping untuk 13 produk yang masih kosong.
Berdasarkan data yang sudah ditemukan dari berbagai kategori LIAO.
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE_IMG = 'https://omo-oss-image.thefastimg.com/portal-saas/pg2026021109282591999/cms/image/'

# Mapping nama produk json -> URL gambar (dari hasil scraping di atas)
FINAL_MAP = {
    'SELF-WRINGING FLAT MOP 32cm':
        BASE_IMG + '6962276a-b73c-4426-9e35-d7dfd0843002.jpg',  # Self-Squeeze Mop
    'SELF-WRINGING FLAT MOP 36cm':
        BASE_IMG + '6962276a-b73c-4426-9e35-d7dfd0843002.jpg',  # Self-Squeeze Mop

    'Scourer 20g':
        BASE_IMG + '84c2d33c-bfdd-4a82-a503-67441e1d0eeb.jpg',  # Scourer
    'Scourer 15g x 4':
        BASE_IMG + '84c2d33c-bfdd-4a82-a503-67441e1d0eeb.jpg',  # Scourer
    'Scourer 20g x 4':
        BASE_IMG + '84c2d33c-bfdd-4a82-a503-67441e1d0eeb.jpg',  # Scourer

    'Sponge Scouring Pad':
        BASE_IMG + '4f934008-d1b2-46a4-8bfd-298eb279b839.jpg',  # Sponge Scourer

    'STAINLESS STEEL SCRUBBER & SPONGE':
        BASE_IMG + '4f934008-d1b2-46a4-8bfd-298eb279b839.jpg',  # Sponge Scourer

    'Mop & Broom holder 3P':
        BASE_IMG + '6a2867ff-fba8-472a-baed-bc4b59e81ac3.jpg',  # Mop & Broom Holder
    'Mop & Broom holder Glue 2P':
        BASE_IMG + '6a2867ff-fba8-472a-baed-bc4b59e81ac3.jpg',  # Mop & Broom Holder
    'Mop & Broom holder Glue 3P':
        BASE_IMG + '6a2867ff-fba8-472a-baed-bc4b59e81ac3.jpg',  # Mop & Broom Holder

    'Broom Holder ABS 3P':
        BASE_IMG + '12349ca5-f7e3-442a-882a-300c64f7208b.jpg',  # Nail Free Mop & Broom Holder
    'Broom Holder ABS 5P':
        BASE_IMG + 'c9d907c8-2f4c-46a1-9363-abf2e07765ba.jpg',  # Nail Free Mop & Broom Holder KZ2102

    'Garbage bag 50L':
        BASE_IMG + 'cf7bbdbb-990e-436e-bc1b-c459e2f953d6.jpg',  # Garbage Bags
}

# Load and update
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

applied = 0
for p in products:
    name = p['name']
    img = p.get('img_c1', '')
    # Only update if missing or placeholder
    if img and img != '' and 'addfa8e3-22fd-4513-a5c9-78074d01d4e6' not in img:
        continue
    if name in FINAL_MAP:
        p['img_c1'] = FINAL_MAP[name]
        p['img_c2'] = FINAL_MAP[name]
        applied += 1
        print(f"  APPLIED: {name}")

print(f"\nApplied: {applied}")

with open('assets/products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

# Final summary
empty = [p for p in products if not p.get('img_c1') or p.get('img_c1') == '']
placeholder = [p for p in products if 'addfa8e3-22fd-4513-a5c9-78074d01d4e6' in p.get('img_c1', '')]
valid = [p for p in products if p.get('img_c1') and 'addfa8e3' not in p.get('img_c1', '') and p.get('img_c1') != '']

print(f"\n=== FINAL STATUS ===")
print(f"  Total: {len(products)}")
print(f"  With valid image: {len(valid)}")
print(f"  Empty: {len(empty)}")
print(f"  Placeholder: {len(placeholder)}")
if empty + placeholder:
    print("\nStill missing:")
    for p in empty + placeholder:
        print(f"  - {p['sku']}: {p['name']}")
else:
    print("\n==> Semua produk sudah memiliki gambar!")
