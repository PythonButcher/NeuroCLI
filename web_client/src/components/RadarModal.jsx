import { useState, useEffect } from 'react'
import { X, Activity, Code, Clock, AlertTriangle } from 'lucide-react'
import { fetchJson } from '../lib/api'

export default function RadarModal({ isOpen, onClose }) {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (isOpen) {
            setLoading(true)
            setError(null)
            fetchJson('/api/radar')
                .then(data => {
                    if (data.error) throw new Error(data.error)
                    setData(data)
                    setLoading(false)
                })
                .catch(err => {
                    setError(err.message)
                    setLoading(false)
                })
        }
    }, [isOpen])

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 sm:p-6 transition-opacity">
            <div
                className="bg-[#0d1117] border border-[#30363d] rounded-lg shadow-2xl w-full max-w-5xl flex flex-col overflow-hidden max-h-full"
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-[#30363d] bg-[#161b22]">
                    <h2 className="text-[#c9d1d9] font-bold text-lg flex items-center gap-2">
                        <Activity className="text-[#3fb950]" size={20} /> Workspace Radar
                    </h2>
                    <button onClick={onClose} className="text-[#8b949e] hover:text-white transition-colors">
                        <X size={20} />
                    </button>
                </div>

                {/* Body */}
                <div className="p-4 flex-1 overflow-y-auto w-full custom-scrollbar">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center h-64 text-[#8b949e] font-mono">
                            <Activity size={32} className="animate-pulse text-[#58a6ff] mb-4" />
                            Scanning Workspace...
                        </div>
                    ) : error ? (
                        <div className="text-[#f85149] p-4 text-center border border-[#f85149]/30 rounded bg-[#f85149]/10">
                            Error loading radar data: {error}
                        </div>
                    ) : data ? (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 font-mono text-sm view-fade-in">

                            {/* Top Left: Code Composition */}
                            <div className="border border-[#30363d] rounded bg-[#010409] overflow-hidden flex flex-col">
                                <div className="p-3 border-b border-[#30363d] bg-[#161b22] font-semibold text-[#c9d1d9] flex items-center gap-2">
                                    <Code size={16} className="text-[#58a6ff]" /> Code Composition
                                    <span className="text-xs text-[#8b949e] ml-auto font-normal">
                                        Total: {data.health.total_loc.toLocaleString()} LOC
                                    </span>
                                </div>
                                <div className="p-4 space-y-3 overflow-y-auto">
                                    {Object.entries(data.health.composition || {}).length > 0 ? (
                                        Object.entries(data.health.composition).map(([lang, stats]) => {
                                            const pct = stats.percentage || 0
                                            return (
                                                <div key={lang} className="mb-2">
                                                    <div className="flex justify-between text-xs mb-1">
                                                        <span className="font-bold text-[#c9d1d9]">{lang}</span>
                                                        <span className="text-[#8b949e]">{stats.loc.toLocaleString()} lines ({pct.toFixed(1)}%)</span>
                                                    </div>
                                                    <div className="h-1.5 w-full bg-[#21262d] rounded overflow-hidden flex">
                                                        <div
                                                            className="h-full bg-gradient-to-r from-[#58a6ff] to-[#3fb950]"
                                                            style={{ width: `${pct}%` }}
                                                        ></div>
                                                    </div>
                                                </div>
                                            )
                                        })
                                    ) : (
                                        <div className="text-[#8b949e] text-center italic py-4">No code composition data available.</div>
                                    )}
                                </div>
                            </div>

                            {/* Top Right: Technical Debt */}
                            <div className="border border-[#30363d] rounded bg-[#010409] overflow-hidden flex flex-col">
                                <div className="p-3 border-b border-[#30363d] bg-[#161b22] font-semibold text-[#c9d1d9] flex items-center gap-2">
                                    <AlertTriangle size={16} className="text-[#e3b341]" /> Technical Debt
                                    <span className="text-xs text-[#8b949e] ml-auto font-normal">
                                        {data.debt?.length || 0} issues
                                    </span>
                                </div>
                                <div className="overflow-y-auto flex-1 h-64">
                                    {data.debt && data.debt.length > 0 ? (
                                        <table className="w-full text-left border-collapse">
                                            <thead className="bg-[#161b22] sticky top-0 text-xs text-[#8b949e] border-b border-[#30363d]">
                                                <tr>
                                                    <th className="py-2 px-3 font-normal">File</th>
                                                    <th className="py-2 px-3 font-normal">Line</th>
                                                    <th className="py-2 px-3 font-normal">Message</th>
                                                </tr>
                                            </thead>
                                            <tbody className="text-xs text-[#c9d1d9]">
                                                {data.debt.map((item, i) => (
                                                    <tr key={i} className="border-b border-[#30363d]/50 hover:bg-[#21262d] transition-colors">
                                                        <td className="py-2 px-3 align-top truncate max-w-[120px]" title={item.file_name}>{item.file_name}</td>
                                                        <td className="py-2 px-3 align-top whitespace-nowrap text-[#8b949e]">{item.line_number}</td>
                                                        <td className="py-2 px-3 align-top text-[#e3b341]">{item.message}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    ) : (
                                        <div className="flex items-center justify-center h-full text-[#8b949e] italic p-4 text-center">
                                            Workspace looks clean! No technical debt detected.
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Bottom (Full Width): Recent Edits Heatmap */}
                            <div className="border border-[#30363d] rounded bg-[#010409] overflow-hidden lg:col-span-2 flex flex-col">
                                <div className="p-3 border-b border-[#30363d] bg-[#161b22] font-semibold text-[#c9d1d9] flex items-center gap-2">
                                    <Clock size={16} className="text-[#a371f7]" /> Recent AI Edits
                                </div>
                                <div className="overflow-y-auto max-h-64">
                                    {data.edits && data.edits.length > 0 ? (
                                        <table className="w-full text-left border-collapse">
                                            <thead className="bg-[#161b22] sticky top-0 text-xs text-[#8b949e] border-b border-[#30363d]">
                                                <tr>
                                                    <th className="py-2 px-4 font-normal">File</th>
                                                    <th className="py-2 px-4 font-normal">Last Edited</th>
                                                </tr>
                                            </thead>
                                            <tbody className="text-xs text-[#c9d1d9]">
                                                {data.edits.map((item, i) => (
                                                    <tr key={i} className="border-b border-[#30363d]/50 hover:bg-[#21262d] transition-colors">
                                                        <td className="py-2 px-4 select-all text-[#a371f7]">{item.original_file}</td>
                                                        <td className="py-2 px-4 whitespace-nowrap text-[#8b949e]">{item.time_ago}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    ) : (
                                        <div className="p-6 text-center text-[#8b949e] italic">
                                            No recent AI edits found in the backup directory tracking system.
                                        </div>
                                    )}
                                </div>
                            </div>

                        </div>
                    ) : null}
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-[#30363d] flex justify-end items-center bg-[#161b22]">
                    <button
                        onClick={onClose}
                        className="px-4 py-1.5 bg-[#21262d] hover:bg-[#30363d] text-white text-sm font-semibold rounded border border-[#30363d] transition-colors"
                    >
                        Close Radar
                    </button>
                </div>
            </div>
        </div>
    )
}
