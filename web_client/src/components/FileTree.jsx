import { useState, useEffect } from 'react'
import { Folder, FolderOpen, File, ChevronRight, ChevronDown } from 'lucide-react'

// Recursive component for rendering the tree
const FileTreeNode = ({ node, level = 0, onSelect, contextPaths = new Set() }) => {
    const [isOpen, setIsOpen] = useState(false)

    const isDir = node.type === 'directory'
    const paddingLeft = `${level * 16}px`
    const inContext = !isDir && contextPaths.has(node.path)

    const toggleOpen = (e) => {
        e.stopPropagation()
        if (isDir) {
            setIsOpen(!isOpen)
        } else {
            onSelect(node.path)
        }
    }

    return (
        <div>
            <div
                className={`flex items-center justify-between py-1 px-2 cursor-pointer hover:bg-[#30363d] select-none text-sm transition-colors duration-150 ${isDir ? 'text-[#c9d1d9]' : inContext ? 'text-[#3fb950]' : 'text-[#8b949e] hover:text-[#c9d1d9]'}`}
                style={{ paddingLeft: `calc(${paddingLeft} + 8px)` }}
                onClick={toggleOpen}
            >
                <div className="flex items-center min-w-0 flex-1 pr-2">
                    <span className="w-4 h-4 mr-1.5 flex-shrink-0 flex items-center justify-center text-[#8b949e]">
                        {isDir ? (
                            isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />
                        ) : (
                            <span className="w-4"></span> // Spacer for files so they align
                        )}
                    </span>

                    <span className="mr-2 flex-shrink-0">
                        {isDir ? (
                            isOpen ? <FolderOpen size={14} className="text-[#e3b341]" /> : <Folder size={14} className="text-[#e3b341]" />
                        ) : (
                            <File size={14} className={inContext ? "text-[#3fb950]" : ""} />
                        )}
                    </span>

                    <span className="truncate">{node.name}</span>
                </div>

                {inContext && (
                    <div className="w-2 h-2 rounded-full bg-[#3fb950] shadow-[0_0_5px_rgba(63,185,80,0.8)] mr-1 shrink-0"></div>
                )}
            </div>

            {isDir && isOpen && node.children && (
                <div>
                    {node.children.map((child) => (
                        <FileTreeNode
                            key={child.path}
                            node={child}
                            level={level + 1}
                            onSelect={onSelect}
                            contextPaths={contextPaths}
                        />
                    ))}
                </div>
            )}
        </div>
    )
}

export default function FileTree({ onFileSelect, contextPaths }) {
    const [treeData, setTreeData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        const fetchTree = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/files')
                if (!res.ok) throw new Error('Failed to fetch files')
                const data = await res.json()

                // Sometimes the root itself shouldn't be rendered as a single node, 
                // we might just want to render its children. We'll render the root for now.
                setTreeData(data)
                setLoading(false)
            } catch (err) {
                setError(err.message)
                setLoading(false)
            }
        }

        fetchTree()
    }, [])

    if (loading) return <div className="text-sm p-4 text-[#8b949e]">Loading workspace...</div>
    if (error) return <div className="text-sm p-4 text-[#f85149]">Error: {error}</div>
    if (!treeData) return null

    return (
        <div className="overflow-y-auto h-full w-full py-2 custom-scrollbar">
            {/* We typically start rendering from the root node itself */}
            <FileTreeNode node={treeData} onSelect={onFileSelect} />
        </div>
    )
}
