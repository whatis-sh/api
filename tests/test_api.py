#!/usr/bin/env python3
"""
Test script for whAtIs.sh API
"""
import asyncio
import httpx
import json
import pytest

API_BASE = "http://localhost:2095"

@pytest.mark.asyncio
async def test_health_check():
    """Test the health check endpoint"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(f"{API_BASE}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "whatis.sh"

@pytest.mark.asyncio
async def test_headless_request():
    """Test headless request (/ls)"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(f"{API_BASE}/ls")
        assert response.status_code == 200
        assert len(response.text) > 0

@pytest.mark.asyncio
async def test_headless_verbose():
    """Test headless request with verbose (/grep?v=true)"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(f"{API_BASE}/grep?v=true")
        assert response.status_code == 200
        assert len(response.text) > 0

@pytest.mark.asyncio
async def test_get_with_json_body():
    """Test GET request with JSON body"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        payload = {
            "cmd_or_func": "print()",
            "verbose": False
        }
        response = await client.request(
            "GET",
            f"{API_BASE}/",
            headers={"Content-Type": "application/json"},
            content=json.dumps(payload)
        )
        assert response.status_code == 200
        assert len(response.text) > 0

@pytest.mark.asyncio
async def test_post_request():
    """Test POST request"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        payload = {
            "cmd_or_func": "awk",
            "verbose": True
        }
        response = await client.post(
            f"{API_BASE}/",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        assert response.status_code == 200
        assert len(response.text) > 0

@pytest.mark.asyncio
async def test_usage_instructions():
    """Test getting usage instructions from root endpoint"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(f"{API_BASE}/")
        assert response.status_code == 200
        assert "whAtIs.sh - Unix 'whatis' command API" in response.text
        assert "Usage:" in response.text

# Manual test runner for non-pytest usage
async def run_all_tests():
    """Run all tests manually for debugging"""
    print("Testing whAtIs.sh API...")
    
    # Test health check
    print("\n1. Testing health check:")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(f"{API_BASE}/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test headless request
    print("\n2. Testing headless request (/ls):")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(f"{API_BASE}/ls")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Headless request failed: {e}")
    
    # Test headless request with verbose
    print("\n3. Testing headless request with verbose (/grep?v=true):")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(f"{API_BASE}/grep?v=true")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Headless verbose request failed: {e}")
    
    # Test JSON body request (GET)
    print("\n4. Testing GET request with JSON body:")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {
                "cmd_or_func": "print()",
                "verbose": False
            }
            response = await client.request(
                "GET",
                f"{API_BASE}/",
                headers={"Content-Type": "application/json"},
                content=json.dumps(payload)
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"GET with JSON body failed: {e}")
    
    # Test POST request
    print("\n5. Testing POST request:")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            payload = {
                "cmd_or_func": "awk",
                "verbose": True
            }
            response = await client.post(
                f"{API_BASE}/",
                headers={"Content-Type": "application/json"},
                json=payload
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"POST request failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
