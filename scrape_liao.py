"""
Scrape ulang semua halaman, ambil nama + gambar per produk,
lalu fuzzy match ke products.json dan update file.
"""
import subprocess, json, re, time, sys
from rapidfuzz import process, fuzz

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'https://www.nb-liao.com'
CURL = ['curl.exe', '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', '-s', '-L', '--max-time', '20']

def fetch(url):
    res = subprocess.run(CURL + [url], capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return res.stdout

def extract_loopitems(html):
    items = []
    # Pisahkan tiap p_loopitem block
    # Cari semua div dengan class p_loopitem
    pattern = r'<div[^>]*class="[^"]*p_loopitem[^"]*"[^>]*>(.*?)(?=<div[^>]*class="[^"]*p_loopitem|$)'
    blocks = re.findall(pattern, html, re.S|re.IGNORECASE)
    
    for block in blocks:
        # Gambar dari lazy attribute
        imgs = re.findall(r'lazy="(https://omo-oss-image\.thefastimg\.com[^"]+)"', block, re.IGNORECASE)
        img = imgs[0] if imgs else ''
        if not img:
            continue  # skip jika tidak ada gambar produk
        
        # Nama produk: strip HTML, ambil teks bermakna
        # Cari pola "Nama Produk CODE VIEW PRODUCTS"
        text = re.sub(r'<[^>]+>', ' ', block)
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'&lt;|&gt;', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Coba extract nama dan kode produk
        # Pola: "Nama Produk AXXXXXX VIEW PRODUCTS" atau "Nama Produk LIAOXXXXX VIEW"
        # Ambil teks sebelum "VIEW PRODUCTS" atau "VIEW DETAIL"
        name_part = re.sub(r'\s*VIEW\s+(PRODUCTS?|DETAILS?|MORE).*', '', text, flags=re.IGNORECASE).strip()
        # Hapus kode produk dari nama (A130002, LIAO67301, L130006)
        code_match = re.search(r'\b([AL]\d{5,}|LIAO\d{5})\b', name_part, re.IGNORECASE)
        code = code_match.group(0) if code_match else ''
        name_clean = re.sub(r'\b[AL]\d{5,}\b|\bLIAO\d{5}\b', '', name_part, flags=re.IGNORECASE).strip()
        name_clean = re.sub(r'\s+', ' ', name_clean).strip()
        
        items.append({
            'img': img,
            'name': name_clean,
            'code': code,
            'raw': text[:100]
        })
    return items

# ── SCRAPE ALL PAGES (multiple category URLs) ─────────────────────────────────
print("Scraping nb-liao.com...")
all_items = []
seen_page_imgs = set()  # track unique img sets per page to detect pagination end

# Try multiple product category pages
category_ids = [17, 18, 19, 20, 21, 22, 23]
for cat_id in category_ids:
    for page in range(1, 30):
        url = f'{BASE_URL}/products/{cat_id}.html?page={page}'
        print(f"  Cat {cat_id} Page {page}...", end=' ', flush=True)
        html = fetch(url)
        if not html or len(html) < 5000:
            print("STOP")
            break
        
        items = extract_loopitems(html)
        if not items:
            print("0 items - STOP")
            break
        
        # Check duplicate page: if all images already seen, pagination is done
        page_img_key = frozenset(i['img'] for i in items)
        if page_img_key in seen_page_imgs:
            print(f"DUPLICATE - STOP")
            break
        seen_page_imgs.add(page_img_key)
        
        print(f"{len(items)} items")
        all_items.extend(items)
        time.sleep(0.3)

# Deduplicate by image URL
seen_imgs = set()
unique_items = []
for item in all_items:
    if item['img'] not in seen_imgs:
        seen_imgs.add(item['img'])
        unique_items.append(item)

print(f"\nTotal unique items: {len(unique_items)}")
print("\nSample items:")
for item in unique_items[:8]:
    print(f"  name='{item['name'][:40]}' | code='{item['code']}' | img=...{item['img'][-30:]}")

# ── LOAD products.json ────────────────────────────────────────────────────────
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"\nProducts in JSON: {len(products)}")

# ── BUILD LOOKUP: nama produk liao -> gambar ──────────────────────────────────
# Build dict: name -> img (prefer unique items)
name_to_img = {}
for item in unique_items:
    if item['name']:
        name_to_img[item['name']] = item['img']

scraped_names = list(name_to_img.keys())
print(f"Unique scraped names: {len(scraped_names)}")

# ── MATCH & UPDATE ────────────────────────────────────────────────────────────
mapped = 0
not_mapped = []

for p in products:
    # Jika sudah ada gambar yang valid (bukan placeholder), skip
    existing = p.get('img_c1', '')
    if existing and 'addfa8e3-22fd-4513-a5c9-78074d01d4e6' not in existing:
        # sudah ada gambar valid
        continue
    
    prod_name = p['name']
    if not scraped_names:
        break
    
    result = process.extractOne(prod_name, scraped_names, scorer=fuzz.token_sort_ratio)
    if result:
        best_name, score, _ = result
        score = int(score)
        if score >= 55:
            img_url = name_to_img[best_name]
            p['img_c1'] = img_url
            p['img_c2'] = img_url
            mapped += 1
            print(f"  MATCH [{score:3d}] '{prod_name}' -> '{best_name[:40]}'")
        else:
            not_mapped.append((score, prod_name, result[0]))

print(f"\nMapped: {mapped} / {len(products)}")
print(f"Not mapped ({len(not_mapped)}):")
for score, pname, bname in sorted(not_mapped):
    print(f"  [{score}] '{pname}' best='{bname}'")

# ── SAVE ──────────────────────────────────────────────────────────────────────
with open('assets/products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

print("\nproducts.json updated!")
