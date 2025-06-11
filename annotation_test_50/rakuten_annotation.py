# -*- coding: utf-8 -*-
"""
Interactive Aspect‑Based Annotation Tool for Rakuten Hotel Reviews
Based on the original Dataset1_200Sentences.py (restaurant domain)
Adapted by Carlos, 2025‑05‑09
"""

import pandas as pd
import json, os, sys

# ======================================================
# 1. Aspect Category Table  (Entity × Attribute)
#    - Keep dataframe style for readability
# ======================================================

data = {
    "entity_label": [                 # 1‑7
        'Hotel', 'Rooms', 'Facilities',
        'Room Amenities', 'Service', 'Location', 'Food & Drinks'
    ],
    "attribute_label": [              # 1‑8
        'General', 'Price', 'Comfort', 'Cleanliness',
        'Quality', 'Design & Features',
        'Style & Options', 'Miscellaneous'
    ]
}
# Pad the shorter column so both have same length (8)
max_len = max(len(v) for v in data.values())
for k, v in data.items():
    v += [''] * (max_len - len(v))

aspect_category = pd.DataFrame(data, index=range(1, max_len + 1))

# ======================================================
# 2. Load existing annotations (progress resume)
# ======================================================

try:
    with open('Annotation_test.json', 'r', encoding='utf-8') as f:
        annotations = json.load(f)
except FileNotFoundError:
    annotations = []

# ======================================================
# 3. Load review dataset  (Rakuten hotel reviews)
# ======================================================

# ここを変更してください

review_dataset = pd.read_csv(
    'AnnotationSplit_part1.csv',
    usecols=['review_id', 'review_text'],   # match your CSV header
    encoding='cp932'                        # Shift‑JIS -> cp932 on Windows
)

# ======================================================
# 4. Interactive loop
# ======================================================

for idx in range(len(annotations), len(review_dataset)):
    # clear screen
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

    review_id  = review_dataset.iloc[idx, 0]
    sentence   = review_dataset.iloc[idx, 1]

    aspect, opinion, category = [], [], []

    answer = 'y'
    while answer.lower() in {'y', 'yes'}:
        print("\nThe sentence is: ", sentence, "\n")

        a = input("aspect: ")
        aspect.append(a)

        o = input("opinion: ")
        opinion.append(o)

        print("\n", aspect_category, "\n")

        # ---- entity label (1‑7) ----
        try:
            entity_index = int(input("Enter the entity label (1‑7):\n"))
        except ValueError:
            entity_index = 0
        while entity_index not in range(1, 8):
            try:
                entity_index = int(input("Invalid input. Enter entity label (1‑7):\n"))
            except ValueError:
                continue

        # ---- attribute label (1‑8) ----
        try:
            attribute_index = int(input("Enter the attribute label (1‑8):\n"))
        except ValueError:
            attribute_index = 0
        while attribute_index not in range(1, 9):
            try:
                attribute_index = int(input("Invalid input. Enter attribute label (1‑8):\n"))
            except ValueError:
                continue

        # Compose category
        entity    = aspect_category.iloc[entity_index - 1, 0]
        attribute = aspect_category.iloc[attribute_index - 1, 1]
        category.append(f"{entity}#{attribute}")

        print("\n" + "-" * 100 + "\n")

        answer = input("Do you wish to add another entry for the same sentence? Type 'y' or 'n':\n")
        # re‑prompt on invalid
        set1 = {'y', 'yes', 'n', 'no'}
        while answer.lower() not in set1:
            answer = input("Invalid input. Type 'y' or 'n':\n")

    # ---- Save one review block ----
    annotations.append({
        "ID":       review_id,
        "Sentence": sentence,
        "Aspect":   aspect,
        "Category": category,
        "Opinion":  opinion
    })

    with open('Annotation_test.json', 'w', encoding='utf-8') as f:
        json.dump(annotations, f, indent=3, ensure_ascii=False)

print("=== Finished ===")
