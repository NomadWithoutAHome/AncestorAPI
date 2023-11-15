from fastapi import FastAPI, Query
from starlette.responses import RedirectResponse
from fuzzywuzzy import fuzz
from helpers import load_json_data
from typing import Optional
import random

app = FastAPI()

quotes = load_json_data('static/quotes.json')

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url='/docs')

@app.get("/quote")
def get_random_quote(num_quotes: int = Query(1, description="The number of random quotes to return.")):
    quote_values = quotes["quotes"]
    num_quotes = min(num_quotes if num_quotes else len(quote_values), len(quote_values))
    return {"quotes": random.sample(quote_values, k=num_quotes)}

@app.get("/search")
def search_quotes(query: str = Query(..., description="The string you are searching for."),
                  type: str = Query('string', description="The type of search to be performed. It can be 'fuzzy', 'pattern', 'partial', or 'string'. 'fuzzy' uses the fuzz ratio to find quotes that are approximately 60% similar to the query. 'pattern' finds quotes that contain the query as a substring. 'partial' finds quotes that contain the query as a whole word. 'string' finds quotes that match the query exactly."),
                  num_results: Optional[int] = Query(None, description="The number of results to return. If not provided, all matching quotes will be returned.")):
    quote_values = quotes["quotes"]
    if type == 'fuzzy':
        matching_quotes = [quote for quote in quote_values if fuzz.ratio(query.lower(), quote.lower()) >= 60]
    elif type == 'pattern':
        matching_quotes = [quote for quote in quote_values if query.lower() in quote.lower()]
    elif type == 'partial':
        matching_quotes = [quote for quote in quote_values if query.lower() in quote.split()]
    else:  # string match
        matching_quotes = [quote for quote in quote_values if query.lower() == quote.lower()]

    if num_results is not None:
        matching_quotes = matching_quotes[:num_results]

    return {"quotes": matching_quotes}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
