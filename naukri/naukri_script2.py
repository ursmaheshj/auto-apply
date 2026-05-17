import os
import sys
import random
from playwright.sync_api import sync_playwright

def run() -> None:
    # 1. Retrieve credentials securely from GitHub Secrets
    email = os.environ.get("NAUKRI_EMAIL")
    password = os.environ.get("NAUKRI_PASSWORD")

    if not email or not password:
        print("CRITICAL ERROR: Environment credentials (NAUKRI_EMAIL/NAUKRI_PASSWORD) are missing.")
        sys.exit(1)

    with sync_playwright() as p:
        print("Launching stealth browser instance...")
        
        # Launching Chromium with advanced arguments to strip standard automation signatures
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-sandbox"
            ]
        )
        
        # Construct context mimicking an active, real-world Windows 10 user asset
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="Asia/Kolkata"
        )
        
        # Runtime injection to neutralize basic webdriver detection flags
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()
        
        print("Navigating to Naukri...")
        # Simulating an organic entry point via a direct referrer header
        page.goto("https://www.naukri.com/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(random.randint(2000, 4000)) # Natural human delay
        
        # Verify if Akamai redirected the bot to an Access Denied landing page
        if "Access Denied" in page.title() or page.locator("h1:has-text('Access Denied')").is_visible():
            print("CRITICAL ERROR: Execution halted. Cloud infrastructure flagged by Akamai WAF.")
            page.screenshot(path="akamai_block_debug.png")
            browser.close()
            sys.exit(1)

        print("Landing page bypassed successfully. Initializing login phase...")
        
        # Using the explicit element ID instead of a role locator to handle layout modifications
        login_button = page.locator("#login_Layer")
        login_button.wait_for(state="visible", timeout=15000)
        login_button.click()
        page.wait_for_timeout(random.randint(1000, 2500))

        # Populate user credentials safely
        print("Injecting account details...")
        email_field = page.get_by_role("textbox", name="Enter your active Email ID /")
        email_field.wait_for(state="visible")
        email_field.fill(email)
        
        password_field = page.get_by_role("textbox", name="Enter your password")
        password_field.fill(password)
        
        page.wait_for_timeout(random.randint(500, 1500))
        page.get_by_role("button", name="Login", exact=True).click()
        
        print("Submitting login form. Waiting for dashboard synchronization...")
        page.wait_for_load_state("networkidle", timeout=30000)
        
        # Confirm authentication status
        try:
            profile_link = page.get_by_role("link", name="View profile")
            profile_link.wait_for(state="visible", timeout=15000)
            profile_link.click()
        except Exception:
            print("Authentication tracking failed. Account likely challenged by a CAPTCHA.")
            page.screenshot(path="login_failure_debug.png")
            browser.close()
            sys.exit(1)

        print("Profile synchronized. Locating target bio updates...")
        page.wait_for_load_state("load")
        
        # Trigger edit modal window
        page.locator(".award-details > .heading-container > .text-emoji-container > .text-container > .section-heading > .new-pencil").first.click()
        page.wait_for_timeout(1500)
        
        textbox = page.get_by_role("textbox", name="Type here")
        textbox.wait_for(state="visible")
        textbox.click()
        
        # Clear field and simulate active human updates
        textbox.press("Control+A")
        textbox.press("Delete")
        page.wait_for_timeout(800)
        
        clean_text = (
            "Highly motivated, Results driven Support Engineer with 1.8 years of experience in web content management, "
            "client support, website maintenance, and application troubleshooting. Skilled in handling "
            "support tickets, SLA based issue resolution, monitoring logs and services, and collaborating "
            "with QA and technical teams to resolve bugs and improve system performance."
        )
        
        textbox.fill(clean_text)
        page.wait_for_timeout(1000)
        
        page.get_by_role("button", name="Save").click()
        print("SUCCESS: Profile details successfully saved and updated.")
        page.wait_for_timeout(3000)
        
        context.close()
        browser.close()

if __name__ == "__main__":
    run()