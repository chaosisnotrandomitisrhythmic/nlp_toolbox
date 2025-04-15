```python
from fasthtml.common import *
css = Style(':root {--pico-font-size:90%,--pico-font-family: Pacifico, cursive;}')
app = FastHTML(hdrs=(picolink, css))

@app.route("/")
def get():
    return (Title("Hello World"), 
            Main(H1('Hello, World'), cls="container"))
```

We’re returning a tuple here (a title and the main page). Returning a tuple, list, FT object, or an object with a __ft__ method tells FastHTML to turn the main body into a full HTML page that includes the headers (including the pico link and our custom css) which we passed in. This only occurs if the request isn’t from HTMX (for HTMX requests we need only return the rendered components).

HTMX addresses some key limitations of HTML. In vanilla HTML, links can trigger a GET request to show a new page, and forms can send requests containing data to the server. A lot of ‘Web 1.0’ design revolved around ways to use these to do everything we wanted. But why should only some elements be allowed to trigger requests? And why should we refresh the entire page with the result each time one does? HTMX extends HTML to allow us to trigger requests from any element on all kinds of events, and to update a part of the page without refreshing the entire page. It’s a powerful tool for building modern web apps.