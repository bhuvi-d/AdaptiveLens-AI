"use client";

import React from "react";
import { BarChart3 } from "lucide-react";

interface ReadabilityBadgeProps {
    score: number;
    label: string;
}

export default function ReadabilityBadge({ score, label }: ReadabilityBadgeProps) {
    const getClass = () => {
        if (score >= 60) return "readability-easy";
        if (score >= 40) return "readability-standard";
        return "readability-hard";
    };

    return (
        <span className={`readability-badge ${getClass()}`}>
            <BarChart3 size={12} />
            Readability: {score} ({label})
        </span>
    );
}
