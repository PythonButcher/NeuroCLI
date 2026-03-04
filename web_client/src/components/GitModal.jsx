import { useState, useEffect } from 'react'
import { X, GitCommit, FileText, CheckCircle2, AlertCircle, Play } from 'lucide-react'

export default function GitModal({ isOpen, onClose }) {
    const [status, setStatus] = useState(null)
    const [diffs, setDiffs] = useState('')
    const [loading, setLoading] = useState(true)
    const [commitMessage, setCommitMessage] = useState('')
    const [committing, setCommitting] = useState(false)
    const [error, setError] = useState(null)

    const fetchGitData = async () => {
        setLoading(true)
        setError(null)
        try {
            const statusRes = await fetch('http://localhost:8000/api/git/status')
            const statusData = await statusRes.json()

            const diffRes = await fetch('http://localhost:8000/api/git/diff')
            const diffData = await diffRes.json()

            setStatus(statusData)
            setDiffs(diffData.diffs)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        if (isOpen) {
            fetchGitData()
            setCommitMessage('')
        }
    }, [isOpen])

    const handleCommit = async () => {
        if (!commitMessage.trim() || committing) return

        setCommitting(true)
        setError(null)

        try {
            const res = await fetch('http://localhost:8000/api/git/commit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: commitMessage })
            })
            const data = await res.json()

            if (!data.success) {
                throw new Error(data.message)
            }

            // Success!
            setCommitMessage('')
            fetchGitData() // Refresh status

            // Could optionally close here, but user might want to see the success state
            // onClose()
        } catch (err) {
            setError(err.message)
        } finally {
            setCommitting(false)
        }
    }

    const handleGenerateMsg = async () => {
        // Porting the 'Generate AI Message' feature would interact with the SSE stream 
        // or a new dedicated endpoint. For now, we'll placeholder it as it requires
        // calling the AI engine directly with the diff.
        setCommitMessage("feat: updated files based on current workspace diff")
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 sm:p-6 transition-opacity">
            <div
                className="bg-[#0d1117] border border-[#30363d] rounded-lg shadow-2xl w-full max-w-4xl flex flex-col overflow-hidden max-h-full h-[85vh]"
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-[#30363d] bg-[#161b22]">
                    <h2 className="text-[#c9d1d9] font-bold text-lg flex items-center gap-2">
                        <GitCommit className="text-[#f85149]" size={20} /> Version Control
                    </h2>
                    <button onClick={onClose} className="text-[#8b949e] hover:text-white transition-colors">
                        <X size={20} />
                    </button>
                </div>

                {/* Body Matrix */}
                <div className="flex-1 overflow-hidden flex flex-col md:flex-row">

                    {/* Left Panel: Status & Files */}
                    <div className="w-full md:w-1/3 border-b md:border-b-0 md:border-r border-[#30363d] bg-[#010409] flex flex-col overflow-hidden">
                        <div className="p-3 border-b border-[#30363d] bg-[#161b22] text-xs font-semibold text-[#8b949e] uppercase tracking-wider">
                            Working Directory
                        </div>

                        <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
                            {loading ? (
                                <div className="text-[#8b949e] text-sm animate-pulse">Running git status...</div>
                            ) : error ? (
                                <div className="text-[#f85149] text-sm flex items-start gap-2">
                                    <AlertCircle size={16} className="mt-0.5" />
                                    <span>{error}</span>
                                </div>
                            ) : (
                                <div className="space-y-4 font-mono text-sm">
                                    <div>
                                        <span className="text-[#c9d1d9] block mb-2">{status?.status_message || "Up to date."}</span>
                                    </div>

                                    {status?.unsaved_files && status.unsaved_files.length > 0 && (
                                        <div className="space-y-1">
                                            <div className="text-xs text-[#8b949e] mb-2 border-b border-[#30363d] pb-1">Uncommitted Changes:</div>
                                            {status.unsaved_files.map((file, idx) => (
                                                <div key={idx} className="flex items-center gap-2 text-[#e3b341] truncate">
                                                    <FileText size={14} className="flex-shrink-0" />
                                                    <span className="truncate">{file}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {(!status?.unsaved_files || status.unsaved_files.length === 0) && (
                                        <div className="flex items-center gap-2 text-[#3fb950] mt-4">
                                            <CheckCircle2 size={16} />
                                            <span>Nothing to commit, working tree clean</span>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right Panel: Diff View & Commit Input */}
                    <div className="flex-1 flex flex-col overflow-hidden bg-[#0d1117]">
                        {/* Diff Viewer */}
                        <div className="flex-1 overflow-y-auto p-4 custom-scrollbar bg-[#010409]">
                            {loading ? (
                                <div className="text-[#8b949e] text-sm font-mono h-full flex flex-col justify-end p-4 pb-0">
                                    <div className="w-full h-px bg-gradient-to-r from-transparent via-[#58a6ff]/50 to-transparent animate-pulse mb-2"></div>
                                    Generating diff...
                                </div>
                            ) : diffs ? (
                                <pre className="text-xs font-mono text-[#c9d1d9] whitespace-pre-wrap">
                                    {diffs.split('\n').map((line, i) => {
                                        let colorClass = 'text-[#c9d1d9]'
                                        if (line.startsWith('+') && !line.startsWith('+++')) colorClass = 'text-[#3fb950] bg-[#3fb950]/10'
                                        else if (line.startsWith('-') && !line.startsWith('---')) colorClass = 'text-[#f85149] bg-[#f85149]/10'
                                        else if (line.startsWith('@@')) colorClass = 'text-[#58a6ff]'

                                        return (
                                            <div key={i} className={`${colorClass} px-2`}>{line}</div>
                                        )
                                    })}
                                </pre>
                            ) : (
                                <div className="h-full flex items-center justify-center text-[#8b949e] italic text-sm">
                                    No changes detected in working directory.
                                </div>
                            )}
                        </div>

                        {/* Commit Form */}
                        <div className="p-4 border-t border-[#30363d] bg-[#161b22] shrink-0">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={commitMessage}
                                    onChange={(e) => setCommitMessage(e.target.value)}
                                    placeholder="Enter commit message..."
                                    className="flex-1 bg-[#010409] border border-[#30363d] rounded px-3 py-2 text-sm text-[#c9d1d9] outline-none focus:border-[#58a6ff] transition-colors font-mono"
                                    disabled={committing || (!status?.unsaved_files || status.unsaved_files.length === 0)}
                                />
                                <button
                                    onClick={handleGenerateMsg}
                                    disabled={committing || (!status?.unsaved_files || status.unsaved_files.length === 0)}
                                    className="px-3 py-2 bg-[#21262d] hover:bg-[#30363d] text-[#58a6ff] text-sm font-semibold rounded border border-[#30363d] transition-colors flex items-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed"
                                    title="Generate structured commit message with AI"
                                >
                                    <Sparkles size={16} /> Auto
                                </button>
                            </div>

                            <div className="mt-3 flex justify-between items-center">
                                <div className="text-xs text-[#8b949e]">
                                    {committing ? "Committing changes..." : "Press Commit to save current snapshot."}
                                </div>
                                <button
                                    onClick={handleCommit}
                                    disabled={!commitMessage.trim() || committing || (!status?.unsaved_files || status.unsaved_files.length === 0)}
                                    className="px-6 py-1.5 bg-[#238636] hover:bg-[#2ea043] text-white text-sm font-semibold rounded shadow-sm transition-colors flex items-center gap-1.5 disabled:bg-[#21262d] disabled:text-[#8b949e] disabled:cursor-not-allowed"
                                >
                                    <CheckCircle2 size={14} /> Commit
                                </button>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    )
}
