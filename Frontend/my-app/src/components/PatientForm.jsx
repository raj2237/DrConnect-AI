import React, { useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const doctors = [
  { id: 'd1', name: 'Dr. Alice Carter', specialty: 'Cardiology' },
  { id: 'd2', name: 'Dr. Brian Singh', specialty: 'Neurology' },
  { id: 'd3', name: 'Dr. Clara Gomez', specialty: 'Pediatrics' },
  { id: 'd4', name: 'Dr. David Kim', specialty: 'Dermatology' },
  { id: 'd5', name: 'Dr. Emma Rossi', specialty: 'Orthopedics' }
];

function PatientForm() {
  const navigate = useNavigate();
  const location = useLocation();
  const signupEmail = location.state?.email || '';
  const signupFullName = location.state?.fullName || '';

  const defaultNames = useMemo(() => {
    const parts = signupFullName.trim().split(/\s+/);
    const first = parts[0] || '';
    const last = parts.slice(1).join(' ') || '';
    return { first, last };
  }, [signupFullName]);

  const [firstName, setFirstName] = useState(defaultNames.first);
  const [lastName, setLastName] = useState(defaultNames.last);
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [contactNumber, setContactNumber] = useState('');
  const [symptoms, setSymptoms] = useState('');
  const [doctorId, setDoctorId] = useState('');

  const selectedDoctor = doctors.find(d => d.id === doctorId) || null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!firstName || !lastName || !age || !gender || !symptoms || !doctorId) {
      alert('Please fill in all required fields.');
      return;
    }

    const profile = {
      email: signupEmail || (typeof window !== 'undefined' ? localStorage.getItem('currentUserEmail') : ''),
      firstName,
      lastName,
      age: Number(age),
      gender,
      contactNumber,
      symptoms,
      doctorId,
      doctorName: selectedDoctor ? selectedDoctor.name : '',
      doctorSpecialty: selectedDoctor ? selectedDoctor.specialty : '',
      createdAt: new Date().toISOString()
    };

    try {
      const emailKey = profile.email || 'anonymous';
      localStorage.setItem(`patientProfile:${emailKey}`, JSON.stringify(profile));
    } catch (err) {}

    navigate('/dashboard', { state: { email: profile.email } });
  };

  return (
    <div className="signin-page">
      <header className="brand-header" aria-label="Application name">
        <span className="brand-mark" aria-hidden>🩺</span>
        <span className="brand-name">DrConnect</span>
      </header>

      <main className="signin-container">
        <section className="signin-card" aria-label="Patient details form">
          <h1 className="signin-title">Complete Your Profile</h1>
          <p className="signin-subtitle">Please provide your details to continue.</p>

          <form className="signin-form" onSubmit={handleSubmit} noValidate>
            <div className="form-field">
              <label htmlFor="firstName">First Name</label>
              <input
                id="firstName"
                name="firstName"
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="lastName">Last Name</label>
              <input
                id="lastName"
                name="lastName"
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="age">Age</label>
              <input
                id="age"
                name="age"
                type="number"
                min="0"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="gender">Gender</label>
              <select id="gender" name="gender" value={gender} onChange={(e) => setGender(e.target.value)} required>
                <option value="" disabled>Select gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="form-field">
              <label htmlFor="contactNumber">Contact No</label>
              <input
                id="contactNumber"
                name="contactNumber"
                type="tel"
                placeholder="e.g., +1 555 123 4567"
                value={contactNumber}
                onChange={(e) => setContactNumber(e.target.value)}
              />
            </div>

            <div className="form-field">
              <label htmlFor="symptoms">Symptoms</label>
              <textarea
                id="symptoms"
                name="symptoms"
                placeholder="Describe your symptoms"
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="doctor">Choose a Doctor</label>
              <select id="doctor" name="doctor" value={doctorId} onChange={(e) => setDoctorId(e.target.value)} required>
                <option value="" disabled>Select doctor</option>
                {doctors.map((doc) => (
                  <option key={doc.id} value={doc.id}>{`${doc.name} — ${doc.specialty}`}</option>
                ))}
              </select>
            </div>

            <button type="submit" className="submit-button">Save and Continue</button>
          </form>
        </section>
      </main>
    </div>
  );
}

export default PatientForm;


