import { useEffect, useState } from 'react'
import { AlertCircle, CheckCircle2, FileText, GitCommit, X } from 'lucide-react'
import { fetchJson, postJson } from '../lib/api'

export default function GitModal({ isOpen, onClose }) {
  const [status, setStatus] = useState(null)
  const [diffs, setDiffs] = useState('')
  const [loading, setLoading] = useState(true)
  const [commitMessage, setCommitMessage] = useState('')
  const [committing, setCommitting] = useState(false)
  const [error, setError] = useState(null)
  const [successMessage, setSuccessMessage] = useState('')

  const fetchGitData = async () => {
    setLoading(true)
    setError(null)

    try {
      const [statusData, diffData] = await Promise.all([
        fetchJson('/api/git/status'),
        fetchJson('/api/git/diff'),
      ])

      setStatus(statusData)
      setDiffs(diffData.diffs || '')
    } catch (fetchError) {
      setError(fetchError.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!isOpen) {
      return
    }

    setCommitMessage('')
    setSuccessMessage('')
    fetchGitData()
  }, [isOpen])

  const handleCommit = async () => {
    if (!commitMessage.trim() || committing) {
      return
    }

    setCommitting(true)
    setError(null)
    setSuccessMessage('')

    try {
      const data = await postJson('/api/git/commit', { message: commitMessage })
      if (!data.success) {
        throw new Error(data.message)
      }

      setSuccessMessage(data.message)
      setCommitMessage('')
      await fetchGitData()
    } catch (commitError) {
      setError(commitError.message)
    } finally {
      setCommitting(false)
    }
  }

  if (!isOpen) {
    return null
  }

  const hasChanges = Boolean(status?.unsaved_files?.length)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm transition-opacity sm:p-6">
      <div
        className="flex h-[85vh] max-h-full w-full max-w-4xl flex-col overflow-hidden rounded-lg border border-[#30363d] bg-[#0d1117] shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-[#30363d] bg-[#161b22] p-4">
          <h2 className="flex items-center gap-2 text-lg font-bold text-[#c9d1d9]">
            <GitCommit className="text-[#f85149]" size={20} />
            Version Control
          </h2>
          <button onClick={onClose} className="text-[#8b949e] transition-colors hover:text-white">
            <X size={20} />
          </button>
        </div>

        <div className="flex flex-1 flex-col overflow-hidden md:flex-row">
          <div className="flex w-full flex-col overflow-hidden border-b border-[#30363d] bg-[#010409] md:w-1/3 md:border-b-0 md:border-r">
            <div className="border-b border-[#30363d] bg-[#161b22] p-3 text-xs font-semibold uppercase tracking-wider text-[#8b949e]">
              Working Directory
            </div>

            <div className="custom-scrollbar flex-1 overflow-y-auto p-4">
              {loading ? (
                <div className="text-sm text-[#8b949e] animate-pulse">Running git status...</div>
              ) : error ? (
                <div className="flex items-start gap-2 text-sm text-[#f85149]">
                  <AlertCircle size={16} className="mt-0.5" />
                  <span>{error}</span>
                </div>
              ) : (
                <div className="space-y-4 font-mono text-sm">
                  <div>
                    <span className="mb-2 block text-[#c9d1d9]">{status?.status_message || 'Up to date.'}</span>
                  </div>

                  {successMessage && (
                    <div className="rounded border border-[#3fb950]/30 bg-[#3fb950]/10 p-2 text-[#3fb950]">
                      {successMessage}
                    </div>
                  )}

                  {hasChanges ? (
                    <div className="space-y-1">
                      <div className="mb-2 border-b border-[#30363d] pb-1 text-xs text-[#8b949e]">
                        Uncommitted Changes:
                      </div>
                      {status.unsaved_files.map((file, index) => (
                        <div key={index} className="flex items-center gap-2 truncate text-[#e3b341]">
                          <FileText size={14} className="flex-shrink-0" />
                          <span className="truncate">{file}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="mt-4 flex items-center gap-2 text-[#3fb950]">
                      <CheckCircle2 size={16} />
                      <span>Nothing to commit, working tree clean</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="flex flex-1 flex-col overflow-hidden bg-[#0d1117]">
            <div className="custom-scrollbar flex-1 overflow-y-auto bg-[#010409] p-4">
              {loading ? (
                <div className="flex h-full flex-col justify-end p-4 pb-0 font-mono text-sm text-[#8b949e]">
                  <div className="mb-2 h-px w-full animate-pulse bg-gradient-to-r from-transparent via-[#58a6ff]/50 to-transparent"></div>
                  Generating diff...
                </div>
              ) : diffs ? (
                <pre className="whitespace-pre-wrap text-xs font-mono text-[#c9d1d9]">
                  {diffs.split('\n').map((line, index) => {
                    let colorClass = 'text-[#c9d1d9]'
                    if (line.startsWith('+') && !line.startsWith('+++')) {
                      colorClass = 'bg-[#3fb950]/10 text-[#3fb950]'
                    } else if (line.startsWith('-') && !line.startsWith('---')) {
                      colorClass = 'bg-[#f85149]/10 text-[#f85149]'
                    } else if (line.startsWith('@@')) {
                      colorClass = 'text-[#58a6ff]'
                    }

                    return (
                      <div key={index} className={`${colorClass} px-2`}>
                        {line}
                      </div>
                    )
                  })}
                </pre>
              ) : (
                <div className="flex h-full items-center justify-center text-sm italic text-[#8b949e]">
                  No changes detected in working directory.
                </div>
              )}
            </div>

            <div className="shrink-0 border-t border-[#30363d] bg-[#161b22] p-4">
              <div className="space-y-2">
                <input
                  type="text"
                  value={commitMessage}
                  onChange={(event) => setCommitMessage(event.target.value)}
                  placeholder="Enter commit message..."
                  className="w-full rounded border border-[#30363d] bg-[#010409] px-3 py-2 font-mono text-sm text-[#c9d1d9] outline-none transition-colors focus:border-[#58a6ff]"
                  disabled={committing || !hasChanges}
                />

                <div className="text-xs text-[#8b949e]">
                  The web client uses the backend git endpoints directly. AI-generated commit messages are not part of the current backend contract.
                </div>
              </div>

              <div className="mt-3 flex items-center justify-between">
                <div className="text-xs text-[#8b949e]">
                  {committing ? 'Committing changes...' : 'Press Commit to save the current snapshot.'}
                </div>
                <button
                  onClick={handleCommit}
                  disabled={!commitMessage.trim() || committing || !hasChanges}
                  className="flex items-center gap-1.5 rounded bg-[#238636] px-6 py-1.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-[#2ea043] disabled:cursor-not-allowed disabled:bg-[#21262d] disabled:text-[#8b949e]"
                >
                  <CheckCircle2 size={14} />
                  Commit
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
