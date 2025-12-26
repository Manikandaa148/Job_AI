import React, { useState } from 'react';
import { MapPin, Building2, ExternalLink, Calendar, DollarSign, Bookmark, Check } from 'lucide-react';
import { Job, createApplication } from '@/lib/api';
import { cn } from '@/lib/utils';


interface JobCardProps {
    job: Job;
    className?: string;
    onMissingInfo?: (missingFields: string[]) => void;
}

export function JobCard({ job, className, onMissingInfo }: JobCardProps) {
    const [isSaved, setIsSaved] = useState(false);
    const [isSaving, setIsSaving] = useState(false);

    const handleSave = async (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (isSaved || isSaving) return;

        setIsSaving(true);
        try {
            await createApplication({
                job_title: job.title,
                company: job.company,
                location: job.location,
                job_url: job.url,
                platform: job.source,
                status: 'Saved',
                salary: job.salary
            });
            setIsSaved(true);
        } catch (e) {
            console.error("Failed to save", e);
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className={cn("group relative bg-white dark:bg-slate-900/50 backdrop-blur-sm border border-slate-200 dark:border-white/10 rounded-xl p-6 hover:bg-slate-50 dark:hover:bg-white/5 hover:shadow-xl hover:shadow-blue-900/10 transition-all duration-300 hover:-translate-y-1", className)}>
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="text-xl font-semibold text-slate-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-300 transition-colors">
                        {job.title}
                    </h3>
                    <div className="flex items-center text-slate-500 dark:text-blue-200/70 mt-1">
                        <Building2 className="w-4 h-4 mr-1.5" />
                        <span className="font-medium">{job.company}</span>
                    </div>
                </div>
                <span className="px-3 py-1 text-xs font-medium text-blue-700 dark:text-blue-300 bg-blue-100 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 rounded-full">
                    {job.source}
                </span>
            </div>

            <div className="flex flex-wrap gap-3 mb-4 text-sm text-slate-600 dark:text-blue-200/60">
                <div className="flex items-center">
                    <MapPin className="w-4 h-4 mr-1.5 text-slate-400 dark:text-blue-400/70" />
                    {job.location || "Remote / Unspecified"}
                </div>
                {job.salary && (
                    <div className="flex items-center">
                        <DollarSign className="w-4 h-4 mr-1.5 text-slate-400 dark:text-blue-400/70" />
                        {job.salary}
                    </div>
                )}
                {job.posted_date && (
                    <div className="flex items-center">
                        <Calendar className="w-4 h-4 mr-1.5 text-slate-400 dark:text-blue-400/70" />
                        {job.posted_date}
                    </div>
                )}
            </div>

            <p className="text-slate-600 dark:text-blue-100/70 text-sm line-clamp-3 mb-6">
                {job.description}
            </p>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3">
                <button
                    onClick={handleSave}
                    disabled={isSaved || isSaving}
                    className={cn(
                        "inline-flex items-center justify-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors border",
                        isSaved
                            ? "bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-800"
                            : "text-slate-700 dark:text-blue-100 bg-white dark:bg-transparent border-slate-200 dark:border-white/10 hover:bg-slate-50 dark:hover:bg-white/5"
                    )}
                >
                    {isSaved ? <Check className="w-4 h-4 mr-2" /> : <Bookmark className="w-4 h-4 mr-2" />}
                    {isSaved ? "Saved" : "Track"}
                </button>

                <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center flex-1 px-4 py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-500 rounded-lg transition-colors shadow-lg shadow-blue-900/20"
                >
                    Apply Manually
                    <ExternalLink className="w-4 h-4 ml-2" />
                </a>
            </div>
        </div>
    );
}

