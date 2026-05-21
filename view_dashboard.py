"""
View Dashboard After Login
Automates login process and waits for dashboard to load
"""

import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from login_automation import setup_driver, login

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
DASHBOARD_WAIT_TIMEOUT = 15


def wait_for_dashboard(driver, timeout=DASHBOARD_WAIT_TIMEOUT):
    """
    Wait for the dashboard to fully load after login
    
    Args:
        driver (WebDriver): Selenium WebDriver instance
        timeout (int): Maximum time to wait for dashboard elements (seconds)
        
    Returns:
        bool: True if dashboard loaded successfully, False otherwise
    """
    try:
        logger.info("Waiting for dashboard to load...")
        
        # Wait for dashboard main container to be present
        # This can be customized based on your actual dashboard structure
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        logger.info("Dashboard body element loaded")
        
        # Sleep to allow dashboard to render
        logger.info("Allowing dashboard DOM to render...")
        time.sleep(2)
        
        # Additional wait - check if page title or main content changed from login page
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.title != "Login" and len(driver.title) > 0
        )
        logger.info(f"Dashboard page title detected: {driver.title}")
        
        # Optional: Wait for specific dashboard elements (customize as needed)
        # Uncomment and modify based on your dashboard HTML structure
        # Example: Wait for a dashboard-specific class or ID
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "dashboard-container"))
            )
            logger.info("Dashboard container found")
        except TimeoutException:
            # If specific dashboard element not found, continue anyway
            logger.warning("Dashboard-specific container not found, but page navigation successful")
        
        # Final sleep to ensure all assets and components are loaded
        logger.info("Waiting for all dashboard components to load...")
        time.sleep(2)
        
        logger.info("Dashboard has loaded successfully")
        return True
        
    except TimeoutException as e:
        logger.error(f"Timeout waiting for dashboard to load: {e}")
        return False
    except Exception as e:
        logger.error(f"Error while waiting for dashboard: {e}")
        return False


def view_dashboard(email, password, headless=False):
    """
    Complete workflow: Login and view dashboard
    
    Args:
        email (str): Email address for login
        password (str): Password for login
        headless (bool): Whether to run browser in headless mode
        
    Returns:
        WebDriver: The WebDriver instance (you must call driver.quit() when done)
    """
    driver = None
    try:
        logger.info("="*60)
        logger.info("Starting Login and Dashboard View")
        logger.info("="*60)
        
        # Setup driver
        driver = setup_driver(headless=headless)
        
        # Perform login
        logger.info("Performing login...")
        success = login(driver, email, password)
        
        if not success:
            logger.error("Login failed")
            driver.quit()
            return None
        
        # Wait for dashboard to load
        dashboard_loaded = wait_for_dashboard(driver)
        
        if dashboard_loaded:
            logger.info("="*60)
            logger.info("DASHBOARD LOADED SUCCESSFULLY")
            logger.info("="*60)
            logger.info(f"Current URL: {driver.current_url}")
            logger.info(f"Page Title: {driver.title}")
            
            # Final sleep to ensure dashboard is fully interactive
            logger.info("Waiting for dashboard to be fully interactive...")
            time.sleep(2)
            
            return driver
        else:
            logger.error("Failed to load dashboard")
            driver.quit()
            return None
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if driver:
            driver.quit()
        return None


if __name__ == "__main__":
    # Example usage
    EMAIL = "faxalo9964@itquoted.com"
    PASSWORD = "Test@123"
    
    driver = view_dashboard(EMAIL, PASSWORD, headless=False)
    
    if driver:
        try:
            # Keep browser open for 10 seconds to view the dashboard
            import time
            time.sleep(10)
            logger.info("Closing dashboard view")
        finally:
            driver.quit()
    else:
        logger.error("Could not access dashboard")