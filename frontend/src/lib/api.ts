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
            // Don't reload, just let the app re-fetch with auto-login
            console.log('Please refresh the page manually or click the user icon again');
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
    skills?: string[];
    avatar?: string;
    education?: any[];
    experience?: any[];
    job_preferences?: string[];
    projects?: any[];
}

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
