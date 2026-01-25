import database
import time

def test_add():
    print("Testing add_schedule...")
    try:
        database.add_schedule(
            url="https://example.com", 
            topic="Test", 
            email="test@example.com", 
            frequency_days=1, 
            scraper_type="CSS",
            unit="minutes"
        )
        print("Success: Schedule added.")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_add()
