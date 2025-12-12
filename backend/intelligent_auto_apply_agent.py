"""
Intelligent Auto-Apply Agent with Browser Automation
Handles automatic job applications across multiple platforms using Selenium
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobPlatformHandler:
    """Base class for job platform handlers"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def detect_platform(self, url: str) -> str:
        """Detect which job platform the URL belongs to"""
        if 'linkedin.com' in url:
            return 'linkedin'
        elif 'indeed.com' in url:
            return 'indeed'
        elif 'naukri.com' in url:
            return 'naukri'
        elif 'monster.com' in url:
            return 'monster'
        elif 'glassdoor.com' in url:
            return 'glassdoor'
        else:
            return 'company_career_page'
    
    def apply_to_job(self, job_url: str, user_data: Dict) -> Dict:
        """Apply to a job - to be implemented by platform-specific handlers"""
        raise NotImplementedError


class LinkedInHandler(JobPlatformHandler):
    """Handler for LinkedIn job applications"""
    
    def apply_to_job(self, job_url: str, user_data: Dict) -> Dict:
        try:
            self.driver.get(job_url)
            time.sleep(2)
            
            # Look for Easy Apply button
            try:
                easy_apply_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'jobs-apply-button')]"))
                )
                easy_apply_btn.click()
                time.sleep(1)
                
                # Fill in the application form
                return self._fill_linkedin_form(user_data)
                
            except TimeoutException:
                return {
                    "success": False,
                    "error": "Easy Apply button not found - may require external application",
                    "platform": "linkedin"
                }
                
        except Exception as e:
            logger.error(f"LinkedIn application error: {str(e)}")
            return {"success": False, "error": str(e), "platform": "linkedin"}
    
    def _fill_linkedin_form(self, user_data: Dict) -> Dict:
        """Fill LinkedIn Easy Apply form"""
        try:
            # Fill phone number if requested
            try:
                phone_input = self.driver.find_element(By.XPATH, "//input[@id='single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-*-phoneNumber*']")
                phone_input.clear()
                phone_input.send_keys(user_data.get('phone', ''))
            except NoSuchElementException:
                pass
            
            # Handle multi-step forms
            while True:
                try:
                    # Look for Next button
                    next_btn = self.driver.find_element(By.XPATH, "//button[@aria-label='Continue to next step']")
                    next_btn.click()
                    time.sleep(1)
                except NoSuchElementException:
                    # No more Next buttons, look for Submit
                    break
            
            # Submit application
            try:
                submit_btn = self.driver.find_element(By.XPATH, "//button[@aria-label='Submit application']")
                submit_btn.click()
                time.sleep(2)
                
                return {
                    "success": True,
                    "message": "Application submitted successfully",
                    "platform": "linkedin"
                }
            except NoSuchElementException:
                return {
                    "success": False,
                    "error": "Could not find submit button",
                    "platform": "linkedin"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e), "platform": "linkedin"}


class IndeedHandler(JobPlatformHandler):
    """Handler for Indeed job applications"""
    
    def apply_to_job(self, job_url: str, user_data: Dict) -> Dict:
        try:
            self.driver.get(job_url)
            time.sleep(2)
            
            # Look for Apply Now button
            try:
                apply_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Apply now')]"))
                )
                apply_btn.click()
                time.sleep(2)
                
                return self._fill_indeed_form(user_data)
                
            except TimeoutException:
                return {
                    "success": False,
                    "error": "Apply button not found",
                    "platform": "indeed"
                }
                
        except Exception as e:
            logger.error(f"Indeed application error: {str(e)}")
            return {"success": False, "error": str(e), "platform": "indeed"}
    
    def _fill_indeed_form(self, user_data: Dict) -> Dict:
        """Fill Indeed application form"""
        try:
            # Fill name
            try:
                name_input = self.driver.find_element(By.ID, "input-applicant.name")
                name_input.clear()
                name_input.send_keys(user_data.get('full_name', ''))
            except NoSuchElementException:
                pass
            
            # Fill email
            try:
                email_input = self.driver.find_element(By.ID, "input-applicant.email")
                email_input.clear()
                email_input.send_keys(user_data.get('email', ''))
            except NoSuchElementException:
                pass
            
            # Fill phone
            try:
                phone_input = self.driver.find_element(By.ID, "input-applicant.phoneNumber")
                phone_input.clear()
                phone_input.send_keys(user_data.get('phone', ''))
            except NoSuchElementException:
                pass
            
            # Submit
            try:
                submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                submit_btn.click()
                time.sleep(2)
                
                return {
                    "success": True,
                    "message": "Application submitted successfully",
                    "platform": "indeed"
                }
            except NoSuchElementException:
                return {
                    "success": False,
                    "error": "Could not submit application",
                    "platform": "indeed"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e), "platform": "indeed"}


