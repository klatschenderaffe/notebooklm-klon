import { useState } from 'react'
import { generatePresentation } from '../api'

interface PresentationPanelProps {
  notebookId: string
  hasSources: boolean
  selectedSourceIds: string[]
}

const COLOR_PRESETS: { label: string; description: string }[] = [
  {
    label: 'Minimal',
    description: 'Minimalistisch, viel Weißraum, gedeckte neutrale Farben, klare Typografie',
  },
  {
    label: 'Bunt',
    description: 'Verspielt und bunt, kräftige kontrastreiche Farben, lebendige Stimmung',
  },
  { label: 'Dunkel', description: 'Dunkles Farbschema mit hellem Text, moderne edle Wirkung' },
  {
    label: 'Corporate',
    description: 'Seriös und professionell, gedecktes Blau/Grau, klassische Business-Optik',
  },
]

const SLIDE_COUNT_OPTIONS = [
  { label: 'Gemini entscheidet', value: '' },
  { label: 'Kurz (~5 Folien)', value: 'ca. 5 Folien' },
  { label: 'Mittel (~10 Folien)', value: 'ca. 10 Folien' },
  { label: 'Lang (~15 Folien)', value: 'ca. 15 Folien' },
]

const TONE_OPTIONS = [
  { label: 'Keine Angabe', value: '' },
  { label: 'Formell', value: 'Formell' },
  { label: 'Locker', value: 'Locker' },
  { label: 'Einfach erklärt', value: 'Einfach erklärt, für Laien verständlich' },
]

function PresentationPanel({ notebookId, hasSources, selectedSourceIds }: PresentationPanelProps) {
  const [topic, setTopic] = useState('')
  const [designDescription, setDesignDescription] = useState('')
  const [tone, setTone] = useState('')
  const [slideCountHint, setSlideCountHint] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [readyToOpenInDrive, setReadyToOpenInDrive] = useState(false)

  const hasSelection = selectedSourceIds.length > 0

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = topic.trim()
    if (!trimmed || isGenerating || !hasSelection) return

    setError(null)
    setReadyToOpenInDrive(false)
    setIsGenerating(true)
    try {
      const blob = await generatePresentation(notebookId, {
        topic: trimmed,
        sourceIds: selectedSourceIds,
        designDescription: designDescription.trim(),
        tone,
        slideCountHint,
      })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'praesentation.pptx'
      link.click()
      URL.revokeObjectURL(url)
      setReadyToOpenInDrive(true)
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

        <textarea
          className="design-textarea"
          value={designDescription}
          onChange={(e) => setDesignDescription(e.target.value)}
          placeholder="Design-Beschreibung (optional), z.B. „modern und minimalistisch in Blau“"
          disabled={!hasSources || isGenerating}
          rows={2}
        />
        <div className="preset-row">
          {COLOR_PRESETS.map((preset) => (
            <button
              key={preset.label}
              type="button"
              className="preset-button"
              disabled={!hasSources || isGenerating}
              onClick={() => setDesignDescription(preset.description)}
            >
              {preset.label}
            </button>
          ))}
        </div>

        <div className="select-row">
          <label className="select-label">
            Ton
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              disabled={!hasSources || isGenerating}
            >
              {TONE_OPTIONS.map((opt) => (
                <option key={opt.label} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
          <label className="select-label">
            Länge
            <select
              value={slideCountHint}
              onChange={(e) => setSlideCountHint(e.target.value)}
              disabled={!hasSources || isGenerating}
            >
              {SLIDE_COUNT_OPTIONS.map((opt) => (
                <option key={opt.label} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <button
          type="submit"
          disabled={!hasSources || !hasSelection || isGenerating || !topic.trim()}
        >
          {isGenerating ? 'Wird erstellt …' : 'Als PPTX herunterladen'}
        </button>
        {!hasSelection && hasSources && (
          <p className="hint-text">Wähle mindestens eine Quelle aus.</p>
        )}
      </form>
      {error && <p className="error-text">{error}</p>}
      {readyToOpenInDrive && (
        <div className="drive-hint">
          <button
            type="button"
            className="drive-button"
            onClick={() => window.open('https://drive.google.com/drive/my-drive', '_blank')}
          >
            In Google Drive öffnen ↗
          </button>
          <p className="hint-text">
            Heruntergeladene Datei dort per Drag &amp; Drop hochladen — Google konvertiert sie
            automatisch zu Google Präsentationen.
          </p>
        </div>
      )}
    </section>
  )
}

export default PresentationPanel
