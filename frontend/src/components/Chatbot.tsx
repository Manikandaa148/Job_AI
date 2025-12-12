"use client";

import { useState, useEffect, useRef } from "react";
import { X, Send, Sparkles } from "lucide-react";

interface Message {
    id: string;
    text: string;
    sender: "user" | "bot";
    timestamp: Date;
}

interface ChatbotProps {
    isOpen: boolean;
    onClose: () => void;
    onProfileComplete?: () => void;
}

export function Chatbot({ isOpen, onClose, onProfileComplete }: ChatbotProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "1",
            text: "Hello! 👋 I'm your AI Job Application Assistant. I can help you:\n\n• Complete your profile for auto-apply\n• Check what information is missing\n• Guide you through the application process\n\nHow may I assist you today?",
            sender: "bot",
            timestamp: new Date()
        }
    ]);
    const [inputValue, setInputValue] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const [currentField, setCurrentField] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async (text: string) => {
        if (!text.trim()) return;

        // Add user message
        const userMessage: Message = {
            id: Date.now().toString(),
            text,
            sender: "user",
            timestamp: new Date()
        };
        setMessages(prev => [...prev, userMessage]);
        setInputValue("");
        setIsTyping(true);

        // Smart response handling for common greetings and questions
        const lowerText = text.toLowerCase().trim();

        // Greetings
        if (["hi", "hello", "hey", "good morning", "good afternoon", "good evening"].some(greeting => lowerText === greeting || lowerText.startsWith(greeting))) {
            const botMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: "Hello! Welcome to the Job Application Assistant. I'm here to help you with:\n\n• Completing your profile for auto-apply\n• Checking missing information\n• Guiding you through job applications\n\nWhat would you like to do today?",
                sender: "bot",
                timestamp: new Date()
            };
            setMessages(prev => [...prev, botMessage]);
            setIsTyping(false);
            return;
        }

        // Help requests
        if (lowerText.includes("help") || lowerText.includes("what can you do") || lowerText === "?") {
            const botMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: "I can assist you with:\n\n📋 **Profile Completion**\n• Check what information is missing\n• Guide you through adding details\n• Update your profile automatically\n\n⚡ **Auto-Apply**\n• Validate your profile for auto-apply\n• Help you apply to jobs automatically\n\n💼 **Job Applications**\n• Answer questions about the process\n• Provide tips for success\n\nTry asking:\n• \"Check my profile\"\n• \"What information do I need?\"\n• \"How does auto-apply work?\"",
                sender: "bot",
                timestamp: new Date()
            };
            setMessages(prev => [...prev, botMessage]);
            setIsTyping(false);
            return;
        }

        // How does auto-apply work
        if (lowerText.includes("how") && (lowerText.includes("auto") || lowerText.includes("apply") || lowerText.includes("work"))) {
            const botMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: "**Auto-Apply** makes job applications effortless! Here's how it works:\n\n1️⃣ **Complete Your Profile**\nEnsure you have all required information (name, location, skills, experience, etc.)\n\n2️⃣ **Click Auto-Apply**\nOn any job card, click the purple \"⚡ Auto Apply\" button\n\n3️⃣ **Automatic Submission**\nWe'll fill out the application with your profile data and submit it instantly\n\n4️⃣ **Track Results**\nGet immediate feedback on application status\n\nWould you like me to check if your profile is ready for auto-apply?",
                sender: "bot",
                timestamp: new Date()
            };
            setMessages(prev => [...prev, botMessage]);
            setIsTyping(false);
            return;
        }

        // Check profile or missing info
        if (lowerText.includes("check") || lowerText.includes("missing") || lowerText.includes("need") || lowerText.includes("complete")) {
            await checkMissingInfo();
            setIsTyping(false);
            return;
        }

        // Thank you
        if (lowerText.includes("thank") || lowerText.includes("thanks")) {
            const botMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: "You're welcome! I'm here to help anytime. Feel free to ask if you need anything else! 😊",
                sender: "bot",
                timestamp: new Date()
            };
            setMessages(prev => [...prev, botMessage]);
            setIsTyping(false);
            return;
        }

        // For profile-related queries, call the backend
        try {
            const token = localStorage.getItem("token");

            if (!token) {
                const botMessage: Message = {
                    id: (Date.now() + 1).toString(),
                    text: "To update your profile or use auto-apply features, please log in first. You can:\n\n• Click the user icon in the top-right corner\n• Register a new account\n• Login with your credentials\n\nOnce logged in, I can help you complete your profile!",
                    sender: "bot",
                    timestamp: new Date()
                };
                setMessages(prev => [...prev, botMessage]);
                setIsTyping(false);
                return;
            }

            const response = await fetch("http://localhost:8000/chatbot/message", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    message: text,
                    field: currentField
                })
            });

            const data = await response.json();

            // Add bot response
            const botMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: data.message || "I'm here to help! Try asking about your profile or auto-apply features.",
                sender: "bot",
                timestamp: new Date()
            };
            setMessages(prev => [...prev, botMessage]);

            // Update current field for next question
            if (data.next_field) {
                setCurrentField(data.next_field.field);
            } else {
                setCurrentField(null);
            }

            // Check if profile is complete
            if (data.completed && onProfileComplete) {
                onProfileComplete();
            }
        } catch (error) {
            console.error("Error sending message:", error);
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: "I'm having trouble connecting right now. Please make sure you're logged in and try again. You can also try:\n\n• Refreshing the page\n• Checking your internet connection\n• Logging in again",
                sender: "bot",
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsTyping(false);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        sendMessage(inputValue);
    };

    const checkMissingInfo = async () => {
        setIsTyping(true);
        try {
            const token = localStorage.getItem("token");

            if (!token) {
                const botMessage: Message = {
                    id: Date.now().toString(),
                    text: "To check your profile completeness, please log in first.\n\n**How to login:**\n1. Click the user icon in the top-right corner\n2. Enter your credentials or register\n3. Come back and I'll help you complete your profile!\n\nAuto-apply requires a complete profile with your personal and professional information.",
                    sender: "bot",
                    timestamp: new Date()
                };
                setMessages(prev => [...prev, botMessage]);
                setIsTyping(false);
                return;
            }

            const response = await fetch("http://localhost:8000/auto-apply/validate", {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            const data = await response.json();

            if (data.can_auto_apply) {
                const botMessage: Message = {
                    id: Date.now().toString(),
                    text: "✅ Great news! Your profile is complete and ready for auto-apply!",
                    sender: "bot",
                    timestamp: new Date()
                };
                setMessages(prev => [...prev, botMessage]);
            } else if (data.prompts && data.prompts.length > 0) {
                const botMessage: Message = {
                    id: Date.now().toString(),
                    text: `I noticed your profile is missing some information. Let me help you complete it! ${data.prompts[0].question}`,
                    sender: "bot",
                    timestamp: new Date()
                };
                setMessages(prev => [...prev, botMessage]);
                setCurrentField(data.prompts[0].field);
            }
        } catch (error) {
            console.error("Error checking profile:", error);
            const errorMessage: Message = {
                id: Date.now().toString(),
                text: "I couldn't check your profile right now. Please make sure you're logged in and try again.",
                sender: "bot",
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsTyping(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed bottom-24 right-6 w-96 h-[600px] bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-white/10 flex flex-col overflow-hidden z-50 animate-in slide-in-from-bottom-4 duration-300">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-500 dark:to-blue-600 p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <div className="w-10 h-10 bg-black rounded-full flex items-center justify-center">
                            <Sparkles className="w-5 h-5 text-yellow-400" fill="currentColor" />
                        </div>
                        <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-white dark:border-slate-900"></div>
                    </div>
                    <div>
                        <h3 className="font-semibold text-white">AI Assistant</h3>
                        <p className="text-xs text-blue-100">Online</p>
                    </div>
                </div>
                <button
                    onClick={onClose}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                    <X className="w-5 h-5 text-white" />
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50 dark:bg-slate-950">
                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                    >
                        <div
                            className={`max-w-[80%] rounded-2xl px-4 py-2 ${message.sender === "user"
                                ? "bg-blue-600 text-white rounded-br-sm"
                                : "bg-white dark:bg-slate-800 text-slate-900 dark:text-white border border-slate-200 dark:border-white/10 rounded-bl-sm"
                                }`}
                        >
                            <p className="text-sm">{message.text}</p>
                            <p className={`text-xs mt-1 ${message.sender === "user" ? "text-blue-100" : "text-slate-400"
                                }`}>
                                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </p>
                        </div>
                    </div>
                ))}
                {isTyping && (
                    <div className="flex justify-start">
                        <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-white/10 rounded-2xl rounded-bl-sm px-4 py-3">
                            <div className="flex gap-1">
                                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions */}
            <div className="px-4 py-2 border-t border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900">
                <button
                    onClick={checkMissingInfo}
                    className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                >
                    Check my profile completeness
                </button>
            </div>

            {/* Input */}
            <form onSubmit={handleSubmit} className="p-4 border-t border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder="Type your message..."
                        className="flex-1 px-4 py-2 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-white/10 rounded-xl text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                        type="submit"
                        disabled={!inputValue.trim() || isTyping}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Send className="w-4 h-4" />
                    </button>
                </div>
            </form>
        </div>
    );
}
