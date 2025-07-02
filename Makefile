.PHONY: all client server
client:
	@cd client && npm run dev

server:
	@cd server && uv run server.py