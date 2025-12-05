import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { LanguageProvider } from './i18n/LanguageContext';
import GamingDemo from './components/GamingDemo';
import AdminPanelWrapper from './components/admin/AdminPanelWrapper';
import './App.css';

function App() {
  return (
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
  );
}

export default App;