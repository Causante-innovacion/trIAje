import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import { Header, Footer } from './components/layout'
import { HomePage } from './components/home'
import { ChatPage } from './components/chat'
import { LegalFormPage } from './components/legal-form'

function AppContent() {
  const location = useLocation()
  const isLegalForm = location.pathname === '/legal-form'

  // Legal form page has its own layout
  if (isLegalForm) {
    return <LegalFormPage />
  }

  return (
    <div className="min-h-screen bg-gradient-main">
      <Header />

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/chat/:tool" element={<ChatPage />} />
      </Routes>

      <Footer />
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/legal-form" element={<LegalFormPage />} />
        <Route path="*" element={<AppContent />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
