#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Core Scraper API for ArabSeed
----------------------------
Handles searching, details fetching, mirror rotation, and link decryption.
"""

import re
import base64
import urllib.parse
import time
from typing import List, Dict, Union, Optional
import requests
from bs4 import BeautifulSoup

# Pre-defined mirror list for failover rotation
MIRRORS = [
    "https://m.asd.ink",
    "https://m.arabseed.show",
    "https://arabseed.show",
    "https://arabseed.live"
]

class ArabSeedAPI:
    """
    A robust, high-performance API client to interact with ArabSeed mirrors,
    scrape search results, series episodes, and decode download/stream links.
    """
    
    def __init__(self, base_url: str = "https://m.asd.ink", timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Referer": self.base_url + "/"
        }
        self.session.headers.update(self.headers)
        
    def set_mirror(self, url: str):
        """Changes the active mirror base URL."""
        self.base_url = url.rstrip('/')
        self.session.headers.update({"Referer": self.base_url + "/"})

    def test_connection(self, url: Optional[str] = None) -> Union[bool, float]:
        """
        Tests if a mirror is responsive and returns its latency in userds.
        If connection fails, returns False.
        """
        target = url.rstrip('/') if url else self.base_url
        start_time = time.time()
        try:
            r = self.session.get(target, timeout=5)
            if r.status_code == 200:
                return time.time() - start_time
            return False
        except Exception:
            return False

    def auto_fallback_mirror(self) -> bool:
        """
        Attempts to find a working mirror from the pre-defined list.
        Measures latencies and selects the fastest responsive mirror.
        """
        latencies = {}
        
        # Test current one first
        current_lat = self.test_connection()
        if current_lat is not False:
            latencies[self.base_url] = current_lat
            
        # Test other mirrors
        for mirror in MIRRORS:
            if mirror.rstrip('/') == self.base_url:
                continue
            lat = self.test_connection(mirror)
            if lat is not False:
                latencies[mirror.rstrip('/')] = lat
                
        if not latencies:
            return False
            
        # Select fastest (lowest latency)
        fastest_mirror = min(latencies, key=latencies.get)
        self.set_mirror(fastest_mirror)
        return True

    def decode_link(self, obfuscated_url: str) -> str:
        """
        Decodes the base64-obfuscated download or watch links used by ArabSeed.
        Example: https://m.asd.ink/l/aHR0cHM6Ly9tLnJldmlld3JhdGUubmV0L2ZxcGM5OGoyNnRydQ==
        returns: https://m.reviewrate.net/fqpc98j26tru
        """
        if not obfuscated_url:
            return ""
            
        if "/l/" in obfuscated_url:
            try:
                parts = obfuscated_url.split("/l/")
                if len(parts) > 1:
                    b64_part = parts[1].rstrip('/')
                    b64_part = urllib.parse.unquote(b64_part)
                    
                    # Fix missing base64 padding
                    missing_padding = len(b64_part) % 4
                    if missing_padding:
                        b64_part += '=' * (4 - missing_padding)
                        
                    decoded_bytes = base64.b64decode(b64_part)
                    decoded_url = decoded_bytes.decode('utf-8', errors='ignore')
                    return decoded_url
            except Exception:
                return obfuscated_url
        return obfuscated_url

    def search(self, query: str) -> List[Dict[str, str]]:
        """
        Searches ArabSeed for movies, series, or music.
        Returns a list of structured dictionaries containing item metadata.
        """
        if not query or not query.strip():
            return []
            
        search_url = f"{self.base_url}/find/"
        params = {"word": query}
        
        try:
            r = self.session.get(search_url, params=params, timeout=self.timeout)
            r.raise_for_status()
        except Exception as e:
            # Try mirror fallback if request fails
            if self.auto_fallback_mirror():
                search_url = f"{self.base_url}/find/"
                r = self.session.get(search_url, params=params, timeout=self.timeout)
            else:
                raise Exception(f"Failed to connect to ArabSeed mirrors: {e}")
                
        soup = BeautifulSoup(r.text, "html.parser")
        blocks = soup.find_all(class_="movie__block")
        
        results = []
        for block in blocks:
            href = block.get("href")
            if not href:
                continue
                
            url = href
            if url.startswith('/'):
                url = self.base_url + url
                
            # Extract poster image safely
            img_tag = block.find("img")
            poster = ""
            if img_tag:
                poster = img_tag.get("data-src") or img_tag.get("src") or ""
                
            # Extract Title (Arabic) safely
            title_tag = block.find(class_="post__name") or block.find("h3")
            title = title_tag.get_text(strip=True) if title_tag else "غير معروف"
            
            # Extract Rating safely
            rating_tag = block.find(class_="post__ratings") or block.find(class_="rating")
            rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"
            
            # Extract Quality Badge safely
            quality_tag = block.find(class_="badge__quality") or block.find(class_="quality")
            quality = quality_tag.get_text(strip=True) if quality_tag else "غير محدد"
            
            # Detect Media Type from title/URL
            media_type = "فيلم"
            if "مسلسل" in title or "s1" in url.lower() or "s2" in url.lower() or "season" in url.lower() or "eps" in url.lower():
                media_type = "مسلسل / حلقة"
            elif "اغنية" in title.lower() or "أغنية" in title or "track" in url.lower() or "song" in url.lower():
                media_type = "موسيقى / أغنية"
            elif "عرض" in title or "wwe" in url.lower() or "مصارعة" in title:
                media_type = "برنامج / مصارعة"
            elif "مسرحية" in title:
                media_type = "مسرحية"
                
            results.append({
                "title": title,
                "url": url,
                "poster": poster,
                "rating": rating,
                "quality": quality,
                "type": media_type
            })
            
        return results

    def get_details(self, item_url: str) -> Dict[str, Union[str, bool, List[Dict[str, str]]]]:
        """
        Fetches the details page of an item.
        Detects if it's a series and extracts all other episodes.
        """
        try:
            r = self.session.get(item_url, timeout=self.timeout)
            r.raise_for_status()
        except Exception as e:
            raise Exception(f"Failed to fetch details page: {e}")
            
        soup = BeautifulSoup(r.text, "html.parser")
        
        episodes_list = []
        is_series = False
        
        # Look for the episodes container safely
        ep_section = soup.find(class_="episodes__list") or soup.find(class_=lambda x: x and "episode" in x.lower())
        if ep_section:
            is_series = True
            anchors = ep_section.find_all("a")
            for a in anchors:
                href = a.get("href")
                if not href:
                    continue
                if href.startswith('/'):
                    href = self.base_url + href
                    
                num_div = a.find(class_="epi__num")
                if num_div:
                    ep_title = num_div.get_text(" ", strip=True)
                else:
                    ep_title = a.get_text(strip=True)
                    
                active = "active" in a.get("class", [])
                
                episodes_list.append({
                    "title": ep_title,
                    "url": href,
                    "active": active
                })
        
        # Parse description safely
        desc_el = soup.find(class_="story") or soup.find(class_="story__content") or soup.find(class_="inner__data")
        description = desc_el.get_text(strip=True) if desc_el else "لا يوجد وصف متوفر."
        
        # Check for direct download/watch button hrefs safely
        download_btn = soup.find("a", class_=re.compile("download"))
        download_page_url = download_btn.get("href") if download_btn else (item_url.rstrip('/') + "/download/")
        
        watch_btn = soup.find("a", class_=re.compile("watch"))
        watch_page_url = watch_btn.get("href") if watch_btn else (item_url.rstrip('/') + "/watch/")

        return {
            "title": soup.find("h1").get_text(strip=True) if soup.find("h1") else "غير معروف",
            "is_series": is_series,
            "episodes": episodes_list,
            "description": description,
            "download_page": download_page_url,
            "watch_page": watch_page_url
        }

    def get_download_links(self, detail_url: str) -> List[Dict[str, str]]:
        """
        Navigates to the download sub-page, extracts all mirrors,
        decodes them, and returns direct high-speed download links.
        """
        if not detail_url.rstrip('/').endswith('/download'):
            download_url = detail_url.rstrip('/') + "/download/"
        else:
            download_url = detail_url
            
        try:
            r = self.session.get(download_url, timeout=self.timeout)
            r.raise_for_status()
        except Exception as e:
            raise Exception(f"Failed to fetch download sub-page: {e}")
            
        soup = BeautifulSoup(r.text, "html.parser")
        dl_list = soup.find(class_="downloads__links__list")
        
        links = []
        
        if dl_list:
            items = dl_list.find_all("li")
            for item in items:
                a_tag = item.find("a")
                if not a_tag:
                    continue
                    
                obfuscated_url = a_tag.get("href") or ""
                raw_text = a_tag.get_text(strip=True)
                
                decoded_url = self.decode_link(obfuscated_url)
                
                quality = "غير محدد"
                quality_match = re.search(r'(\d+p)', raw_text)
                if quality_match:
                    quality = quality_match.group(1)
                    
                host = raw_text.split("التحميل")[0].strip()
                if not host:
                    host = "سيرفر مباشر"
                
                size_tag = item.find(class_="size") or item.find(class_="badge__size")
                size = size_tag.get_text(strip=True) if size_tag else "غير معروف"
                
                links.append({
                    "server": host,
                    "quality": quality,
                    "size": size,
                    "direct_link": decoded_url
                })
        else:
            # Fallback if standard classes aren't present
            anchors = soup.find_all("a")
            for a in anchors:
                href = a.get("href") or ""
                text = a.get_text(strip=True)
                if "/l/" in href or ("تحميل" in text and href.startswith("http")):
                    decoded = self.decode_link(href)
                    links.append({
                        "server": "سيرفر خارجي" if not "/l/" in href else "سيرفر مباشر مرمز",
                        "quality": "غير محدد",
                        "size": "غير معروف",
                        "direct_link": decoded
                    })
                    
        return links

    def get_watch_links(self, detail_url: str) -> List[Dict[str, str]]:
        """
        Navigates to the watch sub-page, extracts the primary stream player
        and other embedded stream servers, decodes them, and returns direct stream links.
        """
        if not detail_url.rstrip('/').endswith('/watch'):
            watch_url = detail_url.rstrip('/') + "/watch/"
        else:
            watch_url = detail_url
            
        try:
            r = self.session.get(watch_url, timeout=self.timeout)
            r.raise_for_status()
        except Exception as e:
            # Fallback to scraping the detail page directly
            watch_url = detail_url
            try:
                r = self.session.get(watch_url, timeout=self.timeout)
                r.raise_for_status()
            except Exception:
                raise Exception(f"Failed to fetch watch sub-page: {e}")
            
        soup = BeautifulSoup(r.text, "html.parser")
        links = []
        
        # 1. Scrape standard play iframes with play.php?url=
        iframes = soup.find_all("iframe")
        for iframe in iframes:
            src = iframe.get("src") or ""
            if "play.php?url=" in src:
                try:
                    b64_part = src.split("play.php?url=")[1].rstrip('/')
                    b64_part = urllib.parse.unquote(b64_part)
                    decoded_url = self.decode_link(f"/l/{b64_part}")
                    links.append({
                        "server": "سيرفر البث المباشر المفضل (عرب سيد)",
                        "direct_link": decoded_url
                    })
                except Exception:
                    if src.startswith('/'):
                        links.append({
                            "server": "سيرفر البث المباشر الرئيسي",
                            "direct_link": self.base_url + src
                        })
                    else:
                        links.append({
                            "server": "سيرفر البث المباشر الرئيسي",
                            "direct_link": src
                        })
            elif src.startswith("http") and not any(x in src for x in ["facebook", "twitter", "telegram", "google"]):
                links.append({
                    "server": f"سيرفر بث بديل {len(links)+1}",
                    "direct_link": src
                })
                
        # 2. Check for other elements in servers__list or qualities if any
        servers_list = soup.find(class_="servers__list")
        if servers_list:
            for li in servers_list.find_all("li"):
                a_tag = li.find("a")
                if a_tag and a_tag.get("href"):
                    href = a_tag.get("href")
                    text = a_tag.get_text(strip=True)
                    decoded_href = self.decode_link(href)
                    links.append({
                        "server": text or f"سيرفر مشاهدة {len(links)+1}",
                        "direct_link": decoded_href
                    })
                    
        # General anchor fallback
        if not links:
            anchors = soup.find_all("a")
            for a in anchors:
                href = a.get("href") or ""
                text = a.get_text(strip=True)
                if "watch" in href.lower() or "play" in href.lower() or "مشاهدة" in text:
                    if href.startswith("http") and not href.rstrip('/').endswith('/watch'):
                        links.append({
                            "server": text or "سيرفر مشاهدة بديل",
                            "direct_link": self.decode_link(href)
                        })
                        
        return links
