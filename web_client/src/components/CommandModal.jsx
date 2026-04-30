import { X, Keyboard } from 'lucide-react'

const ACTIONS = [
  { label: 'Run', description: 'Send the current prompt through the shared workflow.' },
  { label: 'Format', description: 'Format the active target file and show a review diff.' },
  { label: 'Review', description: 'Edit the current proposal before keeping or applying it.' },
  { label: 'Commit', description: 'Open the git status, diff, and commit workflow.' },
  { label: 'Radar', description: 'Open repository health, debt, and recent edit signals.' },
  { label: 'Model', description: 'Set model override and raw model options JSON.' },
  { label: 'Context', description: 'Attach or remove files from the prompt context stack.' },
  { label: 'Clear', description: 'Clear transient prompt, stream, diff, and apply state.' },
  { label: 'Commands', description: 'Open this action reference window.' },
]

export default function CommandModal({ isOpen, onClose }) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm transition-opacity sm:p-6">
      <div
        className="flex max-h-full w-full max-w-2xl flex-col overflow-hidden rounded-lg border border-[#30363d] bg-[#0d1117] shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-[#30363d] bg-[#161b22] p-4">
          <h2 className="flex items-center gap-2 text-lg font-bold text-[#c9d1d9]">
            <Keyboard className="text-[#58a6ff]" size={20} />
            Action Reference
          </h2>
          <button onClick={onClose} className="text-[#8b949e] transition-colors hover:text-white">
            <X size={20} />
          </button>
        </div>

        <div className="custom-scrollbar overflow-y-auto bg-[#010409] p-4">
          <table className="w-full border-collapse font-mono text-sm text-[#c9d1d9]">
            <thead>
              <tr className="border-b border-[#30363d] text-left text-xs uppercase text-[#8b949e]">
                <th className="pb-2 pr-4">Action</th>
                <th className="pb-2">What it does</th>
              </tr>
            </thead>
            <tbody>
              {ACTIONS.map((action, index) => (
                <tr key={index} className="border-b border-[#30363d]/50 hover:bg-[#161b22]">
                  <td className="py-2 pr-4 font-bold text-[#58a6ff] whitespace-nowrap">{action.label}</td>
                  <td className="py-2 text-[#8b949e]">{action.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-end border-t border-[#30363d] bg-[#161b22] p-4">
          <button
            onClick={onClose}
            className="rounded border border-[#30363d] px-6 py-1.5 text-sm font-semibold text-[#f85149] transition-colors hover:bg-[#f85149]/10"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
