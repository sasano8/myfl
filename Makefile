doc-export-openapi:
	@poetry run python export_open_api.py

doc-build: doc-export-openapi
	@poetry run mkdocs build

doc-serve: doc-build
	@poetry run mkdocs serve -a localhost:8001
