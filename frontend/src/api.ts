import { supabase } from './lib/supabaseClient'

export const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface Notebook {
  id: string
  name: string
  created_at: string
}

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

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations: ChatCitation[]
  created_at: string
}

export interface PresentationHistoryItem {
  id: string
  title: string
  topic: string
  created_at: string
}

async function authHeader(): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json()
    return body.detail ?? response.statusText
  } catch {
    return response.statusText
  }
}

// --- Notebooks ---

export async function listNotebooks(): Promise<Notebook[]> {
  const response = await fetch(`${API_URL}/notebooks`, { headers: await authHeader() })
  if (!response.ok) throw new Error(await parseErrorMessage(response))
  return response.json()
}

export async function createNotebook(name: string): Promise<Notebook> {
  const response = await fetch(`${API_URL}/notebooks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(await authHeader()) },
    body: JSON.stringify({ name }),
  })
  if (!response.ok) throw new Error(await parseErrorMessage(response))
  return response.json()
}

export async function renameNotebook(id: string, name: string): Promise<Notebook> {
  const response = await fetch(`${API_URL}/notebooks/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', ...(await authHeader()) },
    body: JSON.stringify({ name }),
  })
  if (!response.ok) throw new Error(await parseErrorMessage(response))
  return response.json()
}

export async function deleteNotebook(id: string): Promise<void> {
  const response = await fetch(`${API_URL}/notebooks/${id}`, {
    method: 'DELETE',
    headers: await authHeader(),
  })
  if (!response.ok) throw new Error(await parseErrorMessage(response))
}

// --- Sources ---

export async function listSources(notebookId: string): Promise<Source[]> {
  const response = await fetch(`${API_URL}/notebooks/${notebookId}/sources`, {
    headers: await authHeader(),
  })
  if (!response.ok) throw new Error(await parseErrorMessage(response))
  return response.json()
}

export async function uploadSource(notebookId: string, file: File): Promise<Source> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(`${API_URL}/notebooks/${notebookId}/sources`, {
    method: 'POST',
    headers: await authHeader(),
    body: formData,
  })
  if (!response.ok) throw new Error(await parseErrorMessage(response))
  return response.json()
}

export async function deleteSource(notebookId: string, id: string): Promise<void> {
  const response = await fetch(`${API_URL}/notebooks/${notebookId}/sources/${id}`, {
    method: 'DELETE',
    headers: await authHeader(),
  })
  if (!response.ok) throw new Error(await parseErrorMessage(response))
}

// --- Chat ---

export async function sendChatMessage(notebookId: string, question: string): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/notebooks/${notebookId}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(await authHeader()) },
    body: JSON.stringify({ question }),
  })
  if (!response.ok) throw new Error(await parseErrorMessage(response))
  return response.json()
}

export async function getChatHistory(notebookId: string): Promise<ChatMessage[]> {
  const response = await fetch(`${API_URL}/notebooks/${notebookId}/chat/history`, {
    headers: await authHeader(),
  })
  if (!response.ok) throw new Error(await parseErrorMessage(response))
  return response.json()
}

// --- Presentations ---

export interface PresentationOptions {
  topic: string
  sourceIds?: string[]
  designDescription?: string
  tone?: string
  slideCountHint?: string
}

export async function generatePresentation(
  notebookId: string,
  options: PresentationOptions
): Promise<Blob> {
  const response = await fetch(`${API_URL}/notebooks/${notebookId}/presentations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(await authHeader()) },
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

export async function listPresentationHistory(
  notebookId: string
): Promise<PresentationHistoryItem[]> {
  const response = await fetch(`${API_URL}/notebooks/${notebookId}/presentations`, {
    headers: await authHeader(),
  })
  if (!response.ok) throw new Error(await parseErrorMessage(response))
  return response.json()
}

export async function downloadPresentation(
  notebookId: string,
  presentationId: string
): Promise<Blob> {
  const response = await fetch(
    `${API_URL}/notebooks/${notebookId}/presentations/${presentationId}/download`,
    { headers: await authHeader() }
  )
  if (!response.ok) throw new Error(await parseErrorMessage(response))
  return response.blob()
}
