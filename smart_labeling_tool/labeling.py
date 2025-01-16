import csv
import os
import re
import sys

from collections import defaultdict

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ATTRIBUTION_DIR = os.path.join(THIS_DIR, 'attributes')
BOM_PATTERN = "\ufeff"
INPUT_CSV_START_PATTERN = "query"

COLOR_PATH = os.path.join(ATTRIBUTION_DIR, "color.txt")
MATERIAL_PATH = os.path.join(ATTRIBUTION_DIR, "material.txt")
STYLE_PATH = os.path.join(ATTRIBUTION_DIR, "style.txt")
FUNCTION_PATH = os.path.join(ATTRIBUTION_DIR, "function.txt")
OCCASION_PATH = os.path.join(ATTRIBUTION_DIR, "occasion.txt")
BRAND_PATH = os.path.join(ATTRIBUTION_DIR, "brand.txt")
PATTERN_PATH = os.path.join(ATTRIBUTION_DIR, "pattern.txt")


def get_label_from_file(file_in):
    if not os.path.exists(file_in):
        return set()
    labels = set()
    with open(file_in, 'r') as f:
        for line in f:
            label = line.strip().lower()
            if label == "":
                continue
            labels.add(label)
    return labels

def load_categories():
    color = get_label_from_file(COLOR_PATH)
    function = get_label_from_file(FUNCTION_PATH)
    material = get_label_from_file(MATERIAL_PATH)
    style = get_label_from_file(STYLE_PATH)
    occasion = get_label_from_file(OCCASION_PATH)
    brand = get_label_from_file(BRAND_PATH)
    pattern = get_label_from_file(PATTERN_PATH)

    categories = {
        'color': color,
        'function': function,
        'material': material,
        'style': style,
        'occasion': occasion,
        'brand': brand,
        'pattern': pattern,
    }
    return categories

def categorize(query_str, categories):
    res_dict = defaultdict(list)
    for category, labels in categories.items():
        for label in labels:
            label = label.lower()
            query_str = query_str.lower()
            if label in query_str:
                res_dict[category].append(label)
    if len(res_dict) == 0:
        res_dict['general'] = []
    return res_dict

def main():
    in_csv = sys.argv[1]
    out_csv = sys.argv[2]
    out_lines = []

    categories = load_categories()
    with open(in_csv, 'r') as f:
        for line in f:
            query_str = line.strip().rstrip(',')
            if query_str == "Query,label":
                continue
            query_str = re.sub(BOM_PATTERN, "", query_str)
            if query_str.lower() == INPUT_CSV_START_PATTERN:
                continue
            cur_category = categorize(query_str, categories)
            category_list = []
            item_list = []
            for category in cur_category:
                items = cur_category[category]
                if len(items) == 0:
                    items_str = ""
                else:
                    items_str = ','.join(items)
                category_list.append(category)
                item_list.append(items_str)
            cur_category_str = "|".join(category_list)
            cur_item_str = "|".join(item_list)
            out_lines.append([query_str, cur_category_str, cur_item_str])

    with open(out_csv, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['query', 'label-1', 'label-2'])
        for row in out_lines:
            writer.writerow(row)

if __name__ == "__main__":
    main()

# # Process all 1000 search terms
# categorized_terms = [categorize(term) for term in search_terms]

# # Print the categorized terms (one per line)
# for term in categorized_terms:
#   print(term)
