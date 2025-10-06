from flask import current_app

def register_context_processors(app):
    @app.context_processor
    def utility_processor():
        def has_endpoint(name: str) -> bool:
            return name in current_app.view_functions
        return dict(has_endpoint=has_endpoint)
