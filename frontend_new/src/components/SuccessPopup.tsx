import { Check } from 'lucide-react';
import { useEffect, useState } from 'react';

interface SuccessPopupProps {
    isVisible: boolean;
    onClose: () => void;
    message?: string;
}

export function SuccessPopup({ isVisible, onClose, message = "Profile Update Successfully" }: SuccessPopupProps) {
    const [show, setShow] = useState(false);

    useEffect(() => {
        if (isVisible) {
            // Small delay to allow mounting before animation starts
            requestAnimationFrame(() => setShow(true));

            const timer = setTimeout(() => {
                setShow(false);
                setTimeout(onClose, 300); // Wait for exit animation
            }, 2000);
            return () => clearTimeout(timer);
        } else {
            setShow(false);
        }
    }, [isVisible, onClose]);

    if (!isVisible && !show) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center pointer-events-none">
            <div className="absolute inset-0 bg-black/20 backdrop-blur-[1px] transition-opacity duration-300" style={{ opacity: show ? 1 : 0 }} />
            <div
                className={`
                    relative flex flex-col items-center justify-center p-8 bg-white dark:bg-slate-900 
                    rounded-3xl shadow-2xl border border-slate-200 dark:border-white/10
                    transform transition-all duration-500 cubic-bezier(0.34, 1.56, 0.64, 1)
                    ${show ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-90 translate-y-8'}
                `}
            >
                <div className={`
                    w-20 h-20 bg-green-100 dark:bg-green-500/20 rounded-full flex items-center justify-center mb-4 text-green-600 dark:text-green-400
                    transform transition-all duration-700 delay-100
                    ${show ? 'scale-100 rotate-0' : 'scale-0 -rotate-90'}
                `}>
                    <Check className="w-10 h-10 stroke-[3]" />
                </div>
                <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-2 tracking-tight">Success!</h3>
                <p className="text-slate-500 dark:text-blue-200/60 font-medium text-lg">{message}</p>
            </div>
        </div>
    );
}
