"use client";

import React from "react";
import { COMPLEXITY_LABELS } from "@/types";
import { Check } from "lucide-react";

const LEVEL_COLORS: Record<number, string> = {
    1: "#D2A59B",
    2: "#C99184",
    3: "#B88375",
    4: "#9B685C",
    5: "#6A4A43",
};

interface ComplexitySliderProps {
    value: number;
    pendingValue: number;
    onChange: (value: number) => void;
    onApply: () => void;
    disabled?: boolean;
}

export default function ComplexitySlider({
    value,
    pendingValue,
    onChange,
    onApply,
    disabled = false,
}: ComplexitySliderProps) {
    const hasChanged = pendingValue !== value;

    return (
        <div className="complexity-control">
            <span className="complexity-label">Complexity</span>
            <div className="complexity-slider-container">
                <span style={{ fontSize: 11, color: "var(--text-tertiary)" }}>Simple</span>
                <input
                    type="range"
                    min={1}
                    max={5}
                    step={1}
                    value={pendingValue}
                    onChange={(e) => onChange(Number(e.target.value))}
                    className="complexity-slider"
                    disabled={disabled}
                />
                <span style={{ fontSize: 11, color: "var(--text-tertiary)" }}>Expert</span>
            </div>
            <span
                className="complexity-badge"
                style={{ background: LEVEL_COLORS[pendingValue] }}
            >
                {COMPLEXITY_LABELS[pendingValue]}
            </span>
            <button
                className={`complexity-apply-btn ${hasChanged ? "visible" : ""}`}
                onClick={onApply}
                disabled={disabled || !hasChanged}
            >
                <Check size={12} style={{ marginRight: 4 }} />
                Apply
            </button>
        </div>
    );
}
