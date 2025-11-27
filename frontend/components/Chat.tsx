'use client'

import { useState, useRef, useEffect } from 'react'
import { sendMessage } from '@/services/api'
import './Chat.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

/**
 * Formats a date to a consistent time string (HH:MM format)
 * This ensures server and client render the same format to avoid hydration errors
 */
const formatTime = (date: Date): string => {
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

export default function Chat() {
  // Initialize with empty array, then set initial message in useEffect to avoid hydration mismatch
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Initialize with welcome message on client side only to avoid hydration mismatch
  useEffect(() => {
    setMessages([
      {
        role: 'assistant',
        content: "Hello! I'm your mental coach. How can I support you today?",
        timestamp: new Date(),
      },
    ])
  }, [])

  // Auto-resize textarea to fit content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [input])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await sendMessage(userMessage.content)
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.reply,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: Message = {
        role: 'assistant',
        content: error instanceof Error 
          ? `Sorry, I encountered an error: ${error.message}` 
          : 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-container">
      <div className="messages-container">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
          >
            <div className="message-content">
              <div className="message-role">
                {message.role === 'user' ? 'You' : 'Coach'}
              </div>
              <div className="message-text">{message.content}</div>
              <div className="message-time">
                {formatTime(message.timestamp)}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant-message">
            <div className="message-content">
              <div className="message-role">Coach</div>
              <div className="message-text typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-container">
        <textarea
          ref={textareaRef}
          className="message-input"
          placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          rows={1}
          disabled={isLoading}
        />
        <button
          className="send-button"
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  )
}

