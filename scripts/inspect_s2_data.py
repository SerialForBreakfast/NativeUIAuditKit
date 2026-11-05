"""Inspect S2 capture rows in dataset/tvos_captures/focus556/out-4k/manifest.json."""
import json
from pathlib import Path

MANIFEST = Path('dataset/tvos_captures/focus556/out-4k/manifest.json')

def main():
    with open(MANIFEST) as f:
        rows = json.load(f)
    print(f"Total S2 rows: {len(rows)}")
    recipes = {}
    classes = {}
    for r in rows:
        rec = r['metadata']['recipeFile']
        recipes[rec] = recipes.get(rec, 0) + 1
        cls = r['metadata']['taxonomyClass']
        classes[cls] = classes.get(cls, 0) + 1
    
    print("\nRecipes:")
    for rec, cnt in sorted(recipes.items()):
        print(f"  {rec}: {cnt} rows")

    print("\nTaxonomy Classes:")
    for cls, cnt in sorted(classes.items()):
        print(f"  {cls}: {cnt} rows")

if __name__ == '__main__':
    main()
