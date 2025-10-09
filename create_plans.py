"""
Script to create default plans
Run with: python create_plans.py
"""

from app import create_app
from app.extensions import db
from app.models import Plan

def create_default_plans():
    app = create_app()
    
    with app.app_context():
        # Check if plans already exist
        if Plan.query.count() > 0:
            print("Plans already exist. Skipping...")
            return
        
        # Free Plan
        free_plan = Plan(
            name="Free",
            description="Perfect for getting started",
            option1="5 Projects",
            option2="1GB Storage",
            option3="Community Support",
            option4="Basic Features",
            option5=None,
            price=0.00,
            currency="USD",
            billing_period="monthly",
            is_active=True,
            is_featured=False,
            sort_order=0
        )
        
        # Pro Plan
        pro_plan = Plan(
            name="Pro",
            description="For professionals and small teams",
            option1="Unlimited Projects",
            option2="50GB Storage",
            option3="Priority Support",
            option4="Advanced Features",
            option5="API Access",
            price=19.99,
            currency="USD",
            billing_period="monthly",
            stripe_price_id="",  # Add your Stripe Price ID here
            stripe_product_id="",  # Add your Stripe Product ID here
            is_active=True,
            is_featured=True,
            sort_order=1
        )
        
        # Enterprise Plan
        enterprise_plan = Plan(
            name="Enterprise",
            description="For large organizations",
            option1="Unlimited Everything",
            option2="Unlimited Storage",
            option3="24/7 Premium Support",
            option4="Custom Integrations",
            option5="Dedicated Account Manager",
            price=99.99,
            currency="USD",
            billing_period="monthly",
            stripe_price_id="",  # Add your Stripe Price ID here
            stripe_product_id="",  # Add your Stripe Product ID here
            is_active=True,
            is_featured=False,
            sort_order=2
        )
        
        # Add plans to database
        db.session.add(free_plan)
        db.session.add(pro_plan)
        db.session.add(enterprise_plan)
        db.session.commit()
        
        print("✅ Default plans created successfully!")
        print(f"  - {free_plan.name}: {free_plan.formatted_price}")
        print(f"  - {pro_plan.name}: {pro_plan.formatted_price}")
        print(f"  - {enterprise_plan.name}: {enterprise_plan.formatted_price}")

if __name__ == "__main__":
    create_default_plans()
