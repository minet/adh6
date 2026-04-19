# Migrations are now handled automatically at startup via the FastAPI lifespan
# (adh6/main.py). To run migrations manually:
#
#   uv run alembic upgrade head
#
# To generate a new migration:
#
#   uv run alembic revision --autogenerate -m "description"
