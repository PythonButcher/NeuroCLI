import { useState, useEffect } from 'react'
import { X, File, Folder, Trash2 } from 'lucide-react'

export default function ContextModal({ isOpen, onClose, contextPaths, setContextPaths, onFileSelect }) {
    const [availableFiles, setAvailableFiles] = useState([])
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        if (isOpen) {
            // In a real app we might want to fetch a flattened list of files from the backend,
            // or just re-use the tree data. For simplicity, we just manage the selected set here.
        }
    }, [isOpen])

    if (!isOpen) return null

    const removePath = (path) => {
        const newPaths = new Set(contextPaths)
        newPaths.delete(path)
        setContextPaths(newPaths)
    }

    const clearAll = () => {
        setContextPaths(new Set())
    }

    // Calculate generic token count based on typical ~4 chars per token rule of thumb
    // Since we aren't fetching contents here immediately, we just use a placeholder
    const estimatedTokens = contextPaths.size * 1500

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 sm:p-6 transition-opacity">
            <div
                className="bg-[#0d1117] border border-[#30363d] rounded-lg shadow-2xl w-full max-w-2xl flex flex-col overflow-hidden max-h-full"
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-[#30363d] bg-[#161b22]">
                    <h2 className="text-[#c9d1d9] font-bold text-lg flex items-center gap-2">
                        <span className="text-xl">📎</span> Context Manager
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-[#8b949e] hover:text-white transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Body */}
                <div className="p-4 flex-1 overflow-y-auto space-y-4">
                    <p className="text-sm text-[#8b949e]">
                        Files in context are included with your prompt when querying the AI model.
                        Select files from the Left Sidebar to add them here (Integration coming).
                    </p>

                    <div className="bg-[#010409] border border-[#30363d] rounded-md overflow-hidden">
                        <div className="flex items-center justify-between p-2 border-b border-[#30363d] bg-[#161b22] text-xs font-semibold text-[#8b949e] uppercase tracking-wider">
                            <span>{contextPaths.size} Files Selected</span>
                            <span>~{estimatedTokens.toLocaleString()} Tokens</span>
                        </div>

                        <div className="p-2 space-y-1 max-h-64 overflow-y-auto">
                            {contextPaths.size === 0 ? (
                                <div className="p-4 text-center text-[#8b949e] italic text-sm">
                                    Context is currently empty.
                                </div>
                            ) : (
                                Array.from(contextPaths).map(path => (
                                    <div key={path} className="flex items-center justify-between p-2 hover:bg-[#30363d] rounded group transition-colors">
                                        <div className="flex items-center gap-2 overflow-hidden cursor-pointer" onClick={() => onFileSelect && onFileSelect(path)}>
                                            <File size={14} className="text-[#8b949e] flex-shrink-0" />
                                            <span className="text-sm text-[#c9d1d9] truncate font-mono">{path}</span>
                                        </div>
                                        <button
                                            onClick={() => removePath(path)}
                                            className="text-[#8b949e] hover:text-[#f85149] opacity-0 group-hover:opacity-100 transition-all p-1"
                                        >
                                            <X size={14} />
                                        </button>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-[#30363d] flex justify-between items-center bg-[#161b22]">
                    <button
                        onClick={clearAll}
                        disabled={contextPaths.size === 0}
                        className="flex items-center gap-2 px-3 py-1.5 text-sm text-[#f85149] hover:bg-[#f85149]/10 disabled:opacity-50 disabled:cursor-not-allowed rounded transition-colors"
                    >
                        <Trash2 size={14} /> Clear All
                    </button>

                    <button
                        onClick={onClose}
                        className="px-4 py-1.5 bg-[#21262d] hover:bg-[#30363d] text-white text-sm font-semibold rounded border border-[#30363d] transition-colors"
                    >
                        Done
                    </button>
                </div>
            </div>
        </div>
    )
}
