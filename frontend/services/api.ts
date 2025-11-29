// API Base URL configuration:
// - Production: Use NEXT_PUBLIC_API_URL env var, or empty string (uses Vercel rewrites)
// - Development: Use localhost when running locally
const API_BASE_URL = 
  process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000'
    : '')

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
  // Construct API URL - handle empty base URL (uses relative path)
  const apiUrl = API_BASE_URL 
    ? `${API_BASE_URL.replace(/\/$/, '')}/api/chat`  // Remove trailing slash if present
    : '/api/chat'  // Relative path for Vercel rewrites
  
  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
      cache: 'no-store', // Disable caching for this request
      body: JSON.stringify({ message }),
    })

    if (!response.ok) {
      // Try to get error message from response
      let errorMessage = `HTTP error! status: ${response.status}`
      try {
        const errorData = await response.json()
        errorMessage = errorData.detail || errorData.message || errorMessage
      } catch {
        // If response is not JSON, use status text
        errorMessage = response.statusText || errorMessage
      }
      throw new Error(errorMessage)
    }

    return response.json()
  } catch (error) {
    // Handle network errors or other fetch failures
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Unable to connect to the server. Please check your connection and ensure the backend is running.')
    }
    throw error
  }
}

