"""
Create Content Module
Automates content creation after dashboard is loaded
Reads from gaming text files and fills the content form
"""

import logging
import os, time, random, json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
CONTENT_PAGE_URL = "https://portal.heyfilo.ai/content"
NEW_CONTENT_PAGE_URL = "https://portal.heyfilo.ai/content/new"
WAIT_TIMEOUT = 15

def react_fill_input(driver, element, value):
    driver.execute_script("""
        const nativeInputValueSetter =
            Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype,
                'value'
            ).set;

        nativeInputValueSetter.call(arguments[0], arguments[1]);

        arguments[0].dispatchEvent(
            new Event('input', { bubbles: true })
        );

        arguments[0].dispatchEvent(
            new Event('change', { bubbles: true })
        );
    """, element, value)

def read_gaming_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)

    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.info(f"Successfully loaded {filename}")
        logger.info(f"Title: {data.get('title')}")

        return data

    except Exception as e:
        logger.error(f"Error reading file {filename}: {e}")
        return None


def navigate_to_content_page(driver):
    """
    Navigate to the content page
    
    Args:
        driver (WebDriver): Selenium WebDriver instance
        
    Returns:
        bool: True if navigation successful, False otherwise
    """
    try:
        logger.info(f"Navigating to content page: {CONTENT_PAGE_URL}")
        driver.get(CONTENT_PAGE_URL)
        
        # Wait for page to load
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        logger.info("Content page loaded")
        
        # Sleep to allow DOM to fully render
        logger.info("Waiting for DOM to fully render...")
        time.sleep(3)
        
        return True
        
    except Exception as e:
        logger.error(f"Error navigating to content page: {e}")
        return False


def click_new_content_button(driver):
    """
    Click the "New Content" button on the content page
    
    Args:
        driver (WebDriver): Selenium WebDriver instance
        
    Returns:
        bool: True if button clicked successfully, False otherwise
    """
    try:
        logger.info("Waiting for 'New Content' button...")
        
        # Look for the button - try multiple selectors
        try:
            # Try by href attribute first
            new_button = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@href='/content/new']//button | //button[contains(text(), 'New Content')]"))
            )
        except TimeoutException:
            # Try alternative selector
            new_button = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, "//button"))
            )
        
        logger.info("'New Content' button found")
        new_button.click()
        logger.info("'New Content' button clicked")
        
        # Wait for navigation to new content page
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.url_to_be(NEW_CONTENT_PAGE_URL)
        )
        logger.info(f"Redirected to: {driver.current_url}")
        
        # Sleep to allow new page DOM to fully render
        logger.info("Waiting for new content page DOM to render...")
        time.sleep(4)
        
        return True
        
    except TimeoutException as e:
        logger.error(f"Timeout waiting for or clicking 'New Content' button: {e}")
        return False
    except Exception as e:
        logger.error(f"Error clicking 'New Content' button: {e}")
        return False


def fill_title_field(driver, title):
    """Fill the title field"""
    try:
        title_field = driver.find_element(By.ID, "title")
        react_fill_input(driver, title_field, title)
        logger.info(f"Filled title: {title}")
        return True
    except Exception as e:
        logger.warning(f"Could not fill title field: {e}")
        return False


def fill_excerpt_field(driver, excerpt):
    """Fill the excerpt field"""
    try:
        excerpt_field = driver.find_element(By.ID, "excerpt")
        react_fill_input(driver, excerpt_field, excerpt)
        logger.info("Filled excerpt field")
        return True
    except Exception as e:
        logger.warning(f"Could not fill excerpt field: {e}")
        return False

def fill_content_body_field(driver, content_body):
    try:
        editor = driver.find_element(By.CSS_SELECTOR, "div.ProseMirror")

        driver.execute_script("""
            arguments[0].focus();

            arguments[0].innerHTML = '';

            const lines = arguments[1].split('\\n');

            arguments[0].innerHTML = lines
                .map(line => `<p>${line}</p>`)
                .join('');

            arguments[0].dispatchEvent(
                new Event('input', { bubbles: true })
            );
        """, editor, content_body)

        logger.info("Filled content body")
        return True

    except Exception as e:
        logger.warning(f"Could not fill content body field: {e}")
        return False

def fill_seo_title_field(driver, seo_title):
    """Fill the SEO title field"""
    try:
        seo_title_field = driver.find_element(By.ID, "seo_title")
        react_fill_input(driver, seo_title_field, seo_title)
        logger.info("Filled SEO title field")
        return True
    except Exception as e:
        logger.warning(f"Could not fill SEO title field: {e}")
        return False


def fill_seo_description_field(driver, seo_description):
    """Fill the SEO description textarea"""
    try:
        # Find the textarea for SEO description
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        if len(textareas) > 0:
            seo_desc_textarea = textareas[0]
            seo_desc_textarea.clear()
            seo_desc_textarea.send_keys(seo_description)
            logger.info("Filled SEO description field")
            return True
        else:
            logger.warning("Could not find SEO description textarea")
            return False
    except Exception as e:
        logger.warning(f"Could not fill SEO description field: {e}")
        return False


def fill_seo_keywords_field(driver, seo_keywords):
    """Fill the SEO keywords field"""
    try:
        seo_keywords_field = driver.find_element(By.ID, "seo_keywords")
        react_fill_input(driver, seo_keywords_field, seo_keywords)
        logger.info("Filled SEO keywords field")
        return True
    except Exception as e:
        logger.warning(f"Could not fill SEO keywords field: {e}")
        return False


