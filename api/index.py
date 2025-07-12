# api/index.py
# Vercel entry point for FastAPI app

from app.main import app

# Optional: Allow running locally with `python api/index.py`
if __name__ == "__main__":
    import uvicorn
<<<<<<< HEAD
    uvicorn.run("api.index:app", host="0.0.0.0", port=8000, reload=True) 
=======
    uvicorn.run("api.index:app", host="0.0.0.0", port=8000, reload=True)
>>>>>>> a4e33e179d3b70acd84f84b3ab035167bb14adb7
