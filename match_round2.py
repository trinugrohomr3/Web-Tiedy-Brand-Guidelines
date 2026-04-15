"""
Smart matching round 2: ambil semua scraped items dan coba manual mapping
untuk produk-produk yang belum ter-match.
"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

# Load products.json
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# Manual mapping: products.json name -> scraped name (yang paling relevan dari website)
# Dipilih berdasarkan output scraper sebelumnya
MANUAL_MAP = {
    # Tornado Mop series -> Spray Mop (yang paling dekat di website, atau ambil gambar mop lain)
    'Tornado Mop':              'Cotton Water Mop',          # mop with bucket
    'Tornado Mop Stainless':    'Cotton Water Mop',
    'Tornado Mop 8L':           'Cotton Water Mop',
    'Tornado Mop Refill':       'Microfiber Flat Mop',       # mop refill
    
    # Self-wringing
    'SELF-WRINGING FLAT MOP 32cm': 'Self-Wringing Flat Mop GSA016',
    'SELF-WRINGING FLAT MOP 36cm': 'Self-Wringing Flat Mop GSA016',
    
    # Spray mop
    'SPRAY MOP 300ML':          'Spray Mop',
    'SPRAY MOP REFILL Velcro':  'Microfiber Flat Mop',

    # Twist mop
    'Twist Mop telescopic handle': 'Twist Mop GSA010',
    'Twist Mop Polyester':      'Twist Mop GSA010',

    # Floor brush
    'TPR RUBBER floor brush Set': 'Floor Brush GSK010',
    'EVA floor squeegee 58cm':  'Floor Squeegee GSK005',

    # Dusters
    'PP Duster':                'Window Cleaner GSB002',     # ketidakcocokan kategori - skip
    'Chenille Duster':          'Chenille Flat Mop GSA001',
    'Chenille Duster 120cm':    'Chenille Flat Mop GSA001',
    'Duster TPR':               'Window Blind Duster KB2208',
    'Duster Telescopic':        'Window Blind Duster KB2208',

    # Brushes
    'Multi-Purpose Brush':      'Dish Brush GSD011',
    'Multi-Purpose Brush XL':   'Dish Brush GSD011',
    'SOAP DISPENSING DISH BRUSH': 'Dish Brush GSD011',

    # Scouring
    'Scourer 20g':              'Scourer GSD023',
    'Scourer 15g x 4':         'Scourer GSD023',
    'Scourer 20g x 4':         'Scourer GSD023',
    'Sponge Scouring Pad':      'Sponge GSD025',
    'STAINLESS STEEL SCRUBBER & SPONGE': 'Scourer GSD023',

    # Holders
    'Mop & Broom holder 3P':    'Broom Holder KB2210',
    'Mop & Broom holder Glue 2P': 'Broom Holder KB2210',
    'Mop & Broom holder Glue 3P': 'Broom Holder KB2210',
    'Broom Holder ABS 3P':      'Broom Holder KB2210',
    'Broom Holder ABS 5P':      'Broom Holder KB2210',

    # Other
    'DUSTPAN & BROOM Comb':     'Dustpan & Broom GSC001',
    'Cleaning brush set':       'Car Cleaning',
    'Mop refill 52cm':          'Microfiber Flat Mop',
    'Microfiber Mop Scouring':  'Microfiber Water Mop',
    'Twist Mop Cotton':         'Twist Mop GSA010',
}

# Load scraped items (build lookup)
import subprocess
BASE_URL = 'https://www.nb-liao.com'
CURL = ['curl.exe', '-A', 'Mozilla/5.0', '-s', '-L', '--max-time', '20']

# Re-use the data we already scraped - load from the previous scrape output
# (we re-run the scraping to build name_to_img dict)
import time

def fetch(url):
    res = subprocess.run(CURL + [url], capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return res.stdout

def extract_loopitems(html):
    items = []
    blocks = re.split(r'(?=<div[^>]*class="[^"]*p_loopitem[^"]*")', html, flags=re.IGNORECASE)
    for block in blocks[1:]:
        imgs = re.findall(r'lazy="(https://omo-oss-image\.thefastimg\.com[^"]+)"', block, re.IGNORECASE)
        img = imgs[0] if imgs else ''
        if not img:
            continue
        text = re.sub(r'<[^>]+>', ' ', block)
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'\s+', ' ', text).strip()
        name_part = re.sub(r'\s*VIEW\s+(PRODUCTS?|DETAILS?|MORE).*', '', text, flags=re.IGNORECASE).strip()
        name_clean = re.sub(r'\b[AL]\d{5,}\b|\bLIAO\d{5}\b', '', name_part, flags=re.IGNORECASE).strip()
        name_clean = re.sub(r'\s+', ' ', name_clean).strip()
        items.append({'img': img, 'name': name_clean})
    return items

print("Re-scraping untuk build lookup table...")
all_items = []
seen_page_imgs = set()
for cat_id in [17, 18, 19, 20, 21, 22, 23]:
    for page in range(1, 5):
        url = f'{BASE_URL}/products/{cat_id}.html?page={page}'
        html = fetch(url)
        if not html or len(html) < 5000:
            break
        items = extract_loopitems(html)
        if not items:
            break
        page_img_key = frozenset(i['img'] for i in items)
        if page_img_key in seen_page_imgs:
            break
        seen_page_imgs.add(page_img_key)
        all_items.extend(items)
        time.sleep(0.2)

# Build name -> img lookup
name_to_img = {}
seen_imgs = set()
for item in all_items:
    if item['img'] not in seen_imgs and item['name']:
        seen_imgs.add(item['img'])
        name_to_img[item['name']] = item['img']

print(f"Scraped {len(name_to_img)} unique name->img mappings")

# Apply manual mapping for unmatched products
fixed = 0
for p in products:
    prod_name = p['name']
    existing = p.get('img_c1', '')
    # Check if already has a valid image (not placeholder)
    if existing and 'addfa8e3-22fd-4513-a5c9-78074d01d4e6' not in existing and existing != '':
        continue
    
    # Try manual map
    target_name = MANUAL_MAP.get(prod_name)
    if target_name and target_name in name_to_img:
        img = name_to_img[target_name]
        p['img_c1'] = img
        p['img_c2'] = img
        fixed += 1
        print(f"  FIXED: '{prod_name}' -> '{target_name}'")
    elif target_name:
        print(f"  MISSING: '{prod_name}' mapped to '{target_name}' but not in scraped data")

print(f"\nAdditional fixed: {fixed}")

# Save
with open('assets/products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

# Summary
empty = [p for p in products if not p.get('img_c1') or p.get('img_c1') == '']
placeholder = [p for p in products if 'addfa8e3-22fd-4513-a5c9-78074d01d4e6' in p.get('img_c1', '')]
valid = [p for p in products if p.get('img_c1') and 'addfa8e3' not in p.get('img_c1', '') and p.get('img_c1') != '']
print(f"\n=== FINAL STATUS ===")
print(f"  Total: {len(products)}")
print(f"  With valid image: {len(valid)}")
print(f"  Empty: {len(empty)}")
print(f"  Placeholder: {len(placeholder)}")
print(f"\nStill missing:")
for p in empty + placeholder:
    print(f"  - {p['sku']}: {p['name']}")
