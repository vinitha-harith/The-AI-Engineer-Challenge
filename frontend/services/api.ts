const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

export interface ChatResponse {
  reply: string
}

/**
 * Sends a message to the Mental Coach API
 * @param message - The user's message to send
 * @returns Promise resolving to the chat response
 * @throws Error if the API request fails
 */
export const sendMessage = async (message: string): Promise<ChatResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP error! status: ${response.status}`)
  }

  return response.json()
}

