import { X, Settings as SettingsIcon } from 'lucide-react'

export default function SettingsModal({ isOpen, onClose }) {
    if (!isOpen) return null

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 transition-opacity">
            <div
                className="bg-[#0d1117] border border-[#30363d] rounded-lg shadow-2xl w-full max-w-lg flex flex-col overflow-hidden"
                onClick={e => e.stopPropagation()}
            >
                <div className="flex items-center justify-between p-4 border-b border-[#30363d] bg-[#161b22]">
                    <h2 className="text-[#c9d1d9] font-bold text-lg flex items-center gap-2">
                        <SettingsIcon size={20} className="text-[#8b949e]" /> Settings
                    </h2>
                    <button onClick={onClose} className="text-[#8b949e] hover:text-white transition-colors">
                        <X size={20} />
                    </button>
                </div>

                <div className="p-6 text-[#8b949e] italic text-center text-sm font-mono border-b border-[#30363d]">
                    Application settings, custom instructions, and API keys will be configurable here in a future update.
                </div>

                <div className="p-4 bg-[#161b22] flex justify-end">
                    <button onClick={onClose} className="px-4 py-1.5 bg-[#21262d] hover:bg-[#30363d] text-white text-sm font-semibold rounded border border-[#30363d] transition-colors">
                        Close
                    </button>
                </div>
            </div>
        </div>
    )
}
