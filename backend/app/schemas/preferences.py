from pydantic import BaseModel, Field


class LayoutPreferences(BaseModel):
    theme: str = Field(default="light", pattern="^(light|dark)$")
    sidebar_collapsed: bool = False
    hidden_nav_slugs: list[str] = Field(default_factory=list)


class UserPreferencesRead(BaseModel):
    layout: LayoutPreferences


class UserPreferencesUpdate(BaseModel):
    layout: LayoutPreferences
