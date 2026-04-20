from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.limiter import limiter as rate_limiter

from app.api.v1 import auth
from app.api.v1 import post
from app.api.v1 import comments
from app.api.v1 import tags
from app.api.v1 import categories


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
app.add_middleware(SlowAPIMiddleware)

app.state.limiter = rate_limiter

register_exception_handlers(app)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) # type: ignore[arg-type]

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(post.router, prefix=settings.API_V1_PREFIX)
app.include_router(categories.router, prefix=settings.API_V1_PREFIX)
app.include_router(tags.router, prefix=settings.API_V1_PREFIX)
app.include_router(comments.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Blog API"}

@app.get("/health", tags=["health"])
def get_health():
    return {"status": "ok", "version": settings.APP_VERSION}
