import os
from playwright.sync_api import sync_playwright

def verify_ui(page):
    # Mock Leaderboard API
    page.route("**/api/leaderboard", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"leaderboard": [{"user_email": "hero@test.com", "reports_count": 10, "total_upvotes": 50, "rank": 1}, {"user_email": "normal@test.com", "reports_count": 2, "total_upvotes": 5, "rank": 2}]}'
    ))

    # Mock Smart Scan API
    page.route("**/api/detect-smart-scan", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"category": "garbage", "confidence": 0.95, "all_scores": []}'
    ))

    # Mock Severity (so it doesn't error)
    page.route("**/api/detect-severity", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"level": "Medium", "confidence": 0.5, "raw_label": "medium urgency"}'
    ))

    # Mock Depth (so it doesn't error)
    page.route("**/api/analyze-depth", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"depth_map": "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"}' # 1x1 GIF
    ))

    # 1. Verify Leaderboard Badge
    print("Navigating to Leaderboard...")
    page.goto("http://localhost:5173/leaderboard")
    try:
        page.wait_for_selector("text=Civic Hero", timeout=5000)
        print("Found Civic Hero badge!")
    except:
        print("Civic Hero badge NOT found!")

    page.screenshot(path="verification/leaderboard_badge.png")

    # 2. Verify Smart Suggestion
    print("Navigating to Report Form...")
    page.goto("http://localhost:5173/report")

    # Upload image
    # We need a dummy image file.
    with open("dummy.jpg", "wb") as f:
        f.write(b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00\x60\x00\x60\x00\x00\xFF\xDB\x00\x43\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\x09\x09\x08\x0A\x0C\x14\x0D\x0C\x0B\x0B\x0C\x19\x12\x13\x0F\x14\x1D\x1A\x1F\x1E\x1D\x1A\x1C\x1C\x20\x24\x2E\x27\x20\x22\x2C\x23\x1C\x1C\x28\x37\x29\x2C\x30\x31\x34\x34\x34\x1F\x27\x39\x3D\x38\x32\x3C\x2E\x33\x34\x32\xFF\xC0\x00\x0B\x08\x00\x0A\x00\x0A\x03\x01\x22\x00\x02\x11\x01\x03\x11\x01\xFF\xC4\x00\x15\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\xFF\xDA\x00\x0C\x03\x01\x00\x02\x11\x03\x11\x00\x3F\x00\x9F\xFF\xD9")

    print("Uploading image...")
    # Use set_input_files on the first file input (Upload)
    page.locator("input[type='file']").first.set_input_files("dummy.jpg")

    # Wait for AI Suggestion
    print("Waiting for AI Suggestion...")
    try:
        page.wait_for_selector("text=AI Suggestion", timeout=5000)
        print("Found AI Suggestion!")
    except:
        print("AI Suggestion NOT found!")

    # Check suggestion text
    content = page.content()
    if "garbage" in content:
        print("Suggestion text 'garbage' found.")

    page.screenshot(path="verification/smart_suggestion.png")

    # Click Apply
    print("Clicking Apply...")
    try:
        page.click("text=Apply", timeout=2000)
    except:
        print("Apply button not clickable or found")

    # Verify dropdown value
    # value="garbage" for garbage
    try:
        dropdown = page.locator("select").nth(0) # First select is Category
        value = dropdown.input_value()
        print(f"Dropdown value: {value}")
        if value == "garbage":
            print("Category successfully applied!")
        else:
            print(f"Category failed to apply. Expected 'garbage', got '{value}'")
    except Exception as e:
        print(f"Error checking dropdown: {e}")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        try:
            verify_ui(page)
        except Exception as e:
            print(f"Verification failed: {e}")
            page.screenshot(path="verification/error.png")
        finally:
            browser.close()
