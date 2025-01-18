import os
import pandas as pd

def preprocess_keywords():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    keywords_path = os.path.join(base_dir, "..", "data", "keywords.xlsx")
    
    if not os.path.exists(keywords_path):
        print(f"Keywords file does not exist: {keywords_path}")
        return
    
    keywords_df = pd.read_excel(keywords_path)
    
    # Check if the required columns exist
    required_columns = ['키워드1', '키워드2', '키워드3', '제목']
    for col in required_columns:
        if col not in keywords_df.columns:
            print(f"Column '{col}' does not exist in the keywords file.")
            return

    keyword_count = {}
    for index, row in keywords_df.iterrows():
        keyword1 = row['키워드1'].strip() if pd.notna(row['키워드1']) else ""
        
        if keyword1:
            if keyword1 in keyword_count:
                keyword_count[keyword1] += 1
                new_title = f"{keyword1}_{keyword_count[keyword1]}"
            else:
                keyword_count[keyword1] = 1
                new_title = keyword1

            keywords_df.at[index, '제목'] = new_title

    keywords_df.to_excel(keywords_path, index=False)
    print("Keywords have been preprocessed and duplicates have been renamed.")

if __name__ == "__main__":
    preprocess_keywords()
