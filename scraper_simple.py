#!/usr/bin/env python3
import os
import re
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup


class ChosunEditorialScraperSimple:
    def __init__(self, output_dir='articles'):
        self.base_url = 'https://www.chosun.com/opinion/editorial/'
        self.output_dir = output_dir
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def get_article_links_from_api(self):
        print("Trying to fetch articles via API...")
        
        api_url = "https://www.chosun.com/pf/api/v3/content/fetch/story-feed"
        
        params = {
            'query': '{"includeContentTypes":"story","excludeContentTypes":"gallery, video","includeSections":"/opinion/editorial","size":20}',
            'filter': '{"excludeContentTypes":["gallery","video"],"includeSections":["/opinion/editorial"]}'
        }
        
        try:
            response = requests.get(api_url, params=params, headers=self.headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                
                articles = []
                if 'content_elements' in data:
                    for item in data['content_elements']:
                        if 'canonical_url' in item:
                            url = item['canonical_url']
                            if not url.startswith('http'):
                                url = 'https://www.chosun.com' + url
                            articles.append(url)
                
                print(f"Found {len(articles)} articles from API")
                return articles
        except Exception as e:
            print(f"API fetch failed: {e}")
        
        return []
    
    def get_article_links_from_rss(self):
        print("Trying to fetch articles via RSS...")
        
        rss_url = "https://www.chosun.com/arc/outboundfeeds/rss/?outputType=xml&size=100"
        
        try:
            response = requests.get(rss_url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                
                items = soup.find_all('item')
                articles = []
                
                for item in items:
                    link_tag = item.find('link')
                    if link_tag:
                        url = link_tag.get_text(strip=True)
                        if '/opinion/editorial/' in url:
                            articles.append(url)
                
                print(f"Found {len(articles)} editorial articles from RSS")
                return articles
        except Exception as e:
            print(f"RSS fetch failed: {e}")
        
        return []
    
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
                        if not any(skip in text.lower() for skip in ['copyright', '©', '기자', '저작권']):
                            content_paragraphs.append(text)
            
            if not content_paragraphs:
                all_paragraphs = soup.find_all('p')
                for p in all_paragraphs:
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
        
        except Exception as e:
            print(f"  ✗ Error extracting content: {e}")
            return None
    
    def save_to_markdown(self, article_data):
        if not article_data or not article_data['title']:
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
        print("Chosun Editorial Scraper (Simple Version)")
        print("=" * 50)
        print()
        
        article_links = self.get_article_links_from_rss()
        
        if not article_links:
            article_links = self.get_article_links_from_api()
        
        if not article_links:
            print("\n⚠️  Could not fetch article links from API or RSS.")
            print("The website may require JavaScript rendering.")
            print("Please use the full scraper.py with Selenium instead.")
            print("\nTo set up Selenium:")
            print("  1. Run: ./setup.sh")
            print("  2. Run: python scraper.py")
            return
        
        print(f"\nStarting to scrape {len(article_links)} articles...\n")
        
        successful = 0
        failed = 0
        
        for i, link in enumerate(article_links, 1):
            print(f"[{i}/{len(article_links)}]", end=' ')
            
            article_data = self.extract_article_content(link)
            if article_data and article_data['content']:
                self.save_to_markdown(article_data)
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


if __name__ == '__main__':
    scraper = ChosunEditorialScraperSimple()
    scraper.run()
