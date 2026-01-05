#!/usr/bin/env python3
import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup


class ChosunEditorialScraperManual:
    def __init__(self, output_dir='articles'):
        self.output_dir = output_dir
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def sanitize_filename(self, text):
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        text = re.sub(r'\s+', '_', text)
        return text[:100]
    
    def extract_article_content(self, url):
        print(f"\nScraping: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = ''
            title_candidates = [
                soup.find('h1', class_=lambda x: x and 'headline' in str(x).lower()),
                soup.find('h1', class_=lambda x: x and 'title' in str(x).lower()),
                soup.find('h1'),
                soup.find('meta', property='og:title')
            ]
            
            for candidate in title_candidates:
                if candidate:
                    if candidate.name == 'meta':
                        title = candidate.get('content', '')
                    else:
                        title = candidate.get_text(strip=True)
                    if title:
                        break
            
            date = ''
            date_candidates = [
                soup.find('time'),
                soup.find(class_=lambda x: x and 'date' in str(x).lower()),
                soup.find('meta', property='article:published_time')
            ]
            
            for candidate in date_candidates:
                if candidate:
                    if candidate.name == 'meta':
                        date = candidate.get('content', '')
                    elif candidate.name == 'time':
                        date = candidate.get('datetime', '') or candidate.get_text(strip=True)
                    else:
                        date = candidate.get_text(strip=True)
                    if date:
                        break
            
            author = ''
            author_tag = soup.find(class_=lambda x: x and 'author' in str(x).lower())
            if author_tag:
                author = author_tag.get_text(strip=True)
            
            if not author:
                author_meta = soup.find('meta', attrs={'name': 'author'})
                if author_meta:
                    author = author_meta.get('content', '')
            
            content_paragraphs = []
            
            article_body = (
                soup.find('div', class_=lambda x: x and 'article-body' in str(x).lower()) or
                soup.find('div', class_=lambda x: x and 'story-body' in str(x).lower()) or
                soup.find('article', class_=lambda x: x and 'content' in str(x).lower()) or
                soup.find('div', class_=lambda x: x and 'content-body' in str(x).lower())
            )
            
            if article_body:
                for p in article_body.find_all('p', recursive=True):
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:
                        if not any(skip in text.lower() for skip in ['copyright', '©', '저작권', 'chosun.com']):
                            content_paragraphs.append(text)
            
            if not content_paragraphs:
                all_paragraphs = soup.find_all('p')
                for p in all_paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 30:
                        if not any(skip in text.lower() for skip in ['copyright', '©']):
                            content_paragraphs.append(text)
            
            return {
                'title': title,
                'date': date,
                'author': author,
                'content': content_paragraphs,
                'url': url
            }
        
        except Exception as e:
            print(f"  ✗ Error extracting content: {e}")
            return None
    
    def save_to_markdown(self, article_data):
        if not article_data or not article_data['title']:
            print("  ⚠️  No title found, skipping...")
            return False
        
        filename = self.sanitize_filename(article_data['title']) + '.md'
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {article_data['title']}\n\n")
            
            if article_data['date']:
                f.write(f"**날짜:** {article_data['date']}\n\n")
            
            if article_data['author']:
                f.write(f"**저자:** {article_data['author']}\n\n")
            
            f.write(f"**출처:** [{article_data['url']}]({article_data['url']})\n\n")
            f.write("---\n\n")
            
            if article_data['content']:
                for paragraph in article_data['content']:
                    f.write(f"{paragraph}\n\n")
            else:
                f.write("*본문 내용을 추출할 수 없습니다.*\n\n")
        
        print(f"  ✓ Saved to {filename}")
        return True
    
    def scrape_from_file(self, filepath):
        print(f"Reading URLs from {filepath}...")
        
        urls = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('http'):
                        urls.append(line)
        except Exception as e:
            print(f"Error reading file: {e}")
            return
        
        if not urls:
            print("No URLs found in file!")
            return
        
        self.scrape_urls(urls)
    
    def scrape_urls(self, urls):
        print(f"\nStarting to scrape {len(urls)} articles...\n")
        
        successful = 0
        failed = 0
        
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}]", end=' ')
            
            article_data = self.extract_article_content(url)
            if article_data and self.save_to_markdown(article_data):
                successful += 1
            else:
                print("  ✗ Failed to extract content")
                failed += 1
            
            time.sleep(1)
        
        print(f"\n{'=' * 50}")
        print(f"✓ Scraping complete!")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Articles saved to '{self.output_dir}/' directory")


def print_usage():
    print("""
Chosun Editorial Scraper (Manual Mode)

Usage:
  python scraper_manual.py <url1> <url2> ...
  python scraper_manual.py --file urls.txt

Options:
  <url>       One or more article URLs to scrape
  --file      Read URLs from a text file (one URL per line)

Examples:
  # Scrape single article
  python scraper_manual.py https://www.chosun.com/opinion/editorial/2025/01/05/ABC123/

  # Scrape multiple articles
  python scraper_manual.py https://www.chosun.com/opinion/editorial/2025/01/05/ABC/ https://www.chosun.com/opinion/editorial/2025/01/04/XYZ/

  # Scrape from file
  python scraper_manual.py --file urls.txt

Note: This scraper requires direct article URLs.
To automatically discover articles, please use scraper.py with Selenium.
""")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    scraper = ChosunEditorialScraperManual()
    
    if sys.argv[1] == '--file':
        if len(sys.argv) < 3:
            print("Error: --file option requires a filename")
            print_usage()
            sys.exit(1)
        scraper.scrape_from_file(sys.argv[2])
    elif sys.argv[1] in ['-h', '--help']:
        print_usage()
    else:
        urls = [arg for arg in sys.argv[1:] if arg.startswith('http')]
        if not urls:
            print("Error: No valid URLs provided")
            print_usage()
            sys.exit(1)
        scraper.scrape_urls(urls)
