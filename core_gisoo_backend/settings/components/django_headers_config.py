from corsheaders.defaults import default_headers, default_methods

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",

    "https://gisoocenter.ir",
    "https://www.gisoocenter.ir",
    "https://gisoocenter.com",
    "https://www.gisoocenter.com",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "x-client",
    "x-token-id",
    "x-token",
    "X-Token",
    "accept-language",
    "x-cart-uuid",
    "Idempotency-Key"
]

CORS_ALLOW_METHODS = list(default_methods)
