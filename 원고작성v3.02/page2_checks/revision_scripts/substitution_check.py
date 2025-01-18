import os
import json
from docx import Document
import re

def load_check_list(model_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    check_list_path = os.path.join(base_dir, 'data', 'model', model_name, 'check_list.json')
    if os.path.exists(check_list_path):
        with open(check_list_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"The check list file {check_list_path} does not exist.")

def substitute_words(doc, substitution_list):
    substitutions_made = []
    for paragraph in doc.paragraphs:
        for sub_pair in substitution_list:
            for original, replacement in sub_pair.items():
                pattern = r'(\w*?)' + re.escape(original) + r'(\w*?)'
                def replace_func(match):
                    prefix, suffix = match.group(1), match.group(2)
                    return prefix + replacement + suffix
                new_text, count = re.subn(pattern, replace_func, paragraph.text)
                if count > 0:
                    substitutions_made.append(f"Substituted: '{original}' with '{replacement}' ({count} occurrences)")
                paragraph.text = new_text
    return substitutions_made

def process_documents(model_name):
    check_list = load_check_list(model_name)
    substitution_list = check_list.get('substitution_pairs', {}).get('substitution_list', [])

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    source_dir = os.path.join(base_dir, 'data', '작업대')
    if not os.path.exists(source_dir):
        print(f"Source directory {source_dir} does not exist.")
        return

    for filename in os.listdir(source_dir):
        if filename.endswith('.docx'):
            docx_path = os.path.join(source_dir, filename)
            doc = Document(docx_path)
            substitutions = substitute_words(doc, substitution_list)
            doc.save(docx_path)
            print(f"Processed and saved: {filename}")
            for sub in substitutions:
                print(sub)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python substitution_check.py <model_name>")
        sys.exit(1)
    model_name = sys.argv[1]
    process_documents(model_name)