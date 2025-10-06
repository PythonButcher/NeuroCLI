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
    name="modern_dark_neutral",
    primary="#5A8DEE",        # Refined cobalt highlight
    secondary="#7F8EA3",      # Muted slate accent
    accent="#E4A788",         # Warm neutral accent
    foreground="#E6ECF4",     # Gentle off-white for text
    background="#0F141C",     # Deep charcoal backdrop
    success="#58C4A3",        # Calming teal success
    warning="#E6B673",        # Soft amber warning
    error="#D96C6C",          # Muted crimson error
    surface="#171D26",        # Elevated surface tone
    panel="#1E2430",          # Panel background
    dark=True,
    variables={
        "block-cursor-text-style": "reverse",
        "footer-key-foreground": "#5A8DEE",
        "input-selection-background": "#5A8DEE 35%",
    },
)


nocturne_theme = Theme(
    name="nocturne",
    primary="#5B8DEF",
    secondary="#22345F",
    accent="#8BA8FF",
    foreground="#E2E8F0",
    background="#060B16",
    success="#58C4A3",
    warning="#E6B673",
    error="#F07178",
    surface="#0B1324",
    panel="#111C33",
    dark=True,
    variables={
        "block-cursor-text-style": "reverse",
        "footer-key-foreground": "#5B8DEF",
        "input-selection-background": "#5B8DEF 35%",
    },
)
