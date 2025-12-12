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
        print("Returning mock jobs as fallback...")
        return _get_mock_jobs(query, location, experience_level, platforms)

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
            return _get_mock_jobs(query, location, experience_level, platforms)
            
        return jobs

    except Exception as e:
        print(f"Error searching Google: {e}")
        # Fallback to mock data on error
        return _get_mock_jobs(query, location, experience_level, platforms)

def _get_mock_jobs(query: str = "", location: str = "", experience_level: List[str] = None, platforms: List[str] = None) -> List[Job]:
    print(f"DEBUG: Returning mock jobs for query='{query}', location='{location}'")
    
    # Comprehensive mock job listings
    all_mock_jobs = [
        Job(
            title="Senior Software Engineer",
            company="Tech Corp",
            location=location or "Remote",
            description=f"We are looking for a senior developer with Python and React experience. {query or 'Software development'} role with competitive salary.",
            url="https://example.com/job1",
            source="LinkedIn"
        ),
        Job(
            title="Product Manager",
            company="Innovation Labs",
            location=location or "New York, NY",
            description=f"Lead our product team to build the next generation of AI tools. {query or 'Product management'} position available.",
            url="https://example.com/job2",
            source="Glassdoor"
        ),
        Job(
            title="Data Scientist",
            company="Data AI",
            location=location or "San Francisco, CA",
            description=f"Analyze large datasets and build predictive models. {query or 'Data science'} role with PyTorch experience required.",
            url="https://example.com/job3",
            source="Indeed"
        ),
        Job(
            title="Frontend Developer",
            company="Startup Inc",
            location=location or "Bangalore",
            description=f"Looking for a developer with React skills. {query or 'Frontend development'} position for freshers and experienced.",
            url="https://example.com/job4",
            source="Naukri"
        ),
        Job(
            title="Full Stack Developer",
            company="WebTech Solutions",
            location=location or "Austin, TX",
            description=f"Build modern web applications using MERN stack. {query or 'Full stack'} development role.",
            url="https://example.com/job5",
            source="LinkedIn"
        ),
        Job(
            title="DevOps Engineer",
            company="Cloud Systems",
            location=location or "Seattle, WA",
            description=f"Manage cloud infrastructure and CI/CD pipelines. {query or 'DevOps'} position with AWS experience.",
            url="https://example.com/job6",
            source="Indeed"
        ),
        Job(
            title="Machine Learning Engineer",
            company="AI Innovations",
            location=location or "Boston, MA",
            description=f"Develop ML models and deploy them to production. {query or 'Machine learning'} role with TensorFlow.",
            url="https://example.com/job7",
            source="Glassdoor"
        ),
        Job(
            title="UI/UX Designer",
            company="Design Studio",
            location=location or "Los Angeles, CA",
            description=f"Create beautiful and intuitive user interfaces. {query or 'Design'} position for creative minds.",
            url="https://example.com/job8",
            source="LinkedIn"
        ),
    ]

    # Always return at least some jobs
    filtered_jobs = all_mock_jobs
    
    # Filter by platform if specified
    if platforms and "All" not in platforms:
        platform_filtered = [job for job in filtered_jobs if any(p.lower() in job.source.lower() for p in platforms)]
        if platform_filtered:  # Only apply filter if it returns results
            filtered_jobs = platform_filtered

    # Filter by experience if specified (simple keyword match in title/description)
    if experience_level and experience_level:
        exp_filtered = [
            job for job in filtered_jobs 
            if any(exp.lower() in job.title.lower() or exp.lower() in job.description.lower() for exp in experience_level)
        ]
        if exp_filtered:  # Only apply filter if it returns results
            filtered_jobs = exp_filtered

    print(f"DEBUG: Returning {len(filtered_jobs)} mock jobs")
    return filtered_jobs
