
# CONTRIBUTING 

이 프로젝트는 **Flask + MySQL 기반의 웹 가계부 서비스**입니다.  
누구나 이슈 제안, 코드 수정, 기능 추가 등을 통해 기여할 수 있습니다 

<br>

## Getting Started
### 1. Fork & Clone
1. 저장소를 자신의 GitHub 계정으로 **Fork** 합니다.  
2. 로컬로 복제합니다:

```bash
   git clone https://github.com/<your-username>/-5-.git
   cd -5-
```

3.  원본 저장소를 upstream으로 등록합니다:
    
```bash
git remote add upstream https://github.com/Gyeong-creator/-5-.git
```

> 쉬운 방법
1. `vscode`의 `시작하기` 창에서 `Git 레파지토리 복제` 클릭
2. 해당 레파지토리 주소 입력
    
 

<br>

### 2. 개발 환경 설정
**[ 파이썬 가상환경 설정 ]**
> 이 프로젝트는 **Python 3.10+** 및 **Flask** 프레임워크를 사용합니다.
가상환경 설정은 권장사항으로, 셋팅하지 않아도 기여할 수 있습니다!

```bash
# 가상환경 생성 및 활성화 (Mac/Linux)
python3 -m venv venv
source venv/bin/activate

# 필수 패키지 설치
pip install -r requirements.txt
```

<br>

**[ 데이터베이스 설정 ]**
> DB는 **MySQL**, `DBeaver`를 사용합니다.  

* 해당 파일 클릭 후 다운로드 > 압축해제: [db_backup.zip](https://github.com/user-attachments/files/23347467/db_backup.zip)

* 적용방법: DBeaver에서 `도구` > `Restore database` > 해당 파일의 sql 선택, log level = Normal > `Start`

<br>

**[ 기타 파일 설정 ]**
* `modules/__init__.py ` 생성, flask 폴더 인식을 위한 파일
	*  `.gitignore` 에 추가되어 수동 생성 필요
	*  파일 내용은 입력하지 않아도 됨(빈 파일)
* `modules/config.py` 파일에 로컬 DB 접속 정보, 중요 변수 값 저장 파일
	*  `.gitignore` 에 추가되어 수동 생성 필요
	* 아래의 내용을 입력
	* `secret`: 세션생성용 변수로, 영문과 숫자를 혼합하여 임의의 값을 입력하면 됨
```py
host = 'your_host'
port = your_port_number
user = 'your_user_name'
passwd = 'your_password!'
db = 'your_db_name'
secret = 'your_secret_key'
```


<br>
<br>

## 🌱 Branch Workflow

-   **main** → 배포용 (PR은 직접 머지 금지)
-   **develop** → 통합 개발 브랜치
-   **feature** → 새로운 기능 개발용 브랜치  
    예: `feature-statistics-chart`, `feature-login-api` 
-   **fix** → 버그 수정용 브랜치  
    예: `fix-transaction-delete`
    

### 브랜치 생성

```bash
git checkout develop
git pull origin develop
git checkout -b feature-<branch-name>
```

<br>

## Commit Message Convention

> 커밋 메시지는 [Conventional Commits](https://www.conventionalcommits.org/) 규칙을 따릅니다.

**형식:**  `<type>(<scope>): <subject>`    
**type 예시**
 * feat: 새로운 기능 추가
 * fix: 버그 수정
 * docs: 문서 수정 	
 * style: 코드 스타일 변경 	
 * refactor: 코드 구조 리팩토링 	
 * chore: 빌드/환경설정 변경

```
feat(ledger): 비용 지출 내역 조회기능 구현
fix(auth): 세션 만료 에러 처리
docs: 리드미 페이지 가이드 작성
```
* 참고: `<type>(<scope>)`영역은 영문 소문자로, `<subject>`영역은 한글로 작성

<br>

## Pull Request Guide

1.  모든 변경사항은 **`develop` 브랜치로 PR**을 생성합니다.
2.  PR 제목은 커밋 규칙과 동일하게 작성합니다.
3.  PR 본문에는 다음 정보를 포함해주세요:
    -   변경 내용 요약
    -   구현 또는 수정 이유
    -   테스트 방법
    -   관련 이슈 번호 (예: `Closes #15`)
    -   UI 변경 시 스크린샷 첨부
4.  최소 1명의 팀 리뷰어가 승인해야 병합됩니다.
    

**예시**
* https://github.com/Gyeong-creator/-5-/pull/13

```markdown
Closes #21(관련 이슈 넘버)
## 변경 사항 요약
- 

## 상세 설명
- 

## 변경 전/후
- ui변경이 있는 경우 이미지 첨부

### 테스트 방법

```

<br>
<br>

## Reporting Issues

- 버그, 개선 제안, 문서 수정 등 모든 기여는 **GitHub Issues**로 등록합니다.
- 이슈 제목은 명확히, 본문에는 아래 형식을 따라 주세요(일부 변경, 추가, 생략 가능):

- 예시: https://github.com/Gyeong-creator/-5-/issues/8

```markdown
## 요청사항
문제 또는 제안의 간단한 요약

## 구현 내용
1. ...
2. ...
3. ...

## 기대 결과
...

## 참고


```

- 라벨(Label)을 지정해주세요:  `bug`, `feature`, `enhancement`, `documentation`, `question`



