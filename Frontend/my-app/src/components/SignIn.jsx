import React, { useState } from 'react';
import './SignIn.css';

function SignIn() {
  const [mode, setMode] = useState('signup'); // 'signup' | 'login'
  const [fullName, setFullName] = useState('');
  const [emailAddress, setEmailAddress] = useState('');
  const [password, setPassword] = useState('');

  // const handleSubmit = (event) => {
  //   event.preventDefault();
  //   if (mode === 'login') {
  //     alert(`Logged in as ${emailAddress}`);
  //   } else {
  //     alert(`Account created for ${fullName}`);
  //   }
  // };
  const handleSubmit = async (event) => {
    event.preventDefault();
  
    let payload = {};
    let endpoint = "";
  
    if (mode === "login") {
      payload = { email: emailAddress, password };
      endpoint = "/login";
    } 
     else if (mode === "signup") {
      payload = { name: fullName, email: emailAddress, password };
      endpoint = "/signup";
    }
  
    try {
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
  
      const data = await response.json();
  
      if (response.ok) {
        alert(data.message || "Success");
      } else {
        alert(data.detail || "Something went wrong");
      }
    } catch (err) {
      console.error("Error:", err);
      alert("Network error");
    }
  };
  
  

  const toggleMode = () => {
    setMode((prev) => (prev === 'login' ? 'signup' : 'login'));
  };

  return (
    <div className="signin-page">
      <header className="brand-header" aria-label="Application name">
        <span className="brand-mark" aria-hidden>🩺</span>
        <span className="brand-name">DrConnect</span>
      </header>

      <main className="signin-container">
        <section className="signin-card" aria-label="Authentication form">
          <h1 className="signin-title">{mode === 'login' ? 'Log In' : 'Create Account'}</h1>
          <p className="signin-subtitle">
            {mode === 'login' ? 'Welcome back. Access your care securely.' : 'Join DrConnect for secure health access.'}
          </p>

          <form className="signin-form" onSubmit={handleSubmit} noValidate>
            {mode === 'signup' && (
              <div className="form-field">
                <label htmlFor="fullName">Full Name</label>
                <input
                  id="fullName"
                  name="fullName"
                  type="text"
                  placeholder="e.g., Jane Doe"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                  autoComplete="name"
                />
              </div>
            )}

            <div className="form-field">
              <label htmlFor="email">Email Address</label>
              <input
                id="email"
                name="email"
                type="email"
                placeholder="you@example.com"
                value={emailAddress}
                onChange={(e) => setEmailAddress(e.target.value)}
                required
                autoComplete="email"
              />
            </div>

            <div className="form-field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                minLength={6}
              />
            </div>

            <button type="submit" className="submit-button">
              {mode === 'login' ? 'Log In' : 'Create Account'}
            </button>

            <div className="form-toggle" aria-live="polite">
              {mode === 'login' ? (
                <span>
                  New to DrConnect?{' '}
                  <button type="button" className="link-button" onClick={toggleMode}>
                    Create account
                  </button>
                </span>
              ) : (
                <span>
                  Already have an account?{' '}
                  <button type="button" className="link-button" onClick={toggleMode}>
                    Log in
                  </button>
                </span>
              )}
            </div>
          </form>
        </section>
      </main>
    </div>
  );
}

export default SignIn;


