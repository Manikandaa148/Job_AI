"use client";
import { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';
import { getApplications, updateApplication, deleteApplication, Application } from '@/lib/api';
import { Header } from '@/components/Header';
import { Plus, MoreVertical, Trash2, ExternalLink } from 'lucide-react';


const COLUMNS = {
    Saved: { id: 'Saved', title: 'Saved', color: 'bg-slate-100 dark:bg-slate-800/50' },
    Applied: { id: 'Applied', title: 'Applied', color: 'bg-blue-50 dark:bg-blue-900/10' },
    Interviewing: { id: 'Interviewing', title: 'Interviewing', color: 'bg-purple-50 dark:bg-purple-900/10' },
    Offer: { id: 'Offer', title: 'Offer', color: 'bg-green-50 dark:bg-green-900/10' },
    Rejected: { id: 'Rejected', title: 'Rejected', color: 'bg-red-50 dark:bg-red-900/10' },
};

export default function ApplicationsPage() {
    const [applications, setApplications] = useState<Application[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadApplications();
    }, []);

    const loadApplications = async () => {
        try {
            const data = await getApplications();
            setApplications(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const onDragEnd = async (result: DropResult) => {
        const { source, destination, draggableId } = result;

        if (!destination) return;
        if (source.droppableId === destination.droppableId) return;

        const appId = parseInt(draggableId);
        const newStatus = destination.droppableId;

        // Optimistic UI Update
        const updatedApps = applications.map(app =>
            app.id === appId ? { ...app, status: newStatus as any } : app
        );
        setApplications(updatedApps);

        try {
            await updateApplication(appId, { status: newStatus });
        } catch (error) {
            console.error("Failed to update status", error);
            // Revert on error
            loadApplications();
        }
    };

    const handleDelete = async (e: React.MouseEvent, appId: number) => {
        e.stopPropagation(); // Prevent drag or other clicks
        if (!confirm("Are you sure you want to remove this application?")) return;

        // Optimistic delete
        setApplications(prev => prev.filter(app => app.id !== appId));

        try {
            await deleteApplication(appId);
        } catch (error) {
            console.error("Failed to delete application", error);
            // Revert (could reload, or just show error toast)
            loadApplications();
        }
    };

    // Helper to group apps
    const getAppsByStatus = (status: string) => {
        return applications.filter(app => app.status === status);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white">
            <Header />
            <div className="max-w-7xl mx-auto px-4 py-8 overflow-x-auto">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Application Tracker</h1>
                        <p className="text-sm text-slate-500 dark:text-slate-400">Drag and drop cards to update your progress</p>
                    </div>
                    {/* Placeholder for Add button - could be modal later */}
                    <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-lg shadow-blue-500/20">
                        <Plus size={18} /> Add Application
                    </button>
                </div>

                <DragDropContext onDragEnd={onDragEnd}>
                    <div className="flex gap-6 min-w-max pb-8">
                        {Object.entries(COLUMNS).map(([columnId, column]) => (
                            <div key={columnId} className={`w-80 flex-shrink-0 flex flex-col rounded-xl ${column.color} p-4 border border-slate-200 dark:border-white/5`}>
                                <div className="flex items-center justify-between mb-4">
                                    <h2 className="font-semibold text-slate-700 dark:text-slate-200">{column.title}</h2>
                                    <span className="text-xs font-mono bg-white dark:bg-black/20 px-2 py-1 rounded-full text-slate-600 dark:text-slate-300">
                                        {getAppsByStatus(columnId).length}
                                    </span>
                                </div>

                                <Droppable droppableId={columnId}>
                                    {(provided) => (
                                        <div
                                            ref={provided.innerRef}
                                            {...provided.droppableProps}
                                            className="flex-1 flex flex-col gap-3 min-h-[150px]"
                                        >
                                            {getAppsByStatus(columnId).map((app, index) => (
                                                <Draggable key={app.id} draggableId={app.id.toString()} index={index}>
                                                    {(provided, snapshot) => (
                                                        <div
                                                            ref={provided.innerRef}
                                                            {...provided.draggableProps}
                                                            {...provided.dragHandleProps}
                                                            style={{
                                                                ...provided.draggableProps.style,
                                                                opacity: snapshot.isDragging ? 0.9 : 1
                                                            }}
                                                            className={`
                                                                bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700 
                                                                hover:shadow-md transition-all group cursor-grab active:cursor-grabbing
                                                                ${snapshot.isDragging ? 'shadow-xl ring-2 ring-blue-500/50 rotate-2' : ''}
                                                            `}
                                                        >
                                                            <div className="flex justify-between items-start mb-2">
                                                                <h3 className="font-medium text-sm line-clamp-2 text-slate-800 dark:text-slate-100">{app.job_title}</h3>
                                                            </div>
                                                            <p className="text-xs text-slate-500 dark:text-slate-400 mb-3 font-medium">{app.company}</p>

                                                            <div className="flex items-center justify-between mt-auto pt-2 border-t border-slate-100 dark:border-slate-700/50">
                                                                <span className="text-[10px] text-slate-400">
                                                                    {new Date(app.applied_date).toLocaleDateString()}
                                                                </span>

                                                                <div className="flex gap-1 opacity-100">
                                                                    {app.job_url && (
                                                                        <a
                                                                            href={app.job_url}
                                                                            target="_blank"
                                                                            rel="noopener noreferrer"
                                                                            className="text-slate-400 hover:text-blue-500 p-1.5 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded transition-colors"
                                                                            title="View Job"
                                                                        >
                                                                            <ExternalLink size={14} />
                                                                        </a>
                                                                    )}
                                                                    <button
                                                                        onClick={(e) => handleDelete(e, app.id)}
                                                                        className="text-slate-400 hover:text-red-500 p-1.5 hover:bg-red-50 dark:hover:bg-red-900/30 rounded transition-colors"
                                                                        title="Delete"
                                                                    >
                                                                        <Trash2 size={14} />
                                                                    </button>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    )}
                                                </Draggable>
                                            ))}
                                            {provided.placeholder}
                                        </div>
                                    )}
                                </Droppable>
                            </div>
                        ))}
                    </div>
                </DragDropContext>
            </div>
        </div>
    );
}
