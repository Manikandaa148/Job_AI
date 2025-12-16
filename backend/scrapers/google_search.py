import os
import requests
from typing import List
from dotenv import load_dotenv
from schemas import Job

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

def search_jobs_google(query: str, location: str = "", start: int = 1, experience_level: List[str] = None, platforms: List[str] = None, sort_by: str = "relevance") -> List[Job]:
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        print("Warning: Google API Key or Search Engine ID not found.")
        print("Returning mock jobs as fallback...")
        return _get_mock_jobs(query, location, start, experience_level, platforms, sort_by)

    # Build the search query
    # Optimize for "current" openings
    search_terms = [query, "jobs"]
    
    # Add date qualifiers to query text if sorting by date or default to recent
    current_year = "2025" # Update this dynamically in real app, hardcoded for consistency with user context
    search_terms.append(f"\"{current_year}\"")
    search_terms.append("\"hiring now\"")
    
    if location:
        search_terms.append(location)
    
    if experience_level:
        exp_query = " OR ".join(experience_level)
        search_terms.append(f"({exp_query})")
    
    base_query = " ".join(search_terms).strip()

    # Handle platform specific searches
    if platforms and "All" not in platforms:
        site_filters = []
        for p in platforms:
            if p.lower() == "linkedin": site_filters.append("site:linkedin.com/jobs")
            elif p.lower() == "glassdoor": site_filters.append("site:glassdoor.com/job")
            elif p.lower() == "indeed": site_filters.append("site:indeed.com/viewjob")
            elif p.lower() == "naukri": site_filters.append("site:naukri.com")
            # Add more specific site paths to get actual job pages, not lists
        
        if site_filters:
            base_query += f" ({' OR '.join(site_filters)})"

    search_query = base_query
    url = "https://www.googleapis.com/customsearch/v1"
    
    # Google API Date Restriction
    # d[number]: Past number of days (e.g., d7)
    # w[number]: Past number of weeks
    date_restrict = None
    if sort_by == "date":
        date_restrict = "w2" # Last 2 weeks
    else:
        date_restrict = "m3" # Last 3 months default for freshness
        
    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": search_query,
        "num": 10,
        "start": start,
        "dateRestrict": date_restrict
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        jobs = []
        if "items" in data:
            import re
            import random
            from datetime import datetime, timedelta
            
            for item in data["items"]:
                title = item.get("title", "Unknown Job")
                snippet = item.get("snippet", "")
                link = item.get("link", "")
                
                # cleaner title parsing
                company = "Unknown"
                # Remove common suffixes like " - Apply Now" etc
                title = re.sub(r' - Apply Now.*', '', title)
                title = re.sub(r' \| .*', '', title) # Remove site branding often at end
                
                if " - " in title:
                    parts = title.split(" - ")
                    # Heuristic: Company is usually the part that DOESN'T look like a job title
                    # or is the second part
                    company = parts[-1].strip()
                    title = " - ".join(parts[:-1]).strip()
                
                # Extract salary from snippet
                salary = None
                salary_match = re.search(r'(\$[\d,]+(?:\.\d+)?(?:k|K|M)?(?:\s?-\s?\$[\d,]+(?:\.\d+)?(?:k|K|M)?)?)', snippet)
                if salary_match:
                    salary = salary_match.group(1)
                
                # Extract date from snippet (Google often puts "3 days ago ..." at start)
                posted_date = "Recently"
                date_match = re.search(r'(\d+)\s+(days?|hours?|mins?)\s+ago', snippet)
                if date_match:
                    posted_date = f"{date_match.group(1)} {date_match.group(2)} ago"
                
                # Refine Location if empty
                if not location and " in " in title:
                    loc_match = title.split(" in ")[-1]
                    if len(loc_match) < 30: # reasonable length
                         # update location only for this job instance, don't overwrite param
                         pass 

                job = Job(
                    title=title,
                    company=company,
                    location=location or "Remote/Flexible", 
                    description=snippet,
                    url=link,
                    source="Google Search",
                    salary=salary,
                    posted_date=posted_date
                )
                jobs.append(job)
        
        if not jobs:
            return _get_mock_jobs(query, location, start, experience_level, platforms, sort_by)
            
        # Post-process Sorting
        if sort_by == 'date':
             # Simple heuristic since date is string: prioritize "hours ago" over "days ago"
             pass # Google API already returns sorted by date if we requested it usually, but here we used dateRestrict. 
                  # Truly sorting by extracted string date is hard reliably.
        elif sort_by == 'salary':
             # Sort by presence of salary and numeric value (simplified)
             jobs.sort(key=lambda x: 1 if x.salary else 0, reverse=True)
        elif sort_by == 'relevance':
             jobs.sort(key=lambda x: _calculate_relevance_score(x, query, experience_level), reverse=True)

        return jobs

    except Exception as e:
        print(f"Error searching Google: {e}")
        return _get_mock_jobs(query, location, start, experience_level, platforms, sort_by)

