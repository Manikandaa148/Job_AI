
interface DonutChartProps {
    score: number;
    size?: number;
    strokeWidth?: number;
    className?: string;
}

export function DonutChart({ score, size = 120, strokeWidth = 8, className = "" }: DonutChartProps) {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (score / 100) * circumference;

    // Color based on score
    let colorClass = "text-red-500";
    if (score >= 70) colorClass = "text-green-500";
    else if (score >= 40) colorClass = "text-yellow-500";

    return (
        <div className={`relative flex items-center justify-center ${className}`} style={{ width: size, height: size }}>
            <svg width={size} height={size} className="transform -rotate-90">
                {/* Background Circle */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    fill="transparent"
                    className="text-slate-200 dark:text-slate-700"
                />
                {/* Progress Circle */}
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    fill="transparent"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    strokeLinecap="round"
                    className={`transition-all duration-1000 ease-out ${colorClass}`}
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-2xl font-bold ${colorClass}`}>
                    {score}%
                </span>
                <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">ATS Score</span>
            </div>
        </div>
    );
}
