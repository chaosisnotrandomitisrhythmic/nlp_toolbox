from fasthtml.common import *


def layout(*args, **kwargs):
    """Dashboard layout for all our dashboard views"""
    return Main(
        H1("Dashboard"),
        Div(*args, **kwargs),
        cls="dashboard",
    )


# usage example
out = layout(
    Ul(*[Li(o) for o in range(3)]),
    P("Some content", cls="description"),
)

print(out)
print(*[o for o in range(3)])
