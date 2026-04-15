"""
Cari kategori yang mengandung produk sisa (scourer, holder, garbage bag, self-wringing mop)
dan update products.json
"""
import subprocess, json, re, sys, time
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'https://www.nb-liao.com'
CURL = ['curl.exe', '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '-s', '-L', '--max-time', '20']

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
        name_clean = re.sub(r'\b[AGLS]\d{5,}\b|\bLIAO\d{5}\b|\bGS[A-Z]\d+\b|\bKB\d+\b|\bKC\d+\b', '', name_part, flags=re.IGNORECASE).strip()
        name_clean = re.sub(r'\s+', ' ', name_clean).strip()
        items.append({'img': img, 'name': name_clean, 'raw': text[:80]})
    return items

# Scrape kategori 10-35 untuk cari produk missing
print("Cari gambar dari berbagai kategori LIAO...")
all_name_img = {}
seen_page_imgs = set()

for cat_id in range(10, 40):
    url = f'{BASE_URL}/products/{cat_id}.html'
    html = fetch(url)
    if not html or len(html) < 5000:
        continue
    items = extract_loopitems(html)
    if not items:
        continue
    
    page_key = frozenset(i['img'] for i in items)
    if page_key in seen_page_imgs:
        continue
    seen_page_imgs.add(page_key)
    
    for item in items:
        if item['name'] and item['img'] not in all_name_img.values():
            all_name_img[item['name']] = item['img']
    
    print(f"  Cat {cat_id}: {len(items)} items | {items[0]['name'][:40] if items else 'N/A'}...")
    time.sleep(0.3)

print(f"\nTotal unique items found: {len(all_name_img)}")

# Print all scraped names containing keywords for missing products
keywords = ['scourer', 'sponge', 'holder', 'broom hold', 'garbage', 'wringing', 'flat mop', 'self']
print("\nScraped items relevant to missing products:")
for name, img in all_name_img.items():
    if any(kw in name.lower() for kw in keywords):
        print(f"  '{name}' -> ...{img[-40:]}")

# Load products.json
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# Check which are still missing
missing = []
for p in products:
    img = p.get('img_c1', '')
    if not img or img == '' or 'addfa8e3-22fd-4513-a5c9-78074d01d4e6' in img:
        missing.append(p)

print(f"\nStill missing: {len(missing)}")
for p in missing:
    print(f"  - {p['name']}")
