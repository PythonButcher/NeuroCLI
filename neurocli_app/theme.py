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
    name="modern_dark_pro",
    primary="#3B82F6",
    secondary="#9DA5B4",
    accent="#3B82F6",
    foreground="#E6EDF3",
    background="#0E1117",
    success="#2EA043",
    warning="#D29922",
    error="#F85149",
    surface="#1C2128",
    panel="#2D333B",
    dark=True,
    variables={
        "block-cursor-text-style": "reverse",
        "footer-key-foreground": "#3B82F6",
        "input-selection-background": "#3B82F6 35%",
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
