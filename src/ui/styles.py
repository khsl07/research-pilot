"""Modern executive styling for ResearchPilot Streamlit UI."""

CUSTOM_CSS = """
<style>
/* Main typography and container spacing */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* Header Branding */
.pilot-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1e3a8a 100%);
    color: #ffffff;
    padding: 24px 32px;
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
}
.pilot-header h1 {
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
    color: #ffffff !important;
}
.pilot-header p {
    font-size: 1.05rem;
    color: #94a3b8;
    margin: 6px 0 0 0;
}

/* Status Badges */
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.badge-verified {
    background-color: #dcfce7;
    color: #15803d;
    border: 1px solid #86efac;
}
.badge-partial {
    background-color: #fef9c3;
    color: #a16207;
    border: 1px solid #fde047;
}
.badge-unsupported {
    background-color: #fee2e2;
    color: #b91c1c;
    border: 1px solid #fca5a5;
}
.badge-high {
    background-color: #fee2e2;
    color: #b91c1c;
}
.badge-medium {
    background-color: #ffedd5;
    color: #c2410c;
}

/* Card Containers */
.pilot-card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.conflict-card {
    background: #ffffff;
    border-left: 5px solid #ef4444;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 14px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}

.scorecard-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
}
.scorecard-val {
    font-size: 2.2rem;
    font-weight: 700;
    color: #1e3a8a;
    line-height: 1;
}
.scorecard-label {
    font-size: 0.85rem;
    color: #64748b;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Stepper Node pill */
.step-pill {
    display: inline-flex;
    align-items: center;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
    margin-right: 8px;
    margin-bottom: 8px;
    background: #f1f5f9;
    color: #475569;
    border: 1px solid #cbd5e1;
}
.step-pill-active {
    background: #dbeafe;
    color: #1d4ed8;
    border-color: #93c5fd;
    font-weight: 600;
}
</style>
"""
