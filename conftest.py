import os
import pytest
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

# Hook to track test results for screenshot on failure
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        # Launch with 'AutomationControlled' disabled for extra safety
        browser = p.chromium.launch(
            headless=False, 
            args=["--disable-blink-features=AutomationControlled"]
        )
        yield browser
        browser.close()

@pytest.fixture
def page(browser, request):
    # Determine test file name (without extension) for folder organization
    test_file_name = request.node.fspath.purebasename
    
    # Create structure: videos/<test_file>/
    #                 screenshots/<test_file>/
    video_dir = os.path.join("videos", test_file_name)
    screenshot_dir = os.path.join("screenshots", test_file_name)
    
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(screenshot_dir, exist_ok=True)

    # Enable video recording
    context = browser.new_context(record_video_dir=video_dir)
    page = context.new_page()
    
    # Apply stealth
    stealth = Stealth()
    stealth.apply_stealth_sync(page)
    
    yield page
    
    # Teardown - Always take screenshot
    # Check if request.node.name contains characters that might be invalid for filenames
    # keeping it simple for now, assuming standard pytest names
    safe_test_name = request.node.name.replace("/", "_").replace(":", "_")
    
    screenshot_name = os.path.join(screenshot_dir, f"{safe_test_name}.png")
    try:
        page.screenshot(path=screenshot_name, full_page=True)
        print(f"\nScreenshot saved: {screenshot_name}")
    except Exception as e:
        print(f"\nFailed to take screenshot: {e}")

    # Capture video path before closing
    video_path = None
    try:
        video_path = page.video.path()
    except:
        pass

    page.close()
    context.close()
    
    # Rename video to match test name
    if video_path and os.path.exists(video_path):
        new_video_name = os.path.join(video_dir, f"{safe_test_name}.webm")
        try:
            # Remove existing file if present to avoid error
            if os.path.exists(new_video_name):
                os.remove(new_video_name)
            os.rename(video_path, new_video_name)
            print(f"Video saved: {new_video_name}")
        except Exception as e:
            print(f"Failed to rename video: {e}")