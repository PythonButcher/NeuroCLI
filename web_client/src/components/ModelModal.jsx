import { useEffect, useState } from 'react'
import { Bot, X } from 'lucide-react'

export default function ModelModal({ isOpen, onClose, model, modelOptionsText, onSave }) {
  const [draftModel, setDraftModel] = useState(model)
  const [draftModelOptionsText, setDraftModelOptionsText] = useState(modelOptionsText)

  useEffect(() => {
    if (!isOpen) {
      return
    }

    setDraftModel(model)
    setDraftModelOptionsText(modelOptionsText)
  }, [isOpen, model, modelOptionsText])

  if (!isOpen) {
    return null
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm transition-opacity">
      <div
        className="flex w-full max-w-lg flex-col overflow-hidden rounded-lg border border-[#30363d] bg-[#0d1117] shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-[#30363d] bg-[#161b22] p-4">
          <h2 className="flex items-center gap-2 text-lg font-bold text-[#c9d1d9]">
            <Bot size={20} className="text-[#f85149]" />
            AI Engine
          </h2>
          <button onClick={onClose} className="text-[#8b949e] transition-colors hover:text-white">
            <X size={20} />
          </button>
        </div>

        <div className="space-y-4 p-6">
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-[#c9d1d9]">Model Override</label>
            <input
              type="text"
              value={draftModel}
              onChange={(event) => setDraftModel(event.target.value)}
              placeholder="Leave blank to use the backend default model"
              className="w-full rounded border border-[#30363d] bg-[#010409] px-3 py-2 font-mono text-sm text-[#c9d1d9] outline-none transition-colors focus:border-[#58a6ff]"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-semibold text-[#c9d1d9]">Model Options JSON</label>
            <textarea
              value={draftModelOptionsText}
              onChange={(event) => setDraftModelOptionsText(event.target.value)}
              placeholder='Example: {"temperature": 0.2}'
              rows={8}
              className="w-full rounded border border-[#30363d] bg-[#010409] px-3 py-2 font-mono text-sm text-[#c9d1d9] outline-none transition-colors focus:border-[#58a6ff]"
            />
            <p className="text-xs text-[#8b949e]">
              These fields are sent directly to the backend as <span className="font-mono text-[#c9d1d9]">model</span> and <span className="font-mono text-[#c9d1d9]">model_options</span>. Leave them empty to let the backend choose defaults.
            </p>
          </div>
        </div>

        <div className="flex justify-end gap-2 border-t border-[#30363d] bg-[#161b22] p-4">
          <button
            onClick={() => {
              setDraftModel('')
              setDraftModelOptionsText('')
            }}
            className="rounded border border-[#30363d] bg-[#21262d] px-4 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-[#30363d]"
          >
            Clear
          </button>
          <button
            onClick={() => {
              onSave({
                model: draftModel.trim(),
                modelOptionsText: draftModelOptionsText,
              })
              onClose()
            }}
            className="rounded border border-[#30363d] bg-[#238636] px-4 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-[#2ea043]"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  )
}