class CompanyCareerPageHandler(JobPlatformHandler):
    """Handler for company career pages - uses AI to detect and fill forms"""
    
    def apply_to_job(self, job_url: str, user_data: Dict) -> Dict:
        try:
            self.driver.get(job_url)
            time.sleep(3)
            
            # Try to find apply button with various common texts
            apply_button_texts = ['Apply', 'Apply Now', 'Submit Application', 'Apply for this job']
            apply_btn = None
            
            for text in apply_button_texts:
                try:
                    apply_btn = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{text}')] | //a[contains(text(), '{text}')]")
                    break
                except NoSuchElementException:
                    continue
            
            if apply_btn:
                apply_btn.click()
                time.sleep(2)
                return self._fill_generic_form(user_data)
            else:
                return {
                    "success": False,
                    "error": "Could not find apply button on career page",
                    "platform": "company_career_page"
                }
                
        except Exception as e:
            logger.error(f"Company career page error: {str(e)}")
            return {"success": False, "error": str(e), "platform": "company_career_page"}
    
    def _fill_generic_form(self, user_data: Dict) -> Dict:
        """Intelligently fill generic application forms"""
        try:
            # Find all input fields
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            
            for input_field in inputs:
                try:
                    field_name = input_field.get_attribute('name') or input_field.get_attribute('id') or ''
                    field_type = input_field.get_attribute('type')
                    field_name_lower = field_name.lower()
                    
                    # Skip hidden, submit, and button fields
                    if field_type in ['hidden', 'submit', 'button']:
                        continue
                    
                    # Fill based on field name patterns
                    if any(keyword in field_name_lower for keyword in ['name', 'full_name', 'fullname']):
                        input_field.clear()
                        input_field.send_keys(user_data.get('full_name', ''))
                    
                    elif any(keyword in field_name_lower for keyword in ['email', 'e-mail']):
                        input_field.clear()
                        input_field.send_keys(user_data.get('email', ''))
                    
                    elif any(keyword in field_name_lower for keyword in ['phone', 'mobile', 'contact']):
                        input_field.clear()
                        input_field.send_keys(user_data.get('phone', ''))
                    
                    elif any(keyword in field_name_lower for keyword in ['address', 'location', 'city']):
                        input_field.clear()
                        input_field.send_keys(user_data.get('location', ''))
                    
                    elif any(keyword in field_name_lower for keyword in ['linkedin']):
                        input_field.clear()
                        input_field.send_keys(user_data.get('linkedin_url', ''))
                    
                    elif any(keyword in field_name_lower for keyword in ['github']):
                        input_field.clear()
                        input_field.send_keys(user_data.get('github_url', ''))
                    
                    elif any(keyword in field_name_lower for keyword in ['portfolio', 'website']):
                        input_field.clear()
                        input_field.send_keys(user_data.get('portfolio_url', ''))
                
                except Exception as e:
                    logger.warning(f"Error filling field: {str(e)}")
                    continue
            
            # Fill textareas (cover letter, etc.)
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            for textarea in textareas:
                try:
                    field_name = textarea.get_attribute('name') or textarea.get_attribute('id') or ''
                    if 'cover' in field_name.lower() or 'letter' in field_name.lower():
                        # Generate a simple cover letter
                        cover_letter = self._generate_cover_letter(user_data)
                        textarea.clear()
                        textarea.send_keys(cover_letter)
                except Exception as e:
                    logger.warning(f"Error filling textarea: {str(e)}")
            
            # Try to submit
            submit_buttons = self.driver.find_elements(By.XPATH, "//button[@type='submit'] | //input[@type='submit']")
            if submit_buttons:
                submit_buttons[0].click()
                time.sleep(2)
                
                return {
                    "success": True,
                    "message": "Application submitted successfully",
                    "platform": "company_career_page"
                }
            else:
                return {
                    "success": False,
                    "error": "Could not find submit button",
                    "platform": "company_career_page"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e), "platform": "company_career_page"}
    
    def _generate_cover_letter(self, user_data: Dict) -> str:
        """Generate a simple cover letter"""
        name = user_data.get('full_name', 'Applicant')
        skills = ', '.join(user_data.get('skills', [])[:5])
        
        return f"""Dear Hiring Manager,

I am writing to express my interest in this position. With my background in {skills}, I believe I would be a valuable addition to your team.

I am excited about the opportunity to contribute to your organization and look forward to discussing how my skills and experience align with your needs.

Thank you for considering my application.

Best regards,
{name}"""


