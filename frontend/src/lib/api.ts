import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Add token interceptor
axios.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Flag to prevent infinite reload loop
let isReloading = false;

// Add response interceptor to handle 401 errors
axios.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401 && !isReloading) {
            console.log('⚠ 401 Unauthorized - Token invalid, clearing...');
            isReloading = true;
            localStorage.removeItem('token');
            if (typeof window !== 'undefined') {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export interface Job {
    id?: string;
    title: string;
    company: string;
    location: string;
    description?: string;
    url: string;
    source: string;
    posted_date?: string;
    salary?: string;
}

export interface User {
    id: number;
    email: string;
    full_name?: string;
    address?: string;
    location?: string;
    experience_level?: string;
    total_experience?: string;
    skills?: string[];
    preferred_locations?: string[];
    avatar?: string;
    education?: any[];
    experience?: any[];
    job_preferences?: string[];
    projects?: any[];
    linkedin_url?: string;
    github_url?: string;
    portfolio_url?: string;
}

export const getNotifications = async (): Promise<any[]> => {
    try {
        const response = await axios.get(`${API_URL}/notifications`);
        return response.data;
    } catch (e) {
        console.error('Failed to fetch notifications', e);
        return [];
    }
};

export const searchJobs = async (
    query: string,
    location: string = '',
    start: number = 1,
    experienceLevel: string[] = [],
    platforms: string[] = [],
    companySize: string[] = []
): Promise<Job[]> => {
    try {
        const response = await axios.post(`${API_URL}/search`, {
            query,
            location,
            limit: 10,
            start,
            experience_level: experienceLevel,
            platforms,
            company_size: companySize
        });
        return response.data;
    } catch (error) {
        console.error("Error searching jobs:", error);
        return [];
    }
};

export const login = async (email: string, password: string): Promise<{ access_token: string }> => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    const response = await axios.post(`${API_URL}/login`, formData);
    return response.data;
};

export const register = async (email: string, password: string, fullName: string): Promise<User> => {
    const response = await axios.post(`${API_URL}/register`, {
        email,
        password,
        full_name: fullName
    });
    return response.data;
};

export const getProfile = async (): Promise<User> => {
    const response = await axios.get(`${API_URL}/users/me`);
    return response.data;
};

export const updateProfile = async (data: Partial<User>): Promise<User> => {
    const response = await axios.put(`${API_URL}/users/me`, data);
    return response.data;
};

export const generateResume = async (formData: FormData): Promise<Blob> => {
    const response = await axios.post(`${API_URL}/generate-resume`, formData, {
        responseType: 'blob'
    });
    return response.data;
};

export const getRecommendations = async (): Promise<any[]> => {
    const response = await axios.get(`${API_URL}/recommendations`);
    return response.data;
};

export const getSuggestions = async (type: string, query: string = ''): Promise<string[]> => {
    const response = await axios.get(`${API_URL}/suggestions`, {
        params: { type, query }
    });
    return response.data;
};

export const analyzeResumeFile = async (file: File) => {
    try {
        const formData = new FormData();
        formData.append('file', file);
        const response = await axios.post(`${API_URL}/analyze-resume-file`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error analyzing resume:', error);
        throw error;
    }
};

export const uploadResume = async (file: File) => {
    try {
        const formData = new FormData();
        formData.append('file', file);
        const response = await axios.post(`${API_URL}/users/me/resume`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error uploading resume:', error);
        throw error;
    }
};

// Auto-Apply API Functions
export interface AutoApplyValidation {
    can_auto_apply: boolean;
    missing_fields: string[];
    prompts: Array<{
        field: string;
        question: string;
        type: string;
    }>;
}

export const validateAutoApply = async (): Promise<AutoApplyValidation> => {
    const response = await axios.get(`${API_URL}/auto-apply/validate`);
    return response.data;
};

export const executeAutoApply = async (jobIds: string[]): Promise<any> => {
    const response = await axios.post(`${API_URL}/auto-apply/execute`, {
        job_ids: jobIds
    });
    return response.data;
};

export const sendChatMessage = async (message: string, field?: string): Promise<any> => {
    const response = await axios.post(`${API_URL}/chatbot/message`, {
        message,
        field
    });
    return response.data;
};

// Application Tracker API
export interface Application {
    id: number;
    user_id: number;
    job_id?: string;
    job_title: string;
    company: string;
    location?: string;
    status: 'Saved' | 'Applied' | 'Interviewing' | 'Offer' | 'Rejected';
    applied_date: string;
    notes?: string;
    salary?: string;
    job_url?: string;
    platform?: string;
    updated_at: string;
}

export const getApplications = async (): Promise<Application[]> => {
    const response = await axios.get(`${API_URL}/applications`);
    return response.data;
};

export const createApplication = async (app: Partial<Application>): Promise<Application> => {
    const response = await axios.post(`${API_URL}/applications`, app);
    return response.data;
};

export const updateApplication = async (id: number, data: { status?: string; notes?: string }): Promise<Application> => {
    const response = await axios.put(`${API_URL}/applications/${id}`, data);
    return response.data;
};

export const deleteApplication = async (id: number): Promise<void> => {
    await axios.delete(`${API_URL}/applications/${id}`);
};
