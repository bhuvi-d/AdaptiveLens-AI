"use client";

import { useState, useEffect, Component, ReactNode } from 'react';
import dynamic from 'next/dynamic';

// Dynamically import Spline (client-only)
const Spline = dynamic(() => import('@splinetool/react-spline'), { ssr: false });

// ---- Error Boundary to catch Spline runtime crashes ----
class SplineErrorBoundary extends Component<{ children: ReactNode; fallback: ReactNode }, { hasError: boolean }> {
    constructor(props: any) {
        super(props);
        this.state = { hasError: false };
    }
    static getDerivedStateFromError() {
        return { hasError: true };
    }
    componentDidCatch(error: any) {
        console.warn("Spline crashed, showing mascot image:", error?.message);
    }
    render() {
        if (this.state.hasError) return this.props.fallback;
        return this.props.children;
    }
}

// ---- Mascot Image (always works) ----
function MascotImage() {
    return (
        <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <img
                src="/mascot.png"
                alt="AdaptiveLens AI Mascot"
                style={{ maxWidth: '80%', maxHeight: '90%', objectFit: 'contain', filter: 'drop-shadow(0 10px 30px rgba(106,74,67,0.15))' }}
            />
        </div>
    );
}

// ---- Main Component ----
// To use your own Spline scene, set SPLINE_URL below.
// Get a public URL from https://app.spline.design → Export → Web Content → Copy Link
const SPLINE_URL = ""; // Paste your public .splinecode URL here

export default function SplineScene() {
    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => { setIsMounted(true); }, []);
    if (!isMounted) return null;

    return (
        <div className="spline-container" style={{
            width: '100%',
            height: '350px',
            position: 'relative',
            marginBottom: '32px',
            borderRadius: '28px',
            overflow: 'hidden',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'white',
            border: '1px solid var(--border-muted)',
            boxShadow: '0 20px 60px rgba(106, 74, 67, 0.1)'
        }}>
            {SPLINE_URL ? (
                <SplineErrorBoundary fallback={<MascotImage />}>
                    <Spline
                        scene={SPLINE_URL}
                        style={{ width: '100%', height: '100%' }}
                    />
                </SplineErrorBoundary>
            ) : (
                <MascotImage />
            )}

            {/* Fade overlay */}
            <div style={{
                position: 'absolute',
                bottom: 0, left: 0, right: 0,
                height: '60px',
                background: 'linear-gradient(to top, white, transparent)',
                pointerEvents: 'none'
            }} />
        </div>
    );
}
