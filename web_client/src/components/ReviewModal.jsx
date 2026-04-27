import { useState, useEffect } from 'react'
import { X, Compass, Search, FileDiff, FlaskConical, Zap, Save, CheckCircle2, RotateCcw } from 'lucide-react'

export default function ReviewModal({
  isOpen,
  onClose,
  targetFile,
  proposedContent,
  onApply,
  setProposedContent
}) {
  const [localContent, setLocalContent] = useState('')

  useEffect(() => {
    if (isOpen) {
      setLocalContent(proposedContent || initialEditorText())
    }
  }, [isOpen, proposedContent])

  const initialEditorText = () => {
    return (
      "No editable proposal is ready yet.\n\n" +
      "Run a file-targeted prompt or format a selected file first, then reopen Review."
    )
  }

  if (!isOpen) return null

  const hasProposal = Boolean(proposedContent)
  const lineCount = localContent ? localContent.split('\n').length : 0
  const fileName = targetFile ? targetFile.split(/[\\/]/).pop() : 'none'

  const handleReset = () => {
    setLocalContent(proposedContent || initialEditorText())
  }

  const handleKeep = () => {
    setProposedContent(localContent)
    onClose()
  }

  const handleApply = () => {
    setProposedContent(localContent)
    onApply(localContent)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm transition-opacity sm:p-6">
      <div
        className="flex h-[85vh] max-h-full w-full max-w-5xl flex-col overflow-hidden rounded-lg border border-[#30363d] bg-[#0d1117] shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#30363d] bg-[#161b22] p-4">
          <h2 className="flex items-center gap-2 text-lg font-bold text-[#c9d1d9]">
            <Compass className="text-[#58a6ff]" size={20} />
            Review Editor
          </h2>
          <button onClick={onClose} className="text-[#8b949e] transition-colors hover:text-white">
            <X size={20} />
          </button>
        </div>

        {/* Metadata Row */}
        <div className="flex items-center justify-between border-b border-[#30363d] bg-[#010409] px-4 py-2 text-xs font-mono">
          <div className="font-bold text-[#c9d1d9]">Target: {fileName}</div>
          <div className="text-[#8b949e]">
            Proposal: {hasProposal ? `editable draft, ${lineCount.toLocaleString()} lines` : 'not ready'}
          </div>
        </div>

        {/* Future Actions Row (Disabled) */}
        <div className="flex items-center gap-4 border-b border-[#30363d] border-dashed bg-[#0d1117] px-4 py-2">
          <button disabled className="flex items-center gap-1.5 text-xs text-[#8b949e] opacity-50 cursor-not-allowed">
            <Search size={14} /> Find
          </button>
          <button disabled className="flex items-center gap-1.5 text-xs text-[#8b949e] opacity-50 cursor-not-allowed">
            <FileDiff size={14} /> Diff
          </button>
          <button disabled className="flex items-center gap-1.5 text-xs text-[#8b949e] opacity-50 cursor-not-allowed">
            <FlaskConical size={14} /> Tests
          </button>
          <button disabled className="flex items-center gap-1.5 text-xs text-[#8b949e] opacity-50 cursor-not-allowed">
            <Zap size={14} /> Explain
          </button>
        </div>

        {/* Main Editor Area */}
        <div className="flex-1 overflow-hidden bg-[#010409]">
          <textarea
            value={localContent}
            onChange={(e) => setLocalContent(e.target.value)}
            className="h-full w-full resize-none bg-transparent p-4 font-mono text-sm text-[#c9d1d9] outline-none"
            spellCheck="false"
          />
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-3 border-t border-[#30363d] bg-[#161b22] p-4">
          <button
            onClick={onClose}
            className="rounded border border-[#30363d] px-4 py-1.5 text-sm font-semibold text-[#f85149] transition-colors hover:bg-[#f85149]/10"
          >
            Cancel
          </button>
          <button
            onClick={handleReset}
            className="flex items-center gap-1.5 rounded border border-[#30363d] px-4 py-1.5 text-sm font-semibold text-[#e3b341] transition-colors hover:bg-[#e3b341]/10"
          >
            <RotateCcw size={14} />
            Reset Draft
          </button>
          <button
            onClick={handleKeep}
            disabled={!hasProposal}
            className="flex items-center gap-1.5 rounded border border-[#30363d] px-4 py-1.5 text-sm font-semibold text-[#58a6ff] transition-colors hover:bg-[#58a6ff]/10 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent"
          >
            <Save size={14} />
            Keep Draft
          </button>
          <button
            onClick={handleApply}
            disabled={!hasProposal}
            className="flex items-center gap-1.5 rounded bg-[#238636] px-6 py-1.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-[#2ea043] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <CheckCircle2 size={14} />
            Apply Edited
          </button>
        </div>
      </div>
    </div>
  )
}
