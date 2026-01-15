from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostCreate, PostResponse
from app.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
import shutil
import os
import uuid
import tempfile



@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    session: AsyncSession = Depends(get_async_session),
):
    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(file.filename)[1],
        ) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        with open(temp_file_path, "rb") as f:
            upload_result = imagekit.files.upload(
                file=f,
                file_name=file.filename,
                use_unique_file_name=True,
                tags=["backend-upload"],
            )

        # Success check for your SDK: did we get a URL back?
        url = getattr(upload_result, "url", None)
        name = getattr(upload_result, "name", None) or file.filename
        if not url:
            raise HTTPException(status_code=502, detail="ImageKit upload failed (no url returned)")

        post = Post(
            caption=caption,
            url=url,
            file_type="video" if (file.content_type or "").startswith("video/") else "image",
            file_name=name,
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)

        # Return JSON-safe response
        return {
            "id": str(post.id),
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat() if post.created_at else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            file.file.close()
        except Exception:
            pass
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass
@app.get("/feed")
async def get_feed(
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat()
            }
        )

    return {"posts": posts_data}


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        await session.delete(post)
        await session.commit()

        return{"success": True, "message": "Post deleted successfully"}

    except HTTPException as e:
        raise HTTPException(status_code=500, detail=str(e))
















#This is a reference for how you started writing posts - don't delete

#text_posts ={1: {title": "New Post", "content": "Cool test post"},
#           2: {"title": "FastAPI Basics", "content": "Learning how POST requests work"},
#            3: {"title": "Draft Post", "content": "This post is not published yet"},
#            4: {"title": "Why FastAPI", "content": "FastAPI is fast, modern, and easy to use"},
#           5: {"title": "Short Post", "content": "Test"},
#            6: {"title": "Long Content", "content": "This is a longer post meant to test how the API handles larger request bodies and text fields"},
#            7: {"title": "Special Characters", "content": "Testing !@#$%^&*() and emojis 🚀🔥"},
#            8: {"title": "Numbers", "content": "This post mentions numbers like 42 and 100"},
#            9: {"title": "Edge Case Title", "content": "Checking edge cases in input validation"},
#            10: {"title": "Minimal", "content": "Min"}
#}

#@app.get("/posts")
#def get_all_posts(limit: int = None):
#    if limit:
#        return list(text_posts.values())[:limit]
#    return text_posts

#@app.get("/posts/{id}")
#def get_posts(id: int) -> PostResponse:
#    if id not in text_posts:
#       raise HTTPException(status_code=404, detail="Not Found")

#    return text_posts.get(id)



#@app.post("/posts")
#def create_post(post: PostCreate) -> PostResponse:
#    new_post = {"title": post.title, "content": post.content}
#    text_posts[max(text_posts.keys()) +1] = new_post
#    return new_post
