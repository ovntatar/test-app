# Flask Auth + Account Settings (Password, Billing, Delete)

Includes:
- App factory + blueprints (`main`, `api`, `auth`, `account`)
- Bootstrap 5 UI
- Register/Login/Logout, email confirmation, forgot/reset password
- **Account settings**: change password, manage billing address (with tax/VAT), delete account
- SQLAlchemy (SQLite by default), Flask-Migrate
- WSGI entrypoint + `/healthz`

## Quickstart
```bash
unzip flask_bootstrap_api_auth_account.zip
cd flask_bootstrap_api_auth_account
python -m venv .venv
source .venv/bin/activate                     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Database
flask --app app db init                       # first time
flask --app app db migrate -m "init"
flask --app app db upgrade

# Run
export FLASK_CONFIG=DevelopmentConfig         # Windows: set FLASK_CONFIG=DevelopmentConfig
flask --app app run --debug
```
Open http://127.0.0.1:5000

## Account URLs
- `/account` overview
- `/account/password` change password
- `/account/billing` edit billing profile (name/company/address/tax_id)
- `/account/delete` delete account (with confirmation prompt)

## Notes
- In development, confirmation/reset links are displayed; in production, send via email provider.
- Switch DB via `DATABASE_URL`. For production use Postgres/MySQL.
# test-app
# test-app
