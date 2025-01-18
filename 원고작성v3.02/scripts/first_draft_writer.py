import os
import pandas as pd
from docx import Document
import openai
import json
import time

from openai import OpenAI
client = OpenAI(api_key='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')

def load_json_data(model_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base_dir, "..", "data", "model", model_name)
    config_path = os.path.join(model_dir, "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_keywords():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    keywords_path = os.path.join(base_dir, "..", "data", "keywords.xlsx")
    if not os.path.exists(keywords_path):
        print(f"Keywords file does not exist: {keywords_path}")
        return pd.DataFrame()
    
    return pd.read_excel(keywords_path)

def ensure_directory_exists(folder_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, folder_name)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    return full_path

def save_responses_to_docx(folder_name, file_name, responses):
    folder_path = ensure_directory_exists(folder_name)
    file_path = os.path.join(folder_path, f"{file_name}.docx")
    
    retry_count = 3
    while retry_count > 0:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            
            doc = Document()
            
            for response in responses:
                doc.add_paragraph(response)
            
            doc.save(file_path)
            print(f"Responses saved to {file_path}")
            return
        except PermissionError as e:
            print(f"PermissionError: {e}")
            retry_count -= 1
            if retry_count > 0:
                print("Retrying after 1 second...")
                time.sleep(1)
            else:
                print("Maximum retries reached. Failed to save responses.")
                return

def chat_with_gpt_and_collect(prompt, model_config, chat_log=None):
    if chat_log is None:
        chat_log = []

    chat_log.append({'role': 'user', 'content': prompt})
    try:
        response = client.chat.completions.create(
            model=model_config["model"],
            messages=chat_log,
            temperature=float(model_config["temperature"]),
            max_tokens=int(model_config["max_tokens"]),
            top_p=float(model_config["top_p"]),
            frequency_penalty=float(model_config["frequency_penalty"]),
            presence_penalty=float(model_config["presence_penalty"])
        )
        
        gpt_response = response.choices[0].message.content.strip()
        print(f"Received response: {gpt_response}")
        chat_log.append({'role': 'assistant', 'content': gpt_response})
    except Exception as e:
        print("An error occurred:", e)
        gpt_response = f"An error occurred: {str(e)}"

    return gpt_response, chat_log

def generate_prompt(keyword1, keyword2, keyword3, template):
    if keyword2 and keyword3:
        prompt = template.format(키워드1=keyword1, 키워드2=keyword2, 키워드3=keyword3)
    elif keyword2:
        prompt = template.format(키워드1=keyword1, 키워드2=keyword2, 키워드3="")
    else:
        prompt = template.format(키워드1=keyword1, 키워드2="", 키워드3="")
    return prompt

def main(model_name, specific_keyword=None):
    data = load_json_data(model_name)
    config = data['model_config']
    prompts = data['prompts']
    folder_name = os.path.join("..", "data", "작업대")
    keywords_df = load_keywords()

    processed_files = set()

    if specific_keyword:
        keywords_to_process = keywords_df[keywords_df['제목'] == specific_keyword]
    else:
        keywords_to_process = keywords_df

    for _, keyword_pair in keywords_to_process.iterrows():
        keyword1 = str(keyword_pair.get('키워드1', '')).strip()
        keyword2 = str(keyword_pair.get('키워드2', '')).strip()
        keyword3 = str(keyword_pair.get('키워드3', '')).strip()
        title = keyword_pair.get('제목', '')
        print(f"Current keyword: {title}")
        
        if not keyword1:
            print(f"Stopping process as 키워드1 is empty.")
            break

        if title in processed_files:
            continue

        responses = []
        chat_log = []

        for template in prompts:
            prompt = generate_prompt(keyword1, keyword2, keyword3, template)
            print(f"Sending prompt: {prompt}")
            response, chat_log = chat_with_gpt_and_collect(prompt, config, chat_log)
            responses.append(response)
            print(f"Received response: {response}")
        
        save_responses_to_docx(folder_name, title, responses)
        processed_files.add(title)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python first_draft_writer.py <model_name> [specific_keyword]")
        sys.exit(1)
    
    model_name = sys.argv[1]
    specific_keyword = sys.argv[2] if len(sys.argv) > 2 else None
    main(model_name, specific_keyword)