def fill_content_form(driver, content_data):
    """
    Fill the content creation form with data from gaming file
    
    Args:
        driver (WebDriver): Selenium WebDriver instance
        content_data (dict): Content data parsed from gaming file
        
    Returns:
        bool: True if form filled successfully, False otherwise
    """
    try:
        logger.info("Waiting for form elements...")
        
        # Wait for title field to be present
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "title"))
        )
        logger.info("Form found and ready to fill")
        
        # Sleep to ensure all form elements are fully rendered
        logger.info("Waiting for all form elements to render...")
        time.sleep(2)
        
        filled_fields = 0
        
        # Fill each field based on the actual form structure
        if content_data.get('title'):
            if fill_title_field(driver, content_data['title']):
                filled_fields += 1
                time.sleep(1)
        
        if content_data.get('content_body'):
            if fill_content_body_field(driver, content_data['content_body']):
                filled_fields += 1
                time.sleep(1)
        
        if content_data.get('excerpt'):
            if fill_excerpt_field(driver, content_data['excerpt']):
                filled_fields += 1
                time.sleep(1)
        
        if content_data.get('seo_title'):
            if fill_seo_title_field(driver, content_data['seo_title']):
                filled_fields += 1
                time.sleep(1)
        
        if content_data.get('seo_description'):
            if fill_seo_description_field(driver, content_data['seo_description']):
                filled_fields += 1
                time.sleep(1)
        
        if content_data.get('seo_keywords'):
            if fill_seo_keywords_field(driver, content_data['seo_keywords']):
                filled_fields += 1
                time.sleep(1)
        
        logger.info(f"Total fields filled: {filled_fields}")
        
        # Sleep before saving to ensure all fields are processed
        logger.info("Waiting before save operation...")
        time.sleep(2)
        
        return filled_fields > 0
        
    except TimeoutException as e:
        logger.error(f"Timeout waiting for form: {e}")
        return False
    except Exception as e:
        logger.error(f"Error filling form: {e}")
        return False


def click_save_button(driver):
    """
    Click the Save button to submit the content form
    
    Args:
        driver (WebDriver): Selenium WebDriver instance
        
    Returns:
        bool: True if button clicked and page changed, False otherwise
    """
    try:
        logger.info("Waiting for Save button...")
        
        # Wait for and find the save button
        # Try multiple selectors to find the save button
        save_button = None
        try:
            # Try finding by button text containing "Save"
            time.sleep(2)
            save_button = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Save')]"))
            )
        except TimeoutException:
            # Try alternative: find all buttons and look for one with Save
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if "Save" in button.text:
                    save_button = button
                    break
        
        if not save_button:
            logger.error("Could not find Save button")
            return False
        
        logger.info("Save button found")
        
        # Store current URL to check if page changes
        original_url = driver.current_url
        
        # Sleep before clicking to ensure button is fully interactive
        logger.info("Waiting before clicking save button...")
        time.sleep(1)
        
        save_button.click()
        logger.info("Save button clicked")
        
        # Wait for page to reload or URL to change
        logger.info("Waiting for page reload/change...")
        time.sleep(3)
        
        try:
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                lambda d: d.current_url != original_url or d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            # Page might not change, check if we're still on the form or got an error
            logger.warning("Page did not change after save - this might be expected behavior")
        
        logger.info(f"Current URL: {driver.current_url}")
        logger.info("Content saved successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error clicking Save button: {e}")
        return False


def create_content(driver):
    """
    Complete workflow: Navigate to content page, create new content, and save
    
    Args:
        driver (WebDriver): Selenium WebDriver instance (from view_dashboard)
        
    Returns:
        bool: True if content creation successful, False otherwise
    """
    file_number = random.randint(1, 5)
    gaming_file = f"gaming_{file_number}.json"

    try:
        logger.info("="*60)
        logger.info("Starting Content Creation Workflow")
        logger.info("="*60)
        
        # Step 1: Read gaming file
        logger.info(f"Reading content from {gaming_file}...")
        content_data = read_gaming_file(gaming_file)
        
        if not content_data:
            logger.error("Failed to read gaming file")
            return False
        
        # Step 2: Navigate to content page
        if not navigate_to_content_page(driver):
            return False
        
        # Step 3: Click "New Content" button
        if not click_new_content_button(driver):
            return False
        
        # Step 4: Fill the form
        if not fill_content_form(driver, content_data):
            logger.warning("Some form fields could not be filled")
        
        # Step 5: Click Save button
        if not click_save_button(driver):
            return False
        
        logger.info("="*60)
        logger.info("CONTENT CREATED SUCCESSFULLY")
        logger.info("="*60)
        return True
        
    except Exception as e:
        logger.error(f"Unexpected error in content creation workflow: {e}")
        return False


if __name__ == "__main__":
    # Example usage with view_dashboard
    from view_dashboard import view_dashboard
    
    EMAIL = "faxalo9964@itquoted.com"
    PASSWORD = "Test@123"
    
    driver = view_dashboard(EMAIL, PASSWORD, headless=False)
    
    if driver:
        try:
            # Create content using the driver
            success = create_content(driver)
            
            if success:
                logger.info("Content creation completed successfully")
                # Keep browser open for 10 seconds to view result
                import time
                time.sleep(10)
            else:
                logger.error("Content creation failed")
        finally:
            driver.quit()
    else:
        logger.error("Failed to login and access dashboard")
