"""
Generate Topics Module
Automates content idea generation after dashboard is loaded
Reads from topics.json and generates ideas
"""

import logging
import os
import json
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
IDEAS_PAGE_URL = "https://portal.heyfilo.ai/ideas"
WAIT_TIMEOUT = 15


def react_fill_input(driver, element, value):
    """Properly fill React input elements by triggering events"""
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


def read_topics_file():
    """
    Read topics from topics.json file
    
    Returns:
        list: List of topics (1-30)
    """
    filepath = os.path.join(os.path.dirname(__file__), 'topics.json')
    
    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to list of values (topics)
        topics = [data[str(i)] for i in range(1, 31) if str(i) in data]
        
        logger.info(f"Successfully loaded {len(topics)} topics from topics.json")
        return topics
        
    except Exception as e:
        logger.error(f"Error reading topics file: {e}")
        return None


def select_random_topic(topics):
    """
    Select a random topic from the list
    
    Args:
        topics (list): List of topics
        
    Returns:
        str: Randomly selected topic
    """
    if not topics:
        logger.error("No topics available")
        return None
    
    selected_topic = random.choice(topics)
    logger.info(f"Selected topic: {selected_topic}")
    return selected_topic


def navigate_to_ideas_page(driver):
    """
    Navigate to the ideas page
    
    Args:
        driver (WebDriver): Selenium WebDriver instance
        
    Returns:
        bool: True if navigation successful, False otherwise
    """
    try:
        logger.info(f"Navigating to ideas page: {IDEAS_PAGE_URL}")
        driver.get(IDEAS_PAGE_URL)
        
        # Wait for page to load
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        logger.info("Ideas page loaded")
        
        # Sleep to allow DOM to fully render
        logger.info("Waiting for DOM to fully render...")
        time.sleep(3)
        
        return True
        
    except Exception as e:
        logger.error(f"Error navigating to ideas page: {e}")
        return False


def click_generate_ideas_button(driver):
    """
    Click the "Generate Ideas" button on the ideas page
    
    Args:
        driver (WebDriver): Selenium WebDriver instance
        
    Returns:
        bool: True if button clicked successfully, False otherwise
    """
    try:
        logger.info("Waiting for 'Generate Ideas' button...")
        
        # Wait for the generate ideas button to be clickable
        generate_button = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Generate Ideas')] | //button[contains(., 'Generate')]"))
        )
        
        logger.info("'Generate Ideas' button found")
        generate_button.click()
        logger.info("'Generate Ideas' button clicked")
        
        # Wait for modal to appear and render
        logger.info("Waiting for modal to open and render...")
        time.sleep(2)
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.visibility_of_element_located((
                By.XPATH,
                "//button[contains(@class,'bg-claude-accent') and normalize-space()='Generate']"
            ))
        )
        
        return True
        
    except TimeoutException as e:
        logger.error(f"Timeout waiting for 'Generate Ideas' button: {e}")
        return False
    except Exception as e:
        logger.error(f"Error clicking 'Generate Ideas' button: {e}")
        return False


def fill_topic_input(driver, topic):
    """
    Fill the topic input field in the modal
    
    Args:
        driver (WebDriver): Selenium WebDriver instance
        topic (str): Topic to fill in
        
    Returns:
        bool: True if input filled successfully, False otherwise
    """
    try:
        logger.info("Waiting for topic input field...")
        
        # Wait for the topic input field in the modal
        topic_input = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='e.g. AI in marketing, Summer sale, etc.']"))
        )
        
        logger.info("Topic input field found")
        
        # Fill the input using React event handling
        react_fill_input(driver, topic_input, topic)
        logger.info(f"Filled topic input with: {topic}")
        
        # Sleep to ensure input is processed
        time.sleep(1)
        
        return True
        
    except TimeoutException as e:
        logger.error(f"Timeout waiting for topic input field: {e}")
        return False
    except Exception as e:
        logger.error(f"Error filling topic input: {e}")
        return False


def click_generate_button(driver):
    """
    Click the Generate button in the modal
    """
    try:
        logger.info("Waiting for Generate button in modal...")

        # Wait for modal button specifically by class + text
        generate_btn = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//button[contains(@class,'bg-claude-accent') and normalize-space()='Generate']"
            ))
        )

        logger.info("Generate button found")

        # Scroll into view
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            generate_btn
        )

        time.sleep(1)

        # Try normal click first
        try:
            generate_btn.click()
        except Exception:
            logger.warning("Normal click failed, trying JS click...")
            driver.execute_script(
                "arguments[0].click();",
                generate_btn
            )

        logger.info("Generate button clicked")

        # Wait for generation
        time.sleep(5)

        return True

    except TimeoutException as e:
        logger.error(f"Timeout waiting for Generate button: {e}")
        return False

    except Exception as e:
        logger.error(f"Error clicking Generate button: {e}")
        return False

def generate_topics(driver):
    """
    Complete workflow: Navigate to ideas page, generate ideas with random topic
    
    Args:
        driver (WebDriver): Selenium WebDriver instance (from view_dashboard)
        
    Returns:
        bool: True if workflow successful, False otherwise
    """
    try:
        logger.info("="*60)
        logger.info("Starting Topic Generation Workflow")
        logger.info("="*60)
        
        # Step 1: Read topics file
        logger.info("Reading topics from topics.json...")
        topics = read_topics_file()
        
        if not topics:
            logger.error("Failed to read topics file")
            return False
        
        # Step 2: Select random topic
        selected_topic = select_random_topic(topics)
        
        if not selected_topic:
            logger.error("Failed to select a topic")
            return False
        
        # Step 3: Navigate to ideas page
        if not navigate_to_ideas_page(driver):
            return False
        
        # Step 4: Click "Generate Ideas" button
        if not click_generate_ideas_button(driver):
            return False
        
        # Step 5: Fill topic input in modal
        if not fill_topic_input(driver, selected_topic):
            logger.warning("Failed to fill topic input")
            return False
        
        # Step 6: Click Generate button
        if not click_generate_button(driver):
            logger.warning("Failed to click Generate button")
            return False
        
        logger.info("="*60)
        logger.info("TOPIC GENERATION SUCCESSFUL")
        logger.info("="*60)
        logger.info(f"Generated ideas for topic: {selected_topic}")
        return True
        
    except Exception as e:
        logger.error(f"Unexpected error in topic generation workflow: {e}")
        return False


if __name__ == "__main__":
    # Example usage with view_dashboard
    from view_dashboard import view_dashboard
    
    EMAIL = "faxalo9964@itquoted.com"
    PASSWORD = "Test@123"
    
    driver = view_dashboard(EMAIL, PASSWORD, headless=False)
    
    if driver:
        try:
            # Generate topics using the driver
            success = generate_topics(driver)
            
            if success:
                logger.info("Topic generation completed successfully")
                # Keep browser open for 15 seconds to view results
                time.sleep(15)
            else:
                logger.error("Topic generation failed")
        finally:
            driver.quit()
    else:
        logger.error("Failed to login and access dashboard")
