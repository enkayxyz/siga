import React, { useState } from 'react';
import { Search, Map as MapIcon, Share2, LayoutDashboard, Settings as SettingsIcon, FileText } from 'lucide-react';
import Map from './components/Map';
import NetworkGraph from './components/NetworkGraph';
import Dashboard from './components/Dashboard';
import Settings from './components/Settings';
import Logs from './components/Logs';
import { researchCompany } from './api';

function App() {
  const [query, setQuery] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [forensicMode, setForensicMode] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard'); // dashboard, map, network

  const performResearch = async (companyName, isForensic) => {
    if (!companyName.trim()) return;

    setQuery(companyName); // Update UI
    setLoading(true);
    setStatus('Initializing...');
    setData(null);

    try {
      const result = await researchCompany(companyName, isForensic, (msg) => setStatus(msg));
      setData(result);
      setActiveTab('dashboard');
    } catch (error) {
      console.error("Search failed:", error);
      setStatus(`Error: ${error.message}`);
    } finally {
      setLoading(false);
      setStatus('');
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    performResearch(query, forensicMode);
  };

  return (
    <div className="min-h-screen bg-background text-foreground p-6 flex flex-col">
      {/* Header & Search */}
      <header className="flex flex-col items-center justify-center mb-8 space-y-6">
        <h1 className="text-4xl font-bold tracking-tighter bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
          Siga Agent
        </h1>

        <form onSubmit={handleSearch} className="w-full max-w-2xl relative flex flex-col items-center space-y-4">
          <div className="relative group w-full">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg blur opacity-30 group-hover:opacity-75 transition duration-200"></div>
            <div className="relative flex items-center bg-black rounded-lg">
              <Search className="absolute left-4 text-muted-foreground" size={20} />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter company name (e.g. Alphabet Inc)..."
                className="w-full bg-transparent border-none py-4 pl-12 pr-4 text-lg focus:ring-0 focus:outline-none text-white placeholder-gray-500"
              />
              <button
                type="submit"
                disabled={loading}
                className="absolute right-2 bg-primary hover:bg-blue-600 text-white px-4 py-2 rounded-md transition-colors disabled:opacity-50"
              >
                {loading ? 'Researching...' : 'Explore'}
              </button>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="sr-only peer"
                checked={forensicMode}
                onChange={(e) => setForensicMode(e.target.checked)}
              />
              <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
              <span className="ml-3 text-sm font-medium text-gray-300">
                Forensic Mode <span className="text-xs text-gray-500">(Slower, Deeper)</span>
              </span>
            </label>
          </div>

          {loading && status && (
            <div className="absolute -bottom-12 left-0 right-0 text-center text-sm text-cyan-400 animate-pulse">
              {status}
            </div>
          )}
        </form>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col max-w-7xl mx-auto w-full relative">
        {/* Top Navigation for Settings/Logs */}
        <div className="absolute top-0 right-0 flex space-x-2">
          <button
            onClick={() => setActiveTab('settings')}
            className={`p-2 rounded-md transition-all ${activeTab === 'settings' ? 'bg-primary text-white' : 'text-muted-foreground hover:bg-white/10'}`}
            title="Settings"
          >
            <SettingsIcon size={20} />
          </button>
          <button
            onClick={() => setActiveTab('logs')}
            className={`p-2 rounded-md transition-all ${activeTab === 'logs' ? 'bg-primary text-white' : 'text-muted-foreground hover:bg-white/10'}`}
            title="Logs"
          >
            <FileText size={20} />
          </button>
        </div>

        {/* Data Tabs - Only show if data exists */}
        {data && (
          <div className="flex space-x-2 mb-6 bg-white/5 p-1 rounded-lg w-fit mx-auto backdrop-blur-sm border border-white/10">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-all ${activeTab === 'dashboard' ? 'bg-primary text-white shadow-lg' : 'hover:bg-white/10 text-muted-foreground'}`}
            >
              <LayoutDashboard size={18} />
              <span>Dashboard</span>
            </button>
            <button
              onClick={() => setActiveTab('map')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-all ${activeTab === 'map' ? 'bg-primary text-white shadow-lg' : 'hover:bg-white/10 text-muted-foreground'}`}
            >
              <MapIcon size={18} />
              <span>Global Map</span>
            </button>
            <button
              onClick={() => setActiveTab('network')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-all ${activeTab === 'network' ? 'bg-primary text-white shadow-lg' : 'hover:bg-white/10 text-muted-foreground'}`}
            >
              <Share2 size={18} />
              <span>Network</span>
            </button>
          </div>
        )}

        {/* Views */}
        <div className="flex-1 min-h-[500px] relative mt-12">
          {activeTab === 'settings' && <Settings />}
          {activeTab === 'logs' && <Logs />}

          {data && (
            <>
              {activeTab === 'dashboard' && (
                <Dashboard
                  data={data}
                  onResearchEntity={(name) => performResearch(name, forensicMode)}
                />
              )}

              <div className={`absolute inset-0 transition-opacity duration-300 ${activeTab === 'map' ? 'opacity-100 z-10' : 'opacity-0 -z-10'}`}>
                <Map data={data} />
              </div>

              <div className={`absolute inset-0 transition-opacity duration-300 ${activeTab === 'network' ? 'opacity-100 z-10' : 'opacity-0 -z-10'}`}>
                <NetworkGraph data={data} />
              </div>
            </>
          )}

          {!data && activeTab !== 'settings' && activeTab !== 'logs' && !loading && (
            <div className="flex-1 flex items-center justify-center text-muted-foreground">
              <p>Start by searching for a global corporation or configure AI settings.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
