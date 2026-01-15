import pytest
import sqlite3
import os
from models import init_db, insert_url, get_url, deleteUrl, getAllUrls, DBNAME

class TestModels:
    """Unit tests for database models"""
    
    def test_init_db(self, test_db):
        """Test database initialization"""
        assert os.path.exists(test_db)
        
        # Check if table exists
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='URLS'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == 'URLS'
    
    def test_insert_url(self, test_db):
        """Test URL insertion"""
        test_url = "https://www.example.com"
        short_code = "abc123"
        
        insert_url(test_url, short_code)
        
        # Verify insertion
        result = get_url(short_code)
        assert result is not None
        assert result[0] == test_url
    
    def test_get_url_existing(self, test_db):
        """Test retrieving existing URL"""
        test_url = "https://www.google.com"
        short_code = "xyz789"
        
        # Insert first
        insert_url(test_url, short_code)
        
        # Retrieve
        result = get_url(short_code)
        assert result is not None
        assert result[0] == test_url
    
    def test_get_url_nonexistent(self, test_db):
        """Test retrieving non-existent URL"""
        result = get_url("nonexistent")
        assert result is None
    
    def test_delete_url_existing(self, test_db):
        """Test deleting existing URL"""
        test_url = "https://www.github.com"
        short_code = "delete123"
        
        # Insert first
        insert_url(test_url, short_code)
        
        # Verify it exists
        result = get_url(short_code)
        assert result is not None
        
        # Delete
        deleteUrl(short_code)
        
        # Verify deletion
        result = get_url(short_code)
        assert result is None
    
    def test_delete_url_nonexistent(self, test_db):
        """Test deleting non-existent URL"""
        # Should not raise an exception
        deleteUrl("nonexistent")
    
    def test_get_all_urls_empty(self, test_db):
        """Test getting all URLs from empty database"""
        result = getAllUrls()
        assert result == []
    
    def test_get_all_urls_with_data(self, test_db):
        """Test getting all URLs with data"""
        # Insert test data
        test_data = [
            ("https://www.example1.com", "abc123"),
            ("https://www.example2.com", "def456"),
            ("https://www.example3.com", "ghi789")
        ]
        
        for url, code in test_data:
            insert_url(url, code)
        
        # Get all URLs
        result = getAllUrls()
        assert len(result) == 3
        
        # Check structure (should be in reverse chronological order)
        assert all('url' in item and 'short_url' in item for item in result)
        
        # Check if all test data is present
        urls = [item['url'] for item in result]
        codes = [item['short_url'] for item in result]
        
        for url, code in test_data:
            assert url in urls
            assert code in codes
    
    def test_duplicate_short_code(self, test_db):
        """Test handling duplicate short codes"""
        test_url1 = "https://www.first.com"
        test_url2 = "https://www.second.com"
        short_code = "duplicate"
        
        # Insert first URL
        insert_url(test_url1, short_code)
        
        # Insert second URL with same short code (should overwrite)
        insert_url(test_url2, short_code)
        
        # Verify only second URL exists
        result = get_url(short_code)
        assert result is not None
        assert result[0] == test_url2
    
    def test_special_characters_in_url(self, test_db):
        """Test URLs with special characters"""
        test_url = "https://example.com/path?param=value&other=test#anchor"
        short_code = "special123"
        
        insert_url(test_url, short_code)
        
        result = get_url(short_code)
        assert result is not None
        assert result[0] == test_url
    
    def test_unicode_in_url(self, test_db):
        """Test URLs with Unicode characters"""
        test_url = "https://例子.测试/路径?参数=值"
        short_code = "unicode123"
        
        insert_url(test_url, short_code)
        
        result = get_url(short_code)
        assert result is not None
        assert result[0] == test_url
