"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";

interface AuthWrapperProps {
    children: React.ReactNode;
}

export function AuthWrapper({ children }: AuthWrapperProps) {
    const router = useRouter();
    const pathname = usePathname();
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [isMounted, setIsMounted] = useState(false);

    // Handle client-side mounting
    useEffect(() => {
        setIsMounted(true);
    }, []);

    useEffect(() => {
        if (!isMounted) return;

        // Check if user is authenticated
        const token = localStorage.getItem("token");

        // If on login page, allow access
        if (pathname === "/login") {
            setIsAuthenticated(true);
            setIsLoading(false);
            return;
        }

        // If no token and not on login page, redirect to login
        if (!token) {
            setIsLoading(false);
            router.push("/login");
            return;
        }

        // Token exists, user is authenticated
        setIsAuthenticated(true);
        setIsLoading(false);
    }, [pathname, router, isMounted]);

    // Don't render anything until mounted (prevents hydration errors)
    if (!isMounted) {
        return null;
    }

    // Show loading state while checking authentication
    if (isLoading) {
        return (
            <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-slate-600 dark:text-blue-200/60">Loading...</p>
                </div>
            </div>
        );
    }

    // If authenticated, show content
    if (isAuthenticated) {
        return <>{children}</>;
    }

    // Otherwise, show nothing (will redirect)
    return null;
}
