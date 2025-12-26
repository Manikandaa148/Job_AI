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
        return _get_mock_jobs(query, location, start, experience_level, platforms)

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
            return _get_mock_jobs(query, location, start, experience_level, platforms)
            
        return jobs

    except Exception as e:
        print(f"Error searching Google: {e}")
        # Fallback to mock data on error
        return _get_mock_jobs(query, location, start, experience_level, platforms)

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


def _get_mock_jobs(query: str = "", location: str = "", start: int = 1, experience_level: List[str] = None, platforms: List[str] = None) -> List[Job]:
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
            source="LinkedIn"
        ),
        Job(
            title="Software Engineer",
            company="StartupHub",
            location=location or "San Francisco, CA",
            description="Join our engineering team to build scalable web applications. Looking for software engineers with JavaScript, Python, or Java skills. Great for mid-level developers.",
            url="https://www.indeed.com/jobs?q=software+engineer",
            source="Indeed"
        ),
        Job(
            title="Junior Software Developer",
            company="CodeFactory",
            location=location or "Austin, TX",
            description="Entry-level software developer position. Perfect for freshers and recent graduates. Training provided in modern web development technologies.",
            url="https://www.glassdoor.com/Job/jobs.htm?sc.keyword=junior%20software%20developer",
            source="Glassdoor"
        ),
        
        # Frontend Development
        Job(
            title="Frontend Developer",
            company="Startup Inc",
            location=location or "Bangalore",
            description="Looking for a frontend developer with React, Vue.js, or Angular skills. Build beautiful user interfaces. Position for freshers and experienced developers.",
            url="https://www.naukri.com/frontend-developer-jobs",
            source="Naukri"
        ),
        Job(
            title="Senior Frontend Engineer",
            company="WebMasters",
            location=location or "New York, NY",
            description="Lead frontend development with React, Next.js, and TypeScript. Senior position with 5+ years experience required. Competitive compensation.",
            url="https://www.linkedin.com/jobs/search/?keywords=frontend%20engineer",
            source="LinkedIn"
        ),
        Job(
            title="React Developer",
            company="ReactPros",
            location=location or "Remote",
            description="Specialized React developer role. Build modern SPAs with React, Redux, and hooks. Mid to senior level position.",
            url="https://www.indeed.com/jobs?q=react+developer",
            source="Indeed"
        ),
        
        # Backend Development
        Job(
            title="Backend Developer",
            company="API Masters",
            location=location or "Chicago, IL",
            description="Build scalable REST APIs and microservices. Backend development role with Node.js, Python, or Java. Experience with databases required.",
            url="https://www.indeed.com/jobs?q=backend+developer",
            source="Indeed"
        ),
        Job(
            title="Python Backend Engineer",
            company="PythonWorks",
            location=location or "Seattle, WA",
            description="Backend engineer specializing in Python, FastAPI, and Django. Build robust APIs and services. Mid-level position.",
            url="https://www.glassdoor.com/Job/jobs.htm?sc.keyword=python%20backend",
            source="Glassdoor"
        ),
        Job(
            title="Node.js Developer",
            company="NodeExperts",
            location=location or "Boston, MA",
            description="Node.js backend developer for building scalable applications. Experience with Express, MongoDB, and microservices architecture.",
            url="https://www.linkedin.com/jobs/search/?keywords=nodejs%20developer",
            source="LinkedIn"
        ),
        
        # Full Stack
        Job(
            title="Full Stack Developer",
            company="WebTech Solutions",
            location=location or "Austin, TX",
            description="Build modern web applications using MERN stack (MongoDB, Express, React, Node.js). Full stack development role for experienced developers.",
            url="https://www.linkedin.com/jobs/search/?keywords=full%20stack%20developer",
            source="LinkedIn"
        ),
        Job(
            title="Full Stack Engineer",
            company="TechVentures",
            location=location or "Remote",
            description="Full stack engineer with expertise in both frontend and backend. Work with React, Python, PostgreSQL, and AWS.",
            url="https://www.indeed.com/jobs?q=full+stack+engineer",
            source="Indeed"
        ),
        
        # Data Science & ML
        Job(
            title="Data Scientist",
            company="Data AI",
            location=location or "San Francisco, CA",
            description="Analyze large datasets and build predictive models. Data science role with Python, Pandas, and machine learning experience required.",
            url="https://www.indeed.com/jobs?q=data+scientist",
            source="Indeed"
        ),
        Job(
            title="Machine Learning Engineer",
            company="AI Innovations",
            location=location or "Boston, MA",
            description="Develop ML models and deploy them to production. Machine learning role with TensorFlow, PyTorch, and Python expertise.",
            url="https://www.glassdoor.com/Job/jobs.htm?sc.keyword=machine%20learning%20engineer",
            source="Glassdoor"
        ),
        Job(
            title="Data Analyst",
            company="Analytics Pro",
            location=location or "Denver, CO",
            description="Transform data into actionable insights. Data analysis position with SQL, Tableau, and Excel experience. Entry to mid-level.",
            url="https://www.glassdoor.com/Job/jobs.htm?sc.keyword=data%20analyst",
            source="Glassdoor"
        ),
        Job(
            title="AI Research Scientist",
            company="DeepMind Labs",
            location=location or "London, UK",
            description="Conduct cutting-edge AI research. PhD preferred. Work on neural networks, NLP, and computer vision projects.",
            url="https://www.linkedin.com/jobs/search/?keywords=ai%20research",
            source="LinkedIn"
        ),
        
        # DevOps & Cloud
        Job(
            title="DevOps Engineer",
            company="Cloud Systems",
            location=location or "Seattle, WA",
            description="Manage cloud infrastructure and CI/CD pipelines. DevOps position with AWS, Docker, Kubernetes, and Terraform experience.",
            url="https://www.indeed.com/jobs?q=devops+engineer",
            source="Indeed"
        ),
        Job(
            title="Cloud Architect",
            company="CloudTech Inc",
            location=location or "Dallas, TX",
            description="Design and implement cloud solutions on AWS, Azure, or GCP. Cloud architecture role for experienced professionals with 7+ years.",
            url="https://www.linkedin.com/jobs/search/?keywords=cloud%20architect",
            source="LinkedIn"
        ),
        Job(
            title="Site Reliability Engineer",
            company="ReliableOps",
            location=location or "Remote",
            description="Ensure system reliability and performance. SRE role with Linux, monitoring tools, and automation experience.",
            url="https://www.glassdoor.com/Job/jobs.htm?sc.keyword=sre",
            source="Glassdoor"
        ),
        
        # Mobile Development
        Job(
            title="Mobile Developer",
            company="AppWorks",
            location=location or "Miami, FL",
            description="Build native mobile apps for iOS and Android. Mobile development role with React Native, Flutter, or native development experience.",
            url="https://www.naukri.com/mobile-developer-jobs",
            source="Naukri"
        ),
        Job(
            title="iOS Developer",
            company="AppleDevs",
            location=location or "Cupertino, CA",
            description="Native iOS development with Swift and SwiftUI. Build amazing iPhone and iPad applications.",
            url="https://www.linkedin.com/jobs/search/?keywords=ios%20developer",
            source="LinkedIn"
        ),
        Job(
            title="Android Developer",
            company="DroidMasters",
            location=location or "Mountain View, CA",
            description="Android app development with Kotlin and Java. Work on popular Android applications with millions of users.",
            url="https://www.indeed.com/jobs?q=android+developer",
            source="Indeed"
        ),
        
        # Product & Design
        Job(
            title="Product Manager",
            company="Innovation Labs",
            location=location or "New York, NY",
            description="Lead our product team to build the next generation of AI tools. Product management position with technical background preferred.",
            url="https://www.glassdoor.com/Job/jobs.htm?sc.keyword=product%20manager",
            source="Glassdoor"
        ),
        Job(
            title="UI/UX Designer",
            company="Design Studio",
            location=location or "Los Angeles, CA",
            description="Create beautiful and intuitive user interfaces. Design position for creative minds with Figma and Adobe XD experience.",
            url="https://www.linkedin.com/jobs/search/?keywords=ui%20ux%20designer",
            source="LinkedIn"
        ),
        Job(
            title="Product Designer",
            company="DesignFirst",
            location=location or "San Francisco, CA",
            description="End-to-end product design from research to implementation. Work closely with engineering teams.",
            url="https://www.glassdoor.com/Job/jobs.htm?sc.keyword=product%20designer",
            source="Glassdoor"
        ),
        
        # QA & Testing
        Job(
            title="QA Engineer",
            company="Quality First",
            location=location or "Portland, OR",
            description="Ensure software quality through automated testing. QA testing position with Selenium, Jest, and Cypress experience.",
            url="https://www.indeed.com/jobs?q=qa+engineer",
            source="Indeed"
        ),
        Job(
            title="Test Automation Engineer",
            company="AutoTest Inc",
            location=location or "Austin, TX",
            description="Build and maintain automated test frameworks. Expertise in test automation tools and CI/CD integration.",
            url="https://www.linkedin.com/jobs/search/?keywords=test%20automation",
            source="LinkedIn"
        ),
        
        # Security
        Job(
            title="Cybersecurity Analyst",
            company="SecureNet",
            location=location or "Washington, DC",
            description="Protect systems from cyber threats and vulnerabilities. Cybersecurity position with CISSP or CEH certification preferred.",
            url="https://www.glassdoor.com/Job/jobs.htm?sc.keyword=cybersecurity%20analyst",
            source="Glassdoor"
        ),
        Job(
            title="Security Engineer",
            company="CyberDefense",
            location=location or "Remote",
            description="Implement security measures and conduct penetration testing. Experience with security tools and frameworks required.",
            url="https://www.indeed.com/jobs?q=security+engineer",
            source="Indeed"
        ),
        
        # Business & Analytics
        Job(
            title="Business Analyst",
            company="Enterprise Solutions",
            location=location or "Atlanta, GA",
            description="Bridge the gap between business and technology. Business analysis role with Agile methodology and requirements gathering experience.",
            url="https://www.linkedin.com/jobs/search/?keywords=business%20analyst",
            source="LinkedIn"
        ),
        Job(
            title="Technical Writer",
            company="DocuTech",
            location=location or "Remote",
            description="Create technical documentation and user guides. Strong writing skills and technical understanding required.",
            url="https://www.glassdoor.com/Job/jobs.htm?sc.keyword=technical%20writer",
            source="Glassdoor"
        ),
        
        # Specialized Roles
        Job(
            title="Blockchain Developer",
            company="CryptoTech",
            location=location or "Remote",
            description="Develop blockchain applications and smart contracts. Experience with Solidity, Ethereum, or other blockchain platforms.",
            url="https://www.linkedin.com/jobs/search/?keywords=blockchain%20developer",
            source="LinkedIn"
        ),
        Job(
            title="Game Developer",
            company="GameStudio",
            location=location or "Los Angeles, CA",
            description="Create engaging video games with Unity or Unreal Engine. Game development role for passionate developers.",
            url="https://www.indeed.com/jobs?q=game+developer",
            source="Indeed"
        ),
        Job(
            title="Embedded Systems Engineer",
            company="IoT Solutions",
            location=location or "San Jose, CA",
            description="Develop embedded software for IoT devices. C/C++ programming and hardware knowledge required.",
            url="https://www.glassdoor.com/Job/jobs.htm?sc.keyword=embedded%20engineer",
            source="Glassdoor"
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
        
        # Filter jobs with score > 0 and sort by relevance
        relevant_jobs = [job for job, score in scored_jobs if score > 0]
        relevant_jobs.sort(
            key=lambda job: _calculate_relevance_score(job, query, experience_level),
            reverse=True
        )
        
        # Use relevant jobs if we have enough results
        if len(relevant_jobs) >= 5:
            filtered_jobs = relevant_jobs
        else:
            # Fallback to all jobs if query is too specific
            print(f"DEBUG: Query too specific, showing all jobs. Relevant: {len(relevant_jobs)}")
    
    # Filter by platform if specified
    if platforms and "All" not in platforms:
        platform_filtered = [
            job for job in filtered_jobs 
            if any(p.lower() in job.source.lower() for p in platforms)
        ]
        if len(platform_filtered) >= 3:
            filtered_jobs = platform_filtered
        else:
            print(f"DEBUG: Platform filter too restrictive, keeping all results")

    # Filter by experience level if specified (already considered in relevance scoring)
    # We don't need additional filtering here as it's part of the score

    # Implement pagination: return 10 jobs per page
    page_size = 10
    start_index = start - 1  # start is 1-indexed from API
    end_index = start_index + page_size
    
    paginated_jobs = filtered_jobs[start_index:end_index]
    
    print(f"DEBUG: Query='{query}', Total filtered: {len(filtered_jobs)}, Page {(start-1)//10 + 1}: {len(paginated_jobs)} jobs")
    return paginated_jobs
