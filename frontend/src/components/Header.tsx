import Link from 'next/link';
import { User, Bell, Menu, Sun, Moon, FileText } from 'lucide-react';
import { useState, useEffect } from 'react';
import { ProfileModal } from './ProfileModal';
import { ResumeBuilderModal } from './ResumeBuilderModal';
import { NotificationPanel } from './NotificationPanel';
import { getProfile, User as UserType } from '@/lib/api';

export function Header() {
    const [isProfileOpen, setIsProfileOpen] = useState(false);
    const [isResumeBuilderOpen, setIsResumeBuilderOpen] = useState(false);
    const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
    const [theme, setTheme] = useState<'light' | 'dark'>('dark'); // Default to dark for premium feel
    const [user, setUser] = useState<UserType | null>(null);

    useEffect(() => {
        // Check system preference or saved theme
        const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
        if (savedTheme) {
            setTheme(savedTheme);
            document.documentElement.classList.add(savedTheme);
            if (savedTheme === 'dark') document.documentElement.classList.remove('light');
            else document.documentElement.classList.remove('dark');
        } else {
            const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const initialTheme = systemPrefersDark ? 'dark' : 'light';
            setTheme(initialTheme);
            document.documentElement.classList.add(initialTheme);
            if (initialTheme === 'dark') document.documentElement.classList.remove('light');
            else document.documentElement.classList.remove('dark');
        }
    }, []);

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const userData = await getProfile();
                setUser(userData);
            } catch (e) {
                console.error("Failed to fetch user for header", e);
                // If no user is logged in, automatically create a guest account
                await autoLoginGuest();
            }
        };
        fetchUser();

        // Listen for profile updates
        const handleProfileUpdate = () => fetchUser();
        window.addEventListener('profileUpdated', handleProfileUpdate);
        return () => window.removeEventListener('profileUpdated', handleProfileUpdate);
    }, []);

    const autoLoginGuest = async () => {
        // Check if we already have a token
        const existingToken = localStorage.getItem('token');
        if (existingToken) return;

        try {
            // Try to login with default guest credentials
            const { login, register } = await import('@/lib/api');

            try {
                const loginResult = await login('guest@jobai.com', 'guest123');
                localStorage.setItem('token', loginResult.access_token);
                console.log('✓ Guest user logged in');

                // Fetch user data after login
                const userData = await getProfile();
                setUser(userData);
            } catch (loginError) {
                // If login fails, register a new guest account
                console.log('Guest account not found, creating new one...');
                await register('guest@jobai.com', 'guest123', 'Guest User');

                // Now login
                const loginResult = await login('guest@jobai.com', 'guest123');
                localStorage.setItem('token', loginResult.access_token);
                console.log('✓ New guest user created and logged in');

                // Fetch user data after login
                const userData = await getProfile();
                setUser(userData);
            }
        } catch (error) {
            console.error('Failed to auto-login guest:', error);
        }
    };

    const toggleTheme = () => {
        const newTheme = theme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);

        document.documentElement.classList.remove('light', 'dark');
        document.documentElement.classList.add(newTheme);
    };

    return (
        <>
            <header className="fixed top-0 left-0 right-0 z-40 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md border-b border-slate-200 dark:border-white/10 transition-colors duration-300">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        {/* Logo */}
                        <div className="flex-shrink-0">
                            <Link href="/" className="flex items-center gap-2">
                                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-700 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20">
                                    <span className="text-white font-bold text-lg">J</span>
                                </div>
                                <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-blue-400 dark:from-white dark:to-blue-200 bg-clip-text text-transparent">
                                    Job AI
                                </span>
                            </Link>
                        </div>

                        {/* Right Side Actions */}
                        <div className="flex items-center gap-4">
                            <button
                                onClick={toggleTheme}
                                className="p-2 text-slate-500 dark:text-blue-200/60 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 rounded-full transition-colors"
                                aria-label="Toggle Theme"
                            >
                                {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                            </button>

                            <button
                                onClick={() => setIsNotificationsOpen(true)}
                                className="p-2 text-slate-500 dark:text-blue-200/60 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 rounded-full transition-colors relative"
                            >
                                <Bell className="w-5 h-5" />
                                <span className="absolute top-2 right-2 w-2 h-2 bg-blue-500 rounded-full border-2 border-white dark:border-slate-950"></span>
                            </button>

                            <div className="h-6 w-px bg-slate-200 dark:bg-white/10 mx-1"></div>

                            <button
                                onClick={() => setIsResumeBuilderOpen(true)}
                                className="p-2 text-slate-500 dark:text-blue-200/60 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-500/10 rounded-full transition-all group"
                                title="Resume Builder"
                            >
                                <FileText className="w-5 h-5 group-hover:scale-110 transition-transform" />
                            </button>

                            <button
                                onClick={() => setIsProfileOpen(true)}
                                className="flex items-center gap-3 pl-2 pr-4 py-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-white/5 border border-transparent hover:border-slate-200 dark:hover:border-white/10 transition-all group"
                            >
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white font-medium shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform overflow-hidden">
                                    {user?.avatar ? (
                                        <img src={user.avatar} alt="Profile" className="w-full h-full object-cover" />
                                    ) : (
                                        <span>{user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'JD'}</span>
                                    )}
                                </div>
                                <div className="hidden sm:block text-left">
                                    <p className="text-sm font-medium text-slate-700 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-200 transition-colors">
                                        {user?.full_name || 'Guest User'}
                                    </p>
                                    <p className="text-xs text-slate-500 dark:text-blue-200/50">
                                        {user ? 'View Profile' : 'Complete Profile'}
                                    </p>
                                </div>
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <ProfileModal isOpen={isProfileOpen} onClose={() => setIsProfileOpen(false)} />
            <ResumeBuilderModal isOpen={isResumeBuilderOpen} onClose={() => setIsResumeBuilderOpen(false)} />
            <NotificationPanel isOpen={isNotificationsOpen} onClose={() => setIsNotificationsOpen(false)} />
        </>
    );
}
