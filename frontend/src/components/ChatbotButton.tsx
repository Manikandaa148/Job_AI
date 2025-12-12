"use client";

import { useState } from "react";
import { Sparkles } from "lucide-react";
import { Chatbot } from "./Chatbot";

export function ChatbotButton() {
    const [isChatOpen, setIsChatOpen] = useState(false);

    return (
        <>
            {/* Floating Button */}
            <button
                onClick={() => setIsChatOpen(!isChatOpen)}
                className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-br from-slate-900 to-slate-800 dark:from-slate-800 dark:to-slate-700 rounded-full shadow-2xl flex items-center justify-center group hover:scale-110 transition-all duration-300 z-50 border-2 border-yellow-400/20"
                aria-label="Open AI Assistant"
            >
                {/* Bubble background effect */}
                <div className="absolute inset-0 rounded-full bg-gradient-to-br from-yellow-400/20 to-transparent animate-pulse"></div>

                {/* Glow effect */}
                <div className="absolute inset-0 rounded-full bg-yellow-400/10 blur-xl group-hover:bg-yellow-400/20 transition-all"></div>

                {/* Star Icon */}
                <Sparkles
                    className="w-7 h-7 text-yellow-400 relative z-10 group-hover:rotate-12 transition-transform duration-300"
                    fill="currentColor"
                />

                {/* Notification badge (optional - can show when there are new messages) */}
                {!isChatOpen && (
                    <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full border-2 border-white dark:border-slate-900 animate-bounce"></div>
                )}
            </button>

            {/* Chatbot Component */}
            <Chatbot
                isOpen={isChatOpen}
                onClose={() => setIsChatOpen(false)}
                onProfileComplete={() => {
                    // Optional: Show success notification
                    console.log("Profile completed!");
                }}
            />
        </>
    );
}
