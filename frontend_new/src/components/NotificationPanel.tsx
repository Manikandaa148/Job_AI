import { X, Briefcase, FileText, Sparkles, Building2 } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getRecommendations } from '../lib/api';

interface Notification {
    id: string;
    type: 'job_alert' | 'resume_analysis' | 'news' | 'application';
    title: string;
    subtitle: string;
    time: string;
    icon?: React.ReactNode;
    image?: string;
    action?: {
        label: string;
        onClick: () => void;
    };
    isRead: boolean;
    searchParams?: {
        q: string;
        location?: string;
    };
}

interface NotificationPanelProps {
    isOpen: boolean;
    onClose: () => void;
}

export function NotificationPanel({ isOpen, onClose }: NotificationPanelProps) {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const router = useRouter();

    useEffect(() => {
        const fetchNotifications = async () => {
            // 1. Local Storage-based Job Alerts (Existing Logic)
            const savedProfile = localStorage.getItem('userProfile');
            let profile = { jobPreferences: [] as string[], preferredLocations: [] as string[] };

            if (savedProfile) {
                try {
                    profile = JSON.parse(savedProfile);
                } catch (e) {
                    console.error("Failed to parse profile for notifications", e);
                }
            }

            const baseNotifications: Notification[] = [
                {
                    id: '1',
                    type: 'resume_analysis',
                    title: 'We analysed your resume and found a few improvement areas',
                    subtitle: 'Resume analyser',
                    time: '1h ago',
                    icon: <Sparkles className="w-5 h-5 text-yellow-500" />,
                    isRead: false
                },
            ];

            const jobNotifications: Notification[] = [];

            if (profile.jobPreferences && profile.jobPreferences.length > 0) {
                const role = profile.jobPreferences[0];
                const location = profile.preferredLocations?.[0] || 'Remote';

                jobNotifications.push({
                    id: '3',
                    type: 'job_alert',
                    title: `5 new ${role} roles where you could become a top applicant`,
                    subtitle: `Jobs based on your profile`,
                    time: '2h ago',
                    icon: <Briefcase className="w-5 h-5 text-blue-500" />,
                    action: {
                        label: 'View Jobs',
                        onClick: () => {
                            const params = new URLSearchParams();
                            params.set('q', role);
                            if (location) params.set('location', location);
                            router.push(`/?${params.toString()}`);
                            onClose();
                        }
                    },
                    searchParams: { q: role, location: location },
                    isRead: true
                });

                if (profile.jobPreferences.length > 1) {
                    const role2 = profile.jobPreferences[1];
                    jobNotifications.push({
                        id: '4',
                        type: 'job_alert',
                        title: `New ${role2} job recommendations`,
                        subtitle: `${role2} • ${location}`,
                        time: '1d ago',
                        icon: <Building2 className="w-5 h-5 text-red-500" />,
                        searchParams: { q: role2, location: location },
                        isRead: true
                    });
                }
            } else {
                jobNotifications.push({
                    id: '3',
                    type: 'job_alert',
                    title: 'Complete your profile to get personalized job alerts',
                    subtitle: 'Profile Recommendation',
                    time: 'Just now',
                    icon: <Briefcase className="w-5 h-5 text-slate-400" />,
                    isRead: false
                });
            }

            // 2. Fetch Skill Recommendations (New API)
            let recNotifications: Notification[] = [];
            try {
                const recommendations = await getRecommendations();
                recNotifications = recommendations.map((rec, index) => ({
                    id: `rec-${index}`,
                    type: 'resume_analysis',
                    title: `Recommended Skill: ${rec.skill}`,
                    subtitle: `${rec.reason} (${rec.role})`,
                    time: 'Just now',
                    icon: <Sparkles className="w-5 h-5 text-purple-500" />,
                    isRead: false
                }));
            } catch (error) {
                // Silently fail if auth missing or API error
                console.log("Could not fetch recommendations", error);
            }

            setNotifications([...recNotifications, ...baseNotifications, ...jobNotifications]);
        };

        fetchNotifications();

        // Listen for profile updates
        window.addEventListener('profileUpdated', fetchNotifications);
        return () => window.removeEventListener('profileUpdated', fetchNotifications);
    }, [router, onClose]);

    const handleNotificationClick = (notification: Notification) => {
        if (notification.searchParams) {
            const params = new URLSearchParams();
            params.set('q', notification.searchParams.q);
            if (notification.searchParams.location) {
                params.set('location', notification.searchParams.location);
            }
            router.push(`/?${params.toString()}`);
            onClose();
        }
    };

    if (!isOpen) return null;

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
                onClick={onClose}
            />

            {/* Panel */}
            <div className="fixed top-0 right-0 h-full w-full sm:w-[400px] bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-white/10 shadow-2xl z-50 transform transition-transform duration-300 ease-in-out animate-in slide-in-from-right">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-white/10">
                    <h2 className="text-xl font-bold text-slate-900 dark:text-white">Notifications</h2>
                    <button
                        onClick={onClose}
                        className="p-2 text-slate-500 dark:text-blue-200/60 hover:bg-slate-100 dark:hover:bg-white/10 rounded-full transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="overflow-y-auto h-[calc(100vh-64px)]">
                    {/* Today Section */}
                    <div className="p-4">
                        <h3 className="text-sm font-medium text-slate-500 dark:text-blue-200/60 mb-3">Today</h3>
                        <div className="space-y-3">
                            {notifications.filter(n => n.time.includes('h ago')).map(notification => (
                                <NotificationItem
                                    key={notification.id}
                                    notification={notification}
                                    onClick={() => handleNotificationClick(notification)}
                                />
                            ))}
                        </div>
                    </div>

                    {/* Earlier Section */}
                    <div className="p-4 pt-0">
                        <h3 className="text-sm font-medium text-slate-500 dark:text-blue-200/60 mb-3">Earlier</h3>
                        <div className="space-y-3">
                            {notifications.filter(n => !n.time.includes('h ago')).map(notification => (
                                <NotificationItem
                                    key={notification.id}
                                    notification={notification}
                                    onClick={() => handleNotificationClick(notification)}
                                />
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}

function NotificationItem({ notification, onClick }: { notification: Notification; onClick: () => void }) {
    return (
        <div
            onClick={onClick}
            className={`flex gap-4 p-4 bg-slate-50 dark:bg-white/5 hover:bg-slate-100 dark:hover:bg-white/10 rounded-xl transition-colors cursor-pointer group border border-transparent hover:border-slate-200 dark:hover:border-white/10 ${notification.searchParams ? 'hover:shadow-md' : ''}`}
        >
            {/* Icon/Image */}
            <div className="flex-shrink-0">
                {notification.image ? (
                    <div className="w-10 h-10 rounded-lg bg-white p-1 border border-slate-200 dark:border-white/10 overflow-hidden">
                        <img src={notification.image} alt="" className="w-full h-full object-contain" />
                    </div>
                ) : (
                    <div className="w-10 h-10 rounded-lg bg-white dark:bg-white/10 border border-slate-200 dark:border-white/10 flex items-center justify-center shadow-sm">
                        {notification.icon}
                    </div>
                )}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900 dark:text-white leading-snug mb-1">
                    {notification.title}
                </p>
                <div className="flex items-center justify-between">
                    <p className="text-xs text-slate-500 dark:text-blue-200/60 truncate">
                        {notification.subtitle}
                    </p>
                    <span className="text-xs text-slate-400 dark:text-blue-200/40 whitespace-nowrap ml-2">
                        {notification.time}
                    </span>
                </div>

                {notification.action && (
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            notification.action?.onClick();
                        }}
                        className="mt-3 px-4 py-1.5 text-xs font-medium text-blue-600 dark:text-blue-300 border border-blue-200 dark:border-blue-500/30 rounded-full hover:bg-blue-50 dark:hover:bg-blue-500/10 transition-colors"
                    >
                        {notification.action.label}
                    </button>
                )}
            </div>
        </div>
    );
}
