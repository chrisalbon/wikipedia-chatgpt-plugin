import json

import quart
import quart_cors
from quart import request
import datetime
import wikipedia

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

# ----------------------------------- #
# Plug-in Behavior
# ----------------------------------- #

# Keep track of todo's. Does not persist if Python session is restarted.
_TODOS = {}
ADDRESS = "https://chrisalbon-bug-free-journey-ppw6pxxrprc665-5003.preview.app.github.dev/"

def search_wikipedia(query, lang='en', top_n=1):
    # Set the language for the search
    wikipedia.set_lang(lang)

    def log_message(message):
        current_time = datetime.datetime.now()
        with open('logs.txt', 'a') as file:
            file.write(f'{current_time} {message}\n')

    # Search for the query
    search_results = wikipedia.search(query)
    log_message(query)

    # Get the top N results
    top_results = search_results[:top_n]

    # Get the full text for each result
    articles = {}
    for title in top_results:
        try:
            page = wikipedia.page(title)
            articles[title] = page.content
        except wikipedia.exceptions.DisambiguationError as e:
            # Handle disambiguation pages by using the first valid option
            for option in e.options:
                try:
                    page = wikipedia.page(option)
                    articles[option] = page.content
                    break
                except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError):
                    continue
        except wikipedia.exceptions.PageError:
            # Skip pages that can't be loaded
            continue

    return articles

@app.get("/")
async def hello_world():
    return f"""Wikipedia ChatGPT Plug-in Is Running. To install in ChatGPT, go to chat.openai.com and paste in {ADDRESS}"""

@app.get("/search")
async def get_articles():
    query = request.args.get("query")
    articles = search_wikipedia(query)
    return quart.Response(response=articles, status=200)

# ----------------------------------- #
# Config functions required by ChatGPT
# ----------------------------------- #

@app.get("/logo.png")
async def plugin_logo():
    filename = "logo.png"
    return await quart.send_file(filename, mimetype="image/png")


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers["Host"]
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers["Host"]
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

# ----------------------------------- #
# Main
# ----------------------------------- #

def main():
    app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()
