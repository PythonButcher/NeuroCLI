import { X, Keyboard } from 'lucide-react'

const COMMANDS = [
  { key: 'Ctrl+R', action: 'Run prompt', result: 'Send the current prompt through the shared workflow.' },
  { key: 'Ctrl+F', action: 'Format file', result: 'Format the active target file and show a review diff.' },
  { key: 'Ctrl+A', action: 'Apply changes', result: 'Apply the reviewed proposal after creating a backup.' },
  { key: 'Ctrl+M', action: 'Model settings', result: 'Set model override and raw model options JSON.' },
  { key: 'Ctrl+O', action: 'Context manager', result: 'Attach or remove files from the prompt context stack.' },
  { key: 'Ctrl+D', action: 'Workspace radar', result: 'Open repository health, debt, and recent edit signals.' },
  { key: 'Ctrl+E', action: 'Review editor', result: 'Edit the current proposal before keeping or applying it.' },
  { key: 'Ctrl+G', action: 'Git review', result: 'Open the git status, diff, and commit workflow.' },
  { key: 'Ctrl+L', action: 'Reset view', result: 'Clear transient prompt, stream, diff, and apply state.' },
  { key: 'Ctrl+K', action: 'Commands', result: 'Open this command reference window.' },
  { key: 'Ctrl+Q', action: 'Quit', result: 'Exit NeuroCLI.' },
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
            Command Reference
          </h2>
          <button onClick={onClose} className="text-[#8b949e] transition-colors hover:text-white">
            <X size={20} />
          </button>
        </div>

        <div className="custom-scrollbar overflow-y-auto bg-[#010409] p-4">
          <table className="w-full border-collapse font-mono text-sm text-[#c9d1d9]">
            <thead>
              <tr className="border-b border-[#30363d] text-left text-xs uppercase text-[#8b949e]">
                <th className="pb-2 pr-4">Key</th>
                <th className="pb-2 pr-4">Action</th>
                <th className="pb-2">Result</th>
              </tr>
            </thead>
            <tbody>
              {COMMANDS.map((cmd, index) => (
                <tr key={index} className="border-b border-[#30363d]/50 hover:bg-[#161b22]">
                  <td className="py-2 pr-4 font-bold text-[#58a6ff]">{cmd.key}</td>
                  <td className="py-2 pr-4 text-[#c9d1d9]">{cmd.action}</td>
                  <td className="py-2 text-[#8b949e]">{cmd.result}</td>
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
