#!/usr/bin/env python3
import os
import time
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


class ChosunEditorialScraper:
    def __init__(self, output_dir='articles'):
        self.base_url = 'https://www.chosun.com/opinion/editorial/'
        self.output_dir = output_dir
        self.driver = None
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
    
    def get_article_links(self):
        print(f"Fetching article list from {self.base_url}...")
        self.driver.get(self.base_url)
        
        time.sleep(5)
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        article_links = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            if '/opinion/editorial/' in href and href != self.base_url:
                if not href.startswith('http'):
                    href = urljoin(self.base_url, href)
                
                if href.count('/') >= 6 and any(year in href for year in ['2024', '2025', '2023']):
                    article_links.add(href)
        
        print(f"Found {len(article_links)} article links")
        return list(article_links)
    
    def sanitize_filename(self, text):
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        text = re.sub(r'\s+', '_', text)
        return text[:100]
    
    def extract_article_content(self, url):
        print(f"\nScraping: {url}")
        self.driver.get(url)
        
        time.sleep(3)
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        title = ''
        title_tag = soup.find('h1')
        if title_tag:
            title = title_tag.get_text(strip=True)
        
        if not title:
            title_tags = soup.find_all(['h1', 'h2'], class_=lambda x: x and ('title' in str(x).lower() or 'headline' in str(x).lower()))
            if title_tags:
                title = title_tags[0].get_text(strip=True)
        
        date = ''
        date_tag = soup.find('time')
        if date_tag:
            date = date_tag.get('datetime', '') or date_tag.get_text(strip=True)
        
        if not date:
            date_tags = soup.find_all(class_=lambda x: x and 'date' in str(x).lower())
            if date_tags:
                date = date_tags[0].get_text(strip=True)
        
        author = ''
        author_tag = soup.find(class_=lambda x: x and 'author' in str(x).lower())
        if author_tag:
            author = author_tag.get_text(strip=True)
        
        content_paragraphs = []
        
        article_body = soup.find('article') or soup.find('div', class_=lambda x: x and ('article' in str(x).lower() or 'content' in str(x).lower() or 'body' in str(x).lower()))
        
        if article_body:
            for p in article_body.find_all(['p', 'div'], class_=lambda x: not x or 'ad' not in str(x).lower()):
                text = p.get_text(strip=True)
                if text and len(text) > 20 and '©' not in text and 'copyright' not in text.lower():
                    content_paragraphs.append(text)
        else:
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if text and len(text) > 30:
                    content_paragraphs.append(text)
        
        return {
            'title': title,
            'date': date,
            'author': author,
            'content': content_paragraphs,
            'url': url
        }
    
    def save_to_markdown(self, article_data):
        if not article_data['title']:
            print("  ⚠️  No title found, skipping...")
            return
        
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
            
            for paragraph in article_data['content']:
                f.write(f"{paragraph}\n\n")
        
        print(f"  ✓ Saved to {filename}")
    
    def run(self):
        try:
            self.setup_driver()
            
            article_links = self.get_article_links()
            
            if not article_links:
                print("No articles found!")
                return
            
            print(f"\nStarting to scrape {len(article_links)} articles...\n")
            
            for i, link in enumerate(article_links, 1):
                print(f"[{i}/{len(article_links)}]", end=' ')
                
                try:
                    article_data = self.extract_article_content(link)
                    self.save_to_markdown(article_data)
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                
                time.sleep(2)
            
            print(f"\n✓ Scraping complete! Articles saved to '{self.output_dir}/' directory")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if self.driver:
                self.driver.quit()


if __name__ == '__main__':
    scraper = ChosunEditorialScraper()
    scraper.run()
