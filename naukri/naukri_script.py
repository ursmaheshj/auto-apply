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
        
        # Wait for navigation after login
        print("Waiting for page to load after login...")
        try:
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            print("Page loaded (domcontentloaded)")
        except Exception as e:
            print(f"DOMContentLoaded timeout: {e}")
        
        page.wait_for_timeout(3000)  # Wait for dynamic content to render
        print(f"Current URL: {page.url}")
        print("Taking screenshot after login...")
        page.screenshot(path="after_login.png")
        
        # Debug: Print all links on the page
        print("Finding View profile link...")
        print("Available links on page:")
        links = page.get_by_role("link").all()
        for i, link in enumerate(links):
            try:
                link_text = link.text_content()
                print(f"  Link {i}: '{link_text}'")
            except:
                print(f"  Link {i}: (unable to read text)")
        
        # Try multiple selector strategies
        try:
            print("Trying exact match 'View profile'...")
            page.get_by_role("link", name="View profile").click(timeout=5000)
        except Exception as e:
            print(f"  Failed: {e}")
            try:
                print("Trying partial match with 'profile'...")
                page.get_by_role("link", name="profile", exact=False).click(timeout=5000)
            except Exception as e2:
                print(f"  Failed: {e2}")
                try:
                    print("Trying text search for 'View profile'...")
                    page.get_by_text("View profile", exact=False).first.click(timeout=5000)
                except Exception as e3:
                    print(f"  Failed: {e3}")
                    try:
                        print("Trying href selector for profile...")
                        page.locator("a[href*='profile']").first.click(timeout=5000)
                    except Exception as e4:
                        print(f"  Failed: {e4}")
                        print("Taking screenshot to debug...")
                        page.screenshot(path="debug_links.png")
                        print("Screenshot saved as debug_links.png")
                        raise Exception("Could not find View profile link with any selector")
        
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
        print(f"\n{'='*60}")
        print(f"Error occurred: {type(e).__name__}: {e}")
        print(f"{'='*60}")
        print(f"Current URL: {page.url}")
        print(f"Page title: {page.title()}")
        
        # Take multiple screenshots for debugging
        print("Taking error screenshots...")
        try:
            page.screenshot(path="error_screenshot.png")
            print("Screenshot saved as error_screenshot.png")
        except Exception as ss_e:
            print(f"Failed to save error_screenshot.png: {ss_e}")
        
        # Save page HTML for debugging
        try:
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("Page HTML saved as debug_page.html")
        except Exception as html_e:
            print(f"Failed to save HTML: {html_e}")
        
        # Dump all links
        try:
            links = page.get_by_role("link").all()
            with open("debug_links.txt", "w", encoding="utf-8") as f:
                f.write(f"Total links found: {len(links)}\n\n")
                for i, link in enumerate(links):
                    try:
                        link_text = link.text_content()
                        link_href = link.get_attribute("href")
                        f.write(f"Link {i}: text='{link_text}', href='{link_href}'\n")
                    except:
                        f.write(f"Link {i}: (unable to read)\n")
            print("Links dump saved as debug_links.txt")
        except Exception as links_e:
            print(f"Failed to dump links: {links_e}")
        
        print(f"{'='*60}\n")
    
    finally:
        print("Closing browser...")
        page.close()
        context.close()
        browser.close()


with sync_playwright() as playwright:
    run(playwright)
