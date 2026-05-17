import os
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    email = os.environ.get("NAUKRI_EMAIL")
    password = os.environ.get("NAUKRI_PASSWORD")
    
    if not email or not password:
        print("Error: NAUKRI_EMAIL and NAUKRI_PASSWORD environment variables must be set")
        return
    
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    try:
        print("Navigating to Naukri...")
        page.goto("https://www.naukri.com/", timeout=30000)
        page.wait_for_load_state("domcontentloaded")
        print("Clicking login link...")
        page.get_by_role("link", name="Login", exact=True).click()
        page.wait_for_load_state("domcontentloaded")
        
        print("Entering credentials...")
        page.get_by_role("textbox", name="Enter your active Email ID /").click()
        page.get_by_role("textbox", name="Enter your active Email ID /").fill(email)
        page.get_by_role("textbox", name="Enter your password").click()
        page.get_by_role("textbox", name="Enter your password").fill(password)
        
        print("Clicking login button...")
        page.get_by_role("button", name="Login", exact=True).click()
        page.wait_for_load_state("load")  # Wait for page to load after login
        page.wait_for_load_state("networkidle")  # Wait for network to be idle
        page.wait_for_timeout(2000)  # Additional wait for dynamic content to load
        
        # Try to find and click "View profile" with timeout and retry logic
        print("Finding View profile link...")
        try:
            page.get_by_role("link", name="View profile").click(timeout=10000)
        except Exception as e:
            print(f"Error clicking 'View profile': {e}")
            # Try alternative selectors or approaches
            page.wait_for_timeout(1000)
            page.get_by_role("link", name="View profile").click()
        
        print("Waiting for profile page to load...")
        page.wait_for_load_state("load")  # Wait for profile page to load
        page.locator(".award-details > .heading-container > .text-emoji-container > .text-container > .section-heading > .new-pencil").first.click()
        page.wait_for_timeout(500)  # Wait for edit modal to appear
        textbox = page.get_by_role("textbox", name="Type here")
        textbox.wait_for()  # Ensure textbox is visible and interactive
        textbox.click()
        textbox.press("Control+A")
        textbox.press("Delete")  # Use Delete instead of Backspace
        page.wait_for_timeout(300)
        clean_text = (
                "Highly motivated,Results driven Support Engineer with 1.8 years of experience in web content management, "
                "client support, website maintenance, and application troubleshooting. Skilled in handling "
                "support tickets, SLA based issue resolution, monitoring logs and services, and collaborating "
                "with QA and technical teams to resolve bugs and improve system performance."
            )
        textbox.fill(clean_text)
        page.wait_for_timeout(500)  # Wait for text to be registered
        save_button = page.get_by_role("button", name="Save")
        save_button.click()
        page.wait_for_timeout(2000)  # Wait for save to complete
        print("Profile updated successfully!")
        
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {e}")
        # Take a screenshot for debugging
        page.screenshot(path="error_screenshot.png")
        print("Screenshot saved as error_screenshot.png")
    
    finally:
        print("Closing browser...")
        page.close()
        context.close()
        browser.close()


with sync_playwright() as playwright:
    run(playwright)
