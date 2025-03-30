import csv
import os
import re
import sys
import xlrd

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


def find_index(tabel_head, key):
    tabel_head = [c.lower() for c in tabel_head]
    key = key.lower()
    assert key in tabel_head, f"{key} is not in the header of the file"
    for i, head in enumerate(tabel_head):
        if head == key:
            return i


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


def get_label_from_str(query_str, categories):
    query_str = re.sub(BOM_PATTERN, "", query_str)
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
    return cur_category_str, cur_item_str


def deal_xlsx(in_xlsx):
    out_lines = []
    workbook = xlrd.open_workbook(in_xlsx)
    sheet_names = workbook.sheet_names()
    table = workbook.sheet_by_index(0)

    categories = load_categories()
    nrows = table.nrows
    table_head = table.row_values(0)
    query_index = find_index(table_head, INPUT_CSV_START_PATTERN)
    new_tabel_head = table_head[:(query_index+1)] + ['label-1', 'label-2'] + table_head[(query_index+1):]
    out_lines.append(new_tabel_head)

    for row_num in range(1, nrows):
        row_value = table.row_values(row_num)
        query_str = str(row_value[query_index])
        cur_category_str, cur_item_str = get_label_from_str(query_str, categories)
        cur_line = row_value[:(query_index+1)] + [cur_category_str, cur_item_str] + row_value[(query_index+1):]
        out_lines.append(cur_line)
    return out_lines


def deal_csv(in_csv):
    out_lines = []
    categories = load_categories()
    with open(in_csv, 'r') as f:
        reader = csv.reader(f)
        rows = [row for row in reader]
    
    nrows = len(rows)
    table_head = rows[0]
    query_index = find_index(table_head, INPUT_CSV_START_PATTERN)
    new_tabel_head = table_head[:(query_index+1)] + ['label-1', 'label-2'] + table_head[(query_index+1):]
    out_lines.append(new_tabel_head)

    for row_num in range(1, nrows):
        row_value = rows[row_num]
        query_str = str(row_value[query_index])
        cur_category_str, cur_item_str = get_label_from_str(query_str, categories)
        cur_line = row_value[:(query_index+1)] + [cur_category_str, cur_item_str] + row_value[(query_index+1):]
        out_lines.append(cur_line)

    return out_lines

def write_to_csv(out_csv, out_lines):
    with open(out_csv, 'w') as f:
        writer = csv.writer(f)
        for row in out_lines:
            writer.writerow(row)


def test():
    in_file = "/Users/timye/codes/smart_labeling_tool/smart_labeling_tool/test/acecolor.csv"
    res = deal_csv(in_file)
    import pdb; pdb.set_trace()

def main():
    if_file = sys.argv[1]
    out_csv = sys.argv[2]
    assert os.path.exists(if_file), f"{if_file} does not exist"
    assert (if_file.endswith('.xlsx') or if_file.endswith('.csv')), f"File type must be .csv or .xlsx, we got {in_file}"

    if if_file.endswith('.xlsx'):
        lines = deal_xlsx(if_file)
    elif if_file.endswith('.csv'):
        lines = deal_csv(if_file)

    write_to_csv(out_csv, lines)
    print(f"Done! labels are extracted and written to file '{out_csv}'")


if __name__ == "__main__":
    main()
    # test()

