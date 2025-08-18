import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import SignIn from './components/SignIn';
import PatientForm from './components/PatientForm';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/form" element={<PatientForm />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
