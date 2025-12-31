# scripts/issue_linker.py
import os
import requests
import subprocess
import re
import urllib.parse
import json
import textwrap

TIER_COLORS = {
    'Unrated': '333333', 'Bronze': 'ad5600', 'Silver': '435f7a',
    'Gold': 'ec9a00', 'Platinum': '27e2a4', 'Diamond': '00b4fc',
    'Ruby': 'ff0062', 'Master': 'b300e0'
}

def get_changed_files():
    """Git 변경 사항 또는 입력된 문제 번호에 해당하는 파일 검색"""
    target_id = os.environ.get('TARGET_ID', '').strip()
    
    # 1. 수동 실행 (문제 번호 입력 시)
    if target_id:
        print(f"🔎 [Manual] 문제 번호 {target_id}번 파일 검색 중...")
        found_files = []
        for root, _, files in os.walk("."):
            if ".git" in root: continue
            for file in files:
                if file.endswith(('.py', '.java', '.cpp', '.c', '.cc', '.js', '.ts')):
                    full_path = os.path.join(root, file)
                    # 경로 전체에서 아이디 검색
                    if str(target_id) in full_path:
                         found_files.append(full_path)
        return found_files

    # 2. 자동 실행 (Git 변경 파일 감지)
    try:
        # 한글 깨짐 방지 설정 후 실행
        subprocess.run(["git", "config", "--global", "core.quotepath", "false"])
        cmd = "git diff --name-only HEAD~1 HEAD"
        output = subprocess.check_output(cmd, shell=True).decode('utf-8')
        return [f.strip().strip('"') for f in output.split('\n') if f.strip()]
    except subprocess.CalledProcessError:
        print("⚠️ 이전 커밋을 찾을 수 없어 변경된 파일을 감지하지 못했습니다.")
        return []

def get_problem_info(problem_id):
    url = f"https://solved.ac/api/v3/problem/show?problemId={problem_id}"
    try:
        res = requests.get(url, headers={"Content-Type": "application/json"}, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f"❌ Solved.ac API Error: {e}")
    return None

def get_existing_issue_url(problem_id):
    """이미 존재하는 이슈가 있는지 검색"""
    cmd = [
        "gh", "issue", "list",
        "--search", f"{problem_id} in:title",
        "--repo", os.environ['REPO'],
        "--json", "url",
        "--limit", "1"
    ]
    try:
        output = subprocess.check_output(cmd).decode('utf-8')
        result = json.loads(output)
        return result[0]['url'] if result else None
    except:
        return None

def update_readme(readme_path, issue_url):
    """README에 이슈 링크 추가"""
    if not os.path.exists(readme_path):
        print(f"⚠️ README 없음: {readme_path}")
        return False
    
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if issue_url in content:
        return False # 이미 링크가 존재함
    
    with open(readme_path, "a", encoding="utf-8") as f:
        f.write(f"\n<br>\n\n### 💡 [노트] 풀이 보러가기\n")
        f.write(f"- [Github Issue 링크]({issue_url})\n")
    
    print(f"✅ README 업데이트: {readme_path}")
    return True

def create_issue(pid, file_path, data):
    repo = os.environ['REPO']
    branch = os.environ['BRANCH']
    
    title_ko = data['titleKo']
    level = data['level']
    
    # 뱃지 생성
    if level == 0: badge_name, badge_color = "Unrated", TIER_COLORS['Unrated']
    else:
        tiers = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Ruby']
        tier_idx = (level - 1) // 5
        tier_num = 5 - ((level - 1) % 5)
        # 인덱스 에러 방지
        if tier_idx < len(tiers):
            tier_name = tiers[tier_idx]
            badge_name = f"{tier_name} {tier_num}"
            badge_color = TIER_COLORS[tier_name]
        else:
             badge_name, badge_color = "Master", TIER_COLORS['Master']
    
    tier_badge_url = f"https://img.shields.io/badge/{badge_name.replace(' ', '%20')}-{badge_color}?style=flat-square&logo=solved.ac&logoColor=white"
    tags = ", ".join([f"`{t['displayNames'][0]['name']}`" for t in data['tags']])
    
    encoded_path = urllib.parse.quote(file_path)
    code_url = f"https://github.com/{repo}/blob/{branch}/{encoded_path}"
    problem_link = f"https://www.acmicpc.net/problem/{pid}"
    
    issue_title = f"[BOJ] {pid}번 {title_ko} - {badge_name}"
    issue_body = textwrap.dedent(f"""\
        # {issue_title}

        ![Tier]({tier_badge_url})

        | 문제 정보 | 바로가기 |
        | :-: | :-: |
        | **난이도** | {badge_name} |
        | **문제 번호** | {pid} |
        | **태그** | {tags} |

        <br>

        ### 🔗 링크
        - [문제 풀러 가기]({problem_link})
        - [내 정답 코드 보기 (Github)]({code_url})

        <br>

        ## 1. 문제 파악
        - 

        ## 2. 접근 방법
        1. 
        2. 

        ## 3. 코드 구현 시 주의점
        - 

        ## 4. 배우고 느낀 점
        - 
    """)
    
    # 이슈 생성 명령
    cmd = [
        "gh", "issue", "create",
        "--title", issue_title,
        "--body", issue_body,
        "--repo", repo
    ]
    
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            return proc.stdout.strip()
        else:
            print(f"❌ 이슈 생성 실패: {proc.stderr}")
    except Exception as e:
        print(f"❌ 시스템 에러: {e}")
    return None

def main():
    files = get_changed_files()
    processed_ids = set()
    changes_made = False

    print(f"🔍 감지된 파일: {files}")

    for file_path in files:
        numbers = re.findall(r'(\d+)', file_path)
        if not numbers: continue
        
        # 백준 문제 번호는 보통 1000번 이상임
        pid = 0
        for num in numbers:
            if int(num) >= 1000:
                pid = int(num)
                break
        
        if pid == 0 or pid in processed_ids: continue

        print(f"-------------------------------------------")
        print(f"🚀 처리 중: {pid}번 (파일: {file_path})")
        
        # README 경로 찾기
        dir_path = os.path.dirname(file_path)
        readme_path = os.path.join(dir_path, "README.md")
        
        issue_url = get_existing_issue_url(pid)

        if not issue_url:
            data = get_problem_info(pid)
            if data:
                print(f"✨ 새 이슈 생성 시도: {pid}번")
                issue_url = create_issue(pid, file_path, data)
                if issue_url:
                    print(f"🎉 이슈 생성 완료: {issue_url}")
            else:
                print(f"❌ 문제 정보를 가져올 수 없음: {pid}")
        else:
            print(f"ℹ️ 이미 존재하는 이슈: {issue_url}")

        if issue_url and update_readme(readme_path, issue_url):
            subprocess.run(["git", "add", readme_path])
            changes_made = True
        
        processed_ids.add(pid)

    if changes_made:
        print("💾 변경사항 커밋 및 푸시 중...")
        subprocess.run(["git", "commit", "-m", "Auto: Link Github Issue to README"])
        subprocess.run(["git", "push"])
    else:
        print("💤 변경사항 없음 (README 업데이트 내역 없음)")

if __name__ == "__main__":
    main()
