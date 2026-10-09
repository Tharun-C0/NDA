from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response schema for application health check endpoint."""

    status: str = Field(default="ok", description="Service health status indicator")
    version: str = Field(description="Current API application version")
    app_name: str = Field(description="Name of the running API application")
