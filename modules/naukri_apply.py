import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from config.personals import *
from config.questions import *
from config.settings import *
from config.search import companies
from modules.naukri_helpers import *
from modules.naukri_clickers_and_finders import *

def answer_questions(driver):
    """
    Attempts to map dynamic questions to our config/personals and config/questions.
    """
    try:
        # Find all inputs
        inputs = driver.find_elements(By.XPATH, "//input[@type='text' or @type='number']")
        for inp in inputs:
            try:
                # Try to find associated label
                label = ""
                try:
                    # Sometimes the label is a sibling or parent
                    parent = inp.find_element(By.XPATH, "..")
                    label = parent.text.lower()
                except:
                    pass
                
                # Check mapping
                answered = False
                for key, val in questions_mapping.items():
                    if key in label:
                        inp.clear()
                        inp.send_keys(val)
                        print_lg(f"Answered '{label}' with {val}")
                        answered = True
                        break
                
                if not answered:
                    # Specific rules
                    if 'phone' in label or 'mobile' in label:
                        inp.clear()
                        inp.send_keys(phone_number)
                    elif 'name' in label:
                        inp.clear()
                        inp.send_keys(full_name)
                    else:
                        inp.clear()
                        inp.send_keys(default_language_exp)
                        print_lg(f"Defaulted '{label}' to {default_language_exp}")
            except Exception as e:
                pass
                
        # Handle selects
        selects = driver.find_elements(By.TAG_NAME, "select")
        for sel in selects:
            try:
                select = Select(sel)
                # Try to find associated label
                label = ""
                try:
                    parent = sel.find_element(By.XPATH, "..")
                    label = parent.text.lower()
                except:
                    pass
                
                # Simple logic for selects - try to pick the highest or first valid option if no exact match
                answered = False
                for key, val in questions_mapping.items():
                    if key in label:
                        # Try to select by visible text
                        for opt in select.options:
                            if val in opt.text:
                                select.select_by_visible_text(opt.text)
                                answered = True
                                break
                
                if not answered and len(select.options) > 1:
                    select.select_by_index(1) # Pick first non-default
            except:
                pass
                
    except Exception as e:
        print_lg(f"Error answering questions: {e}")

def process_job_page(driver):
    """Handles the application logic for a single job."""
    try:
        # Check if "Apply" button exists
        apply_btn = try_xp(driver, "//button[contains(text(), 'Apply')]", 5)
        if apply_btn and apply_btn.is_displayed():
            apply_btn.click()
            buffer(click_gap)
            
            # Now we might be in a modal or new page. Attempt to answer questions.
            # Switch to new tab if Apply opened one
            for handle in driver.window_handles:
                if handle != driver.current_window_handle and handle != driver.window_handles[0]: # Assuming original is 0
                    driver.switch_to.window(handle)
                    break

            # Check if it's an external URL
            if "naukri.com" not in driver.current_url:
                external_url = driver.current_url
                print_lg(f"External company site detected: {external_url}")
                return False, external_url

            answer_questions(driver)
            
            # Try to submit
            submit_btn = try_xp(driver, "//button[contains(text(), 'Submit') or contains(text(), 'Save')]", 2)
            if submit_btn:
                submit_btn.click()
                buffer(click_gap)
            
            print_lg("Successfully completed apply flow.")
            return True, None
        else:
            print_lg("Apply button not found or it's a company site application.")
            external_url = driver.current_url if "naukri.com" not in driver.current_url else None
            return False, external_url
    except Exception as e:
        print_lg(f"Error during application: {e}")
        return False, None

