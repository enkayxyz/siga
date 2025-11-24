import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { Save, Loader } from 'lucide-react';

const Settings = () => {
    const [settings, setSettings] = useState({
        openai_api_key: '',
        openai_model: '',
        groq_api_key: '',
        groq_model: '',
        gemini_api_key: '',
        gemini_model: '',
        tavily_api_key: '',
        llm_provider: 'openai'
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState('');

    const [verifying, setVerifying] = useState({});
    const [availableModels, setAvailableModels] = useState({
        openai: [],
        groq: [],
        gemini: []
    });

    useEffect(() => {
        fetchSettings();
    }, []);

    useEffect(() => {
        if (!loading) {
            fetchModels('openai');
            fetchModels('groq');
            fetchModels('gemini');
        }
    }, [loading]);

    const fetchSettings = async () => {
        try {
            const res = await api.get('/settings');
            setSettings(res.data);
        } catch (err) {
            console.error("Failed to fetch settings", err);
        } finally {
            setLoading(false);
        }
    };

    const fetchModels = async (provider) => {
        try {
            const res = await api.get(`/models/${provider}`);
            setAvailableModels(prev => ({ ...prev, [provider]: res.data.models }));
        } catch (err) {
            console.error(`Failed to fetch models for ${provider}`, err);
        }
    };

    const handleChange = (e) => {
        setSettings({ ...settings, [e.target.name]: e.target.value });
    };

    const verifyProvider = async (provider) => {
        setVerifying({ ...verifying, [provider]: 'loading' });
        try {
            const res = await api.get(`/verify/${provider}`);
            if (res.data.status === 'OK') {
                setVerifying({ ...verifying, [provider]: 'ok' });
                fetchModels(provider); // Refresh models on successful verification
            } else {
                setVerifying({ ...verifying, [provider]: 'fail' });
                setMessage(`${provider} verification failed: ${res.data.message}`);
            }
        } catch (err) {
            setVerifying({ ...verifying, [provider]: 'fail' });
            setMessage(`Failed to verify ${provider}`);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setMessage('');
        try {
            await api.post('/settings', settings);
            setMessage('Settings saved successfully!');
            setTimeout(() => setMessage(''), 3000);
        } catch (err) {
            console.error("Failed to save settings", err);
            setMessage('Error saving settings.');
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="p-8 text-center">Loading settings...</div>;

    const VerifyButton = ({ provider }) => (
        <button
            type="button"
            onClick={() => verifyProvider(provider)}
            disabled={verifying[provider] === 'loading'}
            className={`text-xs px-2 py-1 rounded border transition-colors ${verifying[provider] === 'ok' ? 'border-green-500 text-green-500' :
                    verifying[provider] === 'fail' ? 'border-red-500 text-red-500' :
                        'border-white/20 text-gray-400 hover:text-white'
                }`}
        >
            {verifying[provider] === 'loading' ? 'Checking...' :
                verifying[provider] === 'ok' ? 'Connected' :
                    verifying[provider] === 'fail' ? 'Failed' : 'Verify'}
        </button>
    );

    const ModelSelect = ({ provider, value, name, placeholder }) => (
        <select
            name={name}
            value={value || ''}
            onChange={handleChange}
            className="w-full bg-black/50 border border-white/10 rounded-md p-2 text-white text-sm focus:ring-2 focus:ring-primary focus:border-transparent"
        >
            <option value="" disabled>{placeholder || "Select a model"}</option>
            {availableModels[provider] && availableModels[provider].length > 0 ? (
                availableModels[provider].map(model => (
                    <option key={model} value={model}>{model}</option>
                ))
            ) : (
                <option value={value}>{value || "No models found (Verify API Key)"}</option>
            )}
        </select>
    );

    return (
        <div className="max-w-4xl mx-auto p-6 bg-white/5 rounded-xl border border-white/10 backdrop-blur-sm">
            <h2 className="text-2xl font-bold mb-6 text-white">AI Configuration</h2>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Provider Selection */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-300">Default Provider</label>
                    <select
                        name="llm_provider"
                        value={settings.llm_provider || 'openai'}
                        onChange={handleChange}
                        className="w-full bg-black/50 border border-white/10 rounded-md p-2 text-white focus:ring-2 focus:ring-primary focus:border-transparent"
                    >
                        <option value="openai">OpenAI</option>
                        <option value="groq">Groq</option>
                        <option value="gemini">Gemini</option>
                    </select>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* OpenAI */}
                    <div className="space-y-4 p-4 border border-white/10 rounded-lg bg-black/20">
                        <div className="flex justify-between items-center">
                            <h3 className="text-lg font-semibold text-blue-400">OpenAI</h3>
                            <VerifyButton provider="openai" />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400 mb-1">API Key</label>
                            <input
                                type="password"
                                name="openai_api_key"
                                value={settings.openai_api_key || ''}
                                onChange={handleChange}
                                className="w-full bg-black/50 border border-white/10 rounded-md p-2 text-white text-sm"
                                placeholder="sk-..."
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400 mb-1">Model</label>
                            <ModelSelect
                                provider="openai"
                                name="openai_model"
                                value={settings.openai_model}
                                placeholder="Select OpenAI Model"
                            />
                        </div>
                    </div>

                    {/* Groq */}
                    <div className="space-y-4 p-4 border border-white/10 rounded-lg bg-black/20">
                        <div className="flex justify-between items-center">
                            <h3 className="text-lg font-semibold text-orange-400">Groq</h3>
                            <VerifyButton provider="groq" />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400 mb-1">API Key</label>
                            <input
                                type="password"
                                name="groq_api_key"
                                value={settings.groq_api_key || ''}
                                onChange={handleChange}
                                className="w-full bg-black/50 border border-white/10 rounded-md p-2 text-white text-sm"
                                placeholder="gsk_..."
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400 mb-1">Model</label>
                            <ModelSelect
                                provider="groq"
                                name="groq_model"
                                value={settings.groq_model}
                                placeholder="Select Groq Model"
                            />
                        </div>
                    </div>

                    {/* Gemini */}
                    <div className="space-y-4 p-4 border border-white/10 rounded-lg bg-black/20">
                        <div className="flex justify-between items-center">
                            <h3 className="text-lg font-semibold text-purple-400">Gemini</h3>
                            <VerifyButton provider="gemini" />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400 mb-1">API Key</label>
                            <input
                                type="password"
                                name="gemini_api_key"
                                value={settings.gemini_api_key || ''}
                                onChange={handleChange}
                                className="w-full bg-black/50 border border-white/10 rounded-md p-2 text-white text-sm"
                                placeholder="AIza..."
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400 mb-1">Model</label>
                            <ModelSelect
                                provider="gemini"
                                name="gemini_model"
                                value={settings.gemini_model}
                                placeholder="Select Gemini Model"
                            />
                        </div>
                    </div>

                    {/* Tavily */}
                    <div className="space-y-4 p-4 border border-white/10 rounded-lg bg-black/20">
                        <div className="flex justify-between items-center">
                            <h3 className="text-lg font-semibold text-green-400">Search (Tavily)</h3>
                            <VerifyButton provider="tavily" />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-400 mb-1">API Key</label>
                            <input
                                type="password"
                                name="tavily_api_key"
                                value={settings.tavily_api_key || ''}
                                onChange={handleChange}
                                className="w-full bg-black/50 border border-white/10 rounded-md p-2 text-white text-sm"
                                placeholder="tvly-..."
                            />
                        </div>
                    </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-white/10">
                    <span className={`text-sm ${message.includes('Error') ? 'text-red-400' : 'text-green-400'}`}>
                        {message}
                    </span>
                    <button
                        type="submit"
                        disabled={saving}
                        className="flex items-center space-x-2 bg-primary hover:bg-blue-600 text-white px-6 py-2 rounded-md transition-colors disabled:opacity-50"
                    >
                        {saving ? <Loader className="animate-spin" size={18} /> : <Save size={18} />}
                        <span>Save Configuration</span>
                    </button>
                </div>
            </form>
        </div>
    );
};

export default Settings;
