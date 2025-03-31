from fastapi import FastAPI


app = FastAPI(debug=True)


@app.get("/dummy-summary")
async def get_dummy_summary():
    html_content = """
    <html>
        <head>
            <title>Dummy Summary</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .summary { background-color: #f5f5f5; padding: 20px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>Dummy Summary Report</h1>
            <div class="summary">
                <h2>Key Findings</h2>
                <ul>
                    <li>Sample finding 1: Lorem ipsum dolor sit amet</li>
                    <li>Sample finding 2: Consectetur adipiscing elit</li>
                    <li>Sample finding 3: Sed do eiusmod tempor incididunt</li>
                </ul>
                <p>This is a dummy summary generated for demonstration purposes.</p>
            </div>
        </body>
    </html>
    """
    return {"result": {"id": "dummy-001", "summary": html_content}}


@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI server"}
