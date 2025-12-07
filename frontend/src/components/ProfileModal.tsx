import { User, Briefcase, MapPin, FileText, X, Upload, Plus, GraduationCap, Github, Linkedin, Globe, Trash2, Building, Save, Edit2 } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { POPULAR_JOB_TITLES, POPULAR_LOCATIONS, POPULAR_SKILLS } from '@/lib/constants';
import { getProfile, updateProfile } from '@/lib/api';
import { ImageCropper } from './ImageCropper';

interface ProfileModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export const EXPERIENCE_LEVELS = [
    "Fresher",
    "Internship",
    "Associate",
    "Senior",
    "Lead",
    "Executive"
];

interface TagInputProps {
    label: string;
    icon?: React.ReactNode;
    tags: string[];
    onAddTag: (tag: string) => void;
    onRemoveTag: (tag: string) => void;
    suggestions: string[];
    placeholder: string;
}

function TagInput({ label, icon, tags, onAddTag, onRemoveTag, suggestions, placeholder }: TagInputProps) {
    const [input, setInput] = useState("");
    const [showSuggestions, setShowSuggestions] = useState(false);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (input.trim()) {
                onAddTag(input.trim());
                setInput("");
                setShowSuggestions(false);
            }
        }
    };

    const filteredSuggestions = suggestions.filter(s =>
        s.toLowerCase().includes(input.toLowerCase()) && !tags.includes(s)
    ).slice(0, 5);

    return (
        <div className="space-y-2">
            <label className="block text-sm font-medium text-slate-700 dark:text-blue-200/60 mb-1 flex items-center">
                {icon}
                {label}
            </label>

            <div className="flex flex-wrap gap-2 mb-2">
                {tags.map((tag, index) => (
                    <span key={index} className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-200 border border-blue-200 dark:border-blue-500/30">
                        {tag}
                        <button
                            type="button"
                            onClick={() => onRemoveTag(tag)}
                            className="ml-1.5 hover:text-blue-900 dark:hover:text-white focus:outline-none"
                        >
                            <X className="w-3 h-3" />
                        </button>
                    </span>
                ))}
            </div>

            <div className="relative">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => {
                        setInput(e.target.value);
                        setShowSuggestions(true);
                    }}
                    onKeyDown={handleKeyDown}
                    onFocus={() => setShowSuggestions(true)}
                    onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                    className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-500"
                    placeholder={placeholder}
                />
                {showSuggestions && input && filteredSuggestions.length > 0 && (
                    <div className="absolute z-20 w-full mt-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-lg shadow-xl max-h-48 overflow-y-auto">
                        {filteredSuggestions.map((suggestion) => (
                            <button
                                key={suggestion}
                                type="button"
                                onClick={() => {
                                    onAddTag(suggestion);
                                    setInput("");
                                    setShowSuggestions(false);
                                }}
                                className="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-blue-100 hover:bg-slate-100 dark:hover:bg-white/10 transition-colors flex items-center justify-between group"
                            >
                                {suggestion}
                                <Plus className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

interface Education {
    id: string;
    school: string;
    degree: string;
    field: string;
    startDate: string;
    endDate: string;
    grade: string;
    isEditing?: boolean;
}

interface Experience {
    id: string;
    company: string;
    role: string;
    location: string;
    startDate: string;
    endDate: string;
    description: string;
    logo: string | null;
    isEditing?: boolean;
}

interface Project {
    id: string;
    name: string;
    role: string;
    duration: string;
    technologies: string[];
    description: string;
    link: string;
}

export function ProfileModal({ isOpen, onClose }: ProfileModalProps) {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        address: '',
        location: '',
        skills: [] as string[],
        experience: '',
        experienceLevel: 'Fresher',
        jobPreferences: [] as string[],
        preferredLocations: [] as string[],
        resume: null as File | null,
        avatarType: 'emoji' as 'emoji' | 'image',
        avatarEmoji: '👨‍💻',
        avatarImage: null as string | null,
        githubUrl: '',
        linkedinUrl: '',
        portfolioUrl: '',
        education: [] as Education[],
        workExperience: [] as Experience[],
        projects: [] as Project[]
    });

    // Load from API on mount
    useEffect(() => {
        const fetchProfile = async () => {
            if (!isOpen) return;
            try {
                const user = await getProfile();

                // Ensure education items have IDs
                const educationWithIds = (user.education || []).map((edu: any) => ({
                    ...edu,
                    id: edu.id || Date.now().toString() + Math.random(),
                    isEditing: false
                }));

                // Ensure experience items have IDs
                const experienceWithIds = (user.experience || []).map((exp: any) => ({
                    ...exp,
                    id: exp.id || Date.now().toString() + Math.random(),
                    isEditing: false
                }));

                // Ensure project items have IDs
                const projectsWithIds = (user.projects || []).map((proj: any) => ({
                    ...proj,
                    id: proj.id || Date.now().toString() + Math.random()
                }));

                setFormData(prev => ({
                    ...prev,
                    name: user.full_name || '',
                    email: user.email || '',
                    address: user.address || '',
                    location: user.location || '',
                    experienceLevel: user.experience_level || 'Fresher',
                    skills: user.skills || [],
                    avatarImage: user.avatar || null,
                    avatarType: user.avatar ? 'image' : 'emoji',
                    education: educationWithIds,
                    workExperience: experienceWithIds,
                    jobPreferences: user.job_preferences || [],
                    projects: projectsWithIds
                }));
            } catch (e) {
                console.error("Failed to fetch profile", e);
                // Fallback to local storage if API fails
                const savedProfile = localStorage.getItem('userProfile');
                if (savedProfile) {
                    try {
                        const parsed = JSON.parse(savedProfile);
                        setFormData(prev => ({ ...prev, ...parsed }));
                    } catch (e) { }
                }
            }
        };
        fetchProfile();
    }, [isOpen]);

    const saveToStorage = (data: typeof formData) => {
        // Exclude file objects from storage as they can't be serialized
        const { resume, ...storageData } = data;
        localStorage.setItem('userProfile', JSON.stringify(storageData));
        // Dispatch a custom event so other components (like NotificationPanel) know profile updated
        window.dispatchEvent(new Event('profileUpdated'));
    };

    const fileInputRef = useRef<HTMLInputElement>(null);
    const imageInputRef = useRef<HTMLInputElement>(null);
    const companyLogoInputRef = useRef<HTMLInputElement>(null);
    const [activeExperienceId, setActiveExperienceId] = useState<string | null>(null);
    const [cropImage, setCropImage] = useState<string | null>(null);

    if (!isOpen) return null;

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFormData(prev => ({ ...prev, resume: e.target.files![0] }));
        }
    };

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const reader = new FileReader();
            reader.onload = (event) => {
                setCropImage(event.target?.result as string);
                // Reset file input so same file can be selected again if needed
                if (imageInputRef.current) imageInputRef.current.value = '';
            };
            reader.readAsDataURL(e.target.files[0]);
        }
    };

    const handleCropComplete = (croppedImage: string) => {
        setFormData(prev => ({ ...prev, avatarImage: croppedImage, avatarType: 'image' }));
        setCropImage(null);
    };

    const handleCropCancel = () => {
        setCropImage(null);
    };

    const addTag = (field: 'skills' | 'jobPreferences' | 'preferredLocations', tag: string) => {
        if (!formData[field].includes(tag)) {
            setFormData(prev => ({ ...prev, [field]: [...prev[field], tag] }));
        }
    };

    const removeTag = (field: 'skills' | 'jobPreferences' | 'preferredLocations', tag: string) => {
        setFormData(prev => ({ ...prev, [field]: prev[field].filter(t => t !== tag) }));
    };

    // Education Handlers
    const addEducation = () => {
        const newEducation: Education = {
            id: Date.now().toString(),
            school: '',
            degree: '',
            field: '',
            startDate: '',
            endDate: '',
            grade: '',
            isEditing: true
        };
        setFormData(prev => ({ ...prev, education: [...prev.education, newEducation] }));
    };

    const updateEducation = (id: string, field: keyof Education, value: string) => {
        setFormData(prev => ({
            ...prev,
            education: prev.education.map(edu => edu.id === id ? { ...edu, [field]: value } : edu)
        }));
    };

    const removeEducation = (id: string) => {
        setFormData(prev => ({ ...prev, education: prev.education.filter(edu => edu.id !== id) }));
    };

    const toggleEducationEdit = (id: string) => {
        setFormData(prev => ({
            ...prev,
            education: prev.education.map(edu =>
                edu.id === id ? { ...edu, isEditing: !edu.isEditing } : edu
            )
        }));
    };

    // Experience Handlers
    const addExperience = () => {
        const newExperience: Experience = {
            id: Date.now().toString(),
            company: '',
            role: '',
            location: '',
            startDate: '',
            endDate: '',
            description: '',
            logo: null,
            isEditing: true
        };
        setFormData(prev => ({ ...prev, workExperience: [...prev.workExperience, newExperience] }));
    };

    const updateExperience = (id: string, field: keyof Experience, value: any) => {
        setFormData(prev => ({
            ...prev,
            workExperience: prev.workExperience.map(exp => {
                if (exp.id === id) {
                    const updatedExp = { ...exp, [field]: value };

                    // Auto-fetch logo if company name changes
                    if (field === 'company' && typeof value === 'string' && value.length > 2) {
                        // Simple debounce could be added here, but for now we'll just try to fetch
                        const domain = value.toLowerCase().replace(/\s+/g, '') + '.com';
                        const logoUrl = `https://logo.clearbit.com/${domain}`;
                        // We don't await here, just set it optimistically. 
                        // In a real app, we might want to verify the image exists.
                        // For this demo, we'll set it and let the img tag handle errors (or not show if broken).
                        updatedExp.logo = logoUrl;
                    }
                    return updatedExp;
                }
                return exp;
            })
        }));
    };

    const toggleExperienceEdit = (id: string) => {
        setFormData(prev => ({
            ...prev,
            workExperience: prev.workExperience.map(exp =>
                exp.id === id ? { ...exp, isEditing: !exp.isEditing } : exp
            )
        }));
    };

    const removeExperience = (id: string) => {
        setFormData(prev => ({ ...prev, workExperience: prev.workExperience.filter(exp => exp.id !== id) }));
    };

    const handleCompanyLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0] && activeExperienceId) {
            const reader = new FileReader();
            reader.onload = (event) => {
                setFormData(prev => ({
                    ...prev,
                    workExperience: prev.workExperience.map(exp =>
                        exp.id === activeExperienceId ? { ...exp, logo: event.target?.result as string } : exp
                    )
                }));
            };
            reader.readAsDataURL(e.target.files[0]);
        }
    };

    // Project handlers
    const addProject = () => {
        const newProject: Project = {
            id: Date.now().toString(),
            name: '',
            role: '',
            duration: '',
            technologies: [],
            description: '',
            link: ''
        };
        setFormData(prev => ({ ...prev, projects: [...prev.projects, newProject] }));
    };

    const updateProject = (id: string, field: keyof Project, value: any) => {
        setFormData(prev => ({
            ...prev,
            projects: prev.projects.map(proj =>
                proj.id === id ? { ...proj, [field]: value } : proj
            )
        }));
    };

    const removeProject = (id: string) => {
        setFormData(prev => ({ ...prev, projects: prev.projects.filter(proj => proj.id !== id) }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        console.log('Submitting profile update...');
        try {
            const updateData = {
                full_name: formData.name,
                address: formData.address,
                location: formData.location,
                experience_level: formData.experienceLevel,
                skills: formData.skills,
                avatar: formData.avatarType === 'image' ? (formData.avatarImage || undefined) : undefined,

                education: formData.education.map(({ isEditing, ...rest }) => rest), // Remove UI flags
                experience: formData.workExperience.map(({ isEditing, ...rest }) => rest), // Remove UI flags
                job_preferences: formData.jobPreferences,
                projects: formData.projects
            };

            console.log('Update data:', updateData);
            const result = await updateProfile(updateData);
            console.log('Profile update result:', result);

            // Also save to local storage for offline/fallback
            saveToStorage(formData);
            alert("Profile updated successfully!");
            onClose();
        } catch (e: any) {
            console.error("Failed to update profile", e);
            const errorMessage = e?.response?.data?.detail || e?.message || "Unknown error occurred";
            alert(`Failed to update profile: ${errorMessage}\n\nPlease check the console for more details.`);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            {cropImage && (
                <ImageCropper
                    imageSrc={cropImage}
                    onCropComplete={handleCropComplete}
                    onCancel={handleCropCancel}
                />
            )}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-white/10 rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl animate-in zoom-in-95 duration-200">
                <div className="sticky top-0 z-10 flex items-center justify-between p-6 bg-white/95 dark:bg-slate-900/95 backdrop-blur border-b border-slate-200 dark:border-white/10">
                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Complete Your Profile</h2>
                    <button onClick={onClose} className="p-2 text-slate-500 dark:text-blue-200/60 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/10 rounded-full transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-8">
                    {/* Top Section: Avatar & Basic Info */}
                    <div className="flex flex-col md:flex-row gap-8 items-start">
                        {/* Avatar Section */}
                        <div className="flex flex-col items-center space-y-6 w-full md:w-auto">
                            <div className="relative group">
                                <div className="w-32 h-32 rounded-full bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-500/20 dark:to-purple-500/20 border-4 border-white dark:border-slate-900 ring-2 ring-blue-500/30 flex items-center justify-center overflow-hidden shadow-2xl">
                                    {formData.avatarType === 'emoji' ? (
                                        <span className="text-6xl animate-in zoom-in duration-300">{formData.avatarEmoji}</span>
                                    ) : formData.avatarImage ? (
                                        <img src={formData.avatarImage} alt="Profile" className="w-full h-full object-cover" />
                                    ) : (
                                        <User className="w-16 h-16 text-slate-400 dark:text-blue-200/40" />
                                    )}

                                    <div
                                        className="absolute inset-0 bg-black/60 flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-200 cursor-pointer backdrop-blur-sm"
                                        onClick={() => imageInputRef.current?.click()}
                                    >
                                        <Upload className="w-8 h-8 text-white mb-2" />
                                        <span className="text-xs font-medium text-white">Change Photo</span>
                                    </div>
                                </div>
                                <div className="absolute bottom-2 right-2 w-5 h-5 bg-green-500 border-4 border-white dark:border-slate-900 rounded-full"></div>
                            </div>

                            <div className="flex flex-col items-center gap-4 w-full max-w-xs">
                                <div className="flex p-1 bg-slate-100 dark:bg-white/5 rounded-xl border border-slate-200 dark:border-white/10 w-full">
                                    <button
                                        type="button"
                                        onClick={() => setFormData(prev => ({ ...prev, avatarType: 'emoji' }))}
                                        className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${formData.avatarType === 'emoji' ? 'bg-white dark:bg-blue-600 text-blue-600 dark:text-white shadow-sm' : 'text-slate-500 dark:text-blue-200/60 hover:text-slate-900 dark:hover:text-white'}`}
                                    >
                                        Emoji
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setFormData(prev => ({ ...prev, avatarType: 'image' }));
                                            if (!formData.avatarImage) imageInputRef.current?.click();
                                        }}
                                        className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${formData.avatarType === 'image' ? 'bg-white dark:bg-blue-600 text-blue-600 dark:text-white shadow-sm' : 'text-slate-500 dark:text-blue-200/60 hover:text-slate-900 dark:hover:text-white'}`}
                                    >
                                        Image
                                    </button>
                                </div>

                                {formData.avatarType === 'emoji' && (
                                    <div className="flex gap-2 overflow-x-auto pb-2 w-full justify-center no-scrollbar">
                                        {['👨‍💻', '👩‍💻', '🚀', '⚡', '💼', '🎓', '🦄', '🤖'].map(emoji => (
                                            <button
                                                key={emoji}
                                                type="button"
                                                onClick={() => setFormData(prev => ({ ...prev, avatarEmoji: emoji }))}
                                                className={`w-10 h-10 flex items-center justify-center text-xl rounded-full transition-all ${formData.avatarEmoji === emoji ? 'bg-blue-100 dark:bg-blue-500/20 border-2 border-blue-500 scale-110' : 'hover:bg-slate-100 dark:hover:bg-white/5 border border-transparent'}`}
                                            >
                                                {emoji}
                                            </button>
                                        ))}
                                    </div>
                                )}
                                <input
                                    type="file"
                                    ref={imageInputRef}
                                    className="hidden"
                                    accept="image/*"
                                    onChange={(e) => {
                                        setFormData(prev => ({ ...prev, avatarType: 'image' }));
                                        handleImageChange(e);
                                    }}
                                />
                            </div>
                        </div>

                        {/* Personal & Professional Info Grid */}
                        <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
                            {/* Personal Info */}
                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold text-slate-800 dark:text-blue-200 flex items-center">
                                    <User className="w-4 h-4 mr-2" /> Personal Details
                                </h3>
                                <div className="space-y-3">
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 dark:text-blue-200/60 mb-1">Full Name</label>
                                        <input
                                            type="text"
                                            name="name"
                                            value={formData.name}
                                            onChange={handleInputChange}
                                            className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-500"
                                            placeholder="John Doe"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 dark:text-blue-200/60 mb-1">Email Address</label>
                                        <input
                                            type="email"
                                            name="email"
                                            value={formData.email}
                                            onChange={handleInputChange}
                                            className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-500"
                                            placeholder="john@example.com"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 dark:text-blue-200/60 mb-1">Address</label>
                                        <input
                                            type="text"
                                            name="address"
                                            value={formData.address}
                                            onChange={handleInputChange}
                                            className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-500"
                                            placeholder="123 Main St, Apt 4B"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 dark:text-blue-200/60 mb-1">Current Location</label>
                                        <input
                                            type="text"
                                            name="location"
                                            value={formData.location}
                                            onChange={handleInputChange}
                                            className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-500"
                                            placeholder="City, Country"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Professional Info */}
                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold text-slate-800 dark:text-blue-200 flex items-center">
                                    <Briefcase className="w-4 h-4 mr-2" /> Professional Info
                                </h3>
                                <div className="space-y-3">
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 dark:text-blue-200/60 mb-1">Experience Level</label>
                                        <select
                                            name="experienceLevel"
                                            value={formData.experienceLevel}
                                            onChange={handleInputChange}
                                            className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 outline-none transition-all appearance-none"
                                        >
                                            {EXPERIENCE_LEVELS.map(level => (
                                                <option key={level} value={level} className="bg-white dark:bg-slate-900">{level}</option>
                                            ))}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 dark:text-blue-200/60 mb-1">Total Experience</label>
                                        <input
                                            type="text"
                                            name="experience"
                                            value={formData.experience}
                                            onChange={handleInputChange}
                                            className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-500"
                                            placeholder="e.g. 2 years"
                                        />
                                    </div>
                                    <TagInput
                                        label="Skills"
                                        tags={formData.skills}
                                        onAddTag={(tag) => addTag('skills', tag)}
                                        onRemoveTag={(tag) => removeTag('skills', tag)}
                                        suggestions={POPULAR_SKILLS}
                                        placeholder="Type skill & press Enter"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Social Links Section */}
                    <div className="space-y-4 pt-4 border-t border-slate-200 dark:border-white/5">
                        <h3 className="text-lg font-semibold text-slate-800 dark:text-blue-200 flex items-center">
                            <Globe className="w-4 h-4 mr-2" /> Social Links
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-blue-200/60 mb-1 flex items-center gap-2">
                                    <Github className="w-3 h-3" /> GitHub URL
                                </label>
                                <input
                                    type="url"
                                    name="githubUrl"
                                    value={formData.githubUrl}
                                    onChange={handleInputChange}
                                    className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-500"
                                    placeholder="https://github.com/username"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-blue-200/60 mb-1 flex items-center gap-2">
                                    <Linkedin className="w-3 h-3" /> LinkedIn URL
                                </label>
                                <input
                                    type="url"
                                    name="linkedinUrl"
                                    value={formData.linkedinUrl}
                                    onChange={handleInputChange}
                                    className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-500"
                                    placeholder="https://linkedin.com/in/username"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 dark:text-blue-200/60 mb-1 flex items-center gap-2">
                                    <Globe className="w-3 h-3" /> Portfolio URL
                                </label>
                                <input
                                    type="url"
                                    name="portfolioUrl"
                                    value={formData.portfolioUrl}
                                    onChange={handleInputChange}
                                    className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 outline-none transition-all placeholder:text-slate-400 dark:placeholder:text-slate-500"
                                    placeholder="https://portfolio.com"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Education Section */}
                    <div className="space-y-4 pt-4 border-t border-slate-200 dark:border-white/5">
                        <div className="flex items-center justify-between">
                            <h3 className="text-lg font-semibold text-slate-800 dark:text-blue-200 flex items-center">
                                <GraduationCap className="w-4 h-4 mr-2" /> Education
                            </h3>
                            <button
                                type="button"
                                onClick={addEducation}
                                className="text-xs flex items-center gap-1 bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-300 px-3 py-1.5 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-500/20 transition-colors border border-blue-200 dark:border-blue-500/20"
                            >
                                <Plus className="w-3 h-3" /> Add Education
                            </button>
                        </div>

                        <div className="space-y-4">
                            {formData.education.map((edu, index) => (
                                <div key={edu.id} className="p-4 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl space-y-4 relative group">
                                    <div className="absolute top-4 right-4 flex gap-2 z-10">
                                        <button
                                            type="button"
                                            onClick={() => toggleEducationEdit(edu.id)}
                                            className="text-slate-400 dark:text-blue-200/40 hover:text-blue-500 transition-colors"
                                            title={edu.isEditing ? "Save" : "Edit"}
                                        >
                                            {edu.isEditing ? <Save className="w-4 h-4" /> : <Edit2 className="w-4 h-4" />}
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => removeEducation(edu.id)}
                                            className="text-red-400/60 hover:text-red-500 transition-colors"
                                            title="Delete"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>

                                    {edu.isEditing ? (
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">School / University</label>
                                                <input
                                                    type="text"
                                                    value={edu.school}
                                                    onChange={(e) => updateEducation(edu.id, 'school', e.target.value)}
                                                    className="w-full bg-white dark:bg-black/20 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-blue-500/50 outline-none"
                                                    placeholder="University Name"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">Degree</label>
                                                <input
                                                    type="text"
                                                    value={edu.degree}
                                                    onChange={(e) => updateEducation(edu.id, 'degree', e.target.value)}
                                                    className="w-full bg-white dark:bg-black/20 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-blue-500/50 outline-none"
                                                    placeholder="e.g. Bachelor's"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">Field of Study</label>
                                                <input
                                                    type="text"
                                                    value={edu.field}
                                                    onChange={(e) => updateEducation(edu.id, 'field', e.target.value)}
                                                    className="w-full bg-white dark:bg-black/20 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-blue-500/50 outline-none"
                                                    placeholder="e.g. Computer Science"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">Grade / Score</label>
                                                <input
                                                    type="text"
                                                    value={edu.grade}
                                                    onChange={(e) => updateEducation(edu.id, 'grade', e.target.value)}
                                                    className="w-full bg-white dark:bg-black/20 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-blue-500/50 outline-none"
                                                    placeholder="e.g. 3.8 GPA"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">Start Date</label>
                                                <input
                                                    type="date"
                                                    value={edu.startDate}
                                                    onChange={(e) => updateEducation(edu.id, 'startDate', e.target.value)}
                                                    className="w-full bg-white dark:bg-black/20 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-blue-500/50 outline-none"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">End Date</label>
                                                <input
                                                    type="date"
                                                    value={edu.endDate}
                                                    onChange={(e) => updateEducation(edu.id, 'endDate', e.target.value)}
                                                    className="w-full bg-white dark:bg-black/20 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-blue-500/50 outline-none"
                                                />
                                            </div>
                                            <div className="md:col-span-2 flex justify-end">
                                                <button
                                                    type="button"
                                                    onClick={() => toggleEducationEdit(edu.id)}
                                                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors"
                                                >
                                                    <Save className="w-4 h-4" /> Save Education
                                                </button>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="space-y-1">
                                            <h4 className="text-lg font-semibold text-slate-900 dark:text-white">{edu.school || 'School'}</h4>
                                            <p className="text-sm font-medium text-blue-600 dark:text-blue-400">{edu.degree || 'Degree'} {edu.field ? `in ${edu.field}` : ''}</p>
                                            <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-blue-200/60">
                                                <span>{edu.startDate || 'Start'} - {edu.endDate || 'End'}</span>
                                                {edu.grade && (
                                                    <>
                                                        <span>•</span>
                                                        <span>Grade: {edu.grade}</span>
                                                    </>
                                                )}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                            {formData.education.length === 0 && (
                                <div className="text-center py-8 border border-dashed border-slate-200 dark:border-white/10 rounded-xl bg-slate-50 dark:bg-white/5">
                                    <p className="text-sm text-slate-500 dark:text-blue-200/40">No education details added yet</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Work Experience Section */}
                    <div className="space-y-4 pt-4 border-t border-slate-200 dark:border-white/5">
                        <div className="flex items-center justify-between">
                            <h3 className="text-lg font-semibold text-slate-800 dark:text-blue-200 flex items-center">
                                <Building className="w-4 h-4 mr-2" /> Work Experience & Internships
                            </h3>
                            <button
                                type="button"
                                onClick={addExperience}
                                className="text-xs flex items-center gap-1 bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-300 px-3 py-1.5 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-500/20 transition-colors border border-blue-200 dark:border-blue-500/20"
                            >
                                <Plus className="w-3 h-3" /> Add Experience
                            </button>
                        </div>

                        <div className="space-y-4">
                            {formData.workExperience.map((exp, index) => (
                                <div key={exp.id} className="p-4 bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl space-y-4 relative group">
                                    <div className="absolute top-4 right-4 flex gap-2 z-10">
                                        <button
                                            type="button"
                                            onClick={() => toggleExperienceEdit(exp.id)}
                                            className="text-slate-400 dark:text-blue-200/40 hover:text-blue-500 transition-colors"
                                            title={exp.isEditing ? "Save" : "Edit"}
                                        >
                                            {exp.isEditing ? <Save className="w-4 h-4" /> : <Edit2 className="w-4 h-4" />}
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => removeExperience(exp.id)}
                                            className="text-red-400/60 hover:text-red-500 transition-colors"
                                            title="Delete"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>

                                    <div className="flex gap-4">
                                        {/* Company Logo Upload */}
                                        <div
                                            className="w-16 h-16 flex-shrink-0 rounded-lg bg-white dark:bg-black/30 border border-slate-200 dark:border-white/10 flex items-center justify-center cursor-pointer hover:border-blue-500/50 transition-colors overflow-hidden relative group/logo"
                                            onClick={() => {
                                                if (exp.isEditing) {
                                                    setActiveExperienceId(exp.id);
                                                    companyLogoInputRef.current?.click();
                                                }
                                            }}
                                        >
                                            {exp.logo ? (
                                                <img src={exp.logo} alt="Company Logo" className="w-full h-full object-cover" onError={(e) => {
                                                    // Fallback if image fails
                                                    (e.target as HTMLImageElement).style.display = 'none';
                                                    (e.target as HTMLImageElement).parentElement!.classList.add('fallback-icon');
                                                }} />
                                            ) : (
                                                <Building className="w-6 h-6 text-slate-300 dark:text-blue-200/20" />
                                            )}
                                            {exp.isEditing && (
                                                <div className="absolute inset-0 bg-black/60 flex items-center justify-center opacity-0 group-hover/logo:opacity-100 transition-opacity">
                                                    <Upload className="w-4 h-4 text-white" />
                                                </div>
                                            )}
                                        </div>

                                        <div className="flex-1">
                                            {exp.isEditing ? (
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                    <div>
                                                        <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">Company Name</label>
                                                        <input
                                                            type="text"
                                                            value={exp.company}
                                                            onChange={(e) => updateExperience(exp.id, 'company', e.target.value)}
                                                            className="w-full bg-white dark:bg-black/20 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-blue-500/50 outline-none"
                                                            placeholder="Company Name"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">Role / Job Title</label>
                                                        <input
                                                            type="text"
                                                            value={exp.role}
                                                            onChange={(e) => updateExperience(exp.id, 'role', e.target.value)}
                                                            className="w-full bg-white dark:bg-black/20 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-blue-500/50 outline-none"
                                                            placeholder="e.g. Software Engineer"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">Location</label>
                                                        <input
                                                            type="text"
                                                            value={exp.location}
                                                            onChange={(e) => updateExperience(exp.id, 'location', e.target.value)}
                                                            className="w-full bg-white dark:bg-black/20 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-blue-500/50 outline-none"
                                                            placeholder="e.g. New York, Remote"
                                                        />
                                                    </div>
                                                    <div className="grid grid-cols-2 gap-2">
                                                        <div>
                                                            <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">Start Date</label>
                                                            <input
                                                                type="date"
                                                                value={exp.startDate}
                                                                onChange={(e) => updateExperience(exp.id, 'startDate', e.target.value)}
                                                                className="w-full bg-white dark:bg-black/20 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-blue-500/50 outline-none"
                                                            />
                                                        </div>
                                                        <div>
                                                            <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">End Date</label>
                                                            <input
                                                                type="date"
                                                                value={exp.endDate}
                                                                onChange={(e) => updateExperience(exp.id, 'endDate', e.target.value)}
                                                                className="w-full bg-white dark:bg-black/20 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-blue-500/50 outline-none"
                                                            />
                                                        </div>
                                                    </div>
                                                    <div className="md:col-span-2">
                                                        <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">Description</label>
                                                        <textarea
                                                            value={exp.description}
                                                            onChange={(e) => updateExperience(exp.id, 'description', e.target.value)}
                                                            className="w-full bg-white dark:bg-black/20 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-blue-500/50 outline-none resize-none h-20"
                                                            placeholder="Describe your responsibilities and achievements..."
                                                        />
                                                    </div>
                                                    <div className="md:col-span-2 flex justify-end">
                                                        <button
                                                            type="button"
                                                            onClick={() => toggleExperienceEdit(exp.id)}
                                                            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors"
                                                        >
                                                            <Save className="w-4 h-4" /> Save Experience
                                                        </button>
                                                    </div>
                                                </div>
                                            ) : (
                                                <div className="space-y-1">
                                                    <h4 className="text-lg font-semibold text-slate-900 dark:text-white">{exp.role || 'Role'}</h4>
                                                    <p className="text-sm font-medium text-blue-600 dark:text-blue-400">{exp.company || 'Company'}</p>
                                                    <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-blue-200/60">
                                                        <span>{exp.startDate || 'Start'} - {exp.endDate || 'Present'}</span>
                                                        <span>•</span>
                                                        <span>{exp.location || 'Location'}</span>
                                                    </div>
                                                    <p className="text-sm text-slate-600 dark:text-blue-200/80 mt-2 whitespace-pre-line">
                                                        {exp.description}
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                            {formData.workExperience.length === 0 && (
                                <div className="text-center py-8 border border-dashed border-slate-200 dark:border-white/10 rounded-xl bg-slate-50 dark:bg-white/5">
                                    <p className="text-sm text-slate-500 dark:text-blue-200/40">No work experience added yet</p>
                                </div>
                            )}
                        </div>
                        <input
                            type="file"
                            ref={companyLogoInputRef}
                            className="hidden"
                            accept="image/*"
                            onChange={handleCompanyLogoChange}
                        />
                    </div>

                    {/* Projects Section */}
                    <div className="space-y-4 pt-4 border-t border-slate-200 dark:border-white/5">
                        <div className="flex items-center justify-between">
                            <h3 className="text-lg font-semibold text-slate-800 dark:text-blue-200 flex items-center">
                                <Briefcase className="w-4 h-4 mr-2" /> Projects
                            </h3>
                            <button
                                type="button"
                                onClick={addProject}
                                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
                            >
                                <Plus className="w-4 h-4" /> Add Project
                            </button>
                        </div>
                        <div className="space-y-4">
                            {formData.projects.map((project) => (
                                <div key={project.id} className="bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl p-6 space-y-4">
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <input
                                                type="text"
                                                value={project.name}
                                                onChange={(e) => updateProject(project.id, 'name', e.target.value)}
                                                className="w-full text-lg font-semibold bg-transparent border-none outline-none text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-blue-200/30"
                                                placeholder="Project Name"
                                            />
                                        </div>
                                        <button
                                            type="button"
                                            onClick={() => removeProject(project.id)}
                                            className="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-lg transition-colors"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">Your Role</label>
                                            <input
                                                type="text"
                                                value={project.role}
                                                onChange={(e) => updateProject(project.id, 'role', e.target.value)}
                                                className="w-full bg-white dark:bg-black/20 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-blue-500/50 outline-none"
                                                placeholder="e.g. Lead Developer, Team Member"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">Duration</label>
                                            <input
                                                type="text"
                                                value={project.duration}
                                                onChange={(e) => updateProject(project.id, 'duration', e.target.value)}
                                                className="w-full bg-white dark:bg-black/20 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-blue-500/50 outline-none"
                                                placeholder="e.g. Jan 2024 - Mar 2024, 3 months"
                                            />
                                        </div>
                                        <div className="md:col-span-2">
                                            <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">Technologies Used</label>
                                            <TagInput
                                                label=""
                                                tags={project.technologies}
                                                onAddTag={(tag) => updateProject(project.id, 'technologies', [...project.technologies, tag])}
                                                onRemoveTag={(tag) => updateProject(project.id, 'technologies', project.technologies.filter(t => t !== tag))}
                                                suggestions={[]}
                                                placeholder="Add technologies (e.g., React, Node.js, MongoDB)"
                                            />
                                        </div>
                                        <div className="md:col-span-2">
                                            <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">Description</label>
                                            <textarea
                                                value={project.description}
                                                onChange={(e) => updateProject(project.id, 'description', e.target.value)}
                                                className="w-full bg-white dark:bg-black/20 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-blue-500/50 outline-none resize-none h-20"
                                                placeholder="Describe the project, your contributions, and key achievements..."
                                            />
                                        </div>
                                        <div className="md:col-span-2">
                                            <label className="block text-xs font-medium text-slate-700 dark:text-blue-200/60 mb-1">Project Link (GitHub, Demo, etc.)</label>
                                            <input
                                                type="url"
                                                value={project.link}
                                                onChange={(e) => updateProject(project.id, 'link', e.target.value)}
                                                className="w-full bg-white dark:bg-black/20 border border-slate-200 dark:border-white/10 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-blue-500/50 outline-none"
                                                placeholder="https://github.com/username/project or https://demo.com"
                                            />
                                        </div>
                                    </div>
                                </div>
                            ))}
                            {formData.projects.length === 0 && (
                                <div className="text-center py-8 border border-dashed border-slate-200 dark:border-white/10 rounded-xl bg-slate-50 dark:bg-white/5">
                                    <p className="text-sm text-slate-500 dark:text-blue-200/40">No projects added yet</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Job Preferences */}
                    <div className="space-y-4 pt-4 border-t border-slate-200 dark:border-white/5">
                        <h3 className="text-lg font-semibold text-slate-800 dark:text-blue-200 flex items-center">
                            <MapPin className="w-4 h-4 mr-2" /> Job Preferences
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <TagInput
                                label="Interested Roles"
                                tags={formData.jobPreferences}
                                onAddTag={(tag) => addTag('jobPreferences', tag)}
                                onRemoveTag={(tag) => removeTag('jobPreferences', tag)}
                                suggestions={POPULAR_JOB_TITLES}
                                placeholder="Type role & press Enter"
                            />
                            <TagInput
                                label="Preferred Locations"
                                tags={formData.preferredLocations}
                                onAddTag={(tag) => addTag('preferredLocations', tag)}
                                onRemoveTag={(tag) => removeTag('preferredLocations', tag)}
                                suggestions={POPULAR_LOCATIONS}
                                placeholder="Type location & press Enter"
                            />
                        </div>
                    </div>

                    {/* Resume Upload */}
                    <div className="space-y-4 pt-4 border-t border-slate-200 dark:border-white/5">
                        <h3 className="text-lg font-semibold text-slate-800 dark:text-blue-200 flex items-center">
                            <FileText className="w-4 h-4 mr-2" /> Resume
                        </h3>
                        <div
                            className="border-2 border-dashed border-slate-200 dark:border-white/10 rounded-xl p-8 flex flex-col items-center justify-center hover:border-blue-500/30 hover:bg-slate-50 dark:hover:bg-white/5 transition-all cursor-pointer group"
                            onClick={() => fileInputRef.current?.click()}
                        >
                            <Upload className="w-8 h-8 text-slate-400 dark:text-blue-200/40 group-hover:text-blue-500 dark:group-hover:text-blue-400 transition-colors mb-3" />
                            <div className="text-center">
                                <p className="text-sm font-medium text-slate-700 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-300">
                                    {formData.resume ? formData.resume.name : "Click to upload your resume"}
                                </p>
                                <p className="text-xs text-slate-500 dark:text-blue-200/40 mt-1">PDF, DOCX up to 5MB</p>
                            </div>
                            <input
                                type="file"
                                ref={fileInputRef}
                                className="hidden"
                                accept=".pdf,.doc,.docx"
                                onChange={handleFileChange}
                            />
                        </div>
                    </div>

                    <div className="pt-6 flex justify-end gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-6 py-2.5 text-sm font-medium text-slate-600 dark:text-blue-200 hover:text-slate-900 dark:hover:text-white transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="px-8 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl shadow-lg shadow-blue-900/20 transition-all transform hover:scale-[1.02] active:scale-[0.98]"
                        >
                            Save Profile
                        </button>
                    </div>
                </form>
            </div >
        </div >
    );
}
