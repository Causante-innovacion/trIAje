import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import { Header, Footer } from './components/layout'
import { HomePage } from './components/home'
import { ChatPage } from './components/chat'
import { LegalFormPage } from './components/legal-form'
import { ProjectEvaluationPage } from './components/output-evaluation/ProjectEvaluationPage'
import { LegalAdviserPage } from './components/output-legal-adviser/LegalAdviserPage'

function AppContent() {
  const location = useLocation()
  const isLegalForm = location.pathname === '/legal-form'
  const isEvaluation = location.pathname === '/evaluation'
  const isLegalAdviser = location.pathname === '/legal-adviser'

  // Legal form, evaluation, and legal adviser pages have their own layouts
  if (isLegalForm) {
    return <LegalFormPage />
  }

  if (isEvaluation) {
    return <ProjectEvaluationPage />
  }

  if (isLegalAdviser) {
    return <LegalAdviserPage />
  }

  return (
    <div className="min-h-screen bg-gradient-main">
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
      <Header />
      <Routes>
        <Route path="/legal-form" element={<LegalFormPage />} />
        <Route path="/evaluation" element={<ProjectEvaluationPage />} />
        <Route path="/legal-adviser" element={<LegalAdviserPage />} />
        <Route path="*" element={<AppContent />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
