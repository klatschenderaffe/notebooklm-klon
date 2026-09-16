import { useState } from 'react'
import type { ChatCitation } from '../api'
import { sendChatMessage } from '../api'

interface Message {
  role: 'user' | 'assistant'
  text: string
  citations?: ChatCitation[]
}

interface ChatPanelProps {
  hasSources: boolean
}

function ChatPanel({ hasSources }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [question, setQuestion] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = question.trim()
    if (!trimmed || isLoading) return

    setMessages((prev) => [...prev, { role: 'user', text: trimmed }])
    setQuestion('')
    setIsLoading(true)

    try {
      const response = await sendChatMessage(trimmed)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: response.answer, citations: response.citations },
      ])
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Anfrage fehlgeschlagen'
      setMessages((prev) => [...prev, { role: 'assistant', text: `Fehler: ${message}` }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section className="panel chat-panel">
      <h2>Fragen stellen</h2>

      <div className="chat-messages">
        {messages.length === 0 && (
          <p className="chat-empty">
            {hasSources
              ? 'Stelle eine Frage zu deinen hochgeladenen Quellen.'
              : 'Lade zuerst eine Quelle hoch, um Fragen stellen zu können.'}
          </p>
        )}
        {messages.map((message, i) => (
          <div key={i} className={`chat-message ${message.role}`}>
            <p>{message.text}</p>
            {message.citations && message.citations.length > 0 && (
              <ul className="citations">
                {message.citations.map((citation, j) => (
                  <li key={j}>
                    <strong>{citation.filename}:</strong> „{citation.excerpt}…“
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
        {isLoading && <p className="chat-empty">Antwort wird generiert …</p>}
      </div>

      <form className="chat-input-row" onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Frage zu deinen Quellen …"
          disabled={!hasSources || isLoading}
        />
        <button type="submit" disabled={!hasSources || isLoading || !question.trim()}>
          Senden
        </button>
      </form>
    </section>
  )
}

export default ChatPanel
