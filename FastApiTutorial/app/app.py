from fastapi import FastAPI, HTTPException
from app.schemas import PostCreate, PostResponse
app = FastAPI()

text_posts ={1: {"title": "New Post", "content": "Cool test post"},
            2: {"title": "FastAPI Basics", "content": "Learning how POST requests work"},
            3: {"title": "Draft Post", "content": "This post is not published yet"},
            4: {"title": "Why FastAPI", "content": "FastAPI is fast, modern, and easy to use"},
            5: {"title": "Short Post", "content": "Test"},
            6: {"title": "Long Content", "content": "This is a longer post meant to test how the API handles larger request bodies and text fields"},
            7: {"title": "Special Characters", "content": "Testing !@#$%^&*() and emojis 🚀🔥"},
            8: {"title": "Numbers", "content": "This post mentions numbers like 42 and 100"},
            9: {"title": "Edge Case Title", "content": "Checking edge cases in input validation"},
            10: {"title": "Minimal", "content": "Min"}
}

@app.get("/posts")
def get_all_posts(limit: int = None):
    if limit:
        return list(text_posts.values())[:limit]
    return text_posts

@app.get("/posts/{id}")
def get_posts(id: int) -> PostResponse:
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Not Found")

    return text_posts.get(id)



@app.post("/posts")
def create_post(post: PostCreate) -> PostResponse:
    new_post = {"title": post.title, "content": post.content}
    text_posts[max(text_posts.keys()) +1] = new_post
    return new_post

