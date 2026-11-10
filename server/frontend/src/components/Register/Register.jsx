import React, {useState} from 'react';
import './Register.css';

// All five required inputs: Username, First Name, Last Name, Email, Password.
export default function Register() {
  const [values,setValues]=useState({userName:'',firstName:'',lastName:'',email:'',password:''});
  const [message,setMessage]=useState('');
  const [busy,setBusy]=useState(false);
  const update=(e)=>setValues({...values,[e.target.name]:e.target.value});
  const submit=async(e)=>{
    e.preventDefault();setMessage('');setBusy(true);
    try {
      const response=await fetch('/djangoapp/register', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify(values)
      });
      const body=await response.json();
      setMessage(response.ok ? 'Registration successful. You can now log in.' : body.message||'Registration failed.');
      if(response.ok) setValues({userName:'',firstName:'',lastName:'',email:'',password:''});
    } catch(err) {setMessage('Could not connect to the server.');}
    finally {setBusy(false);}
  };
  return <div className="register-page">
    <nav className="register-nav"><a href="http://127.0.0.1:8000/">BEST CARS</a><a href="http://127.0.0.1:8000/about">About Us</a><a href="http://127.0.0.1:8000/contact">Contact Us</a></nav>
    <main className="register-panel"><h1>Sign Up</h1><p>Create your Best Cars account.</p>
      <form onSubmit={submit}>
      <label htmlFor="userName">Username</label><input id="userName" name="userName" value={values.userName} onChange={update} autoComplete="username" required/>
      <label htmlFor="firstName">First Name</label><input id="firstName" name="firstName" value={values.firstName} onChange={update} autoComplete="given-name" required/>
      <label htmlFor="lastName">Last Name</label><input id="lastName" name="lastName" value={values.lastName} onChange={update} autoComplete="family-name" required/>
      <label htmlFor="email">Email</label><input type="email" id="email" name="email" value={values.email} onChange={update} autoComplete="email" required/>
      <label htmlFor="password">Password</label><input type="password" id="password" name="password" value={values.password} onChange={update} autoComplete="new-password" minLength={8} required/>
      <button type="submit" disabled={busy}>{busy?'Registering…':'Register'}</button>
      </form>
      {message&&<div className="register-message" role="status">{message}</div>}
    </main>
  </div>;
}
