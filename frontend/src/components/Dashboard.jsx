import React from 'react';
import { DollarSign, Building, Globe, Users, CreditCard } from 'lucide-react';
import { X, Search as SearchIcon } from 'lucide-react';
import { useState } from 'react';

const StatCard = ({ icon: Icon, label, value, subtext }) => (
    <div className="p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm flex items-center space-x-4">
        <div className="p-3 rounded-full bg-primary/20 text-primary">
            <Icon size={24} />
        </div>
        <div>
            <p className="text-sm text-muted-foreground">{label}</p>
            <p className="text-xl font-bold text-white">{value || 'N/A'}</p>
            {subtext && <p className="text-xs text-gray-500">{subtext}</p>}
        </div>
    </div>
);

const SubsidiaryModal = ({ subsidiary, onClose, onResearch }) => {
    if (!subsidiary) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <div className="bg-gray-900 border border-white/10 rounded-xl w-full max-w-2xl overflow-hidden shadow-2xl">
                <div className="flex justify-between items-center p-6 border-b border-white/10 bg-white/5">
                    <div>
                        <h2 className="text-2xl font-bold text-white">{subsidiary.name}</h2>
                        <span className="text-sm text-blue-400 font-medium px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 mt-2 inline-block">
                            {subsidiary.type}
                        </span>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
                        <X size={24} />
                    </button>
                </div>

                <div className="p-6 space-y-6">
                    <div className="grid grid-cols-2 gap-6">
                        <div>
                            <h3 className="text-sm font-medium text-gray-500 uppercase mb-1">Location</h3>
                            <p className="text-lg text-white">
                                {subsidiary.location?.city && subsidiary.location?.city !== "Unknown" ? `${subsidiary.location.city}, ` : ''}
                                {subsidiary.location?.country || "Unknown"}
                            </p>
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-gray-500 uppercase mb-1">Source</h3>
                            <p className="text-sm text-gray-300 bg-white/5 p-2 rounded border border-white/5">
                                {subsidiary.source || "General Search"}
                            </p>
                        </div>
                    </div>

                    {subsidiary.description && (
                        <div>
                            <h3 className="text-sm font-medium text-gray-500 uppercase mb-1">Description</h3>
                            <p className="text-gray-300 leading-relaxed">{subsidiary.description}</p>
                        </div>
                    )}

                    <div className="pt-4 border-t border-white/10 flex justify-end">
                        <button
                            onClick={() => onResearch(subsidiary.name)}
                            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg transition-colors font-medium"
                        >
                            <SearchIcon size={18} />
                            <span>Research this Entity</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

const Dashboard = ({ data, onResearchEntity }) => {
    const [selectedSub, setSelectedSub] = useState(null);

    if (!data) return null;

    const subsidiaryCount = data.subsidiaries?.length || 0;
    const countries = new Set(data.subsidiaries?.map(s => s.location?.country).filter(Boolean)).size;

    // Usage Stats
    const cost = data.usage?.estimated_cost ? `$${data.usage.estimated_cost.toFixed(4)}` : '$0.00';
    const usageDetails = data.usage ? `${data.usage.tavily_calls} searches, ${data.usage.llm_tokens} tokens` : '';

    return (
        <div className="space-y-6 relative">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard icon={Building} label="Company" value={data.name} />
                <StatCard icon={DollarSign} label="Total Revenue" value={data.total_revenue} />
                <StatCard icon={Globe} label="Global Presence" value={`${countries} Countries`} />
                <StatCard icon={Users} label="Subsidiaries" value={subsidiaryCount} />
                <StatCard
                    icon={CreditCard}
                    label="Research Cost"
                    value={cost}
                    subtext={usageDetails}
                />
            </div>

            <div className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-sm">
                <h3 className="text-xl font-semibold mb-4 text-white">Subsidiaries & Entities</h3>
                <p className="text-sm text-gray-400 mb-4">Click on any row to view details.</p>
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-gray-300">
                        <thead className="text-xs uppercase bg-white/10 text-gray-200">
                            <tr>
                                <th className="px-4 py-3 rounded-tl-lg">Name</th>
                                <th className="px-4 py-3">Location</th>
                                <th className="px-4 py-3">Type</th>
                                <th className="px-4 py-3 rounded-tr-lg">Source</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.subsidiaries?.map((sub, index) => (
                                <tr
                                    key={index}
                                    onClick={() => setSelectedSub(sub)}
                                    className="border-b border-white/5 hover:bg-white/10 transition-colors cursor-pointer"
                                >
                                    <td className="px-4 py-3 font-medium text-white">{sub.name}</td>
                                    <td className="px-4 py-3">
                                        {sub.location?.city && sub.location?.city !== "Unknown" ? `${sub.location.city}, ` : ''}
                                        {sub.location?.country}
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className="px-2 py-1 rounded-full text-xs bg-blue-500/20 text-blue-300 border border-blue-500/30">
                                            {sub.type}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 text-gray-400 text-xs">{sub.source || 'Unknown'}</td>
                                </tr>
                            ))}
                            {(!data.subsidiaries || data.subsidiaries.length === 0) && (
                                <tr>
                                    <td colSpan="4" className="px-4 py-8 text-center text-gray-500">
                                        No subsidiaries found.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {selectedSub && (
                <SubsidiaryModal
                    subsidiary={selectedSub}
                    onClose={() => setSelectedSub(null)}
                    onResearch={(name) => {
                        if (onResearchEntity) onResearchEntity(name);
                        setSelectedSub(null);
                    }}
                />
            )}
        </div>
    );
};

export default Dashboard;
