export const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface Source {
  id: string
  filename: string
  file_type: 'pdf' | 'md'
  created_at: string
}

export interface ChatCitation {
  filename: string
  excerpt: string
}

export interface ChatResponse {
  answer: string
  citations: ChatCitation[]
}

async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json()
    return body.detail ?? response.statusText
  } catch {
    return response.statusText
  }
}

export async function listSources(): Promise<Source[]> {
  const response = await fetch(`${API_URL}/sources`)
  if (!response.ok) throw new Error(await parseErrorMessage(response))
  return response.json()
}

export async function uploadSource(file: File): Promise<Source> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(`${API_URL}/sources`, { method: 'POST', body: formData })
  if (!response.ok) throw new Error(await parseErrorMessage(response))
  return response.json()
}

export async function deleteSource(id: string): Promise<void> {
  const response = await fetch(`${API_URL}/sources/${id}`, { method: 'DELETE' })
  if (!response.ok) throw new Error(await parseErrorMessage(response))
}

export async function sendChatMessage(question: string): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })
  if (!response.ok) throw new Error(await parseErrorMessage(response))
  return response.json()
}

export interface PresentationOptions {
  topic: string
  sourceIds?: string[]
  designDescription?: string
  tone?: string
  slideCountHint?: string
}

export async function generatePresentation(options: PresentationOptions): Promise<Blob> {
  const response = await fetch(`${API_URL}/presentations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topic: options.topic,
      source_ids: options.sourceIds,
      design_description: options.designDescription || null,
      tone: options.tone || null,
      slide_count_hint: options.slideCountHint || null,
    }),
  })
  if (!response.ok) throw new Error(await parseErrorMessage(response))
  return response.blob()
}
