import os
import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import subprocess
import json
import time
import shutil


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from scripts.progress_window import ProgressWindow, ProgressUpdater

def clear_workspace():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    workspace_dir = os.path.join(base_dir, 'data', '작업대')
    
    if os.path.exists(workspace_dir):
        for filename in os.listdir(workspace_dir):
            file_path = os.path.join(workspace_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        os.makedirs(workspace_dir)

    print("Workspace cleared successfully.")

class WorkerThread(QThread):
    finished = pyqtSignal()

    def __init__(self, model_name, progress_updater):
        super().__init__()
        self.model_name = model_name
        self.progress_updater = progress_updater

    def run(self):
        config, check_list = load_model_settings(self.model_name)
        
        preprocess_keywords(self.progress_updater)
        
        keywords_df = load_keywords()
        
        first_draft_writing(self.model_name, keywords_df, self.progress_updater)
        rewrite_process(self.model_name, keywords_df, self.progress_updater)
        revision_process(self.model_name, self.progress_updater)
        
        self.progress_updater.update_progress("모든 과정이 완료되었습니다.")
        self.finished.emit()

def load_model_settings(model_name):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'data', 'model', model_name, 'config.json')
    check_list_path = os.path.join(base_dir, 'data', 'model', model_name, 'check_list.json')
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    with open(check_list_path, 'r', encoding='utf-8') as f:
        check_list = json.load(f)
    
    return config, check_list

def load_keywords():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    keywords_path = os.path.join(base_dir, 'data', 'keywords.xlsx')
    df = pd.read_excel(keywords_path)
    df['제목'] = df['제목'].fillna('').astype(str)
    return df

def save_keywords(keywords_df):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    keywords_path = os.path.join(base_dir, 'data', 'keywords.xlsx')
    keywords_df.to_excel(keywords_path, index=False)

def run_script(script_path, model_name, progress_updater, keyword=None):
    args = ['python', script_path, model_name]
    if keyword:
        args.append(keyword)
    
    try:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        timeout = 300
        start_time = time.time()
        
        output = ""
        while True:
            return_code = process.poll()
            if return_code is not None:
                stdout, stderr = process.communicate()
                output += stdout
                if return_code != 0:
                    progress_updater.update_progress(f"Error running {script_path}: {stderr}")
                else:
                    progress_updater.update_progress(f"Successfully ran {script_path}")
                break
            
            if time.time() - start_time > timeout:
                process.kill()
                progress_updater.update_progress(f"Timeout running {script_path}")
                break
            
            output_line = process.stdout.readline()
            if output_line:
                output += output_line
                progress_updater.update_progress(output_line.strip())
            
            time.sleep(0.1)
        
        return output
    
    except Exception as e:
        progress_updater.update_progress(f"Error running {script_path}: {str(e)}")
        return ""

def preprocess_keywords(progress_updater):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    preprocess_script = os.path.join(base_dir, 'scripts', 'preprocess_keywords.py')
    
    progress_updater.update_stage("키워드 전처리")
    progress_updater.update_progress("키워드 전처리 시작")
    
    result = run_script(preprocess_script, "", progress_updater)
    
    if "Keywords have been preprocessed" in result:
        progress_updater.update_progress("키워드 전처리 완료")
    else:
        progress_updater.update_progress(f"키워드 전처리 오류: {result}")

def first_draft_writing(model_name, keywords_df, progress_updater):
    progress_updater.update_stage("초벌작성")
    total_keywords = len(keywords_df)
    progress_updater.update_total_keywords(total_keywords)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    first_draft_script = os.path.join(base_dir, 'scripts', 'first_draft_writer.py')
    
    for index, row in enumerate(keywords_df.iterrows()):
        keyword = row[1]['제목']
        if pd.isna(keyword) or keyword == '':
            progress_updater.update_progress(f"Warning: Empty title found at index {index}")
            continue
        
        keyword = str(keyword)
        progress_updater.update_current_keyword(keyword)
        progress_updater.update_keywords_processed(index + 1)
        
        remaining_keywords = keywords_df['제목'][index+1:].dropna().astype(str).tolist()
        progress_updater.update_keywords_remaining(remaining_keywords)
        
        result = run_script(first_draft_script, model_name, progress_updater, keyword)
        
        prompt_start = result.find("Sending prompt: ")
        if prompt_start != -1:
            prompt = result[prompt_start + 16:].split("\n")[0]
            progress_updater.update_prompt(prompt)
        
        progress_updater.update_progress(f"{keyword} 초벌작성 완료")

