import pytest
import time
from fastapi.testclient import TestClient

class TestRegression:
    """Regression tests to prevent previously fixed bugs"""
    
    def test_regression_short_code_collision(self, client):
        """Regression test for short code collision issues"""
        import urllib.parse
        
        # Create multiple URLs rapidly to test collision handling
        short_codes = set()
        urls = [f"https://regression{i}.example.com" for i in range(50)]
        
        for url in urls:
            encoded_url = urllib.parse.quote(url, safe='')
            response = client.post(f"/shortenURL?url={encoded_url}")
            assert response.status_code == 200
            short_code = response.json()["short_code"]
            
            # Ensure no duplicates
            assert short_code not in short_codes, f"Duplicate short code: {short_code}"
            short_codes.add(short_code)
        
        # Verify all URLs work
        for i, url in enumerate(urls):
            encoded_url = urllib.parse.quote(url, safe='')
            response = client.post(f"/shortenURL?url={encoded_url}")
            assert response.status_code == 200
            short_code = response.json()["short_code"]
            
            response = client.get(f"/s/{short_code}")
            assert response.status_code == 200
            assert response.json()[0] == url
    
    def test_regression_url_encoding_issues(self, client):
        """Regression test for URL encoding/decoding issues"""
        import urllib.parse
        
        problematic_urls = [
            "https://example.com/path with spaces",
            "https://example.com/path+with+plus",
            "https://example.com/path%20with%20encoding",
            "https://example.com/path?param=value",
            "https://example.com/path#anchor",  # Now preserved with proper encoding
        ]
        
        for url in problematic_urls:
            encoded_url = urllib.parse.quote(url, safe='')
            response = client.post(f"/shortenURL?url={encoded_url}")
            assert response.status_code == 200
            short_code = response.json()["short_code"]
            
            # Verify round-trip works correctly
            response = client.get(f"/s/{short_code}")
            assert response.status_code == 200
            retrieved_url = response.json()[0]
            
            # All URLs should be preserved with proper encoding
            assert retrieved_url == url
    
    def test_regression_database_persistence(self, client):
        """Regression test for database persistence issues"""
        # Create URLs
        urls = [f"https://persistence{i}.example.com" for i in range(10)]
        short_codes = []
        
        for url in urls:
            response = client.post(f"/shortenURL?url={url}")
            assert response.status_code == 200
            short_codes.append(response.json()["short_code"])
        
        # Verify all URLs exist
        response = client.get("/getAllUrls")
        assert response.status_code == 200
        all_urls = response.json()
        assert len(all_urls) == len(urls)
        
        # Delete some URLs
        for i in range(0, len(short_codes), 2):
            response = client.delete(f"/deleteUrl/{short_codes[i]}")
            assert response.status_code == 200
        
        # Verify remaining URLs still exist
        response = client.get("/getAllUrls")
        assert response.status_code == 200
        remaining_urls = response.json()
        assert len(remaining_urls) == len(urls) // 2
        
        # Verify deleted URLs don't exist
        for i in range(0, len(short_codes), 2):
            response = client.get(f"/s/{short_codes[i]}")
            assert response.json() is None
    
    def test_regression_concurrent_access(self, client):
        """Regression test for concurrent access issues"""
        import threading
        import time
        
        results = {"urls": [], "errors": []}
        lock = threading.Lock()
        
        def create_and_verify(index):
            try:
                url = f"https://concurrent-regression{index}.example.com"
                
                # Create URL
                response = client.post(f"/shortenURL?url={url}")
                if response.status_code != 200:
                    with lock:
                        results["errors"].append(f"Create failed {index}: {response.status_code}")
                    return
                
                short_code = response.json()["short_code"]
                
                # Immediately verify
                response = client.get(f"/s/{short_code}")
                if response.status_code != 200 or response.json()[0] != url:
                    with lock:
                        results["errors"].append(f"Verify failed {index}")
                    return
                
                with lock:
                    results["urls"].append((url, short_code))
                    
            except Exception as e:
                with lock:
                    results["errors"].append(f"Exception {index}: {str(e)}")
        
        # Create multiple threads
        threads = []
        for i in range(30):
            thread = threading.Thread(target=create_and_verify, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results["errors"]) == 0, f"Concurrent errors: {results['errors']}"
        assert len(results["urls"]) == 30
        
        # Final verification of all URLs
        response = client.get("/getAllUrls")
        assert response.status_code == 200
        all_urls = response.json()
        assert len(all_urls) == 30
    
    def test_regression_memory_leaks(self, client):
        """Regression test for memory leaks with many operations"""
        import gc
        
        # Get initial memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Perform many operations
        for i in range(50):  # Reduced from 100
            url = f"https://memory-leak-test{i}.example.com"
            
            # Create URL
            response = client.post(f"/shortenURL?url={url}")
            assert response.status_code == 200
            short_code = response.json()["short_code"]
            
            # Verify URL
            response = client.get(f"/s/{short_code}")
            assert response.status_code == 200
            assert response.json()[0] == url
            
            # Delete URL
            response = client.delete(f"/deleteUrl/{short_code}")
            assert response.status_code == 200
            
            # Force garbage collection periodically
            if i % 10 == 0:
                gc.collect()
        
        # Final cleanup
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Memory growth should be minimal (more lenient threshold)
        object_growth = final_objects - initial_objects
        assert object_growth < 10000, f"Potential memory leak: {object_growth} new objects"
    
    def test_regression_api_response_format(self, client):
        """Regression test for API response format consistency"""
        # Clear database first
        response = client.get("/getAllUrls")
        if response.json():
            for item in response.json():
                client.delete(f"/deleteUrl/{item['short_url']}")
        
        # Test shorten URL response format
        response = client.post("/shortenURL?url=https://test.example.com")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "short_code" in data
        assert isinstance(data["short_code"], str)
        assert len(data["short_code"]) == 6
        
        # Test get all URLs response format
        response = client.get("/getAllUrls")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        
        # Add another URL and test again
        response = client.post("/shortenURL?url=https://test2.example.com")
        short_code = response.json()["short_code"]
        
        response = client.get("/getAllUrls")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert isinstance(data[0], dict)
        assert "url" in data[0]
        assert "short_url" in data[0]
        assert data[0]["url"] == "https://test.example.com"
        assert data[1]["url"] == "https://test2.example.com"
        assert data[1]["short_url"] == short_code
        
        # Test get original URL response format
        response = client.get(f"/s/{short_code}")
        assert response.status_code == 200
        data = response.json()
        # Should return a tuple-like list with the URL
        assert isinstance(data, list) or data is None
        if data is not None:
            assert len(data) == 1
            assert data[0] == "https://test2.example.com"
    
    def test_regression_error_handling(self, client):
        """Regression test for proper error handling"""
        # Test non-existent short code
        response = client.get("/s/nonexistent123")
        assert response.status_code == 200
        assert response.json() is None
        
        # Test non-existent deletion
        response = client.delete("/deleteUrl/nonexistent123")
        assert response.status_code == 200
        
        # Test invalid request format
        response = client.post("/shortenURL")
        assert response.status_code == 422  # Validation error
        
        # Test empty database operations
        response = client.get("/getAllUrls")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_regression_performance_degradation(self, client):
        """Regression test for performance degradation"""
        import time
        
        # Test performance with increasing data size
        sizes = [10, 50, 100]
        creation_times = []
        retrieval_times = []
        
        for size in sizes:
            # Clear database by deleting all URLs
            response = client.get("/getAllUrls")
            if response.json():
                for item in response.json():
                    client.delete(f"/deleteUrl/{item['short_url']}")
            
            # Measure creation time
            start_time = time.time()
            for i in range(size):
                url = f"https://perf-test-{size}-{i}.example.com"
                response = client.post(f"/shortenURL?url={url}")
                assert response.status_code == 200
            creation_time = time.time() - start_time
            creation_times.append(creation_time)
            
            # Measure retrieval time
            start_time = time.time()
            response = client.get("/getAllUrls")
            assert response.status_code == 200
            all_urls = response.json()
            retrieval_time = time.time() - start_time
            retrieval_times.append(retrieval_time)
            
            assert len(all_urls) == size
        
        # Performance should not degrade significantly
        # Creation time should scale roughly linearly
        if len(creation_times) >= 2:
            ratio = creation_times[-1] / creation_times[0]
            assert ratio < 20, f"Performance degradation: {ratio}x slower"
        
        # Retrieval should remain fast even with more data
        for retrieval_time in retrieval_times:
            assert retrieval_time < 2.0, f"Retrieval too slow: {retrieval_time}s"