class IntelligentAutoApplyAgent:
    """
    Intelligent Auto-Apply Agent that can learn and apply to jobs across platforms
    """
    
    def __init__(self, user_data: Dict, headless: bool = True):
        self.user_data = user_data
        self.headless = headless
        self.driver = None
        self.application_history = []
        
    def _setup_driver(self):
        """Setup Selenium WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def _cleanup_driver(self):
        """Cleanup WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def apply_to_job(self, job_url: str, job_details: Dict) -> Dict:
        """
        Apply to a single job using intelligent platform detection
        """
        try:
            # Setup driver if not already done
            if not self.driver:
                self._setup_driver()
            
            # Detect platform
            platform_handler = JobPlatformHandler(self.driver)
            platform = platform_handler.detect_platform(job_url)
            
            logger.info(f"Detected platform: {platform} for URL: {job_url}")
            
            # Get appropriate handler
            if platform == 'linkedin':
                handler = LinkedInHandler(self.driver)
            elif platform == 'indeed':
                handler = IndeedHandler(self.driver)
            else:
                handler = CompanyCareerPageHandler(self.driver)
            
            # Apply to job
            result = handler.apply_to_job(job_url, self.user_data)
            
            # Add job details to result
            result.update({
                "job_title": job_details.get('title', ''),
                "company": job_details.get('company', ''),
                "job_url": job_url,
                "applied_at": datetime.now().isoformat()
            })
            
            # Save to history
            self.application_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error applying to job: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "job_url": job_url,
                "job_title": job_details.get('title', ''),
                "company": job_details.get('company', '')
            }
    
    def apply_to_multiple_jobs(self, jobs: List[Dict]) -> Dict:
        """
        Apply to multiple jobs
        """
        results = []
        
        try:
            self._setup_driver()
            
            for job in jobs:
                job_url = job.get('url', '')
                if not job_url:
                    results.append({
                        "success": False,
                        "error": "No job URL provided",
                        "job_title": job.get('title', ''),
                        "company": job.get('company', '')
                    })
                    continue
                
                result = self.apply_to_job(job_url, job)
                results.append(result)
                
                # Wait between applications to avoid rate limiting
                time.sleep(3)
            
        finally:
            self._cleanup_driver()
        
        # Generate summary
        successful = len([r for r in results if r.get('success', False)])
        failed = len(results) - successful
        
        return {
            "success": True,
            "total_applications": len(results),
            "successful": successful,
            "failed": failed,
            "results": results,
            "summary": {
                "total": len(results),
                "successful": successful,
                "failed": failed,
                "success_rate": f"{(successful/len(results)*100):.1f}%" if results else "0%"
            }
        }
    
    def get_application_history(self) -> List[Dict]:
        """Get history of all applications"""
        return self.application_history


# Helper functions for backward compatibility
def validate_user_for_auto_apply(user_data: Dict) -> Dict:
    """Validate user data for auto-apply"""
    required_fields = {
        "full_name": "Full Name",
        "email": "Email Address",
        "location": "Location",
        "skills": "Skills",
        "experience_level": "Experience Level"
    }
    
    missing = []
    for field, label in required_fields.items():
        value = user_data.get(field)
        if not value or (isinstance(value, list) and len(value) == 0):
            missing.append(field)
    
    # Check education and experience
    if not user_data.get('education') or len(user_data.get('education', [])) == 0:
        missing.append('education')
    
    if not user_data.get('experience') or len(user_data.get('experience', [])) == 0:
        missing.append('experience')
    
    return {
        "can_auto_apply": len(missing) == 0,
        "missing_fields": missing,
        "prompts": [{"field": f, "question": f"Please provide your {f.replace('_', ' ')}"} for f in missing]
    }


def process_auto_apply(user_data: Dict, jobs: List[Dict], headless: bool = True) -> Dict:
    """
    Process auto-apply for multiple jobs with real browser automation
    """
    # Validate first
    validation = validate_user_for_auto_apply(user_data)
    if not validation['can_auto_apply']:
        return {
            "success": False,
            "error": "Profile incomplete",
            "missing_fields": validation['missing_fields'],
            "prompts": validation['prompts']
        }
    
    # Create agent and apply
    agent = IntelligentAutoApplyAgent(user_data, headless=headless)
    return agent.apply_to_multiple_jobs(jobs)
