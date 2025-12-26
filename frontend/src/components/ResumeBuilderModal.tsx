import { useState, useEffect, useRef } from 'react';
import { X, Upload, FileText, Check, ChevronRight, Download, Loader2, Layout, Search, Sparkles, RefreshCw, ArrowRight } from 'lucide-react';
import { getProfile, generateResume, analyzeResumeFile } from '@/lib/api';
import { DonutChart } from './DonutChart';

interface ResumeBuilderModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const TEMPLATES = [
    {
        id: 'modern',
        name: 'Modern Clean',
        description: 'Clean and professional layout suitable for tech and creative roles.',
        color: 'blue'
    },
    {
        id: 'classic',
        name: 'Classic Professional',
        description: 'Traditional layout perfect for corporate and executive positions.',
        color: 'slate'
    },
    {
        id: 'minimal',
        name: 'Minimalist',
        description: 'Simple and elegant design that focuses on your content.',
        color: 'gray'
    },
    {
        id: 'creative',
        name: 'Creative Portfolio',
        description: 'Vibrant and bold, perfect for designers and frontend developers.',
        color: 'purple'
    },
    {
        id: 'executive',
        name: 'Executive Suite',
        description: 'Serious, high-contrast design for senior leadership roles.',
        color: 'slate'
    }
];

