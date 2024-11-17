from fastapi import FastAPI
from .routes import router

app = FastAPI(
    title="Automated fine-tune model with Google Calendar and Google Meets scheduler for business use case",
    description="This API for booking visits for recruitment processes and learning requirements also integrates a fine-tuned LLaMA 2-13B model designed to facilitate understanding of responsibilities, workflows, company policies, corporate history, future vision, and growth opportunities.",
    version="1.0.0",
)

app.include_router(router)
