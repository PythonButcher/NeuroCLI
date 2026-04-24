import { X, Bot } from 'lucide-react'

export default function ModelModal({ isOpen, onClose }) {
    if (!isOpen) return null

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 transition-opacity">
            <div
                className="bg-[#0d1117] border border-[#30363d] rounded-lg shadow-2xl w-full max-w-sm flex flex-col overflow-hidden"
                onClick={e => e.stopPropagation()}
            >
                <div className="flex items-center justify-between p-4 border-b border-[#30363d] bg-[#161b22]">
                    <h2 className="text-[#c9d1d9] font-bold text-lg flex items-center gap-2">
                        <Bot size={20} className="text-[#f85149]" /> AI Engine
                    </h2>
                    <button onClick={onClose} className="text-[#8b949e] hover:text-white transition-colors">
                        <X size={20} />
                    </button>
                </div>

                <div className="p-6 space-y-4">
                    <p className="text-sm text-[#8b949e] leading-relaxed">
                        Support for selecting between Gemini Pro, Claude, and internal OpenAI models will be implemented in the next major patch.
                    </p>
                    <div className="text-xs text-[#58a6ff] bg-[#58a6ff]/10 border border-[#58a6ff]/20 p-2 rounded text-center font-mono">
                        Currently Routing to Default Model
                    </div>
                </div>

                <div className="p-4 border-t border-[#30363d] bg-[#161b22] flex justify-end">
                    <button onClick={onClose} className="px-4 py-1.5 bg-[#21262d] hover:bg-[#30363d] text-white text-sm font-semibold rounded border border-[#30363d] transition-colors">
                        Got it
                    </button>
                </div>
            </div>
        </div>
    )
}
