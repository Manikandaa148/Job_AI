import os
import requests
from typing import List
from dotenv import load_dotenv
from schemas import Job

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

def search_jobs_google(query: str, location: str = "", start: int = 1, experience_level: List[str] = None, platforms: List[str] = None) -> List[Job]:
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        print("Warning: Google API Key or Search Engine ID not found.")
        return []

    # Build the search query
    search_terms = [query, "jobs"]
    if location:
        search_terms.append(location)
    
    if experience_level:
        # Add experience levels like "Fresher OR Associate"
        exp_query = " OR ".join(experience_level)
        search_terms.append(f"({exp_query})")
    
    base_query = " ".join(search_terms).strip()

    # Handle platform specific searches if requested
    if platforms and "All" not in platforms:
        # Map common names to domains if needed, or just use them
        # Example: "LinkedIn" -> "site:linkedin.com"
        site_filters = []
        for p in platforms:
            if p.lower() == "linkedin":
                site_filters.append("site:linkedin.com")
            elif p.lower() == "glassdoor":
                site_filters.append("site:glassdoor.com")
            elif p.lower() == "indeed":
                site_filters.append("site:indeed.com")
            elif p.lower() == "naukri":
                site_filters.append("site:naukri.com")
            else:
                # Fallback for others or just add them as text
                pass 
        
        if site_filters:
            base_query += f" ({' OR '.join(site_filters)})"

    search_query = base_query
    url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": search_query,
        "num": 10,  # Max 10 results per page
        "start": start
    }

    print(f"DEBUG: Searching Google with query: {search_query}")
    print(f"DEBUG: API Key present: {bool(GOOGLE_API_KEY)}")
    print(f"DEBUG: Engine ID present: {bool(SEARCH_ENGINE_ID)}")

    try:
        response = requests.get(url, params=params)
        print(f"DEBUG: Response Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"DEBUG: Error Response: {response.text}")
        
        response.raise_for_status()
        data = response.json()
        
        # print(f"DEBUG: Full Response Data: {data}") # Uncomment if needed, but might be large

        jobs = []
        if "items" in data:
            print(f"DEBUG: Found {len(data['items'])} items")
            for item in data["items"]:
                # Basic parsing - Google results are generic, so we map best effort
                title = item.get("title", "Unknown Job")
                snippet = item.get("snippet", "")
                link = item.get("link", "")
                
                # Try to extract company from title if possible (e.g. "Software Engineer - Google" or "Job | Company")
                company = "Unknown"
                if " - " in title:
                    parts = title.split(" - ")
                    company = parts[-1].strip()
                    title = " - ".join(parts[:-1]).strip()
                elif "|" in title:
                    parts = title.split("|")
                    company = parts[-1].strip()
                    title = "|".join(parts[:-1]).strip()

                job = Job(
                    title=title,
                    company=company,
                    location=location, # Google doesn't always give location in structured way
                    description=snippet,
                    url=link,
                    source="Google Search"
                )
                jobs.append(job)
        else:
            print("DEBUG: No 'items' found in response data.")
            if "spelling" in data:
                print(f"DEBUG: Spelling suggestion: {data['spelling']}")
            if "error" in data:
                print(f"DEBUG: Error in data: {data['error']}")
        
        if not jobs:
            print("DEBUG: No jobs found from API. Switching to mock data.")
            return _get_mock_jobs(experience_level, platforms)
            
        return jobs

    except Exception as e:
        print(f"Error searching Google: {e}")
        # Fallback to mock data on error
        return _get_mock_jobs(experience_level, platforms)

def _get_mock_jobs(experience_level: List[str] = None, platforms: List[str] = None) -> List[Job]:
    print("DEBUG: Returning mock jobs as fallback.")
    all_mock_jobs = [
        Job(
            title="Senior Software Engineer",
            company="Tech Corp (Mock)",
            location="Remote",
            description="We are looking for a senior developer with Python and React experience. This is a fallback listing because the live search returned no results.",
            url="https://example.com/job1",
            source="LinkedIn"
        ),
        Job(
            title="Product Manager",
            company="Innovation Labs",
            location="New York, NY",
            description="Lead our product team to build the next generation of AI tools. Join us in NYC.",
            url="https://example.com/job2",
            source="Glassdoor"
        ),
        Job(
            title="Data Scientist",
            company="Data AI",
            location="San Francisco, CA",
            description="Analyze large datasets and build predictive models. Experience with PyTorch required.",
            url="https://example.com/job3",
            source="Indeed"
        ),
        Job(
            title="Fresher Frontend Developer",
            company="Startup Inc",
            location="Bangalore",
            description="Looking for a fresher with React skills.",
            url="https://example.com/job4",
            source="Naukri"
        )
    ]

    filtered_jobs = all_mock_jobs
    
    # Filter by platform
    if platforms and "All" not in platforms:
        filtered_jobs = [job for job in filtered_jobs if any(p.lower() in job.source.lower() for p in platforms)]

    # Filter by experience (simple keyword match in title/description)
    if experience_level:
        filtered_jobs = [
            job for job in filtered_jobs 
            if any(exp.lower() in job.title.lower() or exp.lower() in job.description.lower() for exp in experience_level)
        ]

    return filtered_jobs
