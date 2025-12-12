"use client";

import { useState } from "react";
import { Zap, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

interface AutoApplyButtonProps {
    jobId: string;
    onMissingInfo?: (missingFields: string[]) => void;
}

export function AutoApplyButton({ jobId, onMissingInfo }: AutoApplyButtonProps) {
    const [isApplying, setIsApplying] = useState(false);
    const [status, setStatus] = useState<"idle" | "success" | "error" | "missing-info">("idle");
    const [message, setMessage] = useState("");

    const handleAutoApply = async () => {
        setIsApplying(true);
        setStatus("idle");

        try {
            const token = localStorage.getItem("token");

            if (!token) {
                setStatus("error");
                setMessage("Please login to use auto-apply");
                setIsApplying(false);
                return;
            }

            // First, validate profile
            const validateResponse = await fetch("http://localhost:8000/auto-apply/validate", {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            const validationData = await validateResponse.json();

            if (!validationData.can_auto_apply) {
                setStatus("missing-info");
                setMessage(`Missing: ${validationData.missing_fields.join(", ")}`);
                if (onMissingInfo) {
                    onMissingInfo(validationData.missing_fields);
                }
                setIsApplying(false);
                return;
            }

            // Execute auto-apply with REAL automation
            // Set use_real_automation to true to actually apply to jobs
            // Set to false for simulation mode (testing)
            const applyResponse = await fetch("http://localhost:8000/auto-apply/execute", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    job_ids: [jobId],
                    use_real_automation: false  // Change to true to enable real browser automation
                })
            });

            const applyData = await applyResponse.json();

            if (applyData.success) {
                setStatus("success");
                setMessage("Applied successfully! ✓");
                setTimeout(() => {
                    setStatus("idle");
                    setMessage("");
                }, 3000);
            } else {
                setStatus("error");
                setMessage(applyData.error || "Application failed");
            }
        } catch (error) {
            console.error("Auto-apply error:", error);
            setStatus("error");
            setMessage("Failed to apply. Please try again.");
        } finally {
            setIsApplying(false);
        }
    };

    const getButtonContent = () => {
        if (isApplying) {
            return (
                <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Applying...</span>
                </>
            );
        }

        if (status === "success") {
            return (
                <>
                    <CheckCircle className="w-4 h-4" />
                    <span>Applied!</span>
                </>
            );
        }

        if (status === "error" || status === "missing-info") {
            return (
                <>
                    <AlertCircle className="w-4 h-4" />
                    <span>Try Again</span>
                </>
            );
        }

        return (
            <>
                <Zap className="w-4 h-4" fill="currentColor" />
                <span>Auto Apply</span>
            </>
        );
    };

    const getButtonClass = () => {
        const baseClass = "flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all duration-300 disabled:cursor-not-allowed";

        if (status === "success") {
            return `${baseClass} bg-green-500 hover:bg-green-600 text-white`;
        }

        if (status === "error") {
            return `${baseClass} bg-red-500 hover:bg-red-600 text-white`;
        }

        if (status === "missing-info") {
            return `${baseClass} bg-orange-500 hover:bg-orange-600 text-white`;
        }

        return `${baseClass} bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg hover:shadow-xl hover:scale-105`;
    };

    return (
        <div className="flex flex-col gap-1">
            <button
                onClick={handleAutoApply}
                disabled={isApplying}
                className={getButtonClass()}
            >
                {getButtonContent()}
            </button>
            {message && (
                <p className={`text-xs ${status === "success" ? "text-green-600 dark:text-green-400" :
                    status === "error" ? "text-red-600 dark:text-red-400" :
                        "text-orange-600 dark:text-orange-400"
                    }`}>
                    {message}
                </p>
            )}
        </div>
    );
}
