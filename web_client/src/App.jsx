import { useEffect, useRef, useState } from 'react'
import FileTree from './components/FileTree'
import ContextModal from './components/ContextModal'
import RadarModal from './components/RadarModal'
import GitModal from './components/GitModal'
import SettingsModal from './components/SettingsModal'
import ModelModal from './components/ModelModal'
import TargetFileModal from './components/TargetFileModal'
import ReviewModal from './components/ReviewModal'
import CommandModal from './components/CommandModal'
import { fetchJson, postJson, streamJsonEvents } from './lib/api'
import {
  RefreshCcw,
  Settings,
  Trash2,
  Bot,
  Paperclip,
  GitCommit,
  Play,
  X,
  Compass,
  Keyboard,
  CheckCircle2,
} from 'lucide-react'

const INITIAL_HISTORY = [
  { id: 'boot-1', type: 'system', content: 'NeuroCLI web client connected to the FastAPI workflow bridge.' },
  { id: 'boot-2', type: 'system', content: 'Prompts stream through /api/ai/stream and fall back to /api/ai/prompt when streaming is unavailable.' },
]

function App() {
  const [history, setHistory] = useState(INITIAL_HISTORY)
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [targetFile, setTargetFile] = useState('')
  const [proposedContent, setProposedContent] = useState('')
  const [generatedProposal, setGeneratedProposal] = useState(null)
  const [validationResult, setValidationResult] = useState(null)
  const [timelineEvents, setTimelineEvents] = useState([])
  const [showApplyBtn, setShowApplyBtn] = useState(false)
  const [isContextModalOpen, setIsContextModalOpen] = useState(false)
  const [contextPaths, setContextPaths] = useState(() => new Set())
  const [isRadarModalOpen, setIsRadarModalOpen] = useState(false)
  const [isGitModalOpen, setIsGitModalOpen] = useState(false)
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false)
  const [isModelModalOpen, setIsModelModalOpen] = useState(false)
  const [isTargetFileModalOpen, setIsTargetFileModalOpen] = useState(false)
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false)
  const [isCommandModalOpen, setIsCommandModalOpen] = useState(false)
  const [selectedModel, setSelectedModel] = useState('')
  const [modelOptionsText, setModelOptionsText] = useState('')
  const bottomRef = useRef(null)
  const abortControllerRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history])

  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort()
    }
  }, [])

  const replaceHistoryEntry = (entryId, updater) => {
    setHistory((previousHistory) =>
      previousHistory.map((entry) => {
        if (entry.id !== entryId) {
          return entry
        }

        return typeof updater === 'function' ? updater(entry) : updater
      }),
    )
  }

  const pushHistoryEntry = (entry) => {
    setHistory((previousHistory) => [...previousHistory, entry])
  }

  const handleToggleContextPath = (path) => {
    setContextPaths((previousPaths) => {
      const nextPaths = new Set(previousPaths)
      if (nextPaths.has(path)) {
        nextPaths.delete(path)
      } else {
        nextPaths.add(path)
      }
      return nextPaths
    })
  }

  const handleFileSelect = async (path) => {
    setTargetFile(path)
    setProposedContent('')
    setGeneratedProposal(null)
    setValidationResult(null)
    setTimelineEvents([])
    setShowApplyBtn(false)

    try {
      const data = await fetchJson(`/api/file?path=${encodeURIComponent(path)}`)
      if (data.error) {
        throw new Error(data.error)
      }

      pushHistoryEntry({
        id: createEntryId('file'),
        type: 'system',
        content: `Viewing ${getFileLabel(path)}\n\n${data.content}`,
      })
    } catch (error) {
      pushHistoryEntry({
        id: createEntryId('error'),
        type: 'error',
        content: `Failed to open file: ${error.message}`,
      })
    }
  }

  const handleApply = async (contentOverride = null) => {
    const finalContent = contentOverride !== null ? contentOverride : proposedContent
    if (!targetFile || !finalContent) {
      return
    }

    try {
      const data = await postJson('/api/apply', {
        file_path: targetFile,
        content: finalContent,
      })

      if (data.error) {
        throw new Error(data.error)
      }

      pushHistoryEntry({
        id: createEntryId('apply'),
        type: 'system',
        content: data.message,
      })
      setProposedContent('')
      setGeneratedProposal(null)
      setValidationResult(null)
      setShowApplyBtn(false)
      await handleFileSelect(targetFile)
      setTimelineEvents(normalizeTimelineEvents(data.timeline))
    } catch (error) {
      pushHistoryEntry({
        id: createEntryId('error'),
        type: 'error',
        content: `Apply Error: ${error.message}`,
      })
    }
  }

  const handleFormat = async () => {
    if (!targetFile) {
      pushHistoryEntry({
        id: createEntryId('error'),
        type: 'error',
        content: 'Select a target file before requesting formatting.',
      })
      return
    }

    pushHistoryEntry({
      id: createEntryId('format'),
      type: 'system',
      content: `Formatting ${targetFile}...`,
    })

    try {
      const data = await postJson('/api/format', { file_path: targetFile })

      if (data.error) {
        throw new Error(data.error)
      }

      if (data.status === 'no_change') {
        pushHistoryEntry({
          id: createEntryId('format'),
          type: 'system',
          content: 'No formatting changes were needed.',
        })
        setProposedContent('')
        setGeneratedProposal(null)
        setValidationResult(null)
        setTimelineEvents([])
        setShowApplyBtn(false)
        return
      }

      pushHistoryEntry({
        id: createEntryId('format'),
        type: 'system',
        content: data.diff,
      })
      setProposedContent(data.proposed_content || '')
      setGeneratedProposal(null)
      setValidationResult(null)
      setTimelineEvents([])
      setShowApplyBtn(Boolean(data.proposed_content))
    } catch (error) {
      pushHistoryEntry({
        id: createEntryId('error'),
        type: 'error',
        content: `Formatter Error: ${error.message}`,
      })
    }
  }

  const handleValidate = async () => {
    pushHistoryEntry({
      id: createEntryId('validate'),
      type: 'system',
      content: 'Running approved validation label python_unittest...',
    })

    try {
      const payload = { command_label: 'python_unittest' }
      if (targetFile.trim()) {
        payload.target_file = targetFile.trim()
      }

      const data = await postJson('/api/validate', payload)
      const normalizedResult = normalizeValidationResult(data)
      setValidationResult(normalizedResult)
      setTimelineEvents(normalizeTimelineEvents(data.timeline))
      pushHistoryEntry({
        id: createEntryId('validate'),
        type: normalizedResult.status === 'passed' ? 'system' : 'error',
        content: buildValidationResultMessage(normalizedResult),
      })
    } catch (error) {
      pushHistoryEntry({
        id: createEntryId('error'),
        type: 'error',
        content: `Validation Error: ${error.message}`,
      })
    }
  }

  const handleCommand = async (event) => {
    event?.preventDefault?.()

    if (!input.trim() || isStreaming) {
      return
    }

    let parsedModelOptions
    try {
      parsedModelOptions = parseModelOptions(modelOptionsText)
    } catch (error) {
      pushHistoryEntry({
        id: createEntryId('error'),
        type: 'error',
        content: error.message,
      })
      return
    }

    const prompt = input.trim()
    const requestPayload = buildRequestPayload({
      prompt,
      targetFile,
      contextPaths,
      model: selectedModel,
      modelOptions: parsedModelOptions,
    })

    const responseEntryId = createEntryId('bot')
    pushHistoryEntry({ id: createEntryId('user'), type: 'user', content: prompt })
    pushHistoryEntry({ id: responseEntryId, type: 'bot', content: '' })

    setInput('')
    setIsStreaming(true)
    setProposedContent('')
    setGeneratedProposal(null)
    setValidationResult(null)
    setTimelineEvents([])
    setShowApplyBtn(false)

    try {
      await runWorkflowRequest({
        payload: requestPayload,
        responseEntryId,
        onComplete: (response) => {
          setTimelineEvents(normalizeTimelineEvents(response.timeline))
          applyWorkflowResponse(response)
        },
        onError: (message) => {
          replaceHistoryEntry(responseEntryId, {
            id: responseEntryId,
            type: 'error',
            content: message,
          })
        },
      })
    } catch (error) {
      replaceHistoryEntry(responseEntryId, {
        id: responseEntryId,
        type: 'error',
        content: `Backend request failed: ${error.message}`,
      })
    } finally {
      abortControllerRef.current = null
      setIsStreaming(false)
    }
  }

  const runWorkflowRequest = async ({ payload, responseEntryId, onComplete, onError }) => {
    const streamAbortController = new AbortController()
    abortControllerRef.current = streamAbortController
    let streamResponse = null
    let streamErrorMessage = null

    try {
      await streamJsonEvents(
        '/api/ai/stream',
        payload,
        {
          onEvent: (event) => {
            if (event.timeline_event) {
              appendTimelineEvent(event.timeline_event)
            }
          },
          onDelta: (event) => {
            replaceHistoryEntry(responseEntryId, (entry) => ({
              ...entry,
              type: 'bot',
              content: `${entry.content}${event.delta || ''}`,
            }))
          },
          onComplete: (event) => {
            streamResponse = event.response || null
          },
          onError: (event) => {
            streamErrorMessage =
              getWorkflowErrorMessage(event.response) || 'The backend returned a streaming error.'
          },
        },
        { signal: streamAbortController.signal },
      )
    } catch (error) {
      if (error.name === 'AbortError') {
        onError('The active request was cancelled.')
        return
      }

      if (!isStreamingUnsupportedError(error)) {
        throw error
      }
    }

    if (streamErrorMessage) {
      onError(streamErrorMessage)
      return
    }

    if (streamResponse) {
      replaceHistoryEntry(responseEntryId, (entry) => ({
        ...entry,
        type: streamResponse.ok ? 'bot' : 'error',
        content: streamResponse.ok ? streamResponse.output_text : getWorkflowErrorMessage(streamResponse),
      }))

      if (streamResponse.ok) {
        onComplete(streamResponse)
      }
      return
    }

    const promptResponse = await postJson('/api/ai/prompt', payload)
    replaceHistoryEntry(responseEntryId, (entry) => ({
      ...entry,
      type: promptResponse.ok ? 'bot' : 'error',
      content: promptResponse.ok ? promptResponse.output_text : getWorkflowErrorMessage(promptResponse),
    }))

    if (promptResponse.ok) {
      onComplete(promptResponse)
      return
    }

    onError(getWorkflowErrorMessage(promptResponse))
  }

  const applyWorkflowResponse = (response) => {
    if (!response.ok) {
      return
    }

    if (response.target_file) {
      setTargetFile(response.target_file)
    }

    setValidationResult(normalizeValidationResult(response.validation_result))
    setTimelineEvents(normalizeTimelineEvents(response.timeline))

    if (response.response_kind === 'file_update') {
      const proposal = normalizeGeneratedProposal(response.proposal)
      const proposalTarget = proposal?.target_path || response.target_file || targetFile

      if (!proposal) {
        setProposedContent('')
        setGeneratedProposal(null)
        setShowApplyBtn(false)
        pushHistoryEntry({
          id: createEntryId('error'),
          type: 'error',
          content: 'The backend did not return a generated-file proposal. Apply is disabled for this response.',
        })
        return
      }

      setGeneratedProposal(proposal)

      if (proposal.status === 'ready') {
        const reviewContent = proposal.normalized_content || proposal.proposed_content || ''
        setProposedContent(reviewContent)
        setShowApplyBtn(Boolean(reviewContent))

        if (proposal.diff_text) {
          pushHistoryEntry({
            id: createEntryId('diff'),
            type: 'system',
            content: proposal.diff_text,
          })
        }
      } else {
        setProposedContent('')
        setShowApplyBtn(false)
      }

      pushHistoryEntry({
        id: createEntryId('system'),
        type: 'system',
        content: buildProposalStatusMessage(proposal, proposalTarget),
      })
      return
    }

    setProposedContent('')
    setGeneratedProposal(null)
    setShowApplyBtn(false)
  }

  const appendTimelineEvent = (rawEvent) => {
    const event = normalizeTimelineEvent(rawEvent)
    if (!event) {
      return
    }

    setTimelineEvents((previousEvents) => [...previousEvents, event].slice(-12))
  }

  return (
    <div className="flex h-screen w-full overflow-hidden bg-[#010409] font-mono leading-relaxed text-[#c9d1d9]">
      <div className="z-20 flex w-64 flex-shrink-0 flex-col border-r border-[#30363d] bg-[#0d1117]">
        <div className="select-none border-b border-[#30363d] p-3 text-sm font-bold tracking-wide text-[#58a6ff]">
          NeuroCLI
        </div>

        <div className="flex-1 overflow-hidden">
          <FileTree
            onFileSelect={handleFileSelect}
            onToggleContextPath={handleToggleContextPath}
            contextPaths={contextPaths}
            targetFile={targetFile}
          />
        </div>

        <div className="border-t border-[#30363d] p-3">
          <button
            className="flex w-full items-center justify-center rounded border border-[#30363d] bg-[#21262d] px-3 py-1.5 text-sm font-medium text-[#c9d1d9] transition-colors hover:bg-[#30363d]"
            onClick={() => {
              abortControllerRef.current?.abort()
              setIsStreaming(false)
              setHistory([{ id: 'reset-1', type: 'system', content: 'Console reset.' }])
              setProposedContent('')
              setGeneratedProposal(null)
              setValidationResult(null)
              setTimelineEvents([])
              setShowApplyBtn(false)
            }}
          >
            <RefreshCcw size={14} className="mr-2" />
            Reset
          </button>
        </div>
      </div>

      <div className="relative flex h-full flex-1 flex-col overflow-hidden bg-[#0d1117]">
        <header className="z-10 flex shrink-0 items-center justify-between border-b border-[#30363d] bg-[#0d1117] p-3 shadow-sm">
          <div className="ml-2 flex items-center gap-3 text-xs font-semibold uppercase tracking-widest text-[#8b949e]">
            <div className="mr-2 flex items-center gap-1.5">
              <div className="h-2.5 w-2.5 rounded-full bg-red-500 shadow-[0_0_6px_rgba(239,68,68,0.5)]"></div>
              <div className="h-2.5 w-2.5 rounded-full bg-amber-500 shadow-[0_0_6px_rgba(245,158,11,0.5)]"></div>
              <div className="h-2.5 w-2.5 rounded-full bg-green-500 shadow-[0_0_6px_rgba(34,197,94,0.5)]"></div>
            </div>
            NeuroCLI / Terminal Workspace
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsCommandModalOpen(true)}
              className="flex items-center gap-1.5 text-xs font-bold text-[#58a6ff] transition-colors hover:text-[#79c0ff]"
            >
              <Keyboard size={16} />
              ⌨ Commands
            </button>

            {showApplyBtn && (
              <button
                onClick={() => handleApply()}
                className="rounded bg-[#238636] px-3 py-1 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-[#2ea043]"
              >
                Apply Changes
              </button>
            )}
          </div>
        </header>

        <div className="flex flex-1 flex-col space-y-2 overflow-y-auto p-4 whitespace-pre-wrap sm:p-6">
          {history.map((entry, index) => (
            <div
              key={entry.id}
              className={`flex break-words ${
                entry.type === 'error'
                  ? 'text-[#f85149]'
                  : entry.type === 'system'
                    ? 'italic text-[#8b949e]'
                    : ''
              }`}
            >
              {entry.type === 'user' && <span className="mr-3 select-none font-black text-[#58a6ff]">❯</span>}
              <span className={entry.type === 'user' ? 'text-white' : ''}>{entry.content}</span>
              {isStreaming && index === history.length - 1 && entry.type === 'bot' && (
                <span className="ml-1 inline-block h-4 w-2 animate-pulse bg-[#c9d1d9] align-middle"></span>
              )}
            </div>
          ))}
          <div ref={bottomRef} className="h-4" />
        </div>

        <div className="z-10 flex shrink-0 flex-col gap-3 border-t border-[#30363d] bg-[#0d1117] p-4 shadow-[0_-10px_30px_rgba(0,0,0,0.3)] sm:p-5">
          <div className="flex items-center gap-3">
            <div className="mr-1 self-stretch rounded-full bg-[#58a6ff] w-1"></div>
            <input
              type="text"
              value={targetFile}
              onChange={(event) => setTargetFile(event.target.value)}
              className="flex-1 border-b border-dashed border-[#30363d] bg-transparent pb-1 text-sm text-[#8b949e] outline-none transition-colors placeholder:text-[#484f58] focus:border-[#58a6ff]"
              placeholder="Target file path (optional)..."
            />

            <button
              type="button"
              onClick={() => setIsTargetFileModalOpen(true)}
              className="rounded px-2 py-1 text-sm font-bold tracking-wide text-[#58a6ff] transition-colors hover:text-[#79c0ff]"
            >
              Browse...
            </button>

            <button
              type="button"
              onClick={() => {
                setTargetFile('')
                setProposedContent('')
                setGeneratedProposal(null)
                setValidationResult(null)
                setTimelineEvents([])
                setShowApplyBtn(false)
              }}
              disabled={!targetFile}
              className="rounded px-2 py-1 text-sm font-bold tracking-wide text-[#58a6ff] transition-colors hover:text-[#79c0ff] disabled:cursor-not-allowed disabled:text-[#484f58]"
            >
              Clear
            </button>
          </div>

          <div className="my-1 w-full border-b border-dashed border-[#30363d]"></div>

          <form onSubmit={handleCommand} className="flex items-center gap-3">
            <span className="pl-2 font-black select-none text-[#8b949e]">❯</span>
            <input
              type="text"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              disabled={isStreaming}
              className="flex-1 border-none bg-transparent text-sm text-white outline-none caret-[#58a6ff] selection:bg-[#58a6ff]/30 placeholder:text-[#484f58] disabled:cursor-not-allowed disabled:opacity-50"
              placeholder={isStreaming ? 'Awaiting response...' : 'Enter your prompt...'}
              autoFocus={!isStreaming}
            />
          </form>

          <div className="my-1 w-full border-b border-dashed border-[#30363d]"></div>

          <div className="pl-2 text-xs text-[#8b949e]">
            {selectedModel ? `Model: ${selectedModel}` : 'Model: backend default'}
            {contextPaths.size > 0 ? ` | Context files: ${contextPaths.size}` : ' | Context files: none'}
            {` | Validation: ${buildValidationStatusLabel(validationResult)}`}
            {` | Timeline: ${buildTimelineStatusLabel(timelineEvents)}`}
          </div>

          <div className="flex flex-wrap items-center gap-x-6 gap-y-3 pl-2">
            <div className="flex items-center gap-4 text-xs font-semibold text-[#8b949e]">
              <button onClick={() => setIsSettingsModalOpen(true)} title="Settings" className="p-1 transition-colors hover:text-white">
                <Settings size={16} />
              </button>

              <button
                onClick={() => {
                  setInput('')
                  setProposedContent('')
                  setGeneratedProposal(null)
                  setValidationResult(null)
                  setShowApplyBtn(false)
                  setHistory([{ id: 'clear-1', type: 'system', content: 'Console cleared.' }])
                }}
                title="Clear Console"
                className="p-1 transition-colors hover:text-white"
              >
                <Trash2 size={16} />
              </button>

              <button
                onClick={() => setIsModelModalOpen(true)}
                className="flex items-center gap-1.5 rounded px-2 py-1 transition-colors hover:text-white"
              >
                <Bot size={16} className="text-[#f85149]" />
                <span>Model</span>
              </button>

              <button
                onClick={() => setIsContextModalOpen(true)}
                className={`flex items-center gap-1.5 rounded px-2 py-1 transition-colors hover:text-white ${
                  contextPaths.size > 0 ? 'bg-[#58a6ff]/10 text-[#58a6ff]' : ''
                }`}
              >
                <Paperclip
                  size={16}
                  className={contextPaths.size > 0 ? 'text-[#58a6ff]' : 'text-[#c9d1d9]'}
                />
                <span>Context {contextPaths.size > 0 && `(${contextPaths.size})`}</span>
              </button>
            </div>

            <div className="flex flex-wrap items-center gap-4 text-xs font-semibold text-[#8b949e]">
              <button
                onClick={() => setIsRadarModalOpen(true)}
                className="flex items-center gap-1.5 rounded px-2 py-1 transition-colors hover:text-white"
              >
                <div className="mr-0.5 flex h-3.5 w-3.5">
                  <div className="h-full w-1 bg-[#f85149]"></div>
                  <div className="h-full w-1 bg-[#3fb950]"></div>
                  <div className="h-full w-1 bg-[#58a6ff]"></div>
                </div>
                <span>Radar</span>
              </button>

              {isStreaming ? (
                <button
                  type="button"
                  onClick={() => abortControllerRef.current?.abort()}
                  className="flex items-center gap-1.5 px-2 py-1 transition-colors hover:text-white"
                >
                  <X size={14} className="text-[#f85149]" />
                  Stop
                </button>
              ) : (
                <button
                  onClick={handleCommand}
                  disabled={!input.trim()}
                  className="flex items-center gap-1.5 px-2 py-1 transition-colors hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <Play size={14} className="text-[#58a6ff]" />
                  Run
                </button>
              )}

              <button onClick={handleFormat} className="px-2 py-1 transition-colors hover:text-white">
                Format
              </button>

              <button
                onClick={() => setIsReviewModalOpen(true)}
                className="flex items-center gap-1.5 px-2 py-1 transition-colors hover:text-white"
              >
                <Compass size={14} className="text-[#58a6ff]" />
                <span>Review</span>
              </button>

              <button
                onClick={handleValidate}
                disabled={isStreaming}
                className="flex items-center gap-1.5 px-2 py-1 transition-colors hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
              >
                <CheckCircle2 size={14} className="text-[#3fb950]" />
                <span>Validate</span>
              </button>

              <button
                onClick={() => setIsGitModalOpen(true)}
                className="flex items-center gap-1.5 px-2 py-1 transition-colors hover:text-[#58a6ff]"
              >
                <span className="text-[#58a6ff]">Commit</span>
                <GitCommit size={14} className="text-[#f85149]" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <ContextModal
        isOpen={isContextModalOpen}
        onClose={() => setIsContextModalOpen(false)}
        contextPaths={contextPaths}
        setContextPaths={setContextPaths}
        onFileSelect={handleFileSelect}
      />

      {isRadarModalOpen && (
        <RadarModal onClose={() => setIsRadarModalOpen(false)} />
      )}

      <GitModal isOpen={isGitModalOpen} onClose={() => setIsGitModalOpen(false)} />

      <TargetFileModal
        isOpen={isTargetFileModalOpen}
        onClose={() => setIsTargetFileModalOpen(false)}
        onFileSelect={handleFileSelect}
        targetFile={targetFile}
      />

      <SettingsModal isOpen={isSettingsModalOpen} onClose={() => setIsSettingsModalOpen(false)} />

      {/* Mount draft-based modals only while open so each session initializes
          directly from the latest saved parent state without synchronization effects. */}
      {isModelModalOpen && (
        <ModelModal
          onClose={() => setIsModelModalOpen(false)}
          model={selectedModel}
          modelOptionsText={modelOptionsText}
          onSave={({ model, modelOptionsText }) => {
            setSelectedModel(model)
            setModelOptionsText(modelOptionsText)
          }}
        />
      )}

      {isReviewModalOpen && (
        <ReviewModal
          onClose={() => setIsReviewModalOpen(false)}
          targetFile={targetFile}
          proposedContent={proposedContent}
          proposal={generatedProposal}
          setProposedContent={setProposedContent}
          onApply={handleApply}
        />
      )}

      <CommandModal
        isOpen={isCommandModalOpen}
        onClose={() => setIsCommandModalOpen(false)}
      />
    </div>
  )
}

