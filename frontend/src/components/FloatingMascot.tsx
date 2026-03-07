"use client";

import { useState, useEffect } from 'react';

const MASCOT_NAME = "Lumi";

export default function FloatingMascot() {
    const [isWaving, setIsWaving] = useState(false);
    const [isHovered, setIsHovered] = useState(false);
    const [eyePos, setEyePos] = useState({ x: 0, y: 0 });
    const [message, setMessage] = useState("");
    const [showName, setShowName] = useState(true);
    const [blink, setBlink] = useState(false);

    const greetings = [
        `Hi! I'm ${MASCOT_NAME} 👋`,
        "Need help? Just ask!",
        "Upload a PDF to start! 📄",
        "Try the Depth slider! 🎛️",
        "I learn from your docs! 🧠",
        "Click me for tips! ✨",
    ];

    useEffect(() => {
        const interval = setInterval(() => {
            setIsWaving(true);
            setTimeout(() => setIsWaving(false), 1500);
        }, 8000);
        const initialTimer = setTimeout(() => {
            setIsWaving(true);
            setMessage(`Hi! I'm ${MASCOT_NAME} 👋`);
            setTimeout(() => setIsWaving(false), 1500);
            setTimeout(() => setMessage(""), 4000);
        }, 1500);
        const nameTimer = setTimeout(() => setShowName(false), 6000);
        return () => { clearInterval(interval); clearTimeout(initialTimer); clearTimeout(nameTimer); };
    }, []);

    useEffect(() => {
        const blinkInterval = setInterval(() => {
            setBlink(true);
            setTimeout(() => setBlink(false), 200);
        }, 4000);
        return () => clearInterval(blinkInterval);
    }, []);

    useEffect(() => {
        const handleMouse = (e: MouseEvent) => {
            const x = Math.min(3, Math.max(-3, (e.clientX / window.innerWidth - 0.5) * 8));
            const y = Math.min(2, Math.max(-2, (e.clientY / window.innerHeight - 0.5) * 6));
            setEyePos({ x, y });
        };
        window.addEventListener('mousemove', handleMouse);
        return () => window.removeEventListener('mousemove', handleMouse);
    }, []);

    const handleClick = () => {
        const msg = greetings[Math.floor(Math.random() * greetings.length)];
        setMessage(msg);
        setIsWaving(true);
        setShowName(true);
        setTimeout(() => setIsWaving(false), 1500);
        setTimeout(() => setMessage(""), 3500);
        setTimeout(() => setShowName(false), 5000);
    };

    return (
        <div
            className="floating-mascot-wrapper"
            onClick={handleClick}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            style={{
                position: 'fixed',
                bottom: '80px',
                left: '75px',
                zIndex: 1000,
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '4px',
            }}
        >
            {/* Speech Bubble */}
            {message && (
                <div style={{
                    position: 'absolute',
                    bottom: '100%',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    background: 'white',
                    border: '2px solid #D2A59B',
                    borderRadius: '18px',
                    padding: '10px 16px',
                    fontSize: '13px',
                    fontWeight: 700,
                    color: '#6A4A43',
                    whiteSpace: 'nowrap',
                    marginBottom: '10px',
                    animation: 'popIn 0.3s ease',
                    boxShadow: '0 6px 20px rgba(106, 74, 67, 0.15)',
                }}>
                    {message}
                    <div style={{
                        position: 'absolute',
                        bottom: '-7px',
                        left: '50%',
                        transform: 'translateX(-50%) rotate(45deg)',
                        width: '12px',
                        height: '12px',
                        background: 'white',
                        borderRight: '2px solid #D2A59B',
                        borderBottom: '2px solid #D2A59B',
                    }} />
                </div>
            )}

            {/* Cute Robot SVG */}
            <div style={{
                transition: 'transform 0.3s ease',
                transform: isHovered ? 'scale(1.12) translateY(-4px)' : 'scale(1)',
                filter: 'drop-shadow(0 12px 25px rgba(106, 74, 67, 0.25))',
            }}>
                <svg width="150" height="180" viewBox="0 0 100 120" style={{
                    animation: 'float 3s ease-in-out infinite',
                }}>
                    {/* Antenna */}
                    <line x1="50" y1="5" x2="50" y2="16" stroke="#D2A59B" strokeWidth="2.5" strokeLinecap="round" />
                    <circle cx="50" cy="4" r="4.5" fill={isWaving ? "#FFD700" : "#D2A59B"} style={{ transition: 'fill 0.3s' }}>
                        {isWaving && <animate attributeName="r" values="4.5;6;4.5" dur="0.6s" repeatCount="indefinite" />}
                    </circle>

                    {/* HEAD - square rounded rect */}
                    <rect x="18" y="16" width="64" height="50" rx="14" fill="white" stroke="#D2A59B" strokeWidth="2.5" />

                    {/* Ears */}
                    <circle cx="14" cy="38" r="6" fill="#EED8D2" stroke="#D2A59B" strokeWidth="1.5" />
                    <circle cx="86" cy="38" r="6" fill="#EED8D2" stroke="#D2A59B" strokeWidth="1.5" />
                    <circle cx="14" cy="38" r="3" fill="#D2A59B" opacity="0.3" />
                    <circle cx="86" cy="38" r="3" fill="#D2A59B" opacity="0.3" />

                    {/* EYES */}
                    {blink ? (
                        <>
                            <path d={`M${33 + eyePos.x} ${40 + eyePos.y} Q${38 + eyePos.x} ${36 + eyePos.y} ${43 + eyePos.x} ${40 + eyePos.y}`} stroke="#6A4A43" strokeWidth="2.5" fill="none" strokeLinecap="round" />
                            <path d={`M${57 + eyePos.x} ${40 + eyePos.y} Q${62 + eyePos.x} ${36 + eyePos.y} ${67 + eyePos.x} ${40 + eyePos.y}`} stroke="#6A4A43" strokeWidth="2.5" fill="none" strokeLinecap="round" />
                        </>
                    ) : (
                        <>
                            {/* Left eye */}
                            <circle cx={38 + eyePos.x} cy={39 + eyePos.y} r="8" fill="#6A4A43" />
                            <circle cx={36 + eyePos.x} cy={36 + eyePos.y} r="3" fill="white" />
                            <circle cx={41 + eyePos.x} cy={41 + eyePos.y} r="1.5" fill="white" opacity="0.6" />
                            {/* Right eye */}
                            <circle cx={62 + eyePos.x} cy={39 + eyePos.y} r="8" fill="#6A4A43" />
                            <circle cx={60 + eyePos.x} cy={36 + eyePos.y} r="3" fill="white" />
                            <circle cx={65 + eyePos.x} cy={41 + eyePos.y} r="1.5" fill="white" opacity="0.6" />
                        </>
                    )}

                    {/* Cheeks - always rosy */}
                    <ellipse cx="26" cy="49" rx="7" ry="4" fill="rgba(210,165,155,0.4)" />
                    <ellipse cx="74" cy="49" rx="7" ry="4" fill="rgba(210,165,155,0.4)" />
                    {isHovered && (
                        <>
                            <ellipse cx="26" cy="49" rx="8" ry="5" fill="rgba(210,140,130,0.35)" />
                            <ellipse cx="74" cy="49" rx="8" ry="5" fill="rgba(210,140,130,0.35)" />
                        </>
                    )}

                    {/* Nose dot */}
                    <circle cx="50" cy="47" r="1.2" fill="#D2A59B" />

                    {/* Mouth */}
                    {isHovered ? (
                        <ellipse cx="50" cy="53" rx="5" ry="4" fill="#E8A090" stroke="#D2A59B" strokeWidth="1" />
                    ) : (
                        <>
                            <path d="M43 52 Q46.5 56 50 52" stroke="#D2A59B" strokeWidth="2" fill="none" strokeLinecap="round" />
                            <path d="M50 52 Q53.5 56 57 52" stroke="#D2A59B" strokeWidth="2" fill="none" strokeLinecap="round" />
                        </>
                    )}

                    {/* BODY */}
                    <rect x="33" y="68" width="34" height="24" rx="12" fill="#D2A59B" />
                    <ellipse cx="50" cy="80" rx="9" ry="7" fill="white" opacity="0.2" />
                    {/* Heart */}
                    <path d="M47 77 C47 75, 50 74, 50 76 C50 74, 53 75, 53 77 C53 79, 50 81, 50 81 C50 81, 47 79, 47 77Z" fill="white" opacity="0.5" />

                    {/* Left Arm - WAVING */}
                    <g style={{
                        transformOrigin: '33px 74px',
                        animation: isWaving ? 'wave 0.4s ease-in-out infinite alternate' : 'armIdle 2s ease-in-out infinite',
                    }}>
                        <rect x="14" y="71" width="19" height="10" rx="5" fill="#C99184" />
                        <circle cx="16" cy="76" r="5.5" fill="#C99184" />
                    </g>

                    {/* Right Arm */}
                    <g>
                        <rect x="67" y="71" width="19" height="10" rx="5" fill="#C99184" />
                        <circle cx="84" cy="76" r="5.5" fill="#C99184" />
                    </g>

                    {/* Feet */}
                    <ellipse cx="40" cy="93" rx="8" ry="5" fill="#B88375" />
                    <ellipse cx="60" cy="93" rx="8" ry="5" fill="#B88375" />
                    <ellipse cx="38" cy="91" rx="3" ry="1.5" fill="white" opacity="0.2" />
                    <ellipse cx="58" cy="91" rx="3" ry="1.5" fill="white" opacity="0.2" />

                    {/* Sparkles on hover */}
                    <g opacity={isHovered ? 1 : 0} style={{ transition: 'opacity 0.3s' }}>
                        <text x="6" y="18" fontSize="8" fill="#FFD700">✦</text>
                        <text x="85" y="14" fontSize="6" fill="#FFD700">✦</text>
                        <text x="90" y="62" fontSize="7" fill="#FFD700">✦</text>
                    </g>
                </svg>
            </div>

            {/* Name Tag */}
            <div style={{
                fontFamily: "'Outfit', sans-serif",
                fontSize: '13px',
                fontWeight: 800,
                color: '#D2A59B',
                textTransform: 'uppercase',
                letterSpacing: '0.15em',
                opacity: showName || isHovered ? 1 : 0,
                transition: 'opacity 0.5s ease',
                marginTop: '-8px',
            }}>
                {MASCOT_NAME}
            </div>

            <style jsx>{`
                @keyframes float {
                    0%, 100% { transform: translateY(0px); }
                    50% { transform: translateY(-8px); }
                }
                @keyframes wave {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(-35deg); }
                }
                @keyframes armIdle {
                    0%, 100% { transform: rotate(0deg); }
                    50% { transform: rotate(-5deg); }
                }
                @keyframes popIn {
                    0% { transform: translateX(-50%) scale(0.5); opacity: 0; }
                    100% { transform: translateX(-50%) scale(1); opacity: 1; }
                }
            `}</style>
        </div>
    );
}
