import { useEffect, useState } from 'react'
import {
  ChevronDown,
  ChevronRight,
  File,
  Folder,
  FolderOpen,
  Paperclip,
} from 'lucide-react'
import { fetchJson } from '../lib/api'

const FileTreeNode = ({
  node,
  level = 0,
  onSelect,
  onToggleContextPath,
  contextPaths = new Set(),
  targetFile = '',
  showContextToggle = true,
}) => {
  const [isOpen, setIsOpen] = useState(level === 0)

  const isDirectory = node.type === 'directory'
  const isInContext = !isDirectory && contextPaths.has(node.path)
  const isTargetFile = !isDirectory && targetFile === node.path

  const handlePrimaryClick = (event) => {
    event.stopPropagation()

    if (isDirectory) {
      setIsOpen((previousState) => !previousState)
      return
    }

    onSelect(node.path)
  }

  const handleContextToggle = (event) => {
    event.stopPropagation()
    if (!isDirectory) {
      onToggleContextPath?.(node.path)
    }
  }

  return (
    <div>
      <div
        className={`flex cursor-pointer items-center justify-between px-2 py-1 text-sm transition-colors duration-150 select-none ${
          isDirectory
            ? 'text-[#c9d1d9] hover:bg-[#30363d]'
            : isTargetFile
              ? 'bg-[#58a6ff]/10 text-[#79c0ff]'
              : isInContext
                ? 'text-[#3fb950] hover:bg-[#30363d]'
                : 'text-[#8b949e] hover:bg-[#30363d] hover:text-[#c9d1d9]'
        }`}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={handlePrimaryClick}
      >
        <div className="min-w-0 flex-1 pr-2">
          <div className="flex items-center">
            <span className="mr-1.5 flex h-4 w-4 flex-shrink-0 items-center justify-center text-[#8b949e]">
              {isDirectory ? (
                isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />
              ) : (
                <span className="w-4"></span>
              )}
            </span>

            <span className="mr-2 flex-shrink-0">
              {isDirectory ? (
                isOpen ? (
                  <FolderOpen size={14} className="text-[#e3b341]" />
                ) : (
                  <Folder size={14} className="text-[#e3b341]" />
                )
              ) : (
                <File size={14} className={isTargetFile ? 'text-[#79c0ff]' : isInContext ? 'text-[#3fb950]' : ''} />
              )}
            </span>

            <span className="truncate">{node.name}</span>
          </div>
        </div>

        {!isDirectory && showContextToggle && (
          <button
            type="button"
            onClick={handleContextToggle}
            title={isInContext ? 'Remove from prompt context' : 'Add to prompt context'}
            className={`rounded p-1 transition-colors ${
              isInContext ? 'text-[#3fb950] hover:bg-[#3fb950]/10' : 'text-[#8b949e] hover:bg-[#21262d] hover:text-white'
            }`}
          >
            <Paperclip size={12} />
          </button>
        )}
      </div>

      {isDirectory && isOpen && node.children && (
        <div>
          {node.children.map((child) => (
            <FileTreeNode
              key={child.path}
              node={child}
              level={level + 1}
              onSelect={onSelect}
              onToggleContextPath={onToggleContextPath}
              contextPaths={contextPaths}
              targetFile={targetFile}
              showContextToggle={showContextToggle}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default function FileTree({
  onFileSelect,
  onToggleContextPath,
  contextPaths,
  targetFile,
  showContextToggle = true,
}) {
  const [treeData, setTreeData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchTree = async () => {
      try {
        const data = await fetchJson('/api/files')
        setTreeData(data)
        setError(null)
      } catch (fetchError) {
        setError(fetchError.message)
      } finally {
        setLoading(false)
      }
    }

    fetchTree()
  }, [])

  if (loading) {
    return <div className="p-4 text-sm text-[#8b949e]">Loading workspace...</div>
  }

  if (error) {
    return <div className="p-4 text-sm text-[#f85149]">Error: {error}</div>
  }

  if (!treeData) {
    return null
  }

  return (
    <div className="h-full w-full overflow-y-auto py-2 custom-scrollbar">
      <FileTreeNode
        node={treeData}
        onSelect={onFileSelect}
        onToggleContextPath={onToggleContextPath}
        contextPaths={contextPaths}
        targetFile={targetFile}
        showContextToggle={showContextToggle}
      />
    </div>
  )
}
