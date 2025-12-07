"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Search, MapPin, Briefcase } from "lucide-react";
import { searchJobs, Job } from "@/lib/api";
import { JobCard } from "@/components/JobCard";
import { Header } from "@/components/Header";

import { POPULAR_JOB_TITLES, POPULAR_LOCATIONS, EXPERIENCE_LEVELS, SEARCH_PLATFORMS, COMPANY_SIZES } from '@/lib/constants';

function HomeContent() {
    const searchParams = useSearchParams();
    const router = useRouter();

    const [query, setQuery] = useState("");
    const [location, setLocation] = useState("");
    const [jobs, setJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(false);
    const [hasSearched, setHasSearched] = useState(false);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);

    // Filters
    const [selectedExperience, setSelectedExperience] = useState<string[]>([]);
    const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(["All"]);
    const [selectedCompanySizes, setSelectedCompanySizes] = useState<string[]>([]);

    // Initialize from URL params
    useEffect(() => {
        const q = searchParams.get('q');
        const loc = searchParams.get('location');

        if (q || loc) {
            setQuery(q || "");
            setLocation(loc || "");
            // Trigger search immediately
            performSearch(q || "", loc || "", 1, true);
        }
    }, [searchParams]);

    const performSearch = async (q: string, loc: string, pageNum: number, isNewSearch: boolean) => {
        setLoading(true);
        try {
            const start = (pageNum - 1) * 10 + 1;
            const results = await searchJobs(
                q,
                loc,
                start,
                selectedExperience,
                selectedPlatforms,
                selectedCompanySizes
            );

            if (isNewSearch) {
                setJobs(results);
                setHasSearched(true);
            } else {
                setJobs(prev => [...prev, ...results]);
            }

            setHasMore(results.length >= 10);
        } catch (error) {
            console.error("Search failed", error);
        } finally {
            setLoading(false);
        }
    };

    const loadJobs = async (pageNum: number, isNewSearch: boolean = false) => {
        await performSearch(query, location, pageNum, isNewSearch);
    };

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        // Update URL without reloading
        const params = new URLSearchParams();
        if (query) params.set('q', query);
        if (location) params.set('location', location);
        router.push(`/?${params.toString()}`);

        setPage(1);
        setHasMore(true);
        await loadJobs(1, true);
    };

    const handleShowMore = async () => {
        const nextPage = page + 1;
        setPage(nextPage);
        await loadJobs(nextPage, false);
    };

    const toggleExperience = (level: string) => {
        setSelectedExperience(prev =>
            prev.includes(level)
                ? prev.filter(l => l !== level)
                : [...prev, level]
        );
    };

    const togglePlatform = (platform: string) => {
        if (platform === "All") {
            setSelectedPlatforms(["All"]);
            return;
        }

        setSelectedPlatforms(prev => {
            if (prev.includes("All")) {
                return [platform];
            }
            if (prev.includes(platform)) {
                const newPlatforms = prev.filter(p => p !== platform);
                return newPlatforms.length === 0 ? ["All"] : newPlatforms;
            }
            return [...prev, platform];
        });
    };

    const toggleCompanySize = (size: string) => {
        setSelectedCompanySizes(prev =>
            prev.includes(size)
                ? prev.filter(s => s !== size)
                : [...prev, size]
        );
    };

    const clearQuery = () => setQuery("");
    const clearLocation = () => setLocation("");

    return (
        <main className="min-h-screen bg-slate-50 dark:bg-gradient-to-br dark:from-slate-950 dark:via-blue-950 dark:to-slate-950 text-slate-900 dark:text-slate-100 transition-colors duration-300">
            <Header />

            {/* Hero Section */}
            <div className="relative overflow-hidden border-b border-slate-200 dark:border-white/10 pt-16">
                <div className="absolute inset-0 bg-grid-slate-200/50 dark:bg-grid-white/5 [mask-image:linear-gradient(0deg,transparent,black)]" />

                <div className="relative max-w-5xl mx-auto px-4 pt-20 pb-16 sm:px-6 lg:px-8 flex flex-col items-center text-center">
                    <h1 className="text-4xl sm:text-6xl font-bold tracking-tight mb-6 bg-gradient-to-r from-blue-600 via-blue-800 to-blue-600 dark:from-blue-200 dark:via-white dark:to-blue-200 bg-clip-text text-transparent drop-shadow-sm">
                        Find Your Dream Job <br className="hidden sm:block" /> Across All Platforms
                    </h1>
                    <p className="max-w-2xl text-lg text-slate-600 dark:text-blue-200/80 mb-10">
                        One search to rule them all. We aggregate listings from LinkedIn, Indeed, Glassdoor, and more to save you time.
                    </p>

                    {/* Search Form */}
                    <div className="w-full max-w-3xl space-y-4">
                        <form onSubmit={handleSearch} className="bg-white dark:bg-white/5 backdrop-blur-md p-2 rounded-2xl shadow-2xl border border-slate-200 dark:border-white/10 flex flex-col sm:flex-row gap-2">
                            <div className="flex-1 flex items-center px-4 h-12 bg-slate-50 dark:bg-white/5 rounded-xl border border-transparent focus-within:border-blue-400/50 transition-all relative group">
                                <Search className="w-5 h-5 text-slate-400 dark:text-blue-300 mr-3" />
                                <input
                                    type="text"
                                    placeholder="Job title, keywords, or company"
                                    className="flex-1 bg-transparent border-none outline-none text-sm text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-blue-200/50 w-full"
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    list="job-suggestions"
                                />
                                {query && (
                                    <button
                                        type="button"
                                        onClick={clearQuery}
                                        className="p-1 hover:bg-slate-200 dark:hover:bg-white/10 rounded-full transition-colors"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-slate-400 dark:text-blue-300">
                                            <path d="M18 6 6 18" />
                                            <path d="m6 6 12 12" />
                                        </svg>
                                    </button>
                                )}
                                <datalist id="job-suggestions">
                                    {POPULAR_JOB_TITLES.map((title, i) => (
                                        <option key={`${title}-${i}`} value={title} />
                                    ))}
                                </datalist>
                            </div>

                            <div className="flex-1 flex items-center px-4 h-12 bg-slate-50 dark:bg-white/5 rounded-xl border border-transparent focus-within:border-blue-400/50 transition-all relative group">
                                <MapPin className="w-5 h-5 text-slate-400 dark:text-blue-300 mr-3" />
                                <input
                                    type="text"
                                    placeholder="City, State, District, or Region"
                                    className="flex-1 bg-transparent border-none outline-none text-sm text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-blue-200/50 w-full"
                                    value={location}
                                    onChange={(e) => setLocation(e.target.value)}
                                    list="location-suggestions"
                                />
                                {location && (
                                    <button
                                        type="button"
                                        onClick={clearLocation}
                                        className="p-1 hover:bg-slate-200 dark:hover:bg-white/10 rounded-full transition-colors"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-slate-400 dark:text-blue-300">
                                            <path d="M18 6 6 18" />
                                            <path d="m6 6 12 12" />
                                        </svg>
                                    </button>
                                )}
                                <datalist id="location-suggestions">
                                    {POPULAR_LOCATIONS.map((loc, i) => (
                                        <option key={`${loc}-${i}`} value={loc} />
                                    ))}
                                </datalist>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="h-12 px-8 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl transition-all shadow-lg shadow-blue-900/20 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                            >
                                {loading && !jobs.length ? "Searching..." : "Search Jobs"}
                            </button>
                        </form>

                        {/* Filters */}
                        <div className="flex flex-col sm:flex-row gap-6 p-4 bg-white dark:bg-white/5 backdrop-blur-sm rounded-xl border border-slate-200 dark:border-white/5 shadow-sm dark:shadow-none">
                            {/* Experience Filter */}
                            <div className="flex-1">
                                <h3 className="text-xs font-semibold text-slate-500 dark:text-blue-200 uppercase tracking-wider mb-3">Experience Level</h3>
                                <div className="flex flex-wrap gap-3">
                                    {EXPERIENCE_LEVELS.map(level => (
                                        <label key={level} className="flex items-center space-x-2 cursor-pointer group">
                                            <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${selectedExperience.includes(level) ? 'bg-blue-500 border-blue-500' : 'border-slate-300 dark:border-blue-200/30 group-hover:border-blue-400'}`}>
                                                {selectedExperience.includes(level) && <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
                                            </div>
                                            <input
                                                type="checkbox"
                                                className="hidden"
                                                checked={selectedExperience.includes(level)}
                                                onChange={() => toggleExperience(level)}
                                            />
                                            <span className={`text-sm ${selectedExperience.includes(level) ? 'text-slate-900 dark:text-white' : 'text-slate-500 dark:text-blue-200/60 group-hover:text-blue-600 dark:group-hover:text-blue-200'}`}>{level}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>

                            {/* Platform Filter */}
                            <div className="flex-1 border-t sm:border-t-0 sm:border-l border-slate-200 dark:border-white/10 pt-4 sm:pt-0 sm:pl-6">
                                <h3 className="text-xs font-semibold text-slate-500 dark:text-blue-200 uppercase tracking-wider mb-3">Platforms</h3>
                                <div className="flex flex-wrap gap-3">
                                    {SEARCH_PLATFORMS.map(platform => (
                                        <label key={platform} className="flex items-center space-x-2 cursor-pointer group">
                                            <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${selectedPlatforms.includes(platform) ? 'bg-blue-500 border-blue-500' : 'border-slate-300 dark:border-blue-200/30 group-hover:border-blue-400'}`}>
                                                {selectedPlatforms.includes(platform) && <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
                                            </div>
                                            <input
                                                type="checkbox"
                                                className="hidden"
                                                checked={selectedPlatforms.includes(platform)}
                                                onChange={() => togglePlatform(platform)}
                                            />
                                            <span className={`text-sm ${selectedPlatforms.includes(platform) ? 'text-slate-900 dark:text-white' : 'text-slate-500 dark:text-blue-200/60 group-hover:text-blue-600 dark:group-hover:text-blue-200'}`}>{platform}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>

                            {/* Company Size Filter */}
                            <div className="flex-1 border-t sm:border-t-0 sm:border-l border-slate-200 dark:border-white/10 pt-4 sm:pt-0 sm:pl-6">
                                <h3 className="text-xs font-semibold text-slate-500 dark:text-blue-200 uppercase tracking-wider mb-3">Company Size</h3>
                                <div className="flex flex-wrap gap-3">
                                    {COMPANY_SIZES.map(size => (
                                        <label key={size} className="flex items-center space-x-2 cursor-pointer group">
                                            <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${selectedCompanySizes.includes(size) ? 'bg-blue-500 border-blue-500' : 'border-slate-300 dark:border-blue-200/30 group-hover:border-blue-400'}`}>
                                                {selectedCompanySizes.includes(size) && <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
                                            </div>
                                            <input
                                                type="checkbox"
                                                className="hidden"
                                                checked={selectedCompanySizes.includes(size)}
                                                onChange={() => toggleCompanySize(size)}
                                            />
                                            <span className={`text-sm ${selectedCompanySizes.includes(size) ? 'text-slate-900 dark:text-white' : 'text-slate-500 dark:text-blue-200/60 group-hover:text-blue-600 dark:group-hover:text-blue-200'}`}>{size}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Results Section */}
            <div className="max-w-7xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
                {jobs.length > 0 ? (
                    <>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {jobs.map((job, index) => (
                                <JobCard key={`${job.id || 'job'}-${index}`} job={job} />
                            ))}
                        </div>

                        {hasMore && (
                            <div className="mt-12 text-center">
                                <button
                                    onClick={handleShowMore}
                                    disabled={loading}
                                    className="inline-flex items-center px-6 py-3 bg-white dark:bg-white/5 hover:bg-slate-50 dark:hover:bg-white/10 border border-slate-200 dark:border-white/10 rounded-xl text-slate-600 dark:text-blue-200 font-medium transition-all disabled:opacity-50 shadow-sm dark:shadow-none"
                                >
                                    {loading ? (
                                        "Loading..."
                                    ) : (
                                        <>
                                            Show More Jobs
                                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="ml-2">
                                                <path d="m6 9 6 6 6-6" />
                                            </svg>
                                        </>
                                    )}
                                </button>
                            </div>
                        )}
                    </>
                ) : loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
                        {[...Array(6)].map((_, i) => (
                            <div key={i} className="h-64 bg-white dark:bg-white/5 rounded-xl border border-slate-200 dark:border-white/10" />
                        ))}
                    </div>
                ) : hasSearched ? (
                    <div className="text-center py-20">
                        <Briefcase className="w-12 h-12 text-slate-300 dark:text-blue-300/50 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-slate-900 dark:text-white">No jobs found</h3>
                        <p className="text-slate-500 dark:text-blue-200/60">Try adjusting your search terms or location.</p>
                    </div>
                ) : (
                    <div className="text-center py-20 opacity-50">
                        <p className="text-slate-500 dark:text-blue-200/60">Start searching to see jobs from across the web.</p>
                    </div>
                )}
            </div>
        </main>
    );
}

export default function Home() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-slate-950 flex items-center justify-center text-white">Loading...</div>}>
            <HomeContent />
        </Suspense>
    );
}
