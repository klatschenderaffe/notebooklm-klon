import { useState } from 'react'
import { generatePresentation } from '../api'

interface PresentationPanelProps {
  hasSources: boolean
}

function PresentationPanel({ hasSources }: PresentationPanelProps) {
  const [topic, setTopic] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = topic.trim()
    if (!trimmed || isGenerating) return

    setError(null)
    setIsGenerating(true)
    try {
      const blob = await generatePresentation(trimmed)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'praesentation.pptx'
      link.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Präsentation konnte nicht erstellt werden')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <section className="panel presentation-panel">
      <h2>Präsentation erstellen</h2>
      <form onSubmit={handleGenerate} className="presentation-form">
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Thema der Präsentation …"
          disabled={!hasSources || isGenerating}
        />
        <button type="submit" disabled={!hasSources || isGenerating || !topic.trim()}>
          {isGenerating ? 'Wird erstellt …' : 'Als PPTX herunterladen'}
        </button>
      </form>
      {error && <p className="error-text">{error}</p>}
    </section>
  )
}

export default PresentationPanel
