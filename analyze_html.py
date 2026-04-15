import re

with open('page1_sample.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find p_loopitem blocks (likely the product cards)
loop_items = re.findall(r'<[^>]*class="[^"]*p_loopitem[^"]*"[^>]*>.*?</(?:li|div|article)>', html, re.S|re.IGNORECASE)
print(f"p_loopitem blocks found: {len(loop_items)}")
if loop_items:
    print("\n--- First p_loopitem block ---")
    print(loop_items[0][:1000])

# Also find p_item blocks
item_blocks = re.findall(r'<[^>]*class="[^"]*p_item[^"]*"[^>]*>.*?</(?:li|div)>', html, re.S|re.IGNORECASE)
print(f"\np_item blocks found: {len(item_blocks)}")
if item_blocks:
    print("\n--- First p_item block ---")
    print(item_blocks[0][:1000])

# Find p_c_item blocks
c_item_blocks = re.findall(r'<[^>]*class="[^"]*p_c_item[^"]*"[^>]*>.*?</(?:li|div)>', html, re.S|re.IGNORECASE)
print(f"\np_c_item blocks found: {len(c_item_blocks)}")
if c_item_blocks:
    print("\n--- First p_c_item block ---")
    print(c_item_blocks[0][:1000])

# Let's look at sections with p_img class
img_sections = re.findall(r'<[^>]*class="[^"]*p_img[^"]*"[^>]*>.*?</div>', html, re.S|re.IGNORECASE)
print(f"\np_img sections: {len(img_sections)}")
for s in img_sections[:3]:
    print(f"  {s[:300]}")

# Check p_title
title_sections = re.findall(r'<[^>]*class="[^"]*p_title[^"]*"[^>]*>(.*?)</[^>]+>', html, re.S|re.IGNORECASE)
print(f"\np_title text: {len(title_sections)}")
for t in title_sections[:5]:
    print(f"  '{t.strip()[:100]}'")
