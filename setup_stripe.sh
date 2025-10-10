#!/bin/bash

echo "🔷 Stripe Integration Setup"
echo "=============================="
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Please activate your virtual environment first:"
    echo "   source .venv/bin/activate"
    exit 1
fi

# Install Stripe
echo "📦 Installing Stripe SDK..."
pip install stripe
pip freeze > requirements.txt
echo "✅ Stripe installed"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Creating one..."
    cat > .env << 'EOF'
SECRET_KEY=dev-secret-change-me
DATABASE_URL=sqlite:///dev.sqlite3
FLASK_CONFIG=DevelopmentConfig
SECURITY_TOKEN_SALT=dev-token-salt

# Stripe Configuration
STRIPE_PUBLIC_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
EOF
    echo "✅ Created .env file"
else
    echo "✅ .env file exists"
fi

echo ""
echo "🔑 Next Steps:"
echo ""
echo "1. Get your Stripe keys:"
echo "   👉 https://dashboard.stripe.com/test/apikeys"
echo ""
echo "2. Update .env file with your keys:"
echo "   nano .env"
echo ""
echo "3. Create products in Stripe:"
echo "   👉 https://dashboard.stripe.com/test/products"
echo ""
echo "4. Update your plans with Stripe Price IDs:"
echo "   - Login as admin"
echo "   - Go to /admin/plans"
echo "   - Edit each plan"
echo "   - Add Stripe Price ID"
echo ""
echo "5. Test webhook forwarding:"
echo "   stripe listen --forward-to localhost:5000/account/stripe/webhook"
echo ""
echo "6. Run your app:"
echo "   flask --app app run --debug"
echo ""
echo "✨ Setup complete! Follow the steps above."
