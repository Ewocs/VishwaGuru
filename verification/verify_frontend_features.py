from playwright.sync_api import sync_playwright, expect
import time

def test_frontend_features(page):
    # Mock the urgency API
    page.route("**/api/analyze-urgency", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"urgency": "High", "sentiment": "negative", "score": 0.95}'
    ))

    # Go to Home
    page.goto("http://localhost:5173")

    # Check Privacy Badge
    expect(page.get_by_text("AI-Powered Privacy Protection Active")).to_be_visible()

    # Go to Report (Report Issue button is inside categories)
    # The home page has categories. "Report Issue" is in "Civic Services" category.
    # It might be hidden if I don't scroll? Playwright auto-scrolls.

    # Let's find the button by text "Report Issue"
    page.get_by_text("Report Issue").click()

    # Check if we are on report page
    expect(page.get_by_text("Report an Issue")).to_be_visible()

    # Enter description
    desc_area = page.get_by_placeholder("Describe the issue...")
    desc_area.fill("This is a very dangerous situation with fire!")
    desc_area.blur() # Trigger onBlur

    # Wait for urgency badge
    # It might take a moment if React state update is slow (even with mock)
    expect(page.get_by_text("Urgency: High")).to_be_visible()
    expect(page.get_by_text("Sentiment: negative")).to_be_visible()

    # Screenshot
    page.screenshot(path="verification/verification.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_frontend_features(page)
            print("Verification script finished successfully.")
        except Exception as e:
            print(f"Verification failed: {e}")
            page.screenshot(path="verification/error.png")
        finally:
            browser.close()
