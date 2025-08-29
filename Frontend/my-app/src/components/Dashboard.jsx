import React, { useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

function Dashboard() {
  const location = useLocation();
  const navigate = useNavigate();
  const email = location.state?.email || (typeof window !== 'undefined' ? localStorage.getItem('currentUserEmail') : '');

  const profile = useMemo(() => {
    if (!email) return null;
    try {
      const raw = localStorage.getItem(`patientProfile:${email}`);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }, [email]);

  const displayName = profile ? `${profile.firstName} ${profile.lastName}`.trim() : email || 'Patient';

  return (
    <div className="signin-page">
      <header className="brand-header" aria-label="Application name">
        <span className="brand-mark" aria-hidden>🩺</span>
        <span className="brand-name">DrConnect</span>
      </header>

      <main className="signin-container">
        <section className="signin-card" aria-label="Patient dashboard">
          <h1 className="signin-title">Welcome, {displayName}</h1>
          <p className="signin-subtitle">Your details</p>

          {profile ? (
            <div className="signin-form">
              <div className="form-field"><strong>Email:</strong> {profile.email}</div>
              <div className="form-field"><strong>Name:</strong> {profile.firstName} {profile.lastName}</div>
              <div className="form-field"><strong>Age:</strong> {profile.age}</div>
              <div className="form-field"><strong>Gender:</strong> {profile.gender}</div>
              <div className="form-field"><strong>Contact No:</strong> {profile.contactNumber || '—'}</div>
              <div className="form-field"><strong>Symptoms:</strong> {profile.symptoms}</div>
              <div className="form-field"><strong>Doctor:</strong> {profile.doctorName} ({profile.doctorSpecialty})</div>
            </div>
          ) : (
            <div className="signin-form">
              <p>No profile found for {email || 'current user'}.</p>
              <button className="submit-button" onClick={() => navigate('/form', { state: { email } })}>Complete Profile</button>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default Dashboard;