function buildRequestPayload({ prompt, targetFile, contextPaths, model, modelOptions }) {
  const payload = { prompt }
  const trimmedTargetFile = targetFile.trim()
  const contextPathList = Array.from(contextPaths)

  if (trimmedTargetFile) {
    payload.target_file = trimmedTargetFile
  }

  if (contextPathList.length > 0) {
    payload.context_paths = contextPathList
  }

  if (model.trim()) {
    payload.model = model.trim()
  }

  if (modelOptions && Object.keys(modelOptions).length > 0) {
    payload.model_options = modelOptions
  }

  return payload
}

function normalizeGeneratedProposal(rawProposal) {
  if (!rawProposal || typeof rawProposal !== 'object') {
    return null
  }

  const targetPath = typeof rawProposal.target_path === 'string' ? rawProposal.target_path : ''
  const status = typeof rawProposal.status === 'string' ? rawProposal.status : 'error'

  // Keep proposal consumption strict so React review mirrors the backend artifact.
  return {
    target_path: targetPath,
    original_content: typeof rawProposal.original_content === 'string' ? rawProposal.original_content : '',
    original_content_reference:
      typeof rawProposal.original_content_reference === 'string'
        ? rawProposal.original_content_reference
        : targetPath,
    proposed_content: typeof rawProposal.proposed_content === 'string' ? rawProposal.proposed_content : '',
    normalized_content:
      typeof rawProposal.normalized_content === 'string' ? rawProposal.normalized_content : '',
    diff_text: typeof rawProposal.diff_text === 'string' ? rawProposal.diff_text : '',
    status,
    errors: Array.isArray(rawProposal.errors)
      ? rawProposal.errors.filter((error) => typeof error === 'string')
      : [],
  }
}

