import os
import pytest
from dotenv import load_dotenv
from Pages.login_page import LoginPage # Make sure folder name case matches!

# Load environment variables
load_dotenv()

def test_successful_login(page):
    # 1. Setup
    login_pg = LoginPage(page)
    
    # 2. Action
    login_pg.navigate()
    admin_email = os.getenv("ADMIN_LOGIN")
    admin_pass = os.getenv("ADMIN_PASSWORD")
    page.wait_for_timeout(10000)
    login_pg.login(admin_email, admin_pass)
    page.wait_for_url(login_pg.SUCCESS_URL, timeout=15000)
    assert page.url == login_pg.SUCCESS_URL


def test_invalid_password_login(page):
    login_pg = LoginPage(page)
    login_pg.navigate()
    test_email = "test@ainthinai.com"
    test_password = "test"
    page.wait_for_timeout(10000)
    login_pg.login(test_email, test_password)

@pytest.mark.parametrize("invalid_email", [
    "invalid@example.com",
    "wrong@test.com",
    "fake@email.com",
    "notreal@domain.com",
    "test@wrong.com"
])
def test_failed_login_invalid_emails(page, invalid_email):
    login_pg = LoginPage(page)
    login_pg.navigate()
    invalid_password = "WrongPassword123"
    login_pg.login(invalid_email, invalid_password)
    page.wait_for_timeout(2000)

    


    
    
    
    

# --- New Email Validation Tests ---

def test_login_empty_email(page):
    """TC-EMAIL-001: should show error for empty email"""
    login_pg = LoginPage(page)
    login_pg.navigate()
    login_pg.login("", "AnyPassword123")
    
    # Verify error message
    error = login_pg.get_error_message()
    # Expecting some validation message - assertion depends on actual app behavior
    # If app uses HTML5 validation, we might look for :invalid pseudo-class or validationMessage property
    # For now assuming UI error message
    assert error is not None, "Error message should be displayed for empty email"


@pytest.mark.parametrize("invalid_email_format", [
    "plainaddress",
    "#@%^%#$@#$@#.com",
    "@example.com",
    "Joe Smith <email@example.com>",
    "email.example.com",
    "email@example@example.com",
    ".email@example.com",
    "email.@example.com",
    "email..email@example.com",
])
def test_login_invalid_email_formats(page, invalid_email_format):
    """Test various invalid email formats (Special Characters, Format)"""
    login_pg = LoginPage(page)
    login_pg.navigate()
    login_pg.login(invalid_email_format, "Password123!")
    
    error = login_pg.get_error_message()
    assert error is not None, f"Error should be displayed for invalid format: {invalid_email_format}"


def test_login_email_case_insensitivity(page):
    """TC-EMAIL-007: Email Case Sensitivity"""
    # Assuming successful login is possible with ADMIN credentials in different case
    # If not, this test should be adapted to expect success or specific behavior
    
    login_pg = LoginPage(page)
    login_pg.navigate()
    
    admin_email = os.getenv("ADMIN_LOGIN")
    admin_pass = os.getenv("ADMIN_PASSWORD")
    
    if not admin_email or not admin_pass:
        pytest.skip("Admin credentials not set")

    # Mix case
    mixed_case_email = admin_email.upper()
    
    login_pg.login(mixed_case_email, admin_pass)
    
    # Should login successfully
    try:
        page.wait_for_url(login_pg.SUCCESS_URL, timeout=15000)
        assert page.url == login_pg.SUCCESS_URL
    except:
        pytest.fail("Login failed with uppercase email - check if system is case sensitive")


def test_login_email_max_length(page):
    """TC-EMAIL-008: Maximum Length Email"""
    login_pg = LoginPage(page)
    login_pg.navigate()
    
    # Create a very long email
    long_email = "a" * 255 + "@example.com"
    login_pg.login(long_email, "Password123")
    
    # Should fail locally or show error
    error = login_pg.get_error_message()
    assert error is not None, "Error should be displayed for max length email"


def test_login_email_sql_injection(page):
    """TC-EMAIL-009: SQL Injection in Email"""
    login_pg = LoginPage(page)
    login_pg.navigate()
    
    payloads = ["' OR '1'='1", "admin' --", "' UNION SELECT 1,2,3--"]
    
    for payload in payloads:
        login_pg.login(payload, "Password123")
        # Should NOT redirect to success
        page.wait_for_timeout(2000)
        assert page.url != login_pg.SUCCESS_URL
        assert login_pg.get_error_message() is not None


def test_login_email_xss(page):
    """TC-EMAIL-010: XSS in Email Field"""
    login_pg = LoginPage(page)
    login_pg.navigate()
    
    xss_payload = "<script>alert('XSS')</script>"
    login_pg.login(xss_payload, "Password123")
    
    # Check if alert dialog appears (Playwright handles dialogs automatically by dismissing, 
    # but we can listen for it if we want to confirm vulnerability - here we assert NO vulnerability)
    
    dialog_triggered = False
    def handle_dialog(dialog):
        nonlocal dialog_triggered
        dialog_triggered = True
        dialog.dismiss()

    page.on("dialog", handle_dialog)
    
    page.wait_for_timeout(2000)
    
    assert not dialog_triggered, "XSS payload triggered an alert dialog!"
    # Also expect login failure
    assert page.url != login_pg.SUCCESS_URL

# --- Password Security Tests ---

def test_password_field_masking(page):
    """TC-PASS-002: Password Masking (type='password')"""
    login_pg = LoginPage(page)
    login_pg.navigate()
    
    # Default state should be masked
    assert login_pg.get_password_input_type() == "password", "Password field should be masked by default"


def test_password_toggle_visibility(page):
    """TC-PASS-003 & TC-PASS-004: Show/Hide Password Toggle"""
    login_pg = LoginPage(page)
    login_pg.navigate()
    
    # 1. Check initial state
    assert login_pg.get_password_input_type() == "password"
    
    # 2. Click toggle (Show)
    login_pg.toggle_password_visibility()
    page.wait_for_timeout(500) # Wait for UI update
    
    # 3. Check if type changed to text (visible)
    assert login_pg.get_password_input_type() == "text", "Password should be visible after clicking toggle"
    
    # 4. Click toggle again (Hide)
    login_pg.toggle_password_visibility()
    page.wait_for_timeout(500)
    
    # 5. Check if type changed back to password (masked)
    assert login_pg.get_password_input_type() == "password", "Password should be masked after clicking toggle again"


def test_login_password_sql_injection(page):
    """TC-PASS-009: SQL Injection in Password"""
    login_pg = LoginPage(page)
    login_pg.navigate()
    
    email = "test@ainthinai.com" # Valid or generic email
    payloads = ["' OR '1'='1", "' OR '1'='1' --", "admin' #"]
    
    for payload in payloads:
        # Re-navigate or clear fields if needed, but simple login calls usually refilled
        # For safety/cleanliness, reload
        login_pg.navigate()
        
        login_pg.login(email, payload)
        
        # Verify NO success redirect
        page.wait_for_timeout(2000)
        assert page.url != login_pg.SUCCESS_URL
        # Should see an error message
        assert login_pg.get_error_message() is not None
