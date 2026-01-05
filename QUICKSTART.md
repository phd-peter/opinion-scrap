# Quick Start Guide

조선일보 사설 스크래퍼를 빠르게 시작하는 방법입니다.

## 가장 빠른 방법 (추천)

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 스크래퍼 선택

#### Option A: 자동 스크래핑 (Selenium - 권장)

Chrome/Chromium이 설치되어 있어야 합니다.

```bash
# 설정 (최초 1회)
./setup.sh

# 스크래핑 실행
python scraper.py
```

#### Option B: 간단한 방법 (RSS - 빠르지만 제한적)

```bash
python scraper_simple.py
```

#### Option C: 수동 URL 입력

1. 브라우저에서 https://www.chosun.com/opinion/editorial/ 방문
2. 원하는 기사 URL 복사
3. 스크래퍼 실행:

```bash
# 하나의 기사
python scraper_manual.py https://www.chosun.com/opinion/editorial/2025/01/05/ARTICLE_ID/

# 여러 기사
python scraper_manual.py url1 url2 url3

# 파일로부터 (urls.txt 파일에 URL 저장)
python scraper_manual.py --file urls.txt
```

### 3. 결과 확인

```bash
ls articles/
```

모든 기사가 Markdown 형식(.md)으로 `articles/` 폴더에 저장됩니다.

## 문제 해결

### Chrome이 없다는 오류
```bash
sudo apt-get install chromium-browser  # Ubuntu/Debian
brew install chromium                   # macOS
```

### RSS로 기사를 못 찾음
Selenium 버전(`scraper.py`)을 사용하거나, 수동 URL 입력 방식(`scraper_manual.py`)을 사용하세요.

## 더 자세한 정보

자세한 문서는 [README.md](README.md)를 참조하세요.
