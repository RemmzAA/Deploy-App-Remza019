import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { LanguageProvider } from './i18n/LanguageContext';
import { AuthProvider } from './context/AuthContext';
import GamingDemo from './components/GamingDemo';
import AdminPanelWrapper from './components/admin/AdminPanelWrapper';
import MemberAuth from './components/member/MemberAuth';
import MemberDashboard from './components/member/MemberDashboard';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <LanguageProvider>
        <Router>
          <div className="App">
            <Routes>
              <Route path="/" element={<GamingDemo />} />
              <Route path="/gaming" element={<GamingDemo />} />
              <Route path="/admin" element={<AdminPanelWrapper />} />
              <Route path="/admin/*" element={<AdminPanelWrapper />} />
              <Route path="*" element={<GamingDemo />} />
            </Routes>
          </div>
        </Router>
      </LanguageProvider>
    </AuthProvider>
  );
}

export default App;