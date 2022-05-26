from fedml_sample import app
from fastapi.openapi.docs import get_redoc_html
import json

html = get_redoc_html(
    openapi_url="./openapi.json",
    title=app.title + " - ReDoc",
    # redoc_js_url="/static/redoc.standalone.js",
    redoc_js_url="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js",
)


with open("docs/openapi/openapi.json", "w") as f:
    json.dump(app.openapi(), f, indent=4, ensure_ascii=False)


with open("docs/openapi/api.html", "w") as f:
    f.write(html.body.decode("utf8"))
