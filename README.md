# Unified Job Applier

The **Unified Job Applier** is an automated bot designed to streamline the job application process across multiple platforms (LinkedIn and Naukri). Built with Python and Selenium, it automatically logs in, searches for roles based on strict filter criteria, and answers job application forms by securely pulling data from your `.env` profile. 

It also includes a local Flask web dashboard to review your application history and track the status of previously applied jobs.

## Features
- **Multi-Platform Automation:** Supports both LinkedIn Easy Apply and Naukri.com.
- **AI-Powered Answers:** Optionally connects to OpenAI to dynamically extract skills and answer unexpected free-text questions.
- **Smart Tracking:** Prevents duplicate applications and maintains a centralized CSV log of every job you've ever applied to.
- **Flask Dashboard:** Run `python app.py` to view an interactive UI of your applied jobs and external company links.
- **Blacklisting:** Automatically skips blacklisted companies and filters out jobs containing "Bad Words" in their descriptions (e.g., C2C, US Citizen, etc).

---

## Setup & Installation

1. **Install Requirements**
   Ensure Python 3 is installed. Then, install the global dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   The bot relies on a strict `.env` file to answer questions and filter searches. You must rename your `.env` template and fill in your details. A full breakdown of the environment variables is below.

3. **Run the Bot**
   ```bash
   python main.py
   ```
   *Follow the terminal prompts to select the target platform (LinkedIn, Naukri, or Both).*

4. **Run the Dashboard**
   ```bash
   python app.py
   ```
   *Visit `http://localhost:5000` to view your application history.*

---

## Environment Variables (`.env`) Reference

Your `.env` file is divided into several configuration blocks. Make sure these are filled out accurately, as they determine both your search results and your automatic application answers!

### Core Settings
- `LINKEDIN_EMAIL_OR_PHONE` / `LINKEDIN_PASSWORD`: LinkedIn Login credentials.
- `NAUKRI_USERNAME` / `NAUKRI_PASSWORD`: Naukri Login credentials.
- `PLATFORM`: The default platform to run (`linkedin`, `naukri`, or `both`).
- `TOTAL_EXPERIENCE`: Your total years of experience (e.g., `3`).
- `EXPECTED_SALARY` / `CURRENT_SALARY`: Your CTC details (e.g., `120000`).
- `NOTICE_PERIOD`: Your notice period in days (e.g., `30`).

### Search Configuration
- `SEARCH_LANGUAGES`: Comma-separated search queries (e.g., `"Python, React"`).
- `SEARCH_LOCATION`: Target location (e.g., `"New York, NY, United States"`).
- `SWITCH_NUMBER`: Number of applications before switching platforms/queries.
- `EASY_APPLY_ONLY`: Set to `True` to exclusively target quick-apply jobs.
- `ON_SITE`: Preferred working model (`"Remote"`, `"Hybrid"`, etc).
- `BAD_WORDS`: A critical comma-separated list of words to reject (e.g., `"US Citizen, No C2C"`). If the bot finds these in the description, it skips the job.
- `ABOUT_COMPANY_BAD_WORDS`: Specific companies you want to blacklist.

### Personal Configuration (Auto-Fill Data)
These variables are used to inject your personal information into application forms:
- `FIRST_NAME`, `LAST_NAME`, `PHONE_NUMBER`, `STREET`, `STATE`, `ZIPCODE`, `COUNTRY`
- `US_CITIZENSHIP`, `REQUIRE_VISA`
- `LINKEDIN_URL`, `WEBSITE_URL` (GitHub)

### Questions Configuration
- `WORKING_DAYS`: Your expected working days (e.g., `"5"`).
- `LINKEDIN_HEADLINE`: A professional summary string injected into free-text fields.
- `LINKEDIN_SUMMARY`: A longer paragraph injected when asked for a cover letter or bio.
- `CONFIDENCE_LEVEL`: A default number to inject when asked to rate your skills (1-10).

### AI Configuration (Optional)
- `USE_AI`: Set to `True` if you want the bot to use LLMs to dynamically answer complex application questions.
- `OPENAI_API_KEY`: Your API key for AI generation.
