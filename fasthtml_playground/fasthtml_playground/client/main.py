from fasthtml.common import *


app = FastHTMLWithLiveReload()


@app.get("/")
def home():
    return Title("Page Demo"), Div(
        H1("Hello, World"),
        P("Some text"),
        P("Some more text"),
        Div(
            Safe(
                """
                <details>
                    <summary>Click to expand</summary>
                    <div class="summary-content">
                        <h3>Important Points</h3>
                        <ul>
                            <li>First important point</li>
                            <li>Second important point</li>
                            <li>Third important point</li>
                        </ul>
                    </div>
                </details>
            """
            )
        ),
    )


serve()
