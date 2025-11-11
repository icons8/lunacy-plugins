#!/usr/bin/env python3

import requests

API = "http://localhost:31415"

def main():
    try:
        response = requests.post(f"{API}/showtoast", json={
            "text": "Hello from your first Python plugin!",
            "iconType": 2,
            "priority": 5,
            "durationSeconds": 5
        })
        
        print("Plugin executed successfully!")
    except Exception as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    main()
