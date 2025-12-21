"""
Quick test script for UniBus Core API
Run this with the server running: python test_api.py
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def main():
    print("🚀 Testing UniBus Core API")
    
    # Test 1: Health check
    response = requests.get(f"{BASE_URL}/health")
    print_response("1. Health Check", response)
    
    # Test 2: Create a student
    student_data = {
        "name": "Maria Silva",
        "email": "maria.silva@example.com",
        "city": "Rio de Janeiro"
    }
    response = requests.post(f"{BASE_URL}/students", json=student_data)
    print_response("2. Create Student", response)
    student_id = response.json().get("id") if response.status_code == 201 else None
    
    # Test 3: Get students
    response = requests.get(f"{BASE_URL}/students")
    print_response("3. List Students", response)
    
    # Test 4: Create a route (will try to call geo-api, may fail with 202)
    route_data = {
        "name": "Rio - São Paulo Express",
        "origin_city": "Rio de Janeiro",
        "destination_city": "São Paulo"
    }
    response = requests.post(f"{BASE_URL}/routes", json=route_data)
    print_response("4. Create Route", response)
    route_id = response.json().get("id") if response.status_code in [201, 202] else None
    
    # Test 5: Get routes
    response = requests.get(f"{BASE_URL}/routes")
    print_response("5. List Routes", response)
    
    # Test 6: Create a trip
    if route_id:
        trip_data = {
            "route_id": route_id,
            "bus_plate": "ABC-1234",
            "departure_time": "2025-12-15T08:00:00",
            "available_seats": 40
        }
        response = requests.post(f"{BASE_URL}/trips", json=trip_data)
        print_response("6. Create Trip", response)
        
        # Test 7: Get trips
        response = requests.get(f"{BASE_URL}/trips")
        print_response("7. List Trips", response)
    
    print(f"\n{'='*60}")
    print("✅ All tests completed!")
    print(f"{'='*60}\n")
    print("📚 API Documentation available at:")
    print(f"   - Swagger UI: {BASE_URL}/docs")
    print(f"   - ReDoc: {BASE_URL}/redoc")
    print()

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API.")
        print("Make sure the server is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
