import os
import pandas as pd
from docx import Document
import json

def load_keywords():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    keywords_path = os.path.join(base_dir, 'data', 'keywords.xlsx')
    if not os.path.exists(keywords_path):
        raise FileNotFoundError(f"Keywords file does not exist: {keywords_path}")
    
    return pd.read_excel(keywords_path)

def load_check_list_settings(model_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    settings_path = os.path.join(base_dir, 'data', 'model', model_name, 'check_list.json')
    
    if not os.path.exists(settings_path):
        raise FileNotFoundError(f"Check list settings file does not exist: {settings_path}")
    
    with open(settings_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_forbidden_words(doc_path, forbidden_words):
    doc = Document(doc_path)
    content = ' '.join([para.text for para in doc.paragraphs])
    found_words = [word for word in forbidden_words if word in content]
    return len(found_words) == 0, found_words

def main(model_name):
    keywords_df = load_keywords()
    check_list_settings = load_check_list_settings(model_name)
    forbidden_words = check_list_settings["forbidden_words_check"]["forbidden_words"]
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    작업대_dir = os.path.join(base_dir, 'data', '작업대')
    
    for index, row in keywords_df.iterrows():
        title = row['제목']
        doc_path = os.path.join(작업대_dir, f"{title}.docx")
        if os.path.exists(doc_path):
            is_valid, found_words = check_forbidden_words(doc_path, forbidden_words)
            keywords_df.at[index, '금지어'] = 'O' if is_valid else 'X'
            print(f"Title: {title}, Valid: {'O' if is_valid else 'X'}, Found forbidden words: {', '.join(found_words)}")
        else:
            print(f"Document not found for title: {title}")
            keywords_df.at[index, '금지어'] = 'X'
    
    keywords_path = os.path.join(base_dir, 'data', 'keywords.xlsx')
    keywords_df.to_excel(keywords_path, index=False)
    print("Forbidden words check completed and results saved.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python forbiddenword_check.py <model_name>")
        sys.exit(1)
    
    model_name = sys.argv[1]
    main(model_name)