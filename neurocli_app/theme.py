from textual.theme import Theme

arctic_theme = Theme(
    name="arctic",
    primary="#88C0D0",
    secondary="#81A1C1",
    accent="#B48EAD",
    foreground="#D8DEE9",
    background="#2E3440",
    success="#A3BE8C",
    warning="#EBCB8B",
    error="#BF616A",
    surface="#3B4252",
    panel="#434C5E",
    dark=True,
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#88C0D0",
        "input-selection-background": "#81a1c1 35%",
    },
)


modern_theme = Theme(
    name="modern_dark_neon",
    primary="#00E5FF",        # Neon cyan (main highlight)
    secondary="#FF4081",      # Neon magenta (secondary / hover)
    accent="#00FF94",         # Neon green accent (rare use, "pop")
    foreground="#ECEFF4",     # Soft white text (not blinding)
    background="#0D1117",     # Deep charcoal (GitHub dark / modern terminals)
    success="#00FF94",        # Neon green success
    warning="#FFD54F",        # Warm yellow (modern, not eye-burn)
    error="#FF1744",          # Bold crimson red (cleaner than NES)
    surface="#161B22",        # Slightly lighter panel background
    panel="#1E242C",          # Even lighter surface for widgets
    dark=True,
    variables={
        "block-cursor-text-style": "reverse",
        "footer-key-foreground": "#00E5FF",  # footer hint neon
        "input-selection-background": "#00E5FF 40%",  # cyan selection glow
    },
)


solid_modern = Theme(
    name="solid_modern",
    primary="#37474F",        # Blue Grey 800
    secondary="#546E7A",      # Blue Grey 600
    accent="#00ACC1",         # Cyan 600
    foreground="#ECEFF1",     # Blue Grey 50
    background="#263238",     # Blue Grey 900
    success="#43A047",        # Green 600
    warning="#FB8C00",        # Orange 600
    error="#E53935",          # Red 600
    surface="#263238",        # Match background for solid look
    panel="#263238",          # Match background for solid look
    dark=True,
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#00ACC1",
        "input-selection-background": "#00ACC1 35%",
    },
)


fleet_dark = Theme(
    name="fleet_dark",
    primary="#4A90E2",        # Clean bright blue for primary actions
    secondary="#1C2E4A",      # Deep blue secondary
    accent="#4A90E2",         # Accent blue
    foreground="#F0F4F8",     # Crisp white/light-grey text
    background="#091425",     # Deep navy base background
    success="#10B981",        # Clean green
    warning="#F59E0B",        # Clean yellow
    error="#EF4444",          # Clean red
    surface="#0F1E36",        # Slightly lighter navy for inputs
    panel="#091425",          # Same as background to avoid boxed-in look
    dark=True,
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#4A90E2",
        "input-selection-background": "#4A90E2 35%",
    },
)
