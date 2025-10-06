# Multi‑role Setup (user/admin)

This patch adds basic role support to your Flask app.

## What changed
- **User model**: `role` column (`user` default).
- **Decorator**: `app/security.py` with `@roles_required(...)`.
- **Admin routes**: Admin blueprint routes protected with `@roles_required('admin')` (where detected).
- **Templates**: Admin menu link now only shows for admins (in base template if found).
- **CLI**: `flask create-admin EMAIL PASSWORD` to make an admin.
- **Alembic**: Migration stub created (set correct `down_revision`).

## How to apply

1. Install deps (if not already):

```bash
pip install Flask-Login Flask SQLAlchemy Alembic
```

2. **Database migration**

If you use Alembic:

```bash
# Set the correct down_revision in the generated migration file first!
flask db upgrade
```

If you don't use Alembic yet, run a one-off SQL:

```sql
ALTER TABLE user ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user';
```

3. **Create an admin**

```bash
export FLASK_APP=app
flask create-admin admin@example.com "change_this_password"
```

4. **Protect additional routes**

For any sensitive view add:

```python
from app.security import roles_required

@bp.route("/secret")
@roles_required("admin")
def secret():
    ...
```

## Notes
- If you already had a `role` column, nothing is changed.
- If your migrations have multiple heads, resolve them first (e.g., `flask db merge`).
- The template injection is minimal; tweak your navbar as desired.
