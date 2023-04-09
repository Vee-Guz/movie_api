import uvicorn

if __name__ == "__main__":
    config = uvicorn.Config(
        "src.api.server:app", port=3000, log_level="info", reload=True, env_file=".env"
    )
    server = uvicorn.Server(config)
    server.run()

# running on terminal: python3 -m uvicorn src.api.server:app --host 0.0.0.0 --port 3001