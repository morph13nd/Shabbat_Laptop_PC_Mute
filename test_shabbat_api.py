#!/usr/bin/env python3
"""
Quick test script to verify Shabbat API connectivity
"""
import requests
from datetime import datetime

GEONAME_ID = "5128581"  # New York City
HAVDALAH_MINUTES = 50

def test_api():
    try:
        url = f"https://www.hebcal.com/shabbat?cfg=json&geonameid={GEONAME_ID}&M=on&m={HAVDALAH_MINUTES}"
        print(f"Testing API: {url}")

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        print("\nAPI Response received successfully!")
        print(f"Location: {data.get('location', {}).get('title', 'Unknown')}")

        items = data.get('items', [])
        for item in items:
            if item.get('category') in ['candles', 'havdalah']:
                print(f"{item.get('title')}: {item.get('date')}")

        return True

    except Exception as e:
        print(f"API test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Shabbat API connectivity...")
    if test_api():
        print("\n✅ API test successful! The main script should work.")
    else:
        print("\n❌ API test failed. Check your internet connection.")
