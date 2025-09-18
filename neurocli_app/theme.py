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
