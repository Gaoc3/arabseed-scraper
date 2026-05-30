#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rigorous Test Suite for ArabSeed Scraper
---------------------------------------
Puts the scraper under multiple integration and unit tests to ensure high stability.
"""

import sys
import os
import unittest

# Configure terminal output encoding for Arabic compatibility
sys.stdout.reconfigure(encoding='utf-8')

# Add the package root directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arabseed_scraper import ArabSeedAPI, MIRRORS

class TestArabSeedScraper(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Initialize the API client and ensure a mirror is active."""
        cls.api = ArabSeedAPI()
        # Find a working mirror or fallback automatically
        connected = cls.api.auto_fallback_mirror()
        print(f"\n[Test Environment] Active Mirror: {cls.api.base_url} (Connected: {connected})")
        if not connected:
            print("⚠️ Warning: Could not connect to any live ArabSeed mirror. Integration tests might fail.")

    def test_01_mirror_fallback_and_latency(self):
        """Test mirror rotation, latency measurement, and fallback handling."""
        print("\n🧪 Running Test: Mirror Fallback & Connection Test")
        
        # Test connection status & latency on active mirror
        latency = self.api.test_connection()
        self.assertNotEqual(latency, False, "Active mirror should be responsive.")
        self.assertGreater(latency, 0, "Latency should be a positive float.")
        print(f"  - Active mirror latency: {latency:.4f}s")
        
        # Inject a dead URL and test failover
        dead_api = ArabSeedAPI(base_url="https://dead-mirror-test-arabseed-xyz.xyz")
        self.assertFalse(dead_api.test_connection(), "A fake dead mirror should fail connection.")
        
        # Verify automatic failover switches to a working mirror from pre-defined list
        fallback_success = dead_api.auto_fallback_mirror()
        self.assertTrue(fallback_success, "Failover should successfully find a working mirror.")
        self.assertNotEqual(dead_api.base_url, "https://dead-mirror-test-arabseed-xyz.xyz", "Base URL should have updated.")
        print(f"  - Fallback successful! Switched from dead mirror to: {dead_api.base_url}")

    def test_02_base64_decryption(self):
        """Test the link decryption engine under standard, padded, and edge case scenarios."""
        print("\n🧪 Running Test: Link Decryption Engine")
        
        # Standard valid decryption
        obfuscated = "https://m.asd.ink/l/aHR0cHM6Ly9tLnJldmlld3JhdGUubmV0L2ZxcGM5OGoyNnRydQ=="
        expected = "https://m.reviewrate.net/fqpc98j26tru"
        decoded = self.api.decode_link(obfuscated)
        self.assertEqual(decoded, expected, "Should decode standard link successfully.")
        
        # Link missing base64 padding '='
        obfuscated_no_pad = "https://m.asd.ink/l/aHR0cHM6Ly9tLnJldmlld3JhdGUubmV0L2ZxcGM5OGoyNnRydQ"
        decoded_no_pad = self.api.decode_link(obfuscated_no_pad)
        self.assertEqual(decoded_no_pad, expected, "Should handle missing base64 padding gracefully.")
        
        # Non-encoded fallback link
        direct = "https://filespayouts.com/video.mp4"
        decoded_direct = self.api.decode_link(direct)
        self.assertEqual(decoded_direct, direct, "Should return original link if no base64 coding is detected.")
        
        # Empty inputs
        self.assertEqual(self.api.decode_link(""), "", "Should return empty string for empty input.")
        self.assertEqual(self.api.decode_link(None), "", "Should handle None gracefully.")
        
        print("  - Decryption engine passed standard, padded, and fallback test cases!")

    def test_03_search_queries(self):
        """Test search query parsing with valid, empty, and nonexistent entries."""
        print("\n🧪 Running Test: Search Queries Resilience")
        
        # 1. Nonexistent / random text search (should return empty list, no crash)
        empty_res = self.api.search("random_non_existent_text_12345_query")
        self.assertIsInstance(empty_res, list, "Search results should be a list.")
        self.assertEqual(len(empty_res), 0, "Nonexistent search should return empty list.")
        
        # 2. Empty query handling
        self.assertEqual(self.api.search(""), [], "Empty query should return empty list immediately.")
        self.assertEqual(self.api.search("   "), [], "Spaces query should return empty list immediately.")
        
        # 3. Live search for a valid Movie
        movie_res = self.api.search("الست")
        self.assertGreater(len(movie_res), 0, "Search for 'الست' should return at least one result.")
        first_movie = movie_res[0]
        self.assertIn("title", first_movie)
        self.assertIn("url", first_movie)
        self.assertIn("type", first_movie)
        self.assertEqual(first_movie["type"], "فيلم", "Result should be detected as a Movie.")
        print(f"  - Search Movie Success: Found '{first_movie['title']}' of type '{first_movie['type']}'")
        
        # 4. Live search for a Series
        series_res = self.api.search("ليل")
        self.assertGreater(len(series_res), 0, "Search for 'ليل' should return at least one result.")
        first_series = series_res[0]
        self.assertIn("title", first_series)
        self.assertIn("url", first_series)
        self.assertEqual(first_series["type"], "مسلسل / حلقة", "Result should be detected as a Series/Episode.")
        print(f"  - Search Series Success: Found '{first_series['title']}' of type '{first_series['type']}'")

    def test_04_details_and_episodes_parsing(self):
        """Test movie/series detail pages parsing and episodes listing."""
        print("\n🧪 Running Test: Details Page & Episodes Parsing")
        
        # Search for a known series with episodes
        results = self.api.search("ليل")
        self.assertGreater(len(results), 0)
        
        # Select first result and fetch details
        series = results[0]
        details = self.api.get_details(series["url"])
        
        self.assertIn("title", details)
        self.assertIn("description", details)
        self.assertIn("is_series", details)
        self.assertIn("episodes", details)
        
        # Verify it lists episodes
        self.assertTrue(details["is_series"], "Series should be detected as is_series = True.")
        self.assertGreater(len(details["episodes"]), 0, "Series should contain at least one episode.")
        
        first_ep = details["episodes"][0]
        self.assertIn("title", first_ep)
        self.assertIn("url", first_ep)
        self.assertIn("active", first_ep)
        print(f"  - Series Details Success: Loaded series '{details['title']}' with {len(details['episodes'])} episodes. First episode: {first_ep['title']}")

    def test_05_download_and_watch_extraction(self):
        """Test extracting and decrypting watch and download links from a live media page."""
        print("\n🧪 Running Test: Watch & Download Links Extraction")
        
        # Search for a movie
        results = self.api.search("الست")
        self.assertGreater(len(results), 0)
        movie = results[0]
        
        # 1. Scrape streaming watch links
        print("  - Fetching watch links...")
        watch_links = self.api.get_watch_links(movie["url"])
        self.assertIsInstance(watch_links, list, "Watch links should be a list.")
        self.assertGreater(len(watch_links), 0, "Should find at least one streaming link.")
        
        first_watch = watch_links[0]
        self.assertIn("server", first_watch)
        self.assertIn("direct_link", first_watch)
        self.assertTrue(first_watch["direct_link"].startswith("http"), "Stream URL should be a valid http link.")
        print(f"    * Watch Link Decrypted: Server '{first_watch['server']}' -> URL: '{first_watch['direct_link']}'")
        
        # 2. Scrape download links
        print("  - Fetching download links...")
        download_links = self.api.get_download_links(movie["url"])
        self.assertIsInstance(download_links, list, "Download links should be a list.")
        self.assertGreater(len(download_links), 0, "Should find at least one download link.")
        
        first_dl = download_links[0]
        self.assertIn("server", first_dl)
        self.assertIn("quality", first_dl)
        self.assertIn("size", first_dl)
        self.assertIn("direct_link", first_dl)
        self.assertTrue(first_dl["direct_link"].startswith("http"), "Download URL should be a valid http link.")
        print(f"    * Download Link Decrypted: Server '{first_dl['server']}' ({first_dl['quality']}) -> URL: '{first_dl['direct_link']}'")

if __name__ == "__main__":
    unittest.main()
