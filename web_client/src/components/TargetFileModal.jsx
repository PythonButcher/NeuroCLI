import { X } from 'lucide-react'
import FileTree from './FileTree'

export default function TargetFileModal({
  isOpen,
  onClose,
  onFileSelect,
  targetFile,
}) {
  if (!isOpen) {
    return null
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm transition-opacity sm:p-6">
      <div
        className="flex h-[80vh] max-h-full w-full max-w-3xl flex-col overflow-hidden rounded-lg border border-[#30363d] bg-[#0d1117] shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-[#30363d] bg-[#161b22] p-4">
          <div>
            <h2 className="text-lg font-bold text-[#c9d1d9]">Browse Target File</h2>
            <p className="text-sm text-[#8b949e]">
              Choose the file to send as <span className="font-mono text-[#c9d1d9]">target_file</span>.
            </p>
          </div>
          <button onClick={onClose} className="text-[#8b949e] transition-colors hover:text-white">
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-hidden">
          <FileTree
            onFileSelect={(path) => {
              onFileSelect(path)
              onClose()
            }}
            onToggleContextPath={null}
            contextPaths={new Set()}
            targetFile={targetFile}
            showContextToggle={false}
          />
        </div>

        <div className="flex justify-end border-t border-[#30363d] bg-[#161b22] p-4">
          <button
            onClick={onClose}
            className="rounded border border-[#30363d] bg-[#21262d] px-4 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-[#30363d]"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