function normalizeValidationResult(rawResult) {
  if (!rawResult || typeof rawResult !== 'object') {
    return null
  }

  return {
    status: typeof rawResult.status === 'string' ? rawResult.status : 'skipped',
    command_label: typeof rawResult.command_label === 'string' ? rawResult.command_label : 'not_run',
    duration_seconds: Number.isFinite(Number(rawResult.duration_seconds))
      ? Number(rawResult.duration_seconds)
      : 0,
    exit_code: Number.isInteger(rawResult.exit_code) ? rawResult.exit_code : null,
    skipped: Boolean(rawResult.skipped),
    output_excerpt:
      typeof rawResult.output_excerpt === 'string' ? rawResult.output_excerpt : '',
    error_details:
      typeof rawResult.error_details === 'string' ? rawResult.error_details : null,
  }
}

function normalizeTimelineEvents(rawEvents) {
  if (!Array.isArray(rawEvents)) {
    return []
  }

  return rawEvents.map(normalizeTimelineEvent).filter(Boolean)
}

function normalizeTimelineEvent(rawEvent) {
  if (!rawEvent || typeof rawEvent !== 'object') {
    return null
  }

  return {
    event_type: typeof rawEvent.event_type === 'string' ? rawEvent.event_type : 'unknown',
    status: typeof rawEvent.status === 'string' ? rawEvent.status : 'skipped',
    label: typeof rawEvent.label === 'string' ? rawEvent.label : 'Workflow Event',
    summary: typeof rawEvent.summary === 'string' ? rawEvent.summary : '',
    metadata: rawEvent.metadata && typeof rawEvent.metadata === 'object' ? rawEvent.metadata : {},
    occurred_at: typeof rawEvent.occurred_at === 'string' ? rawEvent.occurred_at : '',
  }
}

