#!/usr/bin/env python3
"""Extract all chunks from Weaviate for LightRAG ingestion."""
import requests, json, time

KEY = "WVF5YThaHlkYwhGUSmCRgsX3tD5ngdN8pkih"
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
cls = "Vector_index_c8b822da_da9e_4b7f_b7fb_005d7e23ebb3_Node"

all_chunks = []
batch_size = 500
offset = 0

while True:
    query = '{ Get { ' + cls + '(limit: ' + str(batch_size) + ' offset: ' + str(offset) + ') { text source } } }'
    r = requests.post('http://localhost:8080/v1/graphql', headers=HEADERS, json={"query": query}, timeout=30)
    
    if r.status_code != 200:
        print(f"Error at offset {offset}: {r.status_code} {r.text[:200]}")
        break
    
    data = r.json()
    items = data.get('data', {}).get('Get', {}).get(cls)
    
    if not items:
        break
    
    for item in items:
        txt = (item.get('text', '') or '').strip()
        if len(txt) > 50:
            all_chunks.append(txt)
    
    offset += batch_size
    print(f"Offset {offset}: {len(all_chunks)} usable chunks", flush=True)
    time.sleep(0.1)  # Be gentle

    if len(items) < batch_size:
        break

# Save
with open("/home/steve/lightrag-data/holisticseo_chunks.jsonl", "w") as f:
    for chunk in all_chunks:
        f.write(json.dumps({"text": chunk}) + "\n")

print(f"\nDone! {len(all_chunks)} chunks saved. Total chars: {sum(len(c) for c in all_chunks):,}")
