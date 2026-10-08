import React, { useState, useEffect } from 'react';
import {
  Award,
  FileCheck,
  PlusCircle,
  RefreshCw,
  Download,
  AlertCircle,
  CheckCircle2,
  Clock,
  Palette,
  LayoutDashboard,
  Layers,
  Search,
  Trash2,
  FileText
} from 'lucide-react';
import {
  JobStatusResponse,
  CertificateItem,
  Recipient,
  JobStatus
} from './types';

const API_BASE = '/api/v1';

export default function App() {
  const [theme, setTheme] = useState<'blue' | 'indigo' | 'teal'>('blue');
  const [activeTab, setActiveTab] = useState<'dashboard' | 'create' | 'details' | 'certificates' | 'settings'>('dashboard');

  // Dashboard Data
  const [jobs, setJobs] = useState<JobStatusResponse[]>([]);
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  // Job Details Data
  const [currentJob, setCurrentJob] = useState<JobStatusResponse | null>(null);
  const [jobCertificates, setJobCertificates] = useState<CertificateItem[]>([]);
  const [autoPoll, setAutoPoll] = useState(true);

  // Form State
  const [eventName, setEventName] = useState('Python Backend Workshop 2026');
  const [eventDate, setEventDate] = useState('2026-10-15');
  const [recipients, setRecipients] = useState<Recipient[]>([
    { name: 'Hemasri', email: 'hema@example.com' },
    { name: 'Ananya Sharma', email: 'ananya@example.com' },
    { name: 'Rahul Verma', email: 'rahul@example.com' }
  ]);
  const [creating, setCreating] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Apply Theme Attribute
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Fetch Jobs List
  const fetchJobs = async () => {
    setLoadingJobs(true);
    try {
      const res = await fetch(`${API_BASE}/jobs/`);
      if (res.ok) {
        const data = await res.json();
        setJobs(data.jobs || []);
      }
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
    } finally {
      setLoadingJobs(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  // Fetch Selected Job Details
  const fetchJobDetails = async (jobId: string) => {
    try {
      const [statusRes, certsRes] = await Promise.all([
        fetch(`${API_BASE}/jobs/${jobId}`),
        fetch(`${API_BASE}/jobs/${jobId}/certificates`)
      ]);

      if (statusRes.ok) {
        const statusData = await statusRes.json();
        setCurrentJob(statusData);
      }
      if (certsRes.ok) {
        const certsData = await certsRes.json();
        setJobCertificates(certsData.certificates || []);
      }
    } catch (err) {
      console.error('Failed to fetch job details:', err);
    }
  };

  // Poll Job Details if processing
  useEffect(() => {
    if (!selectedJobId || !autoPoll) return;
    fetchJobDetails(selectedJobId);

    const interval = setInterval(() => {
      fetchJobDetails(selectedJobId);
    }, 2000);

    return () => clearInterval(interval);
  }, [selectedJobId, autoPoll]);

  // Create Job Handler
  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    if (!eventName.trim()) {
      setFormError('Event name is required.');
      return;
    }
    if (!eventDate.trim()) {
      setFormError('Event date is required.');
      return;
    }
    if (recipients.length === 0) {
      setFormError('At least one recipient is required.');
      return;
    }
    for (const r of recipients) {
      if (!r.name.trim() || !r.email.trim()) {
        setFormError('All recipient fields must be filled.');
        return;
      }
    }

    setCreating(true);
    try {
      const res = await fetch(`${API_BASE}/jobs/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_name: eventName,
          event_date: eventDate,
          recipients
        })
      });

      if (!res.ok) {
        const errData = await res.json();
        setFormError(errData.error?.message || 'Failed to create job.');
        return;
      }

      const data = await res.json();
      setSelectedJobId(data.job_id);
      await fetchJobs();
      setActiveTab('details');
    } catch (err: any) {
      setFormError('Network error while connecting to server.');
    } finally {
      setCreating(false);
    }
  };

  // Add & Remove Recipient Rows
  const addRecipientRow = () => {
    setRecipients([...recipients, { name: '', email: '' }]);
  };

  const removeRecipientRow = (index: number) => {
    setRecipients(recipients.filter((_, i) => i !== index));
  };

  const updateRecipient = (index: number, field: 'name' | 'email', value: string) => {
    const updated = [...recipients];
    updated[index][field] = value;
    setRecipients(updated);
  };

  const quickFillSampleRecipients = () => {
    setEventName('AEREO Software Engineering Summit 2026');
    setEventDate('2026-10-15');
    setRecipients([
      { name: 'Hemasri', email: 'hema@example.com' },
      { name: 'Ananya Sharma', email: 'ananya@example.com' },
      { name: 'Rahul Verma', email: 'rahul@example.com' },
      { name: 'Priya Patel', email: 'priya@example.com' },
      { name: 'Vikram Malhotra', email: 'vikram@example.com' }
    ]);
  };

  // Status Badge Helper
  const renderStatusBadge = (status: JobStatus) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800"><CheckCircle2 className="w-3.5 h-3.5" /> Completed</span>;
      case 'PROCESSING':
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800"><RefreshCw className="w-3.5 h-3.5 animate-spin" /> Processing</span>;
      case 'PARTIALLY_COMPLETED':
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800"><AlertCircle className="w-3.5 h-3.5" /> Partial Success</span>;
      case 'FAILED':
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-800"><AlertCircle className="w-3.5 h-3.5" /> Failed</span>;
      default:
        return <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700"><Clock className="w-3.5 h-3.5" /> Pending</span>;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Enterprise Header Banner */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-theme-primary text-white p-2 rounded-lg flex items-center justify-center">
              <Award className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-900 tracking-tight">AEREO</h1>
              <p className="text-xs text-slate-500 font-medium">Bulk Certificate Generator</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex space-x-1 sm:space-x-4">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
              { id: 'create', label: 'New Bulk Job', icon: PlusCircle },
              { id: 'details', label: 'Job Progress', icon: Layers },
              { id: 'certificates', label: 'Certificates', icon: FileCheck },
              { id: 'settings', label: 'Theme Settings', icon: Palette },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`inline-flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-theme-primary-light text-theme-primary font-semibold'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden md:inline">{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* DASHBOARD TAB */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-2xl font-bold text-slate-900">Operations Dashboard</h2>
                <p className="text-sm text-slate-600">Track and manage certificate generation jobs in real time.</p>
              </div>
              <button
                onClick={() => setActiveTab('create')}
                className="inline-flex items-center justify-center space-x-2 bg-theme-primary hover:bg-theme-primary-hover text-white px-4 py-2.5 rounded-lg font-medium shadow-sm transition-all"
              >
                <PlusCircle className="w-4 h-4" />
                <span>Create Generation Job</span>
              </button>
            </div>

            {/* Metrics Overview Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Jobs</p>
                <p className="text-3xl font-bold text-slate-900 mt-2">{jobs.length}</p>
              </div>
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Completed</p>
                <p className="text-3xl font-bold text-emerald-600 mt-2">
                  {jobs.filter((j) => j.status === 'COMPLETED').length}
                </p>
              </div>
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Processing</p>
                <p className="text-3xl font-bold text-blue-600 mt-2">
                  {jobs.filter((j) => j.status === 'PROCESSING' || j.status === 'PENDING').length}
                </p>
              </div>
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Partial / Failed</p>
                <p className="text-3xl font-bold text-amber-600 mt-2">
                  {jobs.filter((j) => j.status === 'PARTIALLY_COMPLETED' || j.status === 'FAILED').length}
                </p>
              </div>
            </div>

            {/* Recent Jobs Table */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
              <div className="p-5 border-b border-slate-200 flex items-center justify-between">
                <h3 className="font-semibold text-slate-900">Recent Generation Jobs</h3>
                <button
                  onClick={fetchJobs}
                  className="text-xs font-medium text-slate-500 hover:text-slate-900 flex items-center space-x-1"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${loadingJobs ? 'animate-spin' : ''}`} />
                  <span>Refresh</span>
                </button>
              </div>

              {jobs.length === 0 ? (
                <div className="p-12 text-center text-slate-500">
                  <FileText className="w-12 h-12 mx-auto text-slate-300 mb-3" />
                  <p className="font-medium">No certificate jobs found.</p>
                  <p className="text-xs text-slate-400 mt-1">Click "Create Generation Job" to generate bulk certificates.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200">
                      <tr>
                        <th className="py-3 px-4">Event Name</th>
                        <th className="py-3 px-4">Date</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4">Progress</th>
                        <th className="py-3 px-4">Recipients</th>
                        <th className="py-3 px-4 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {jobs.map((job) => (
                        <tr key={job.job_id} className="hover:bg-slate-50 transition-colors">
                          <td className="py-3.5 px-4 font-medium text-slate-900">{job.event_name}</td>
                          <td className="py-3.5 px-4 text-slate-600">{job.event_date}</td>
                          <td className="py-3.5 px-4">{renderStatusBadge(job.status)}</td>
                          <td className="py-3.5 px-4">
                            <div className="w-32 bg-slate-100 rounded-full h-2.5 overflow-hidden">
                              <div
                                className="bg-theme-primary h-2.5 rounded-full transition-all duration-500"
                                style={{ width: `${job.progress_percentage}%` }}
                              ></div>
                            </div>
                            <span className="text-xs text-slate-500 mt-1 inline-block">{job.progress_percentage}%</span>
                          </td>
                          <td className="py-3.5 px-4 text-slate-600">
                            {job.successful_count + job.failed_count} / {job.total_recipients}
                          </td>
                          <td className="py-3.5 px-4 text-right">
                            <button
                              onClick={() => {
                                setSelectedJobId(job.job_id);
                                setActiveTab('details');
                              }}
                              className="text-xs font-semibold text-theme-primary hover:underline"
                            >
                              View Details
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* CREATE JOB TAB */}
        {activeTab === 'create' && (
          <div className="max-w-3xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-slate-900">Create Certificate Job</h2>
                <p className="text-sm text-slate-600">Enter event metadata and add recipient details for bulk PDF rendering.</p>
              </div>
              <button
                type="button"
                onClick={quickFillSampleRecipients}
                className="text-xs font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-md border border-slate-300"
              >
                Auto-fill Demo Data
              </button>
            </div>

            {formError && (
              <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-xl flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
                <p className="text-sm">{formError}</p>
              </div>
            )}

            <form onSubmit={handleCreateJob} className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">Event Name</label>
                  <input
                    type="text"
                    value={eventName}
                    onChange={(e) => setEventName(e.target.value)}
                    placeholder="e.g. Python Workshop 2026"
                    className="w-full px-3.5 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-theme-primary"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">Event Date</label>
                  <input
                    type="text"
                    value={eventDate}
                    onChange={(e) => setEventDate(e.target.value)}
                    placeholder="e.g. 2026-10-15"
                    className="w-full px-3.5 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-theme-primary"
                    required
                  />
                </div>
              </div>

              {/* Recipients List */}
              <div className="space-y-3">
                <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                  <h3 className="font-semibold text-slate-900 text-sm">Recipients ({recipients.length})</h3>
                  <button
                    type="button"
                    onClick={addRecipientRow}
                    className="text-xs font-semibold text-theme-primary hover:underline flex items-center space-x-1"
                  >
                    <PlusCircle className="w-3.5 h-3.5" />
                    <span>Add Recipient</span>
                  </button>
                </div>

                <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                  {recipients.map((recipient, idx) => (
                    <div key={idx} className="flex items-center space-x-2">
                      <input
                        type="text"
                        placeholder="Recipient Full Name"
                        value={recipient.name}
                        onChange={(e) => updateRecipient(idx, 'name', e.target.value)}
                        className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-theme-primary"
                        required
                      />
                      <input
                        type="email"
                        placeholder="recipient@example.com"
                        value={recipient.email}
                        onChange={(e) => updateRecipient(idx, 'email', e.target.value)}
                        className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-theme-primary"
                        required
                      />
                      {recipients.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeRecipientRow(idx)}
                          className="p-2 text-slate-400 hover:text-rose-600 rounded-lg"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-4 flex justify-end">
                <button
                  type="submit"
                  disabled={creating}
                  className="w-full sm:w-auto bg-theme-primary hover:bg-theme-primary-hover text-white px-6 py-2.5 rounded-lg font-semibold shadow-sm transition-all flex items-center justify-center space-x-2"
                >
                  {creating ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Creating Job...</span>
                    </>
                  ) : (
                    <>
                      <Award className="w-4 h-4" />
                      <span>Start Bulk Generation</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* JOB DETAILS TAB */}
        {activeTab === 'details' && (
          <div className="space-y-6">
            {!selectedJobId ? (
              <div className="bg-white p-12 text-center rounded-xl border border-slate-200">
                <Search className="w-12 h-12 mx-auto text-slate-300 mb-3" />
                <p className="font-semibold text-slate-800">No Job Selected</p>
                <p className="text-xs text-slate-500 mt-1">Please select a job from the Dashboard or create a new bulk job.</p>
                <button
                  onClick={() => setActiveTab('dashboard')}
                  className="mt-4 bg-theme-primary text-white text-xs font-semibold px-4 py-2 rounded-lg"
                >
                  Go to Dashboard
                </button>
              </div>
            ) : currentJob ? (
              <>
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
                    <div>
                      <div className="flex items-center space-x-3">
                        <h2 className="text-2xl font-bold text-slate-900">{currentJob.event_name}</h2>
                        {renderStatusBadge(currentJob.status)}
                      </div>
                      <p className="text-xs text-slate-500 mt-1">
                        Job ID: <code className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-700">{currentJob.job_id}</code> | Date: {currentJob.event_date}
                      </p>
                    </div>

                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => fetchJobDetails(selectedJobId)}
                        className="p-2 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-50"
                        title="Refresh Status"
                      >
                        <RefreshCw className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Progress bar */}
                  <div>
                    <div className="flex justify-between text-sm font-semibold mb-1.5">
                      <span className="text-slate-700">Generation Progress</span>
                      <span className="text-theme-primary">{currentJob.progress_percentage}%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-theme-primary h-3 rounded-full transition-all duration-500"
                        style={{ width: `${currentJob.progress_percentage}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Metric Counters */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
                    <div className="bg-slate-50 p-3 rounded-lg text-center border border-slate-200">
                      <span className="text-xs font-semibold text-slate-500 block">Total</span>
                      <span className="text-lg font-bold text-slate-900">{currentJob.total_recipients}</span>
                    </div>
                    <div className="bg-emerald-50 p-3 rounded-lg text-center border border-emerald-200">
                      <span className="text-xs font-semibold text-emerald-700 block">Successful</span>
                      <span className="text-lg font-bold text-emerald-800">{currentJob.successful_count}</span>
                    </div>
                    <div className="bg-rose-50 p-3 rounded-lg text-center border border-rose-200">
                      <span className="text-xs font-semibold text-rose-700 block">Failed</span>
                      <span className="text-lg font-bold text-rose-800">{currentJob.failed_count}</span>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-lg text-center border border-slate-200">
                      <span className="text-xs font-semibold text-slate-500 block">Pending</span>
                      <span className="text-lg font-bold text-slate-700">{currentJob.pending_count}</span>
                    </div>
                  </div>
                </div>

                {/* Certificates for Job */}
                <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
                  <div className="p-4 border-b border-slate-200">
                    <h3 className="font-semibold text-slate-900">Generated Certificates ({jobCertificates.length})</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200">
                        <tr>
                          <th className="py-3 px-4">Recipient Name</th>
                          <th className="py-3 px-4">Email</th>
                          <th className="py-3 px-4">Certificate ID</th>
                          <th className="py-3 px-4">Status</th>
                          <th className="py-3 px-4 text-right">Download</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {jobCertificates.map((cert) => (
                          <tr key={cert.id} className="hover:bg-slate-50">
                            <td className="py-3 px-4 font-medium text-slate-900">{cert.recipient_name}</td>
                            <td className="py-3 px-4 text-slate-600">{cert.recipient_email}</td>
                            <td className="py-3 px-4 font-mono text-xs text-slate-600">{cert.certificate_number}</td>
                            <td className="py-3 px-4">
                              {cert.status === 'GENERATED' && <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">GENERATED</span>}
                              {cert.status === 'FAILED' && <span className="text-xs font-semibold text-rose-700 bg-rose-50 px-2 py-0.5 rounded" title={cert.error_message || ''}>FAILED</span>}
                              {cert.status === 'PENDING' && <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded">PENDING</span>}
                            </td>
                            <td className="py-3 px-4 text-right">
                              {cert.status === 'GENERATED' ? (
                                <a
                                  href={`${API_BASE}/certificates/${cert.id}/download`}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="inline-flex items-center space-x-1 text-xs font-semibold text-theme-primary bg-theme-primary-light hover:bg-slate-200 px-2.5 py-1.5 rounded-md"
                                >
                                  <Download className="w-3.5 h-3.5" />
                                  <span>PDF</span>
                                </a>
                              ) : (
                                <span className="text-xs text-slate-400">N/A</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            ) : (
              <div className="p-8 text-center text-slate-500">Loading job status...</div>
            )}
          </div>
        )}

        {/* CERTIFICATES LIST TAB */}
        {activeTab === 'certificates' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-900">Certificates Library</h2>
              <p className="text-sm text-slate-600">Browse and download all rendered certificates.</p>
            </div>

            {selectedJobId && (
              <div className="bg-white rounded-xl border border-slate-200 p-4">
                <p className="text-sm font-semibold text-slate-800">Showing certificates for selected job ID: <code className="bg-slate-100 px-2 py-0.5 rounded">{selectedJobId}</code></p>
                <div className="mt-3 overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200">
                      <tr>
                        <th className="py-3 px-4">Recipient</th>
                        <th className="py-3 px-4">Email</th>
                        <th className="py-3 px-4">Cert Number</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {jobCertificates.map((cert) => (
                        <tr key={cert.id} className="hover:bg-slate-50">
                          <td className="py-3 px-4 font-medium text-slate-900">{cert.recipient_name}</td>
                          <td className="py-3 px-4 text-slate-600">{cert.recipient_email}</td>
                          <td className="py-3 px-4 font-mono text-xs text-slate-600">{cert.certificate_number}</td>
                          <td className="py-3 px-4">
                            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700">{cert.status}</span>
                          </td>
                          <td className="py-3 px-4 text-right">
                            {cert.status === 'GENERATED' && (
                              <a
                                href={`${API_BASE}/certificates/${cert.id}/download`}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center space-x-1 text-xs font-semibold text-white bg-theme-primary hover:bg-theme-primary-hover px-3 py-1.5 rounded-md"
                              >
                                <Download className="w-3.5 h-3.5" />
                                <span>Download PDF</span>
                              </a>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* SETTINGS / THEME TAB */}
        {activeTab === 'settings' && (
          <div className="max-w-2xl mx-auto space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-900">Admin Theme Settings</h2>
              <p className="text-sm text-slate-600">Select an enterprise light SaaS theme for the dashboard UI.</p>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
              <h3 className="font-semibold text-slate-900 text-sm">Theme Selection</h3>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {[
                  { id: 'blue', label: 'Professional Blue', accent: 'bg-blue-600', bg: 'bg-slate-50' },
                  { id: 'indigo', label: 'Modern Indigo', accent: 'bg-indigo-600', bg: 'bg-purple-50' },
                  { id: 'teal', label: 'Enterprise Teal', accent: 'bg-teal-600', bg: 'bg-teal-50' },
                ].map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setTheme(t.id as any)}
                    className={`p-4 rounded-xl border-2 text-left transition-all ${
                      theme === t.id
                        ? 'border-slate-900 ring-2 ring-slate-900/10 bg-white'
                        : 'border-slate-200 hover:border-slate-300 bg-white'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className={`w-4 h-4 rounded-full ${t.accent}`}></span>
                      {theme === t.id && <CheckCircle2 className="w-4 h-4 text-slate-900" />}
                    </div>
                    <p className="font-semibold text-sm text-slate-900">{t.label}</p>
                    <p className="text-xs text-slate-500 mt-1">Light Enterprise Theme</p>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
