# Chosun Editorial Scraper

조선일보 사설 페이지(https://www.chosun.com/opinion/editorial/)의 기사들을 자동으로 스크랩하여 Markdown 파일로 저장하는 스크립트입니다.

## 주요 기능

- 조선일보 사설 페이지에서 기사 목록을 가져옵니다
- 각 기사의 본문 내용을 추출합니다
- 제목, 날짜, 저자, 본문을 포함한 Markdown 파일로 저장합니다
- 각 기사는 별도의 `.md` 파일로 저장됩니다

## 스크래퍼 종류

이 프로젝트는 3가지 스크래퍼를 제공합니다:

### 1. **scraper.py** (권장 - Selenium 사용)
가장 강력한 방법으로, JavaScript로 동적 로딩되는 페이지를 완전히 렌더링합니다.

**장점:**
- 자동으로 사설 목록 페이지에서 모든 기사 링크를 추출
- JavaScript 렌더링 완벽 지원
- 가장 신뢰성 높음

**단점:**
- Chrome/Chromium 브라우저 설치 필요
- 약간 느림

**사용법:**
```bash
# 설정 스크립트 실행 (최초 1회)
./setup.sh

# 스크래퍼 실행
python scraper.py
```

### 2. **scraper_simple.py** (간단한 방법 - RSS 사용)
RSS 피드를 통해 기사를 가져옵니다. 브라우저가 필요 없습니다.

**장점:**
- 추가 소프트웨어 설치 불필요
- 빠른 실행 속도

**단점:**
- RSS에 사설 기사가 포함되지 않을 수 있음
- 최신 기사만 제공될 수 있음

**사용법:**
```bash
python scraper_simple.py
```

### 3. **scraper_manual.py** (수동 URL 입력)
직접 기사 URL을 제공하여 스크랩합니다.

**장점:**
- 특정 기사만 선택적으로 스크랩 가능
- 추가 소프트웨어 불필요

**단점:**
- 기사 URL을 수동으로 수집해야 함

**사용법:**
```bash
# 단일 기사
python scraper_manual.py https://www.chosun.com/opinion/editorial/2025/01/05/...

# 여러 기사
python scraper_manual.py url1 url2 url3

# 파일에서 읽기
python scraper_manual.py --file urls.txt
```

## 설치 방법

### 1. Python 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. (scraper.py 사용 시) Chrome/Chromium 설치

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install chromium-browser
```

**macOS:**
```bash
brew install chromium
```

**Windows:**
Chrome 브라우저를 다운로드하여 설치: https://www.google.com/chrome/

또는 자동 설치 스크립트 사용:
```bash
./setup.sh
```

## 출력 형식

모든 기사는 `articles/` 디렉토리에 Markdown 형식으로 저장됩니다:

```markdown
# 기사 제목

**날짜:** 2025-01-05

**저자:** 조선일보

**출처:** [https://www.chosun.com/...](https://www.chosun.com/...)

---

본문 단락 1

본문 단락 2

...
```

## 고급 사용법

### 출력 디렉토리 변경

스크립트 파일을 수정하여 `output_dir` 매개변수를 변경할 수 있습니다:

```python
scraper = ChosunEditorialScraper(output_dir='my_articles')
```

### 스크래핑 지연 시간 조정

서버 부하를 줄이기 위해 각 스크립트에 지연 시간이 설정되어 있습니다.
필요시 `time.sleep()` 값을 조정할 수 있습니다.

## 문제 해결

### scraper.py 오류

**문제:** `ChromeDriver error` 또는 `Chrome not found`
**해결:** Chrome/Chromium이 설치되어 있는지 확인하고 `./setup.sh`를 실행하세요.

### scraper_simple.py가 기사를 찾지 못함

**문제:** RSS 피드에 사설 기사가 없음
**해결:** 
1. `scraper.py`(Selenium 버전)를 사용하세요.
2. 또는 수동으로 기사 URL을 수집하여 `scraper_manual.py`를 사용하세요.

### 기사 내용이 제대로 추출되지 않음

**문제:** 웹사이트 구조가 변경됨
**해결:** 스크립트의 CSS 선택자를 업데이트해야 할 수 있습니다. GitHub Issues에 보고해주세요.

## 주의사항

1. **법적 책임**: 이 스크래퍼는 교육 및 개인 연구 목적으로만 사용하세요.
2. **서버 부하**: 과도한 요청은 서버에 부담을 주고 IP 차단의 원인이 될 수 있습니다.
3. **이용 약관**: 조선일보의 이용 약관을 준수하세요.
4. **저작권**: 스크랩한 콘텐츠의 저작권은 조선일보에 있습니다.

## 기술 스택

- **Python 3.8+**
- **requests**: HTTP 요청
- **BeautifulSoup4**: HTML 파싱
- **lxml**: XML 파싱
- **Selenium**: 브라우저 자동화 (선택사항)

## 라이센스

MIT License - 교육 및 연구 목적으로 자유롭게 사용하실 수 있습니다.

## 기여

버그 리포트, 기능 제안, 풀 리퀘스트를 환영합니다!

## 예제 워크플로우

### 방법 1: 완전 자동 (권장)

```bash
# 1. 설정 (최초 1회만)
./setup.sh

# 2. 스크랩 실행
python scraper.py

# 3. 결과 확인
ls articles/
```

### 방법 2: 수동 URL 수집

```bash
# 1. 기사 URL 수집 (브라우저에서 수동으로)
# https://www.chosun.com/opinion/editorial/ 페이지 방문
# 원하는 기사 URL을 복사하여 urls.txt 파일에 저장

# 2. 스크랩 실행
python scraper_manual.py --file urls.txt

# 3. 결과 확인
ls articles/
```

## 버전 정보

- **v1.0.0**: 초기 릴리스
  - Selenium 기반 자동 스크래퍼
  - RSS 기반 간단한 스크래퍼
  - 수동 URL 입력 스크래퍼