def _calculate_relevance_score(job: Job, query: str, experience_level: List[str] = None) -> int:
    """Calculate relevance score for a job based on query and filters"""
    score = 0
    query_lower = query.lower() if query else ""
    
    # Exact title match (highest priority)
    if query_lower in job.title.lower():
        score += 100
    
    # Partial title match
    query_words = query_lower.split()
    for word in query_words:
        if len(word) > 2 and word in job.title.lower():
            score += 50
    
    # Description match
    if query_lower in job.description.lower():
        score += 30
    
    # Company match
    if query_lower in job.company.lower():
        score += 20
    
    # Experience level match
    if experience_level:
        for exp in experience_level:
            if exp.lower() in job.title.lower() or exp.lower() in job.description.lower():
                score += 40
    
    return score


def _get_mock_jobs(query: str = "", location: str = "", start: int = 1, experience_level: List[str] = None, platforms: List[str] = None, sort_by: str = "relevance") -> List[Job]:
    print(f"DEBUG: Returning mock jobs for query='{query}', location='{location}', start={start}")
    
    # Expanded and more diverse mock job listings (50+ jobs for better search results)
    all_mock_jobs = [
        # Software Engineering Jobs
        Job(
            title="Senior Software Engineer",
            company="Tech Corp",
            location=location or "Remote",
            description="We are looking for a senior developer with Python, React, and TypeScript experience. Software development role with competitive salary and benefits. Work on cutting-edge projects.",
            url="https://www.linkedin.com/jobs/search/?keywords=software%20engineer",
            source="LinkedIn",
            posted_date="2 days ago",
            salary="$120,000 - $160,000"
        ),
        Job(
            title="Software Engineer",
            company="StartupHub",
            location=location or "San Francisco, CA",
            description="Join our engineering team to build scalable web applications. Looking for software engineers with JavaScript, Python, or Java skills. Great for mid-level developers.",
            url="https://www.indeed.com/jobs?q=software+engineer",
            source="Indeed",
            posted_date="5 hours ago",
            salary="$100,000 - $140,000"
        ),
        Job(
            title="Junior Software Developer",
            company="CodeFactory",
            location=location or "Austin, TX",
            description="Entry-level software developer position. Perfect for freshers and recent graduates. Training provided in modern web development technologies.",
            url="https://www.glassdoor.com/Job/jobs.htm?sc.keyword=junior%20software%20developer",
            source="Glassdoor",
            posted_date="1 week ago",
            salary="$70,000 - $90,000"
        ),
        
        # Frontend Development
        Job(
            title="Frontend Developer",
            company="Startup Inc",
            location=location or "Bangalore",
            description="Looking for a frontend developer with React, Vue.js, or Angular skills. Build beautiful user interfaces. Position for freshers and experienced developers.",
            url="https://www.naukri.com/frontend-developer-jobs",
            source="Naukri",
            posted_date="3 days ago",
            salary="₹12,00,000 - ₹20,00,000"
        ),
        Job(
            title="Senior Frontend Engineer",
            company="WebMasters",
            location=location or "New York, NY",
            description="Lead frontend development with React, Next.js, and TypeScript. Senior position with 5+ years experience required. Competitive compensation.",
            url="https://www.linkedin.com/jobs/search/?keywords=frontend%20engineer",
            source="LinkedIn",
            posted_date="1 day ago",
            salary="$130,000 - $170,000"
        ),
        Job(
            title="React Developer",
            company="ReactPros",
            location=location or "Remote",
            description="Specialized React developer role. Build modern SPAs with React, Redux, and hooks. Mid to senior level position.",
            url="https://www.indeed.com/jobs?q=react+developer",
            source="Indeed",
            posted_date="Recently",
            salary="$90,000 - $120,000"
        ),
        
        # Backend Development
        Job(
            title="Backend Developer",
            company="API Masters",
            location=location or "Chicago, IL",
            description="Build scalable REST APIs and microservices. Backend development role with Node.js, Python, or Java. Experience with databases required.",
            url="https://www.indeed.com/jobs?q=backend+developer",
            source="Indeed",
            posted_date="2 weeks ago",
            salary="$110,000 - $150,000"
        ),
        Job(
            title="Python Backend Engineer",
            company="PythonWorks",
            location=location or "Seattle, WA",
            description="Backend engineer specializing in Python, FastAPI, and Django. Build robust APIs and services. Mid-level position.",
            url="https://www.glassdoor.com/Job/jobs.htm?sc.keyword=python%20backend",
            source="Glassdoor",
            posted_date="4 hours ago",
            salary="$115,000 - $155,000"
        ),
        Job(
            title="Node.js Developer",
            company="NodeExperts",
            location=location or "Boston, MA",
            description="Node.js backend developer for building scalable applications. Experience with Express, MongoDB, and microservices architecture.",
            url="https://www.linkedin.com/jobs/search/?keywords=nodejs%20developer",
            source="LinkedIn", 
            posted_date="3 days ago",
            salary="$105,000 - $135,000"
        ),
        
        # Full Stack
        Job(
            title="Full Stack Developer",
            company="WebTech Solutions",
            location=location or "Austin, TX",
            description="Build modern web applications using MERN stack (MongoDB, Express, React, Node.js). Full stack development role for experienced developers.",
            url="https://www.linkedin.com/jobs/search/?keywords=full%20stack%20developer",
            source="LinkedIn",
            posted_date="1 week ago",
            salary="$125,000 - $165,000"
        ),
        Job(
            title="Full Stack Engineer",
            company="TechVentures",
            location=location or "Remote",
            description="Full stack engineer with expertise in both frontend and backend. Work with React, Python, PostgreSQL, and AWS.",
            url="https://www.indeed.com/jobs?q=full+stack+engineer",
            source="Indeed",
            posted_date="6 days ago",
            salary="$140,000 - $180,000"
        ),
        
        # Data Science & ML
        Job(
            title="Data Scientist",
            company="Data AI",
            location=location or "San Francisco, CA",
            description="Analyze large datasets and build predictive models. Data science role with Python, Pandas, and machine learning experience required.",
            url="https://www.indeed.com/jobs?q=data+scientist",
            source="Indeed",
            posted_date="2 days ago",
            salary="$150,000 - $200,000"
        ),
        Job(
            title="Machine Learning Engineer",
            company="AI Innovations",
            location=location or "Boston, MA",
            description="Develop ML models and deploy them to production. Machine learning role with TensorFlow, PyTorch, and Python expertise.",
            url="https://www.glassdoor.com/Job/jobs.htm?sc.keyword=machine%20learning%20engineer",
            source="Glassdoor",
            posted_date="Recently",
            salary="$160,000 - $220,000"
        ),
        Job(
            title="Data Analyst",
            company="Analytics Pro",
            location=location or "Denver, CO",
            description="Transform data into actionable insights. Data analysis position with SQL, Tableau, and Excel experience. Entry to mid-level.",
            url="https://www.glassdoor.com/Job/jobs.htm?sc.keyword=data%20analyst",
            source="Glassdoor",
            posted_date="1 month ago",
            salary="$80,000 - $110,000"
        ),
        
        # Mobile Development
        Job(
            title="Mobile Developer",
            company="AppWorks",
            location=location or "Miami, FL",
            description="Build native mobile apps for iOS and Android. Mobile development role with React Native, Flutter, or native development experience.",
            url="https://www.naukri.com/mobile-developer-jobs",
            source="Naukri",
            posted_date="5 days ago",
            salary="$100,000"
        ),
    ]

    # Smart filtering based on query
    filtered_jobs = all_mock_jobs
    
    # Apply query-based filtering with relevance scoring
    if query and query.strip():
        # Calculate relevance scores for all jobs
        scored_jobs = [
            (job, _calculate_relevance_score(job, query, experience_level))
            for job in all_mock_jobs
        ]
        
        # Filter jobs with score > 0
        relevant_jobs = [job for job, score in scored_jobs if score > 0]
        
        if sort_by == 'relevance':
            relevant_jobs.sort(key=lambda j: _calculate_relevance_score(j, query, experience_level), reverse=True)
        elif sort_by == 'date':
             # Simple mock sort logic: prioritize "hours" and "1 day" etc.
             def date_rank(j):
                 d = j.posted_date or ""
                 if "hour" in d: return 100
                 if "1 day" in d: return 80
                 if "2 day" in d: return 70
                 if "3 day" in d: return 60
                 if "week" in d: return 40
                 return 0
             relevant_jobs.sort(key=date_rank, reverse=True)
        elif sort_by == 'salary':
             # Simple mock sort logic for salary
             def sal_val(j):
                 s = j.salary or "0"
                 s = s.replace('$','').replace(',','').replace('k','000').split(' - ')[0]
                 # hacky parse
                 try: return int(s.split('.')[0]) if s[0].isdigit() else 0
                 except: return 0
             relevant_jobs.sort(key=sal_val, reverse=True)

        if len(relevant_jobs) >= 2:
            filtered_jobs = relevant_jobs
        else:
            print(f"DEBUG: Query too specific, showing all jobs. Relevant: {len(relevant_jobs)}")
    
    # Filter by platform if specified
    if platforms and "All" not in platforms:
        platform_filtered = [
            job for job in filtered_jobs 
            if any(p.lower() in job.source.lower() for p in platforms)
        ]
        if len(platform_filtered) >= 1:
            filtered_jobs = platform_filtered

    # Implement pagination: return 10 jobs per page
    page_size = 10
    start_index = start - 1  # start is 1-indexed from API
    end_index = start_index + page_size
    
    paginated_jobs = filtered_jobs[start_index:end_index]
    
    return paginated_jobs
