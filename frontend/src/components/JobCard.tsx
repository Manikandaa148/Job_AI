import React from 'react';
import { MapPin, Building2, ExternalLink, Calendar, DollarSign } from 'lucide-react';
import { Job } from '@/lib/api';
import { cn } from '@/lib/utils';

interface JobCardProps {
    job: Job;
    className?: string;
}

export function JobCard({ job, className }: JobCardProps) {
    return (
        <div className={cn("group relative bg-white dark:bg-white/5 backdrop-blur-sm border border-slate-200 dark:border-white/10 rounded-xl p-6 hover:bg-slate-50 dark:hover:bg-white/10 hover:shadow-xl hover:shadow-blue-900/20 transition-all duration-300 hover:-translate-y-1", className)}>
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

            <a
                href={job.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center w-full px-4 py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-500 rounded-lg transition-colors shadow-lg shadow-blue-900/20"
            >
                Apply Now
                <ExternalLink className="w-4 h-4 ml-2" />
            </a>
        </div>
    );
}
