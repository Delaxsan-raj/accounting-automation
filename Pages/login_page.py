from playwright.sync_api import Page
import time

class LoginPage:
    # Environment specific URLs
    LOGIN_URL = "https://ainthinaiaccountingfrontend.vercel.app/"
    SUCCESS_URL = "https://ainthinaiaccountingfrontend.vercel.app/founder/dashboard"

    def __init__(self, page: Page):
        self.page = page
        # Updated selectors to use 'name' attributes
        self._username_input = page.locator("input[name='email']")
        self._password_input = page.locator("input[name='password']")
        self._login_button = page.locator("button[type='submit']")
        # Password toggle button (matches both show and hide states)
        self._password_toggle = page.locator("button[aria-label='Show password'], button[aria-label='Hide password']")
        # Error message locator - attempting to match Chakra UI pattern or generic alert
        self._error_message = page.locator("[role='alert'], .chakra-form__error-message")

    def navigate(self):
        self.page.goto(self.LOGIN_URL)
        # Wait for the page to be fully loaded to help stealth bypass
        self.page.wait_for_load_state("domcontentloaded")

    def login(self, username, password):
        # 1. Type like a human (avoids triggering bot detection)
        # We use .type() with a 'delay' instead of .fill()
        self._username_input.type(username, delay=100)
        
        # Small random-ish pause between fields
        self.page.wait_for_timeout(500)
        
        self._password_input.type(password, delay=100)
        
        # 2. Ensure the button is not just visible, but ready
        self._login_button.wait_for(state="visible")
        
        # Give Turnstile a moment to validate the "human" typing
        self.page.wait_for_timeout(1000)
        
        # 3. Click the button
        self._login_button.click()

    def get_error_message(self):
        """Returns the text of the error message if visible."""
        try:
            self._error_message.first.wait_for(state="visible", timeout=3000)
            return self._error_message.first.inner_text()
        except:
            return None

    def toggle_password_visibility(self):
        """Clicks the password visibility toggle button."""
        self._password_toggle.click()

    def get_password_input_type(self):
        """Returns the current type attribute of the password input."""
        return self._password_input.get_attribute("type")
        
        # 4. Wait for the navigation to finish
        # Increased timeout slightly as Vercel + Auth can sometimes be slo