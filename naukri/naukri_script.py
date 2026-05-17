import os
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    email = os.environ.get("NAUKRI_EMAIL")
    password = os.environ.get("NAUKRI_PASSWORD")
    
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.naukri.com/")
    page.get_by_role("link", name="Login", exact=True).click()
    page.get_by_role("textbox", name="Enter your active Email ID /").click()
    page.get_by_role("textbox", name="Enter your active Email ID /").fill("nikitashinde3469@gmail.com")
    page.get_by_role("textbox", name="Enter your password").click()
    page.get_by_role("textbox", name="Enter your password").fill("Wine@123")
    page.get_by_role("button", name="Login", exact=True).click()
    page.wait_for_load_state("load")  # Wait for page to load after login
    page.get_by_role("link", name="View profile").click()
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
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
