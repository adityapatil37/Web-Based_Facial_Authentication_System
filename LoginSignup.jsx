import React from 'react' 
import './LoginSignup.css'
import { useState } from 'react'

import user_icon from '../Assets/person.png'
import email_icon from '../Assets/email.png'
import password_icon from '../Assets/password.png'

const LoginSignup = () => {

    const [action,setAction] = useState("Sign Up");

    return (
        <div className='container'>
            <div className="header">
                <div className="text">{action}</div>
                <div className="underline"></div>
            </div>
            <div className="inputs">
                <div className="input">
                    <img src={user_icon} alt="" />
                    <input type="text" placeholder='Enter your username' />  
                </div>
                
                   
                <div className="input">
                    <img src={password_icon} alt="" />
                    <input type="password" placeholder='Enter Your Password' />  
                </div>
            </div>
            {action==="Sign Up"?<div></div>:<div className="forgot-password">Lost Password? <span>Click Here!</span></div>}
                <div className="submit-container">
                    <div className= {action==="Login"?"submit gray":"submit"} onClick={() => {setAction("Sign Up")}}>Sign Up</div>
                    <div className={action==="Sign Up"?"suubmit gray":"submit"} onClick={() => {setAction("Login")}}>Login In</div>
                </div>
        </div>
    );
};

export default LoginSignup