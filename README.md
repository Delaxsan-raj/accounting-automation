# Accounting Automation Tests

This project contains automated tests for the Accounting Application using Playwright and Pytest.

## Setup

1.  **Clone the repository**
2.  **Install dependencies**:
    ```bash
    pip install -r requirement.txt
    playwright install chromium
    ```
3.  **Environment Variables**:
    Create a `.env` file in the root directory with the following variables:
    ```
    ADMIN_LOGIN=your_admin_email
    ADMIN_PASSWORD=your_admin_password
    ```

## Running Tests

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_login.py
```

## Artifacts

Screenshots and videos of test executions are saved in:
-   `screenshots/`
-   `videos/`
