import { useState, useRef, useEffect } from 'react'
import FileTree from './components/FileTree'
import ContextModal from './components/ContextModal'
import RadarModal from './components/RadarModal'
import GitModal from './components/GitModal'
import SettingsModal from './components/SettingsModal'
import ModelModal from './components/ModelModal'
import {
  RefreshCcw, Settings, Trash2, Bot, Paperclip,
  Activity, GitCommit, Play, Sparkles
} from 'lucide-react'

const API_BASE_URL = 'http://127.0.0.1:8010'

function App() {
  const [history, setHistory] = useState([
    { type: 'system', content: 'NeuroCLI v2.0.0 - Web Integrated Environment initialized...' },
    { type: 'system', content: 'Type "help" for a list of available commands.' }
  ])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)

  // New State for Phase 3 Features
  const [targetFile, setTargetFile] = useState('')
  const [proposedContent, setProposedContent] = useState('')
  const [showApplyBtn, setShowApplyBtn] = useState(false)

  // New State for Phase 4 Context Modal
  const [isContextModalOpen, setIsContextModalOpen] = useState(false)
  const [contextPaths, setContextPaths] = useState(new Set())

  // New State for Radar Modal
  const [isRadarModalOpen, setIsRadarModalOpen] = useState(false)

  // New State for Git Modal
  const [isGitModalOpen, setIsGitModalOpen] = useState(false)

  // New State for Placeholders
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false)
  const [isModelModalOpen, setIsModelModalOpen] = useState(false)

  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history])

  const handleCommand = async (e) => {
    e.preventDefault()
    if (!input.trim() || isStreaming) return

    const userCmd = input.trim()

    // Add user command to history and initialize an empty bot response
    setHistory(prev => [
      ...prev,
      { type: 'user', content: userCmd },
      { type: 'bot', content: '' }
    ])
    setInput('')
    setIsStreaming(true)

    try {
      const eventSource = new EventSource(`${API_BASE_URL}/stream?command=${encodeURIComponent(userCmd)}`)

      eventSource.onmessage = (event) => {
        const newData = JSON.parse(event.data)

        // Update the last history item (the bot response) with new stream text
        setHistory(prev => {
          const newHistory = [...prev]
          const lastItem = newHistory[newHistory.length - 1]
          if (lastItem.type === 'bot') {
            lastItem.content += newData
          }
          return newHistory
        })
      }

      eventSource.onerror = (error) => {
        console.error("EventSource failed:", error)
        eventSource.close()
        setIsStreaming(false)
      }

      // We need a way to detect stream end. 
      // Standard SSE from Starlette closes connection when generator exhausted.
      // So listen to close/error to stop stream.
      // In a real app we might send a specific {"done": true} message.
      // Let's rely on standard logic where the generator completion closes the connection.
      // The `onerror` handler captures the disconnection usually but we can add:
      eventSource.addEventListener('close', () => {
        eventSource.close()
        setIsStreaming(false)
      })

    } catch (err) {
      setHistory(prev => {
        const newHistory = [...prev]
        newHistory[newHistory.length - 1] = {
          type: 'error',
          content: `Connection to backend failed. Error: ${err.message}`
        }
        return newHistory
      })
      setIsStreaming(false)
    }
  }

  const handleFileSelect = async (path) => {
    setTargetFile(path)
    setProposedContent('')
    setShowApplyBtn(false)

    try {
      const res = await fetch(`${API_BASE_URL}/api/file?path=${encodeURIComponent(path)}`)
      const data = await res.json()

      if (data.error) throw new Error(data.error)

      setHistory(prev => [...prev, {
        type: 'system',
        content: `### Viewing: ${path.split('\\').pop() || path.split('/').pop()}\n\n\`\`\`\n${data.content}\n\`\`\``
      }])
    } catch (err) {
      setHistory(prev => [...prev, { type: 'error', content: `Failed to open file: ${err.message}` }])
    }
  }

  const handleFormat = async () => {
    if (!targetFile) {
      setHistory(prev => [...prev, { type: 'error', content: 'Please select a valid file to format first.' }])
      return
    }

    setHistory(prev => [...prev, { type: 'system', content: `Formatting ${targetFile}...` }])

    try {
      const res = await fetch(`${API_BASE_URL}/api/format`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: targetFile })
      })
      const data = await res.json()

      if (data.error) throw new Error(data.error)

      if (data.status === 'no_change') {
        setHistory(prev => [...prev, { type: 'system', content: 'No formatting needed.' }])
        setProposedContent('')
        setShowApplyBtn(false)
      } else {
        setHistory(prev => [...prev, { type: 'system', content: data.diff }])
        setProposedContent(data.proposed_content)
        setShowApplyBtn(true)
      }
    } catch (err) {
      setHistory(prev => [...prev, { type: 'error', content: `Formatter Error: ${err.message}` }])
    }
  }

  const handleApply = async () => {
    if (!targetFile || !proposedContent) return

    try {
      const res = await fetch(`${API_BASE_URL}/api/apply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: targetFile, content: proposedContent })
      })
      const data = await res.json()

      if (data.error) throw new Error(data.error)

      setHistory(prev => [...prev, { type: 'system', content: data.message }])
      setProposedContent('')
      setShowApplyBtn(false)

      // Optionally reload the file content
      handleFileSelect(targetFile)
    } catch (err) {
      setHistory(prev => [...prev, { type: 'error', content: `Apply Error: ${err.message}` }])
    }
  }

  return (
    <div className="flex h-screen w-full bg-[#010409] text-[#c9d1d9] font-mono leading-relaxed overflow-hidden">

      {/* LEFT SIDEBAR (File Tree + Reset) */}
      <div className="w-64 flex flex-col border-r border-[#30363d] bg-[#0d1117] flex-shrink-0 z-20">
        <div className="p-3 border-b border-[#30363d] font-bold text-[#58a6ff] tracking-wide text-sm select-none">
          NeuroCLI
        </div>

        <div className="flex-1 overflow-hidden">
          <FileTree onFileSelect={handleFileSelect} contextPaths={contextPaths} />
        </div>

        <div className="p-3 border-t border-[#30363d]">
          <button
            className="w-full flex items-center justify-center py-1.5 px-3 bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] rounded border border-[#30363d] transition-colors text-sm font-medium"
            onClick={() => setHistory([{ type: 'system', content: 'Console reset.' }])}
          >
            <RefreshCcw size={14} className="mr-2" />
            Reset
          </button>
        </div>
      </div>

      {/* MAIN WORKSPACE */}
      <div className="flex-1 flex flex-col h-full bg-[#0d1117] relative overflow-hidden">
        {/* Header Pane */}
        <header className="flex items-center justify-between border-b border-[#30363d] p-3 shadow-sm bg-[#0d1117] z-10 shrink-0">
          <div className="text-xs text-[#8b949e] font-semibold tracking-widest uppercase ml-2 flex items-center gap-3">
            <div className="flex items-center gap-1.5 mr-2">
              <div className="w-2.5 h-2.5 rounded-full bg-red-500 shadow-[0_0_6px_rgba(239,68,68,0.5)]"></div>
              <div className="w-2.5 h-2.5 rounded-full bg-amber-500 shadow-[0_0_6px_rgba(245,158,11,0.5)]"></div>
              <div className="w-2.5 h-2.5 rounded-full bg-green-500 shadow-[0_0_6px_rgba(34,197,94,0.5)]"></div>
            </div>
            NeuroCLI / Terminal Workspace
          </div>

          {/* Right Header Action */}
          {showApplyBtn && (
            <button
              onClick={handleApply}
              className="bg-[#238636] hover:bg-[#2ea043] text-white px-3 py-1 text-sm font-semibold rounded shadow-sm transition-colors"
            >
              Apply Changes
            </button>
          )}
        </header>

        {/* Terminal Output Area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-2 scroll-smooth whitespace-pre-wrap flex flex-col">
          {history.map((entry, i) => (
            <div key={i} className={`flex break-words ${entry.type === 'error' ? 'text-[#f85149]' : entry.type === 'system' ? 'text-[#8b949e] italic' : ''}`}>
              {entry.type === 'user' && <span className="text-[#58a6ff] mr-3 font-black select-none">❯</span>}
              <span className={entry.type === 'user' ? 'text-white' : ''}>{entry.content}</span>
              {isStreaming && i === history.length - 1 && entry.type === 'bot' && (
                <span className="w-2 h-4 bg-[#c9d1d9] inline-block animate-pulse ml-1 align-middle"></span>
              )}
            </div>
          ))}
          <div ref={bottomRef} className="h-4" />
        </div>

        {/* Command Input Area */}
        <div className="p-4 sm:p-5 bg-[#0d1117] border-t border-[#30363d] shadow-[0_-10px_30px_rgba(0,0,0,0.3)] z-10 shrink-0 flex flex-col gap-3">

          {/* Target File Row */}
          <div className="flex items-center gap-3">
            <div className="w-1 bg-[#58a6ff] self-stretch rounded-full mr-1"></div>
            <input
              type="text"
              value={targetFile}
              onChange={(e) => setTargetFile(e.target.value)}
              className="flex-1 bg-transparent border-b border-[#30363d] border-dashed pb-1 text-[#8b949e] outline-none text-sm font-mono placeholder-[#484f58] focus:border-[#58a6ff] transition-colors"
              placeholder="Target file path (optional)..."
            />

            <button className="text-[#58a6ff] hover:text-[#79c0ff] text-sm font-bold tracking-wide transition-colors">
              Browse...
            </button>
          </div>

          <div className="w-full border-b border-[#30363d] border-dashed my-1"></div>

          {/* Prompt Entry Row */}
          <form onSubmit={handleCommand} className="flex items-center gap-3">
            <span className="text-[#8b949e] font-black select-none pl-2">❯</span>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isStreaming}
              className="flex-1 bg-transparent outline-none border-none text-white placeholder-[#484f58] caret-[#58a6ff] selection:bg-[#58a6ff]/30 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-mono"
              placeholder={isStreaming ? "Awaiting response..." : "Enter your prompt..."}
              autoFocus={!isStreaming}
            />
          </form>

          <div className="w-full border-b border-[#30363d] border-dashed my-1"></div>

          {/* Action Toolbar */}
          <div className="flex items-center justify-between pl-2">

            {/* Left Tool Icons */}
            <div className="flex items-center gap-4 text-xs font-semibold text-[#8b949e]">
              <button onClick={() => setIsSettingsModalOpen(true)} title="Settings" className="hover:text-white transition-colors p-1"><Settings size={16} /></button>
              <button
                onClick={() => setContextPaths(new Set())}
                title="Clear Context"
                className="hover:text-white transition-colors p-1"
              >
                <Trash2 size={16} />
              </button>

              <button
                onClick={() => setIsModelModalOpen(true)}
                className="flex items-center gap-1.5 hover:text-white transition-colors px-2 py-1 rounded"
              >
                <Bot size={16} className="text-[#f85149]" />
                <span>Model</span>
              </button>

              <button
                onClick={() => setIsContextModalOpen(true)}
                className={`flex items-center gap-1.5 hover:text-white transition-colors px-2 py-1 rounded ${contextPaths.size > 0 ? 'bg-[#58a6ff]/10 text-[#58a6ff]' : ''}`}
              >
                <Paperclip size={16} className={contextPaths.size > 0 ? "text-[#58a6ff]" : "text-[#c9d1d9]"} />
                <span>Context {contextPaths.size > 0 && `(${contextPaths.size})`}</span>
              </button>

              <button
                onClick={() => setIsRadarModalOpen(true)}
                className="flex items-center gap-1.5 hover:text-white transition-colors px-2 py-1 rounded"
              >
                <div className="flex w-3.5 h-3.5 mr-0.5">
                  <div className="w-1 h-full bg-[#f85149]"></div>
                  <div className="w-1 h-full bg-[#3fb950]"></div>
                  <div className="w-1 h-full bg-[#58a6ff]"></div>
                </div>
                <span>Radar</span>
              </button>
            </div>

            {/* Right Action Buttons */}
            <div className="flex items-center gap-4 text-xs font-semibold text-[#8b949e]">
              <button
                onClick={() => setIsGitModalOpen(true)}
                className="flex items-center gap-1.5 hover:text-[#58a6ff] transition-colors px-2 py-1"
              >
                <span className="text-[#58a6ff]">Commit</span> <GitCommit size={14} className="text-[#f85149]" />
              </button>

              <button onClick={handleFormat} className="hover:text-white transition-colors px-2 py-1">
                Format
              </button>

              <button
                onClick={handleCommand}
                disabled={isStreaming || !input.trim()}
                className="flex items-center gap-1.5 hover:text-white transition-colors px-2 py-1 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Play size={14} className={isStreaming ? "text-[#8b949e]" : "text-[#58a6ff]"} /> Run
              </button>
            </div>

          </div>

        </div>
      </div>

      {/* Modals */}
      <ContextModal
        isOpen={isContextModalOpen}
        onClose={() => setIsContextModalOpen(false)}
        contextPaths={contextPaths}
        setContextPaths={setContextPaths}
        onFileSelect={handleFileSelect}
      />

      <RadarModal
        isOpen={isRadarModalOpen}
        onClose={() => setIsRadarModalOpen(false)}
      />

      <GitModal
        isOpen={isGitModalOpen}
        onClose={() => setIsGitModalOpen(false)}
      />

      <SettingsModal
        isOpen={isSettingsModalOpen}
        onClose={() => setIsSettingsModalOpen(false)}
      />

      <ModelModal
        isOpen={isModelModalOpen}
        onClose={() => setIsModelModalOpen(false)}
      />

    </div>
  )
}

export default App
