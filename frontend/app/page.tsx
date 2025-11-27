import Chat from '@/components/Chat'

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