function buildValidationStatusLabel(validationResult) {
  if (!validationResult) {
    return 'not available'
  }

  const commandLabel = validationResult.command_label || 'not_run'
  if (validationResult.status === 'skipped') {
    return `skipped, ${commandLabel}`
  }

  return `${validationResult.status}, ${commandLabel}`
}

function buildTimelineStatusLabel(timelineEvents) {
  if (!timelineEvents.length) {
    return 'idle'
  }

  return timelineEvents
    .slice(-4)
    .map((event) => `${event.label}: ${event.status}`)
    .join(' / ')
}

function buildValidationResultMessage(validationResult) {
  if (!validationResult) {
    return 'Validation did not return a result.'
  }

  const exitCode = validationResult.exit_code === null ? 'none' : validationResult.exit_code
  const details = validationResult.error_details || 'No error details.'
  const output = validationResult.output_excerpt || 'No output captured.'

  return [
    `Validation: ${validationResult.status}`,
    `Command label: ${validationResult.command_label}`,
    `Duration: ${validationResult.duration_seconds.toFixed(2)}s`,
    `Exit code: ${exitCode}`,
    `Skipped: ${validationResult.skipped ? 'yes' : 'no'}`,
    `Details: ${details}`,
    '',
    output,
  ].join('\n')
}