// Helper Component for Preview
function ResumePreview({ templateId, userData }: { templateId: string, userData: any }) {
    if (!userData) return <div className="h-full w-full bg-slate-100 dark:bg-slate-800 animate-pulse rounded-lg" />;

    // Modern = Two Column Layout
    if (templateId === 'modern') {
        return (
            <div className="w-full h-full bg-white text-[6px] flex shadow-sm overflow-hidden select-none cursor-default font-sans">
                {/* Sidebar */}
                <div className="w-1/3 bg-slate-100 p-2 flex flex-col gap-2 border-r border-slate-200">
                    <div className="font-bold text-slate-800 uppercase tracking-widest mt-2 border-b border-slate-300 pb-0.5 mb-1">Contact</div>
                    <div className="text-slate-600 truncate">{userData.email}</div>
                    <div className="text-slate-600">{userData.location}</div>

                    <div className="font-bold text-slate-800 uppercase tracking-widest mt-4 border-b border-slate-300 pb-0.5 mb-1">Skills</div>
                    <div className="text-slate-600 leading-tight">
                        {userData.skills?.slice(0, 8).map((s: string) => <div key={s}>• {s}</div>)}
                    </div>

                    <div className="font-bold text-slate-800 uppercase tracking-widest mt-4 border-b border-slate-300 pb-0.5 mb-1">Education</div>
                    <div className="font-bold text-slate-700">B.Sc. Comp Sci</div>
                    <div className="text-slate-500">2020 - 2024</div>
                </div>
                {/* Main Content */}
                <div className="w-2/3 p-4 flex flex-col">
                    <div className="text-2xl font-bold text-slate-800 uppercase leading-none">{userData.full_name}</div>
                    <div className="text-slate-500 font-medium mb-4">{userData.job_title || 'Professional'}</div>

                    <div className="font-bold text-slate-800 uppercase tracking-widest border-b border-slate-300 pb-0.5 mb-1">Profile</div>
                    <p className="text-slate-600 mb-2 leading-tight">
                        Highly motivated professional with 5+ years of experience in designing and implementing scalable software solutions. Proficient in modern development methodologies with a focus on writing clean, maintainable code. Proven track record of collaborating with cross-functional teams to drive project success and innovation.
                    </p>

                    <div className="font-bold text-slate-800 uppercase tracking-widest border-b border-slate-300 pb-0.5 mb-1 mt-2">Experience</div>
                    <div className="font-bold text-slate-700">Senior Role</div>
                    <div className="text-slate-500 italic mb-1">2022 - Present</div>
                    <div className="text-slate-600 leading-tight mb-2">
                        • Led key initiatives and optimized performance.<br />
                        • Managed team of 5 developers.<br />
                        • Delivered project 2 weeks ahead of schedule.
                    </div>

                    <div className="font-bold text-slate-800 uppercase tracking-widest border-b border-slate-300 pb-0.5 mb-1 mt-2">Projects</div>
                    <div className="font-bold text-slate-700">AI Resume Builder</div>
                    <div className="text-slate-600 leading-tight">
                        • Built with React & FastAPI.<br />
                        • Implemented real-time PDF generation.
                    </div>
                </div>
            </div>
        )
    }

    // Classic / Default / Other Single Column Layouts
    const getStyles = () => {
        switch (templateId) {
            case 'classic': return { fontFamily: 'Times New Roman, serif', headerColor: 'text-[#0e4c92]', align: 'text-center', lineColor: 'border-[#0e4c92]' };
            case 'minimal': return { fontFamily: 'sans-serif', headerColor: 'text-black', align: 'text-left', lineColor: 'border-black' };
            case 'creative': return { fontFamily: 'sans-serif', headerColor: 'text-purple-600', align: 'text-center', lineColor: 'border-purple-200' }; // Purple center
            case 'executive': return { fontFamily: 'serif', headerColor: 'text-slate-900', align: 'text-left', lineColor: 'border-slate-800' };
            default: return { fontFamily: 'sans-serif', headerColor: 'text-blue-600', align: 'text-left', lineColor: 'border-blue-200' };
        }
    };

    const styles = getStyles();

    return (
        <div className="w-full h-full bg-white text-[6px] p-4 shadow-sm overflow-hidden select-none cursor-default flex flex-col" style={{ fontFamily: styles.fontFamily }}>
            {/* Header */}
            <div className={`font-bold text-lg mb-0.5 ${styles.headerColor} ${styles.align}`}>{userData.full_name || 'Your Name'}</div>
            <div className={`text-gray-500 mb-2 truncate ${styles.align}`}>
                {userData.email} | {userData.location}
            </div>

            {/* Minimal doesn't typically have a big divider, others might */}
            {templateId !== 'minimal' && <div className={`border-b mb-3 ${styles.lineColor}`}></div>}

            {/* Content Sections */}
            <div className={`font-bold mb-1 mt-1 uppercase tracking-wider ${styles.headerColor} ${templateId === 'classic' ? 'border-b ' + styles.lineColor : ''}`}>Summary</div>
            <p className="text-gray-600 mb-2 leading-relaxed text-justify">
                Dedicated professional with experience in {userData.experience_level || 'technology'}. Passionate about building great products. Committed to continuous learning and leveraging expertise to contribute effectively to organizational growth while upholding high standards of quality. Strong communicator and team player, ready to take on challenging roles in a dynamic environment.
            </p>

            <div className={`font-bold mb-1 mt-2 uppercase tracking-wider ${styles.headerColor} ${templateId === 'classic' ? 'border-b ' + styles.lineColor : ''}`}>Experience</div>
            <div className="mb-1">
                <div className="font-bold flex justify-between">
                    <span>Current Role</span>
                    <span className="font-normal italic text-gray-400">Present</span>
                </div>
                <div className="pl-3 mt-0.5 text-gray-600">
                    <div>• Analyze requirements and design solutions.</div>
                    <div>• Collaborate with stakeholders.</div>
                </div>
            </div>

            <div className={`font-bold mb-1 mt-2 uppercase tracking-wider ${styles.headerColor} ${templateId === 'classic' ? 'border-b ' + styles.lineColor : ''}`}>Projects</div>
            <div className="mb-1">
                <div className="font-bold">Project Name</div>
                <div className="pl-3 mt-0.5 text-gray-600">
                    <div>• Description of amazing project.</div>
                    <div>• Tech Stack: React, Node.js</div>
                </div>
            </div>

            <div className={`font-bold mb-1 mt-2 uppercase tracking-wider ${styles.headerColor} ${templateId === 'classic' ? 'border-b ' + styles.lineColor : ''}`}>Education</div>
            <div className="mb-1">
                <div className="font-bold">Degree Name</div>
                <div className="text-gray-500">University, 2024</div>
            </div>

            <div className={`font-bold mb-1 mt-2 uppercase tracking-wider ${styles.headerColor} ${templateId === 'classic' ? 'border-b ' + styles.lineColor : ''}`}>Skills</div>
            <div className="text-gray-600 pl-3">
                <div className="grid grid-cols-2 gap-x-2">
                    {userData.skills && userData.skills.length > 0 ? (
                        userData.skills.slice(0, 8).map((s: string) => <div key={s}>• {s}</div>)
                    ) : (
                        <>
                            <div>• Python</div>
                            <div>• React</div>
                            <div>• TypeScript</div>
                            <div>• FastAPI</div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}

export function ResumeBuilderModal({ isOpen, onClose }: ResumeBuilderModalProps) {
    const [mode, setMode] = useState<'build' | 'analyze' | null>(null); // 'build' or 'analyze'
    const [step, setStep] = useState(1);
    const [isLoading, setIsLoading] = useState(false);
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);
    const [selectedTemplate, setSelectedTemplate] = useState(TEMPLATES[0].id);
    const [userData, setUserData] = useState<any>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Analysis State
    const [analysisResult, setAnalysisResult] = useState<any>(null);

    useEffect(() => {
        if (isOpen) {
            loadUserData();
            setStep(1);
            setMode(null);
            setAnalysisResult(null);
            setUploadedFile(null);
        }
    }, [isOpen]);

    const loadUserData = async () => {
        try {
            const data = await getProfile();
            setUserData(data);
        } catch (e) {
            console.error("Failed to load user data", e);
        }
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setUploadedFile(file);

            if (mode === 'analyze') {
                setIsLoading(true);
                try {
                    const data = await analyzeResumeFile(file);
                    setAnalysisResult(data);
                } catch (error) {
                    console.error("Analysis failed", error);
                    alert("Failed to analyze resume.");
                } finally {
                    setIsLoading(false);
                }
            }
        }
    };

    const handleGenerate = async () => {
        setIsLoading(true);
        try {
            const formData = new FormData();
            // In build mode, we only support Profile Data now as requested? 
            // "remove the add Upload Existing Resume option from the resume builder Ai" 
            // So we assume generating from profile data.
            formData.append('template_id', selectedTemplate);

            const blob = await generateResume(formData);

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `resume_${userData?.full_name?.replace(/\s+/g, '_') || 'user'}_${selectedTemplate}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            onClose();
        } catch (error) {
            console.error('Error generating resume:', error);
            alert('Failed to generate resume. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl animate-in zoom-in-95 duration-200 flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-white/10">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-500/20 flex items-center justify-center text-blue-600 dark:text-blue-400">
                            <FileText className="w-6 h-6" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-slate-900 dark:text-white">AI Resume Assistant</h2>
                            <p className="text-sm text-slate-500 dark:text-blue-200/60">Build a new resume or analyze your existing one</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 text-slate-500 dark:text-blue-200/60 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 rounded-full transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 p-8">
                    {!mode ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
                            <button
                                onClick={() => { setMode('build'); setStep(2); }} // Skip step 1 (source selection) since we only support profile data now
                                className="flex flex-col items-center justify-center p-8 rounded-2xl border-2 border-slate-200 dark:border-white/10 hover:border-blue-500 dark:hover:border-blue-500 bg-slate-50 dark:bg-white/5 hover:bg-blue-50 dark:hover:bg-blue-500/10 transition-all group gap-4"
                            >
                                <div className="w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-500/20 flex items-center justify-center text-blue-600 dark:text-blue-400 group-hover:scale-110 transition-transform">
                                    <Layout className="w-8 h-8" />
                                </div>
                                <div className="text-center">
                                    <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Build Resume</h3>
                                    <p className="text-sm text-slate-500 dark:text-blue-200/60">Generate a professional resume using your profile data.</p>
                                </div>
                            </button>

                            <button
                                onClick={() => { setMode('analyze'); }}
                                className="flex flex-col items-center justify-center p-8 rounded-2xl border-2 border-slate-200 dark:border-white/10 hover:border-purple-500 dark:hover:border-purple-500 bg-slate-50 dark:bg-white/5 hover:bg-purple-50 dark:hover:bg-purple-500/10 transition-all group gap-4"
                            >
                                <div className="w-16 h-16 rounded-full bg-purple-100 dark:bg-purple-500/20 flex items-center justify-center text-purple-600 dark:text-purple-400 group-hover:scale-110 transition-transform">
                                    <Search className="w-8 h-8" />
                                </div>
                                <div className="text-center">
                                    <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Resume Analyzer</h3>
                                    <p className="text-sm text-slate-500 dark:text-blue-200/60">Get an ATS score and insights for your existing resume.</p>
                                </div>
                            </button>
                        </div>
                    ) : mode === 'analyze' ? (
                        <div className="max-w-2xl mx-auto space-y-8 animate-in slide-in-from-right-4">
                            <div className="flex items-center gap-2 mb-4">
                                <button onClick={() => setMode(null)} className="flex items-center text-sm text-slate-500 hover:text-slate-900 dark:text-blue-200/60 dark:hover:text-white">
                                    Back
                                </button>
                                <span className="text-slate-300">/</span>
                                <span className="text-sm font-medium text-slate-900 dark:text-white">Resume Analyzer</span>
                            </div>

                            <div className="border-2 border-dashed border-slate-200 dark:border-white/10 rounded-2xl p-10 flex flex-col items-center justify-center text-center">
                                {isLoading ? (
                                    <div className="flex flex-col items-center">
                                        <Loader2 className="w-10 h-10 text-purple-500 animate-spin mb-4" />
                                        <p className="text-lg font-medium text-slate-900 dark:text-white">Analyzing your resume...</p>
                                        <p className="text-sm text-slate-500">This might take a few seconds</p>
                                    </div>
                                ) : analysisResult ? (
                                    <div className="w-full space-y-6">
                                        <div className="flex flex-col items-center">
                                            <DonutChart score={analysisResult.score} size={140} strokeWidth={8} />
                                            <h3 className="text-2xl font-bold text-slate-900 dark:text-white mt-4">ATS Score</h3>
                                        </div>

                                        <div className="bg-slate-50 dark:bg-white/5 rounded-xl p-6 text-left">
                                            <h4 className="font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                                                <Sparkles className="w-5 h-5 text-purple-500" /> Key Insights
                                            </h4>
                                            <div className="space-y-4">
                                                <div>
                                                    <p className="text-sm font-medium text-slate-700 dark:text-blue-200 mb-2">Improvements Needed:</p>
                                                    <ul className="space-y-2">
                                                        {analysisResult.breakdown?.slice(0, 5).map((point: string, i: number) => (
                                                            <li key={i} className="flex gap-2 text-sm text-slate-600 dark:text-blue-200/80">
                                                                <span className="text-red-500 mt-0.5">•</span>
                                                                {point}
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            </div>
                                        </div>

                                        <button
                                            onClick={() => { setAnalysisResult(null); setUploadedFile(null); }}
                                            className="px-6 py-2 bg-slate-100 dark:bg-white/10 hover:bg-slate-200 text-slate-900 dark:text-white rounded-lg text-sm font-medium transition-colors"
                                        >
                                            Analyze Another Resume
                                        </button>
                                    </div>
                                ) : (
                                    <>
                                        <div className="w-16 h-16 bg-purple-100 dark:bg-purple-500/20 rounded-full flex items-center justify-center text-purple-600 dark:text-purple-400 mb-4">
                                            <Upload className="w-8 h-8" />
                                        </div>
                                        <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Upload your Resume</h3>
                                        <p className="text-slate-500 dark:text-blue-200/60 mb-6 max-w-md">
                                            Upload a PDF or DOCX file to get an instant ATS compatibility score and personalized improvement suggestions.
                                        </p>
                                        <button
                                            onClick={() => fileInputRef.current?.click()}
                                            className="px-8 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-xl transition-all hover:scale-105 shadow-lg shadow-purple-500/25"
                                        >
                                            Select File
                                        </button>
                                        <p className="mt-4 text-xs text-slate-400">Supported formats: PDF, DOCX (Max 5MB)</p>
                                    </>
                                )}
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    className="hidden"
                                    accept=".pdf,.docx,.doc"
                                    onChange={handleFileUpload}
                                />
                            </div>
                        </div>
                    ) : (
                        // Build Mode (Existing Logic Logic but skipping source selection)
                        <div className="space-y-6 animate-in slide-in-from-right-4 duration-300">
                            <div className="flex items-center gap-2 mb-4">
                                <button onClick={() => setMode(null)} className="flex items-center text-sm text-slate-500 hover:text-slate-900 dark:text-blue-200/60 dark:hover:text-white">
                                    Back
                                </button>
                                <span className="text-slate-300">/</span>
                                <span className="text-sm font-medium text-slate-900 dark:text-white">Build Resume</span>
                            </div>

                            {/* Progress Indicator for Build Mode */}
                            <div className="flex items-center justify-center mb-8">
                                <div className={`flex items-center gap-2 ${step >= 2 ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400'}`}>
                                    <div className="w-8 h-8 rounded-full border-2 border-current flex items-center justify-center font-bold">1</div>
                                    <span className="font-medium">Template</span>
                                </div>
                                <div className={`w-12 h-0.5 mx-4 ${step >= 3 ? 'bg-blue-600 dark:bg-blue-400' : 'bg-slate-200 dark:bg-white/10'}`}></div>
                                <div className={`flex items-center gap-2 ${step >= 3 ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400'}`}>
                                    <div className="w-8 h-8 rounded-full border-2 border-current flex items-center justify-center font-bold">2</div>
                                    <span className="font-medium">Generate</span>
                                </div>
                            </div>

                            {step === 2 && (
                                <div className="space-y-6">
                                    <div className="text-center mb-6">
                                        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Choose a Template</h3>
                                        <p className="text-slate-500 dark:text-blue-200/60">Select a professional design for your resume.</p>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                        {TEMPLATES.map((template) => (
                                            <div
                                                key={template.id}
                                                onClick={() => setSelectedTemplate(template.id)}
                                                className={`cursor-pointer rounded-xl border-2 transition-all overflow-hidden relative group ${selectedTemplate === template.id ? 'border-blue-500 ring-4 ring-blue-500/10' : 'border-slate-200 dark:border-white/10 hover:border-blue-300'}`}
                                            >
                                                <div className="aspect-[1/1.4] bg-slate-100 dark:bg-slate-800 relative overflow-hidden rounded-t-lg">
                                                    {/* Live Template Preview */}
                                                    <div className="absolute inset-0 transform scale-[1] origin-top p-0">
                                                        <ResumePreview templateId={template.id} userData={userData || { full_name: 'John Doe', email: 'john@example.com' }} />
                                                    </div>

                                                    {selectedTemplate === template.id && (
                                                        <div className="absolute inset-0 bg-blue-500/10 flex items-center justify-center">
                                                            <div className="bg-blue-500 text-white p-2 rounded-full shadow-lg">
                                                                <Check className="w-6 h-6" />
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                                <div className="p-4 bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-white/5">
                                                    <h4 className="font-semibold text-slate-900 dark:text-white">{template.name}</h4>
                                                    <p className="text-xs text-slate-500 mt-1">{template.description}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>

                                    <div className="flex justify-between mt-8">
                                        <button
                                            onClick={() => setMode(null)}
                                            className="text-slate-500 hover:text-slate-700 dark:text-blue-200/60 dark:hover:text-white font-medium"
                                        >
                                            Back to Menu
                                        </button>
                                        <button
                                            onClick={() => setStep(3)}
                                            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors"
                                        >
                                            Review & Generate <ChevronRight className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            )}

                            {step === 3 && (
                                <div className="space-y-6 max-w-2xl mx-auto">
                                    <div className="text-center mb-8">
                                        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Ready to Build?</h3>
                                        <p className="text-slate-500 dark:text-blue-200/60">We'll generate a PDF resume based on your profile and selections.</p>
                                    </div>

                                    <div className="bg-slate-50 dark:bg-white/5 rounded-xl p-6 border border-slate-200 dark:border-white/10 space-y-4">
                                        <div className="flex justify-between items-center pb-4 border-b border-slate-200 dark:border-white/10">
                                            <span className="text-slate-600 dark:text-blue-200/80">Selected Template</span>
                                            <span className="font-medium text-slate-900 dark:text-white">
                                                {TEMPLATES.find(t => t.id === selectedTemplate)?.name}
                                            </span>
                                        </div>
                                        <div className="flex justify-between items-center pb-4 border-b border-slate-200 dark:border-white/10">
                                            <span className="text-slate-600 dark:text-blue-200/80">Data Source</span>
                                            <span className="font-medium text-slate-900 dark:text-white">
                                                Profile Data Only
                                            </span>
                                        </div>
                                    </div>

                                    <div className="flex justify-between mt-8">
                                        <button
                                            onClick={() => setStep(2)}
                                            className="text-slate-500 hover:text-slate-700 dark:text-blue-200/60 dark:hover:text-white font-medium"
                                        >
                                            Back
                                        </button>
                                        <button
                                            onClick={handleGenerate}
                                            disabled={isLoading}
                                            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-bold shadow-lg shadow-blue-500/25 transition-all hover:scale-105 disabled:opacity-70 disabled:hover:scale-100"
                                        >
                                            {isLoading ? (
                                                <>
                                                    <Loader2 className="w-5 h-5 animate-spin" />
                                                    Building...
                                                </>
                                            ) : (
                                                <>
                                                    <Download className="w-5 h-5" />
                                                    Generate PDF Resume
                                                </>
                                            )}
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
