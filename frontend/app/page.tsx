import Chat from '@/components/Chat'

// Force dynamic rendering to prevent static generation
export const dynamic = 'force-dynamic'
export const revalidate = 0

export default function Home() {
  return (
    <main className="app">
      <header className="app-header">
        <h1>🧠 Mental Coach</h1>
        <p>Your supportive AI companion for mental wellness</p>
      </header>
      <Chat />
    </main>
  )
}

