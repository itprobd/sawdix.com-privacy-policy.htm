import os
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from github import Github
from typing import Optional, List

# Initialize FastAPI app
app = FastAPI(title="Pro Web-GitHub Portal API", version="1.0.0")

# Configuration (Use environment variables in production)
GITHUB_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN", "your_github_token_here")
g = Github(GITHUB_TOKEN)

# --- Schemas ---
class UserBase(BaseModel):
    username: str
    is_admin: bool = False

class GitHubRepoInfo(BaseModel):
    name: str
    description: Optional[str]
    url: str
    stars: int

# --- Authentication Logic (Simulated) ---
def get_current_user(admin_required: bool = False):
    # In a real app, you would verify a JWT token here
    def dependency(user_role: str = "user"):
        if admin_required and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrative privileges required"
            )
        return {"user": "current_user", "role": user_role}
    return dependency

# --- Routes ---

@app.get("/")
def health_check():
    return {"status": "online", "message": "High Power API is running"}

# User Route: Get GitHub Profile Data
@app.get("/user/github-profile/{username}", response_model=GitHubRepoInfo)
async def get_github_repo(username: str, current_user: dict = Depends(get_current_user())):
    try:
        user = g.get_user(username)
        return {
            "name": user.name or user.login,
            "description": user.bio,
            "url": user.html_url,
            "stars": user.public_repos
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"GitHub user not found: {str(e)}")

# Admin Route: List All Repositories for an Organization
@app.get("/admin/org-repos/{org_name}", response_model=List[GitHubRepoInfo])
async def admin_get_org_repos(org_name: str, current_user: dict