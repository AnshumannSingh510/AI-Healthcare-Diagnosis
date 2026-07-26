import React, { useEffect, useState, useRef } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { chatApi } from '../services/api'
import Card from '../components/common/Card.jsx'
import Disclaimer from '../components/common/Disclaimer.jsx'
import { ChatBubble, ChatInput } from '../components/chat/ChatComponents.jsx'

export default function ChatPage() {
  const { user } = useAuth()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    if (!user) return
    chatApi.history(user.id).then(({ data }) => {
      const flat = data.flatMap((e) => [
        { role: 'user', content: e.question },
        { role: 'assistant', content: e.answer },
      ])
      setMessages(flat)
    })
  }, [user])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim()) return
    const question = input
    setInput('')
    setMessages((m) => [...m, { role: 'user', content: question }])
    setSending(true)
    try {
      const { data } = await chatApi.send(question)
      setMessages((m) => [...m, { role: 'assistant', content: data.answer }])
    } catch {
      setMessages((m) => [...m, { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' }])
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-6 py-10 space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">AI Chat Assistant</h1>
      <Disclaimer text="This assistant provides general information only and never gives a definitive diagnosis. Always consult a licensed physician." />
      <Card className="flex flex-col h-[60vh]">
        <div className="flex-1 overflow-y-auto space-y-3 pr-1">
          {messages.length === 0 && (
            <p className="text-gray-400 text-sm">Ask a general question about chest X-ray findings, terminology, or next steps.</p>
          )}
          {messages.map((m, i) => <ChatBubble key={i} role={m.role} content={m.content} />)}
          <div ref={bottomRef} />
        </div>
        <div className="pt-2">
          <ChatInput value={input} onChange={setInput} onSend={handleSend} disabled={sending} />
        </div>
      </Card>
    </div>
  )
}
