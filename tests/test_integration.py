import pytest
import requests
import time
import threading
from fastapi.testclient import TestClient

class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_workflow(self, client):
        """Test complete URL shortening workflow"""
        # 1. Create a short URL
        original_url = "https://www.example.com/complete-test"
        response = client.post(f"/shortenURL?url={original_url}")
        assert response.status_code == 200
        short_code = response.json()["short_code"]
        
        # 2. Verify it appears in all URLs list
        response = client.get("/getAllUrls")
        assert response.status_code == 200
        urls = response.json()
        assert len(urls) == 1
        assert urls[0]["url"] == original_url
        assert urls[0]["short_url"] == short_code
        
        # 3. Retrieve original URL
        response = client.get(f"/s/{short_code}")
        assert response.status_code == 200
        assert response.json()[0] == original_url
        
        # 4. Delete the URL
        response = client.delete(f"/deleteUrl/{short_code}")
        assert response.status_code == 200
        
        # 5. Verify it's gone
        response = client.get("/getAllUrls")
        assert response.status_code == 200
        assert response.json() == []
        
        response = client.get(f"/s/{short_code}")
        assert response.json() is None
    
    def test_multiple_urls_workflow(self, client):
        """Test workflow with multiple URLs"""
        urls = [
            "https://www.google.com",
            "https://www.github.com",
            "https://stackoverflow.com",
            "https://example.com/path/to/resource"
        ]
        
        # Create multiple URLs
        short_codes = []
        for url in urls:
            response = client.post(f"/shortenURL?url={url}")
            assert response.status_code == 200
            short_codes.append(response.json()["short_code"])
        
        # Verify all URLs are in the list
        response = client.get("/getAllUrls")
        assert response.status_code == 200
        all_urls = response.json()
        assert len(all_urls) == len(urls)
        
        # Verify each URL can be retrieved
        for i, url in enumerate(urls):
            response = client.get(f"/s/{short_codes[i]}")
            assert response.status_code == 200
            assert response.json()[0] == url
        
        # Delete half of them
        for i in range(0, len(short_codes), 2):
            response = client.delete(f"/deleteUrl/{short_codes[i]}")
            assert response.status_code == 200
        
        # Verify remaining URLs still work
        for i in range(1, len(short_codes), 2):
            response = client.get(f"/s/{short_codes[i]}")
            assert response.status_code == 200
            assert response.json()[0] == urls[i]
        
        # Verify deleted URLs don't work
        for i in range(0, len(short_codes), 2):
            response = client.get(f"/s/{short_codes[i]}")
            assert response.json() is None
    
    def test_edge_cases_workflow(self, client):
        """Test workflow with edge cases"""
        import urllib.parse
        
        edge_cases = [
            "",  # Empty URL
            "https://example.com",  # Simple URL
            "https://example.com/path",  # URL with path
            "https://example.com/path?param=value",  # URL with query
            "https://example.com/path?param=value&other=test",  # Multiple params
            "https://example.com/path#anchor",  # URL with anchor (now preserved)
        ]
        
        # Create URLs
        short_codes = []
        for url in edge_cases:
            if url:  # Only encode non-empty URLs
                encoded_url = urllib.parse.quote(url, safe='')
                response = client.post(f"/shortenURL?url={encoded_url}")
            else:
                response = client.post("/shortenURL?url=")
            
            assert response.status_code == 200
            short_codes.append(response.json()["short_code"])
        
        # Verify all can be retrieved correctly
        for i, url in enumerate(edge_cases):
            response = client.get(f"/s/{short_codes[i]}")
            assert response.status_code == 200
            retrieved_url = response.json()[0]
            
            # All URLs should be preserved with proper encoding
            assert retrieved_url == url
    
    def test_performance_workflow(self, client):
        """Test performance with many URLs"""
        import time
        
        # Measure time for creating 100 URLs
        start_time = time.time()
        
        urls = [f"https://example{i}.com" for i in range(100)]
        short_codes = []
        
        for url in urls:
            response = client.post(f"/shortenURL?url={url}")
            assert response.status_code == 200
            short_codes.append(response.json()["short_code"])
        
        creation_time = time.time() - start_time
        
        # Measure time for retrieving all URLs
        start_time = time.time()
        response = client.get("/getAllUrls")
        assert response.status_code == 200
        all_urls = response.json()
        retrieval_time = time.time() - start_time
        
        # Measure time for individual lookups
        start_time = time.time()
        for short_code in short_codes[:10]:  # Test first 10
            response = client.get(f"/s/{short_code}")
            assert response.status_code == 200
        lookup_time = time.time() - start_time
        
        # Performance assertions (adjust based on requirements)
        assert creation_time < 5.0  # Should create 100 URLs in under 5 seconds
        assert retrieval_time < 1.0  # Should retrieve all URLs in under 1 second
        assert lookup_time < 1.0  # Should lookup 10 URLs in under 1 second
        assert len(all_urls) == 100
    
    def test_concurrent_workflow(self, client):
        """Test concurrent operations"""
        results = {"created": [], "errors": []}
        
        def create_url(index):
            try:
                url = f"https://concurrent{index}.example.com"
                response = client.post(f"/shortenURL?url={url}")
                if response.status_code == 200:
                    results["created"].append((url, response.json()["short_code"]))
                else:
                    results["errors"].append(f"Create error {index}: {response.status_code}")
            except Exception as e:
                results["errors"].append(f"Create exception {index}: {str(e)}")
        
        def delete_url(url_data):
            try:
                url, short_code = url_data
                response = client.delete(f"/deleteUrl/{short_code}")
                if response.status_code != 200:
                    results["errors"].append(f"Delete error {short_code}: {response.status_code}")
            except Exception as e:
                results["errors"].append(f"Delete exception {short_code}: {str(e)}")
        
        # Create URLs concurrently
        threads = []
        for i in range(20):
            thread = threading.Thread(target=create_url, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no errors during creation
        assert len(results["errors"]) == 0, f"Creation errors: {results['errors']}"
        assert len(results["created"]) == 20
        
        # Delete URLs concurrently
        threads = []
        for url_data in results["created"]:
            thread = threading.Thread(target=delete_url, args=(url_data,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no errors during deletion
        assert len(results["errors"]) == 0, f"Deletion errors: {results['errors']}"
        
        # Verify all URLs are deleted
        response = client.get("/getAllUrls")
        assert response.json() == []
    
    def test_data_integrity_workflow(self, client):
        """Test data integrity across operations"""
        test_data = [
            ("https://example1.com", "Special chars: !@#$%^&*()"),
            ("https://example2.com", "Unicode: 测试🚀"),
            ("https://example3.com", "Long string: " + "a" * 1000),
            ("https://example4.com", "Mixed: test123!@#测试"),
        ]
        
        # Create URLs with special data
        short_codes = []
        for url, description in test_data:
            response = client.post(f"/shortenURL?url={url}")
            assert response.status_code == 200
            short_codes.append(response.json()["short_code"])
        
        # Verify data integrity after multiple operations
        for i in range(3):  # Repeat 3 times
            # Retrieve all URLs
            response = client.get("/getAllUrls")
            assert response.status_code == 200
            all_urls = response.json()
            assert len(all_urls) == len(test_data)
            
            # Verify each URL
            for j, (original_url, _) in enumerate(test_data):
                response = client.get(f"/s/{short_codes[j]}")
                assert response.status_code == 200
                assert response.json()[0] == original_url
            
            # Wait a bit between iterations
            time.sleep(0.1)
    
    def test_error_recovery_workflow(self, client):
        """Test error recovery and graceful handling"""
        # Test invalid operations
        response = client.get("/s/invalid")
        assert response.status_code == 200
        assert response.json() is None
        
        response = client.delete("/deleteUrl/invalid")
        assert response.status_code == 200
        
        # Test malformed requests
        response = client.post("/shortenURL")
        assert response.status_code == 422  # Validation error
        
        # Test with very long URL
        long_url = "https://example.com/" + "a" * 10000
        response = client.post(f"/shortenURL?url={long_url}")
        assert response.status_code == 200
        
        # Verify system still works after errors
        response = client.post("/shortenURL?url=https://recovery.test")
        assert response.status_code == 200
        short_code = response.json()["short_code"]
        
        response = client.get(f"/s/{short_code}")
        assert response.status_code == 200
        assert response.json()[0] == "https://recovery.test"
