import subprocess
import json
import time
import re
from rapidfuzz import process, fuzz

print('Starting cURL scraping...')

scraped_items = []
for page in range(1, 15):
    url = f'https://www.nb-liao.com/products/17.html?page={page}'
    cmd = ['curl.exe', '-A', 'Mozilla/5.0', '-s', url]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if not res.stdout: break
    
    # We want data-original preferably, else src. We must exclude /npublic/img/s.png
    blocks = re.findall(r'<div[^>]*class="[^"]*pro-img[^"]*"[^>]*>.*?<img[^>]*(?:data-original|src)="([^"]+)"[^>]*>.*?<div[^>]*class="[^"]*pro-name[^"]*"[^>]*>.*?<a[^>]*>(.*?)</a>', res.stdout, re.S | re.IGNORECASE)
    
    for img, name in blocks:
        if 's.png' in img:
            continue
        if img.startswith('/'): img = 'https://www.nb-liao.com' + img
        scraped_items.append({'name': name.strip(), 'img': img.strip()})

with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# exclude any existing s.png
for p in products:
    if p.get('img_c1') and 's.png' in p.get('img_c1'):
        p['img_c1'] = ''
        p['img_c2'] = ''

scraped_names = list(set([x['name'] for x in scraped_items]))
img_map = {x['name']: x['img'] for x in scraped_items}
mapped = 0

for p in products:
    t = p['name']
    if scraped_names:
        best, score, idx = process.extractOne(t, scraped_names, scorer=fuzz.partial_ratio)
        if score >= 60:  # increased threshold
            p['img_c1'] = img_map[best]
            p['img_c2'] = img_map[best]
            mapped += 1

print(f'Mapped {mapped} / {len(products)}')

with open('assets/products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2)

print("Done.")
