#!/usr/bin/env python3
"""Merge Jild 9 tashreeh chunks into content/tashreeh/jild-09.json.

Re-runnable: reads every jild-09-chunk-NN.json present, merges in chunk
order, validates (unique ids, page coverage vs manifest, no empty jawab),
writes jild-09.json, and updates chunks-manifest-jild9.json statuses.

Duplicate-id rule (Jild 4 precedent): if a mas'ala number repeats in a
later chunk (numbering restarts per risala), the EARLIEST item keeps the
plain id and the later one is renamed to "<id>-p<startpage>".
"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))

def main():
    manifest = json.load(open(os.path.join(BASE, 'chunks-manifest-jild9.json')))
    all_items = []
    merged_chunks = []
    for entry in manifest['chunks']:
        nn = entry['chunk']
        path = os.path.join(BASE, f'jild-09-chunk-{nn}.json')
        if not os.path.exists(path):
            print(f'chunk {nn}: not yet written')
            continue
        try:
            d = json.load(open(path, encoding='utf-8'))
        except json.JSONDecodeError as e:
            # File may still be streaming from its translator; skip it
            # for now instead of crashing the whole merge.
            print(f'chunk {nn}: not valid JSON yet ({e}) — skipping for now')
            continue
        items = d['masail']
        # Normalize: some translators omit start_page; derive it from pages.
        for it in items:
            if 'start_page' not in it:
                assert it.get('pages'), f'chunk {nn} item {it.get("id")} has no pages'
                it['start_page'] = it['pages'][0]
                print(f'chunk {nn}: derived start_page={it["start_page"]} for {it["id"]}')
            assert it['start_page'] == min(it['pages']), \
                f'chunk {nn} item {it["id"]}: start_page != first page'
        all_items.extend(items)
        merged_chunks.append(nn)
        entry['status'] = 'merged'
        print(f'chunk {nn}: {len(items)} items merged')
    # de-duplicate ids: earliest keeps plain id, later ones get -p<startpage>
    seen = {}
    for it in all_items:
        if it['id'] in seen:
            new_id = f"{it['id']}-p{it['start_page']}"
            print(f'DUPLICATE ID {it["id"]} (start {it["start_page"]}) -> renamed {new_id}')
            it['id'] = new_id
        seen[it['id']] = True
    ids = [it['id'] for it in all_items]
    assert len(ids) == len(set(ids)), f'STILL DUPLICATE IDS: {[i for i in ids if ids.count(i) > 1]}'
    empty = [it['id'] for it in all_items if not it.get('tashreeh_jawab')]
    assert not empty, f'EMPTY JAWAB: {empty}'
    pages = set()
    for it in all_items:
        pages.update(it['pages'])
    expected = set()
    for entry in manifest['chunks']:
        if entry['chunk'] in merged_chunks:
            expected.update(range(entry['start_page'], entry['end_page'] + 1))
            expected.difference_update(entry['missing_pages'])
    missing_covered = expected - pages
    extra = pages - expected
    print(f'total items: {len(all_items)} | pages covered: {len(pages)} | expected: {len(expected)}')
    print(f'uncovered expected pages: {sorted(missing_covered)}')
    print(f'extra pages (outside merged chunks): {sorted(extra)}')
    assert not missing_covered, 'pages missing from merged chunks!'
    assert not extra, 'pages outside merged chunks!'
    # sort by start_page for the final file
    all_items.sort(key=lambda it: it['start_page'])
    with open(os.path.join(BASE, 'jild-09.json'), 'w', encoding='utf-8') as f:
        json.dump({'masail': all_items}, f, ensure_ascii=False, indent=1)
    with open(os.path.join(BASE, 'chunks-manifest-jild9.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f'WROTE jild-09.json: {len(all_items)} items, {len(pages)} pages, chunks merged: {merged_chunks}')

if __name__ == '__main__':
    main()