function buildProposalStatusMessage(proposal, targetPath) {
  const fileLabel = getFileLabel(targetPath)

  if (proposal.status === 'ready') {
    return `Generated a backend proposal for ${fileLabel}. Review the diff and editable draft before applying.`
  }

  if (proposal.status === 'no_change') {
    return `Generated proposal for ${fileLabel}, but the backend found no content changes to apply.`
  }

  const details = proposal.errors.length > 0 ? ` ${proposal.errors.join(' ')}` : ''
  return `Generated proposal for ${fileLabel} is not applicable.${details}`
}

function parseModelOptions(rawText) {
  if (!rawText.trim()) {
    return null
  }

  try {
    const parsed = JSON.parse(rawText)
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      throw new Error()
    }
    return parsed
  } catch {
    throw new Error('Model options must be a valid JSON object before sending the request.')
  }
}

function getWorkflowErrorMessage(response) {
  if (!response) {
    return 'The backend returned an unknown error.'
  }

  if (typeof response.error === 'string' && response.error.trim()) {
    return response.error
  }

  return 'The backend returned an unknown error.'
}

function getFileLabel(path) {
  if (!path) {
    return 'selected file'
  }

  const segments = path.split(/[\\/]/)
  return segments[segments.length - 1] || path
}

function createEntryId(prefix) {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function isStreamingUnsupportedError(error) {
  return error.message === 'Streaming is not supported by this browser response.'
}

export default App
