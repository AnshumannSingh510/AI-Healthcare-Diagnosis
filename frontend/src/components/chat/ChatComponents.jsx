import React from 'react'

export function ChatBubble({ role, content }) {
  const isUser = role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm whitespace-pre-wrap
          ${isUser ? 'bg-brand-600 text-white rounded-br-sm' : 'bg-gray-100 text-gray-800 rounded-bl-sm'}`}
      >
        {content}
      </div>
    </div>
  )
}

export function ChatInput({ value, onChange, onSend, disabled }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSend()
    }
  }
  return (
    <div className="flex gap-2 border-t border-gray-200 pt-3">
      <textarea
        rows={1}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a general question about your results..."
        className="flex-1 resize-none rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
      />
      <button
        onClick={onSend}
        disabled={disabled || !value.trim()}
        className="bg-brand-600 disabled:bg-gray-300 text-white px-4 rounded-lg text-sm font-medium hover:bg-brand-700"
      >
        Send
      </button>
    </div>
  )
}
