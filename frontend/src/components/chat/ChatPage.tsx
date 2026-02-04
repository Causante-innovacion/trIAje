import { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ChatContainer } from './ChatContainer'
import { useChatStore } from '../../stores/chatStore'
import { ToolType } from '../../types/chat'

export function ChatPage() {
  const navigate = useNavigate()
  const { tool } = useParams<{ tool?: string }>()
  const { currentTool, startTool } = useChatStore()

  useEffect(() => {
    // If we have a tool param but no current tool, start that tool
    if (tool && !currentTool) {
      const validTools: ToolType[] = ['evaluation', 'compliance', 'advisor']
      if (validTools.includes(tool as ToolType)) {
        startTool(tool as ToolType)
      } else {
        navigate('/')
      }
    }

    // If no tool param and no current tool, redirect to home
    if (!tool && !currentTool) {
      navigate('/')
    }
  }, [tool, currentTool, startTool, navigate])

  if (!currentTool) {
    return null // Will redirect
  }

  return (
    <div className="min-h-screen flex flex-col pt-16 pb-4">
      <ChatContainer />
    </div>
  )
}
