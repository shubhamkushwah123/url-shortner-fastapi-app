import pytest
from fastapi.testclient import TestClient
import json

class TestAPI:
    """Integration tests for API endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == "Welcome to URL Shortner Microservice"
    
    def test_shorten_url_valid(self, client):
        """Test URL shortening with valid URL"""
        test_url = "https://www.example.com"
        response = client.post(f"/shortenURL?url={test_url}")
        
        assert response.status_code == 200
        data = response.json()
        assert "short_code" in data
        assert len(data["short_code"]) == 6
        assert data["short_code"].isalnum()
    
    def test_shorten_url_invalid(self, client):
        """Test URL shortening with invalid URL"""
        # Test with missing URL parameter
        response = client.post("/shortenURL")
        assert response.status_code == 422  # Validation error
        
        # Test with empty URL
        response = client.post("/shortenURL?url=")
        assert response.status_code == 200  # Should still work (no validation)
    
    def test_shorten_url_multiple(self, client):
        """Test multiple URL shortenings"""
        urls = [
            "https://www.google.com",
            "https://www.github.com",
            "https://stackoverflow.com"
        ]
        
        short_codes = []
        for url in urls:
            response = client.post(f"/shortenURL?url={url}")
            assert response.status_code == 200
            data = response.json()
            short_codes.append(data["short_code"])
        
        # Verify all short codes are unique
        assert len(set(short_codes)) == len(short_codes)
    
    def test_get_all_urls_empty(self, client):
        """Test getting all URLs when database is empty"""
        response = client.get("/getAllUrls")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_all_urls_with_data(self, client):
        """Test getting all URLs with data"""
        # Insert some URLs first
        urls = [
            "https://www.example1.com",
            "https://www.example2.com"
        ]
        
        for url in urls:
            client.post(f"/shortenURL?url={url}")
        
        # Get all URLs
        response = client.get("/getAllUrls")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Check structure
        for item in data:
            assert "url" in item
            assert "short_url" in item
    
    def test_get_original_url_existing(self, client):
        """Test retrieving original URL for existing short code"""
        test_url = "https://www.example.com"
        
        # First, create a short URL
        response = client.post(f"/shortenURL?url={test_url}")
        assert response.status_code == 200
        short_code = response.json()["short_code"]
        
        # Retrieve original URL
        response = client.get(f"/s/{short_code}")
        assert response.status_code == 200
        assert response.json()[0] == test_url
    
    def test_get_original_url_nonexistent(self, client):
        """Test retrieving original URL for non-existent short code"""
        response = client.get("/s/nonexistent")
        assert response.status_code == 200
        assert response.json() is None
    
    def test_delete_url_existing(self, client):
        """Test deleting existing URL"""
        test_url = "https://www.example.com"
        
        # First, create a short URL
        response = client.post(f"/shortenURL?url={test_url}")
        assert response.status_code == 200
        short_code = response.json()["short_code"]
        
        # Delete it
        response = client.delete(f"/deleteUrl/{short_code}")
        assert response.status_code == 200
        
        # Verify it's deleted
        response = client.get(f"/s/{short_code}")
        assert response.json() is None
    
    def test_delete_url_nonexistent(self, client):
        """Test deleting non-existent URL"""
        response = client.delete("/deleteUrl/nonexistent")
        assert response.status_code == 200
    
    def test_url_encoding(self, client):
        """Test URL encoding/decoding"""
        import urllib.parse
        test_url = "https://example.com/path?param=value&other=test"
        encoded_url = urllib.parse.quote(test_url, safe='')
        
        response = client.post(f"/shortenURL?url={encoded_url}")
        assert response.status_code == 200
        short_code = response.json()["short_code"]
        
        # Retrieve and verify
        response = client.get(f"/s/{short_code}")
        assert response.status_code == 200
        assert response.json()[0] == test_url
    
    def test_unicode_urls(self, client):
        """Test URLs with Unicode characters"""
        test_url = "https://例子.测试/路径"
        
        response = client.post(f"/shortenURL?url={test_url}")
        assert response.status_code == 200
        short_code = response.json()["short_code"]
        
        # Retrieve and verify
        response = client.get(f"/s/{short_code}")
        assert response.status_code == 200
        assert response.json()[0] == test_url
    
    def test_long_urls(self, client):
        """Test very long URLs"""
        test_url = "https://example.com/" + "a" * 1000 + "?param=" + "b" * 1000
        
        response = client.post(f"/shortenURL?url={test_url}")
        assert response.status_code == 200
        short_code = response.json()["short_code"]
        
        # Retrieve and verify
        response = client.get(f"/s/{short_code}")
        assert response.status_code == 200
        assert response.json()[0] == test_url
    
    def test_concurrent_requests(self, client):
        """Test handling concurrent requests"""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request(url):
            try:
                response = client.post(f"/shortenURL?url={url}")
                if response.status_code == 200:
                    results.append(response.json()["short_code"])
                else:
                    errors.append(f"Status: {response.status_code}")
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(f"https://example{i}.com",))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10
        assert len(set(results)) == 10  # All short codes should be unique
