import { File, Trash2, X } from 'lucide-react'

export default function ContextModal({ isOpen, onClose, contextPaths, setContextPaths, onFileSelect }) {
  if (!isOpen) {
    return null
  }

  const selectedPaths = Array.from(contextPaths).sort((left, right) => left.localeCompare(right))
  const estimatedTokens = selectedPaths.length * 1500

  const removePath = (path) => {
    const nextPaths = new Set(contextPaths)
    nextPaths.delete(path)
    setContextPaths(nextPaths)
  }

  const clearAll = () => {
    setContextPaths(new Set())
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm transition-opacity sm:p-6">
      <div
        className="flex max-h-full w-full max-w-2xl flex-col overflow-hidden rounded-lg border border-[#30363d] bg-[#0d1117] shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-[#30363d] bg-[#161b22] p-4">
          <h2 className="flex items-center gap-2 text-lg font-bold text-[#c9d1d9]">
            <span className="text-xl">📎</span>
            Context Manager
          </h2>
          <button onClick={onClose} className="text-[#8b949e] transition-colors hover:text-white">
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto p-4">
          <p className="text-sm text-[#8b949e]">
            Files attached here are sent to the backend as <span className="font-mono text-[#c9d1d9]">context_paths</span>.
            Add or remove files from the tree using the paperclip control, then review the exact list here before running a prompt.
          </p>

          <div className="overflow-hidden rounded-md border border-[#30363d] bg-[#010409]">
            <div className="flex items-center justify-between border-b border-[#30363d] bg-[#161b22] p-2 text-xs font-semibold uppercase tracking-wider text-[#8b949e]">
              <span>{selectedPaths.length} Files Selected</span>
              <span>~{estimatedTokens.toLocaleString()} Tokens</span>
            </div>

            <div className="max-h-64 space-y-1 overflow-y-auto p-2">
              {selectedPaths.length === 0 ? (
                <div className="p-4 text-center text-sm italic text-[#8b949e]">Context is currently empty.</div>
              ) : (
                selectedPaths.map((path) => (
                  <div
                    key={path}
                    className="group flex items-center justify-between rounded p-2 transition-colors hover:bg-[#30363d]"
                  >
                    <div
                      className="flex cursor-pointer items-center gap-2 overflow-hidden"
                      onClick={() => onFileSelect?.(path)}
                    >
                      <File size={14} className="flex-shrink-0 text-[#8b949e]" />
                      <span className="truncate font-mono text-sm text-[#c9d1d9]">{path}</span>
                    </div>
                    <button
                      onClick={() => removePath(path)}
                      className="p-1 text-[#8b949e] transition-all hover:text-[#f85149] group-hover:opacity-100"
                    >
                      <X size={14} />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between border-t border-[#30363d] bg-[#161b22] p-4">
          <button
            onClick={clearAll}
            disabled={selectedPaths.length === 0}
            className="flex items-center gap-2 rounded px-3 py-1.5 text-sm text-[#f85149] transition-colors hover:bg-[#f85149]/10 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Trash2 size={14} />
            Clear All
          </button>

          <button
            onClick={onClose}
            className="rounded border border-[#30363d] bg-[#21262d] px-4 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-[#30363d]"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  )
}