def apply_to_jobs(driver, max_pages, applied_jobs_file):
    print_lg("Starting to iterate over job listings...")
    
    applied_job_ids = get_applied_job_ids(applied_jobs_file)
    saved_company_urls = get_saved_company_urls("company_website_jobs.csv")
    blacklisted_companies = set(companies)
    
    for page in range(1, max_pages + 1):
        print_lg(f"--- Processing Page {page} ---")
        
        try:
            # Re-fetch job cards on each page
            job_cards = driver.find_elements(By.CSS_SELECTOR, "div.srp-jobtuple-wrapper")
            if not job_cards:
                job_cards = driver.find_elements(By.CSS_SELECTOR, "article.jobTuple")
            
            print_lg(f"Found {len(job_cards)} jobs on this page.")
            
            original_window = driver.current_window_handle
            
            for idx in range(len(job_cards)):
                try:
                    # Re-find the job cards to avoid stale element reference
                    cards = driver.find_elements(By.CSS_SELECTOR, "div.srp-jobtuple-wrapper")
                    if not cards:
                        cards = driver.find_elements(By.CSS_SELECTOR, "article.jobTuple")
                    
                    if idx >= len(cards):
                        break
                        
                    card = cards[idx]
                    title_elem = card.find_element(By.CSS_SELECTOR, "a.title")
                    job_title = title_elem.text
                    job_url = title_elem.get_attribute("href")
                    
                    from config.search import search_terms
                    
                    if not any(term.lower() in job_title.lower() for term in search_terms):
                        print_lg(f"[{idx+1}] Skipping: {job_title} - Doesn't match search terms.")
                        continue
                    
                    # Extract ID from URL or attributes (mocking ID extraction here)
                    job_id = job_url.split('-')[-1].split('?')[0] if '-' in job_url else str(idx)
                    
                    try:
                        company = card.find_element(By.CSS_SELECTOR, "a.comp-name").text
                    except:
                        company = "Unknown"
                        
                    print_lg(f"[{idx+1}] Evaluating: {job_title} at {company}")
                    
                    # Check blacklist and applied history
                    if company in blacklisted_companies:
                        print_lg(f"Skipping {company} - blacklisted.")
                        continue
                        
                    if job_id in applied_job_ids:
                        print_lg(f"Skipping {job_id} - already applied.")
                        continue
                        
                    if "naukri.com/job-listings" not in job_url:
                        print_lg(f"Skipping {company} - Company website job.")
                        if job_url not in saved_company_urls:
                            save_company_website_job("company_website_jobs.csv", job_id, job_title, company, job_url)
                            saved_company_urls.add(job_url)
                        continue
                    
                    # Open job in new tab
                    driver.execute_script(f"window.open('{job_url}', '_blank');")
                    buffer(2)
                    
                    # Switch to the new tab
                    for window_handle in driver.window_handles:
                        if window_handle != original_window:
                            driver.switch_to.window(window_handle)
                            break
                    
                    # Attempt to apply
                    success, external_url = process_job_page(driver)
                    if success:
                        save_applied_job_id(applied_jobs_file, job_id, job_title, company, job_url)
                        applied_job_ids.add(job_id)
                    else:
                        url_to_save = external_url if external_url else job_url
                        if url_to_save not in saved_company_urls:
                            save_company_website_job("company_website_jobs.csv", job_id, job_title, company, url_to_save)
                            saved_company_urls.add(url_to_save)
                    
                    # Close all tabs except the original window and switch back
                    for handle in driver.window_handles:
                        if handle != original_window:
                            driver.switch_to.window(handle)
                            driver.close()
                    driver.switch_to.window(original_window)
                    buffer(1)
                    
                except Exception as e:
                    print_lg(f"Error processing job card {idx+1}: {e}")
                    # Ensure we clean up any extra tabs
                    for handle in driver.window_handles:
                        if handle != original_window:
                            driver.switch_to.window(handle)
                            driver.close()
                    driver.switch_to.window(original_window)
                    
        except Exception as e:
            print_lg(f"Error reading job cards on page {page}: {e}")
            
        # Try to click the Next button
        try:
            next_btn = driver.find_element(By.XPATH, "//a[span[contains(text(), 'Next')]]")
            if next_btn:
                next_btn.click()
                buffer(5)
            else:
                print_lg("No next button found. Reached the end.")
                break
        except Exception:
            print_lg("Next button not clickable or found. Ending search.")
            break
