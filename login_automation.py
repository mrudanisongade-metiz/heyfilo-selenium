"""
Selenium Login Automation Module
Provides functions to automate login form interactions
"""

import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
LOGIN_URL = "https://portal.heyfilo.ai/login"
WAIT_TIMEOUT = 10


def setup_driver(headless=False):
    """
    Initialize and return Chrome WebDriver
    
    Args:
        headless (bool): Whether to run browser in headless mode
        
    Returns:
        WebDriver: Chrome WebDriver instance
        
    Raises:
        WebDriverException: If WebDriver initialization fails
    """
    try:
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Chrome WebDriver initialized successfully")
        return driver
    except WebDriverException as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        raise


def login(driver, email, password):
    """
    Navigate to login page and fill in credentials
    
    Args:
        driver (WebDriver): Selenium WebDriver instance
        email (str): Email address to enter
        password (str): Password to enter
        
    Returns:
        bool: True if login was successful, False otherwise
    """
    try:
        logger.info(f"Navigating to {LOGIN_URL}")
        driver.get(LOGIN_URL)
        
        # Wait for email input field to be present
        logger.info("Waiting for email field to load...")
        email_field = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        logger.info("Email field found")
        
        # Sleep to ensure form is fully rendered
        logger.info("Waiting for form to fully render...")
        time.sleep(1)
        
        # Fill email field
        email_field.clear()
        email_field.send_keys(email)
        logger.info(f"Email field filled with: {email}")
        
        time.sleep(0.5)
        
        # Wait for password input field to be present
        logger.info("Waiting for password field to load...")
        password_field = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        logger.info("Password field found")
        
        # Fill password field
        password_field.clear()
        password_field.send_keys(password)
        logger.info("Password field filled")
        
        time.sleep(0.5)
        
        # Wait for the submit button and click it
        logger.info("Waiting for Sign in button...")
        submit_button = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        logger.info("Sign in button found and clickable")
        
        time.sleep(0.5)
        
        submit_button.click()
        logger.info("Sign in button clicked")
        
        # Wait for navigation after form submission
        logger.info("Waiting for page to load after submission...")
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.url_changes(LOGIN_URL)
        )
        logger.info("Form submitted successfully. Page navigation detected.")
        
        # Sleep to allow dashboard to start loading
        logger.info("Waiting for dashboard to load...")
        time.sleep(2)
        
        return True
        
    except TimeoutException as e:
        logger.error(f"Timeout while waiting for element: {e}")
        return False
    except NoSuchElementException as e:
        logger.error(f"Element not found: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        return False
