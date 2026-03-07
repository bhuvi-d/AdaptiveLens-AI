"use client";

import React from "react";

// Cute chibi Lumi face for chat avatar
export default function LumiAvatar({ size = 40 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 50 50" style={{ display: 'block' }}>
            {/* Head - big round */}
            <ellipse cx="25" cy="26" rx="22" ry="19" fill="white" stroke="#D2A59B" strokeWidth="2" />

            {/* Antenna */}
            <line x1="25" y1="3" x2="25" y2="8" stroke="#D2A59B" strokeWidth="2" strokeLinecap="round" />
            <circle cx="25" cy="2.5" r="3" fill="#D2A59B" />

            {/* Ears */}
            <circle cx="4" cy="22" r="4" fill="#EED8D2" stroke="#D2A59B" strokeWidth="1.5" />
            <circle cx="46" cy="22" r="4" fill="#EED8D2" stroke="#D2A59B" strokeWidth="1.5" />

            {/* Eyes - big kawaii */}
            <circle cx="17" cy="25" r="5.5" fill="#6A4A43" />
            <circle cx="33" cy="25" r="5.5" fill="#6A4A43" />
            {/* Eye sparkle */}
            <circle cx="15" cy="23" r="2" fill="white" />
            <circle cx="31" cy="23" r="2" fill="white" />
            <circle cx="19" cy="27" r="1" fill="white" opacity="0.5" />
            <circle cx="35" cy="27" r="1" fill="white" opacity="0.5" />

            {/* Cheeks */}
            <ellipse cx="10" cy="31" rx="5" ry="3" fill="rgba(210,165,155,0.4)" />
            <ellipse cx="40" cy="31" rx="5" ry="3" fill="rgba(210,165,155,0.4)" />

            {/* Nose dot */}
            <circle cx="25" cy="30" r="1" fill="#D2A59B" />

            {/* Cat smile :3 */}
            <path d="M20 33 Q22.5 36 25 33" stroke="#D2A59B" strokeWidth="1.5" fill="none" strokeLinecap="round" />
            <path d="M25 33 Q27.5 36 30 33" stroke="#D2A59B" strokeWidth="1.5" fill="none" strokeLinecap="round" />

            {/* Tiny body peek */}
            <rect x="17" y="44" width="16" height="6" rx="3" fill="#D2A59B" />
        </svg>
    );
}