def rewrite_process(model_name, keywords_df, progress_updater):
    progress_updater.update_stage("재작성")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rewrite_dir = os.path.join(base_dir, 'page2_checks', 'rewrite_scripts')
    
    all_passed = False
    iteration = 0
    while not all_passed:
        iteration += 1
        progress_updater.update_progress(f"재작성 iteration {iteration} 시작")
        
        for script in os.listdir(rewrite_dir):
            if script.endswith('.py'):
                script_path = os.path.join(rewrite_dir, script)
                run_script(script_path, model_name, progress_updater)
        
        keywords_df = load_keywords()
        failed_keywords = keywords_df[(keywords_df['글자수'] == 'X') | (keywords_df['금지어'] == 'X')]
        
        if failed_keywords.empty:
            all_passed = True
            progress_updater.update_progress("모든 키워드가 검사를 통과했습니다.")
        else:
            progress_updater.update_keywords_failed(failed_keywords['제목'].tolist())
            progress_updater.update_progress(f"{len(failed_keywords)}개의 키워드가 기준을 충족하지 못했습니다.")
            
            for check_type in ['글자수', '금지어']:
                failed_for_check = failed_keywords[failed_keywords[check_type] == 'X']
                if not failed_for_check.empty:
                    failed_titles = failed_for_check['제목'].tolist()
                    progress_updater.update_progress(f"{check_type} 미준수 키워드: {', '.join(failed_titles)}")
            
            progress_updater.update_progress("재작성을 시작합니다.")
            
            for index, row in failed_keywords.iterrows():
                keyword = row['제목']
                progress_updater.update_current_keyword(keyword)
                progress_updater.update_progress(f"{keyword} 재작성 중")
                
                first_draft_script = os.path.join(base_dir, 'scripts', 'first_draft_writer.py')
                run_script(first_draft_script, model_name, progress_updater, keyword)
                
                progress_updater.update_progress(f"{keyword} 재작성 완료")
                progress_updater.update_keywords_processed(index + 1)
        
        passed_keywords = keywords_df[(keywords_df['글자수'] == 'O') & (keywords_df['금지어'] == 'O')]
        progress_updater.update_keywords_passed(passed_keywords['제목'].tolist())
        progress_updater.update_keywords_processed(len(passed_keywords))
        progress_updater.update_keywords_remaining(failed_keywords['제목'].tolist())

        if iteration > 10:
            progress_updater.update_progress("최대 반복 횟수 초과. 재작성 과정을 종료합니다.")
            break

    progress_updater.update_progress("재작성 과정 완료")

def revision_process(model_name, progress_updater):
    progress_updater.update_stage("수정")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    revision_dir = os.path.join(base_dir, 'page2_checks', 'revision_scripts')
    
    for script in os.listdir(revision_dir):
        if script.endswith('.py'):
            script_path = os.path.join(revision_dir, script)
            progress_updater.update_progress(f"실행 중: {script}")
            result = run_script(script_path, model_name, progress_updater)
            progress_updater.update_progress(f"{script} 실행 완료")
            
            if "Processed and saved:" in result:
                processed_files = result.count("Processed and saved:")
                progress_updater.update_progress(f"{processed_files}개 파일 처리 완료")
                
                # 대체 단어 정보 추출 및 표시
                substitutions = [line for line in result.split('\n') if "Substituted:" in line]
                if substitutions:
                    progress_updater.update_progress("대체된 단어:")
                    for sub in substitutions:
                        progress_updater.update_progress(sub)
                else:
                    progress_updater.update_progress("대체할 단어가 없습니다.")
            else:
                progress_updater.update_progress(f"Warning: {script} 실행 결과 확인 필요")
    
    progress_updater.update_progress("수정 과정 완료")

def main(model_name):
    clear_workspace()
    app = QApplication(sys.argv)
    window = ProgressWindow(model_name)
    progress_updater = ProgressUpdater(window)
    window.show()

    worker = WorkerThread(model_name, progress_updater)
    worker.finished.connect(lambda: window.set_finished_state())
    worker.start()

    sys.exit(app.exec_())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python writing_sequence.py <model_name>")
        sys.exit(1)
    
    model_name = sys.argv[1]
    main(model_name)