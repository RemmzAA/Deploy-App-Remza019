import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import GamingDemo from './components/GamingDemo';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<GamingDemo />} />
          <Route path="/gaming" element={<GamingDemo />} />
          <Route path="*" element={<GamingDemo />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;