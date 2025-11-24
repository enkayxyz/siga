import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { RefreshCw, Terminal } from 'lucide-react';

const Logs = () => {
    const [logs, setLogs] = useState('');
    const [logType, setLogType] = useState('backend'); // backend, frontend
    const [loading, setLoading] = useState(false);

    const fetchLogs = async () => {
        setLoading(true);
        try {
            const res = await api.get(`/logs/${logType}`);
            setLogs(res.data.logs);
        } catch (err) {
            console.error("Failed to fetch logs", err);
            setLogs("Error fetching logs.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
        const interval = setInterval(fetchLogs, 5000); // Auto-refresh every 5s
        return () => clearInterval(interval);
    }, [logType]);

    return (
        <div className="h-full flex flex-col bg-black/90 rounded-xl border border-white/10 overflow-hidden font-mono text-sm">
            <div className="flex items-center justify-between p-4 bg-white/5 border-b border-white/10">
                <div className="flex space-x-4">
                    <button
                        onClick={() => setLogType('backend')}
                        className={`flex items-center space-x-2 px-3 py-1 rounded ${logType === 'backend' ? 'bg-primary/20 text-primary' : 'text-gray-400 hover:text-white'}`}
                    >
                        <Terminal size={14} />
                        <span>Backend Logs</span>
                    </button>
                    <button
                        onClick={() => setLogType('frontend')}
                        className={`flex items-center space-x-2 px-3 py-1 rounded ${logType === 'frontend' ? 'bg-primary/20 text-primary' : 'text-gray-400 hover:text-white'}`}
                    >
                        <Terminal size={14} />
                        <span>Frontend Logs</span>
                    </button>
                </div>
                <button
                    onClick={fetchLogs}
                    disabled={loading}
                    className="text-gray-400 hover:text-white transition-colors"
                >
                    <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
                </button>
            </div>

            <div className="flex-1 p-4 overflow-auto bg-black text-gray-300 whitespace-pre-wrap">
                {logs || "No logs available."}
            </div>
        </div>
    );
};

export default Logs;
