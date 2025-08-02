from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from dateutil.relativedelta import relativedelta
from werkzeug.security import generate_password_hash, check_password_hash
import re
import pandas as pd
import numpy as np
from functools import lru_cache
import json
import os

# Telugu translations dictionary
TRANSLATIONS = {
    'en': {
        'choose_account_type': 'Choose Your Account Type',
        'select_dashboard': 'Select the dashboard that best suits your needs',
        'farmer_dashboard': 'Farmer Dashboard',
        'individual_dashboard': 'Individual Dashboard',
        'company_dashboard': 'Company Dashboard',
        'farmer_desc': 'Agricultural insights and financial management for farmers',
        'individual_desc': 'Personal finance management and investment tracking',
        'company_desc': 'Business analytics and financial management',
        'crop_analytics': 'Crop Analytics',
        'weather_insights': 'Weather Insights',
        'market_prices': 'Market Prices',
        'expense_tracking': 'Expense Tracking',
        'budget_planning': 'Budget Planning',
        'investment_goals': 'Investment Goals',
        'business_analytics': 'Business Analytics',
        'financial_reports': 'Financial Reports',
        'team_management': 'Team Management',
        'access_dashboard': 'Access Dashboard',
        'total_income': 'Total Income',
        'total_expenses': 'Total Expenses',
        'remaining_balance': 'Remaining Balance',
        'monthly_net': 'Monthly Net',
        'expense_categories': 'Expense Categories',
        'expense_trends': 'Expense Trends',
        'add_transaction': 'Add Transaction',
        'amount': 'Amount',
        'category': 'Category',
        'description': 'Description',
        'transaction_type': 'Transaction Type',
        'income': 'Income',
        'expense': 'Expense',
        'submit': 'Submit',
        'dashboard': 'Dashboard',
        'logout': 'Logout',
        'farmer_login': 'Farmer Login',
        'individual_login': 'Individual Login',
        'company_login': 'Company Login',
        'all_rights_reserved': 'All rights reserved',
        'privacy_policy': 'Privacy Policy',
        'terms_of_service': 'Terms of Service',
        'contact_us': 'Contact Us',
        'remember_me': 'Remember me',
        'forgot_password': 'Forgot your password?',
        'sign_in': 'Sign in',
        'register': 'Register',
        'create_account': 'Create Account',
        'already_have_account': 'Already have an account?',
        'dont_have_account': "Don't have an account?",
        'or_continue_with': 'Or continue with',
        'google': 'Google',
        'apple': 'Apple',
        'invalid_credentials': 'Invalid email or password'
    },
    'te': {
        'choose_account_type': 'మీ ఖాతా రకాన్ని ఎంచుకోండి',
        'select_dashboard': 'మీ అవసరాలకు సరిపోయే డాష్‌బోర్డ్‌ను ఎంచుకోండి',
        'farmer_dashboard': 'రైతు డాష్‌బోర్డ్',
        'individual_dashboard': 'వ్యక్తిగత డాష్‌బోర్డ్',
        'company_dashboard': 'కంపెనీ డాష్‌బోర్డ్',
        'farmer_desc': 'రైతులకు వ్యవసాయ అంతర్దృష్టులు మరియు ఆర్థిక నిర్వహణ',
        'individual_desc': 'వ్యక్తిగత ఆర్థిక నిర్వహణ మరియు పెట్టుబడి ట్రాకింగ్',
        'company_desc': 'వ్యాపార విశ్లేషణలు మరియు ఆర్థిక నిర్వహణ',
        'crop_analytics': 'పంట విశ్లేషణలు',
        'weather_insights': 'వాతావరణ అంతర్దృష్టులు',
        'market_prices': 'మార్కెట్ ధరలు',
        'expense_tracking': 'ఖర్చుల ట్రాకింగ్',
        'budget_planning': 'బడ్జెట్ ప్రణాళిక',
        'investment_goals': 'పెట్టుబడి లక్ష్యాలు',
        'business_analytics': 'వ్యాపార విశ్లేషణలు',
        'financial_reports': 'ఆర్థిక నివేదికలు',
        'team_management': 'టీమ్ నిర్వహణ',
        'access_dashboard': 'డాష్‌బోర్డ్‌ను యాక్సెస్ చేయండి',
        'total_income': 'మొత్తం ఆదాయం',
        'total_expenses': 'మొత్తం ఖర్చులు',
        'remaining_balance': 'మిగిలిన నిల్వ',
        'monthly_net': 'నెలవారీ నికర',
        'expense_categories': 'ఖర్చుల వర్గాలు',
        'expense_trends': 'ఖర్చుల ధోరణులు',
        'add_transaction': 'లావాదేవీని జోడించండి',
        'amount': 'మొత్తం',
        'category': 'వర్గం',
        'description': 'వివరణ',
        'transaction_type': 'లావాదేవీ రకం',
        'income': 'ఆదాయం',
        'expense': 'ఖర్చు',
        'submit': 'సమర్పించండి',
        'dashboard': 'డాష్‌బోర్డ్',
        'logout': 'లాగ్అవుట్',
        'farmer_login': 'రైతు లాగిన్',
        'individual_login': 'వ్యక్తిగత లాగిన్',
        'company_login': 'కంపెనీ లాగిన్',
        'all_rights_reserved': 'అన్ని హక్కులు రిజర్వ్ చేయబడ్డాయి',
        'privacy_policy': 'గోప్యతా విధానం',
        'terms_of_service': 'సేవా నిబంధనలు',
        'contact_us': 'మమ్మల్ని సంప్రదించండి',
        'remember_me': 'నన్ను గుర్తుంచుకో',
        'forgot_password': 'పాస్‌వర్డ్ మర్చిపోయారా?',
        'sign_in': 'సైన్ ఇన్',
        'register': 'నమోదు',
        'create_account': 'ఖాతాను సృష్టించండి',
        'already_have_account': 'ఇప్పటికే ఖాతా ఉందా?',
        'dont_have_account': 'ఖాతా లేదా?',
        'or_continue_with': 'లేదా వీటితో కొనసాగించండి',
        'google': 'గూగుల్',
        'apple': 'ఆపిల్',
        'invalid_credentials': 'చెల్లని ఇమెయిల్ లేదా పాస్‌వర్డ్'
    }
}

def get_text(key, lang='en'):
    """Get text in specified language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, TRANSLATIONS['en'].get(key, key))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_type_selection'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.unauthorized_handler
def unauthorized():
    flash('Please log in to access this page.', 'info')
    return redirect(url_for('user_type_selection'))

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'farmer', 'individual'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def get_id(self):
        return str(self.id)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

def process_agricultural_data():
    """Process agricultural data from CSV file"""
    try:
        df = pd.read_csv('dataset/agriculture.csv')
        
        # Calculate total metrics
        total_area = df['Farm_Area(acres)'].sum()
        total_yield = df['Yield(tons)'].sum()
        total_water = df['Water_Usage(cubic meters)'].sum()
        total_fertilizer = df['Fertilizer_Used(tons)'].sum()
        total_pesticide = df['Pesticide_Used(kg)'].sum()
        
        # Calculate crop-specific data
        crops_data = []
        for crop in df['Crop_Type'].unique():
            crop_df = df[df['Crop_Type'] == crop]
            avg_yield = crop_df['Yield(tons)'].mean()
            max_yield = crop_df['Yield(tons)'].max()
            growth_percentage = (avg_yield / max_yield) * 100 if max_yield > 0 else 0
            
            crops_data.append({
                'name': crop,
                'growth_percentage': round(growth_percentage, 1)
            })
        
        # Calculate resource usage percentages
        fertilizer_percentage = (total_fertilizer / (total_area * 0.1)) * 100  # Assuming 0.1 tons per acre is optimal
        pesticide_percentage = (total_pesticide / (total_area * 0.05)) * 100  # Assuming 0.05 kg per acre is optimal
        water_efficiency = (total_yield / total_water) * 100  # Yield per cubic meter of water
        
        # Calculate crop health based on yield and resource usage
        crop_health = min(100, (total_yield / (total_area * 0.5)) * 100)  # Assuming 0.5 tons per acre is optimal
        
        return {
            'total_area': round(total_area, 1),
            'total_yield': round(total_yield, 1),
            'water_usage': round(total_water, 1),
            'crop_health': round(crop_health, 1),
            'crops': crops_data,
            'fertilizer_usage': round(total_fertilizer, 1),
            'pesticide_usage': round(total_pesticide, 1),
            'fertilizer_percentage': round(fertilizer_percentage, 1),
            'pesticide_percentage': round(pesticide_percentage, 1),
            'water_efficiency': round(water_efficiency, 1)
        }
    except Exception as e:
        print(f"Error processing agricultural data: {str(e)}")
        return None

def generate_farming_recommendations(farm_data):
    """Generate AI-powered recommendations for better farming practices"""
    recommendations = []
    
    # Analyze water efficiency
    if farm_data['water_efficiency'] < 50:
        recommendations.append({
            'type': 'water',
            'priority': 'high',
            'message': 'Water efficiency is low. Consider implementing drip irrigation systems to reduce water wastage and improve crop yield.',
            'action': 'Upgrade irrigation system to drip irrigation'
        })
    elif farm_data['water_efficiency'] < 70:
        recommendations.append({
            'type': 'water',
            'priority': 'medium',
            'message': 'Water efficiency can be improved. Monitor soil moisture levels and adjust irrigation schedules accordingly.',
            'action': 'Optimize irrigation schedule'
        })
    
    # Analyze fertilizer usage
    if farm_data['fertilizer_percentage'] > 120:
        recommendations.append({
            'type': 'fertilizer',
            'priority': 'high',
            'message': 'Fertilizer usage is excessive. This can harm soil health and increase costs. Consider soil testing and balanced fertilization.',
            'action': 'Conduct soil test and adjust fertilizer application'
        })
    elif farm_data['fertilizer_percentage'] < 80:
        recommendations.append({
            'type': 'fertilizer',
            'priority': 'medium',
            'message': 'Fertilizer usage is below optimal. Consider increasing fertilizer application to improve crop yield.',
            'action': 'Increase fertilizer application'
        })
    
    # Analyze pesticide usage
    if farm_data['pesticide_percentage'] > 120:
        recommendations.append({
            'type': 'pesticide',
            'priority': 'high',
            'message': 'Pesticide usage is high. Consider integrated pest management (IPM) practices to reduce chemical dependency.',
            'action': 'Implement IPM practices'
        })
    
    # Analyze crop health
    if farm_data['crop_health'] < 60:
        recommendations.append({
            'type': 'crop_health',
            'priority': 'high',
            'message': 'Overall crop health is poor. Review soil quality, nutrient levels, and pest management practices.',
            'action': 'Conduct comprehensive crop health assessment'
        })
    elif farm_data['crop_health'] < 80:
        recommendations.append({
            'type': 'crop_health',
            'priority': 'medium',
            'message': 'Crop health needs improvement. Consider crop rotation and soil enrichment practices.',
            'action': 'Implement crop rotation'
        })
    
    # Analyze individual crops
    for crop in farm_data['crops']:
        if crop['growth_percentage'] < 60:
            recommendations.append({
                'type': 'crop_specific',
                'priority': 'high',
                'message': f"{crop['name']} is performing poorly. Review growing conditions and management practices for this crop.",
                'action': f'Review {crop["name"]} growing conditions'
            })
    
    # Sort recommendations by priority
    recommendations.sort(key=lambda x: x['priority'] == 'high', reverse=True)
    return recommendations

def process_company_data():
    """Process company data from CSV file"""
    try:
        # Check if file exists
        csv_path = 'dataset/company.csv'
        if not os.path.exists(csv_path):
            print(f"Error: File not found at {csv_path}")
            return None
            
        df = pd.read_csv(csv_path)
        
        # Calculate financial metrics
        total_revenue = df['Total Revenue (₹)'].sum()
        total_expenses = df['Expenses (₹)'].sum()
        total_costs = df['Total Cost (₹)'].sum()
        net_profit = total_revenue - (total_expenses + total_costs)
        profit_margin = (net_profit / total_revenue) * 100 if total_revenue > 0 else 0
        
        # Calculate revenue growth
        df['Month'] = pd.to_datetime(df['Month'], format='%B')
        df = df.sort_values('Month')
        current_month_revenue = df.iloc[-1]['Total Revenue (₹)'] if not df.empty else 0
        previous_month_revenue = df.iloc[-2]['Total Revenue (₹)'] if len(df) > 1 else 0
        revenue_growth = ((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100 if previous_month_revenue > 0 else 0

        # Calculate resource utilization based on available metrics
        resource_utilization = round((total_revenue / (total_costs + total_expenses) * 100) if (total_costs + total_expenses) > 0 else 0, 1)
        
        # Calculate employee and customer satisfaction based on variance metrics
        variance_income_percent = df['Variance Income %'].mean()
        employee_satisfaction = round(max(0, min(100, 75 + variance_income_percent)), 1)
        customer_satisfaction = round(max(0, min(100, 80 + variance_income_percent)), 1)
        
        # Generate synthetic department data based on revenue segments
        departments = ['Sales', 'Operations', 'Marketing', 'Finance']
        departments_data = []
        for dept in departments:
            performance = round(max(0, min(100, 70 + variance_income_percent)), 1)
            departments_data.append({
                'name': dept,
                'performance': performance,
                'efficiency': performance,
                'productivity': performance
            })
        
        return {
            'total_revenue': round(total_revenue, 2),
            'total_expenses': round(total_expenses + total_costs, 2),
            'net_profit': round(net_profit, 2),
            'profit_margin': round(profit_margin, 1),
            'departments': departments_data,
            'resource_utilization': resource_utilization,
            'employee_satisfaction': employee_satisfaction,
            'customer_satisfaction': customer_satisfaction,
            'revenue_growth': round(revenue_growth, 1)
        }
    except Exception as e:
        print(f"Error processing company data: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generate_company_recommendations(company_data):
    """Generate AI-powered recommendations for better business practices"""
    recommendations = []
    
    # Analyze profit margin
    if company_data['profit_margin'] < 10:
        recommendations.append({
            'type': 'financial',
            'priority': 'high',
            'message': 'Low profit margin. Review pricing strategy and cost structure.',
            'action': 'Conduct pricing and cost analysis'
        })
    
    # Analyze resource utilization
    if company_data['resource_utilization'] < 70:
        recommendations.append({
            'type': 'operations',
            'priority': 'high',
            'message': 'Resource utilization is below optimal. Optimize resource allocation and workflow.',
            'action': 'Implement resource optimization plan'
        })
    
    # Analyze employee satisfaction
    if company_data['employee_satisfaction'] < 75:
        recommendations.append({
            'type': 'hr',
            'priority': 'high',
            'message': 'Employee satisfaction needs improvement. Review HR policies and work environment.',
            'action': 'Conduct employee satisfaction survey and implement improvements'
        })
    
    # Analyze customer satisfaction
    if company_data['customer_satisfaction'] < 80:
        recommendations.append({
            'type': 'customer',
            'priority': 'high',
            'message': 'Customer satisfaction could be improved. Review customer service and product quality.',
            'action': 'Implement customer feedback system'
        })
    
    # Analyze department performance
    for dept in company_data['departments']:
        if dept['performance'] < 70:
            recommendations.append({
                'type': 'department',
                'priority': 'medium',
                'message': f"{dept['name']} department performance is below target. Review operations and provide necessary support.",
                'action': f'Review {dept["name"]} department operations'
            })
    
    # Revenue growth recommendations
    if company_data['revenue_growth'] < 5:
        recommendations.append({
            'type': 'growth',
            'priority': 'medium',
            'message': 'Revenue growth is slow. Consider new market opportunities and sales strategies.',
            'action': 'Develop revenue growth strategy'
        })
    
    # Sort recommendations by priority
    recommendations.sort(key=lambda x: x['priority'] == 'high', reverse=True)
    return recommendations

def process_individual_data():
    """Process individual financial data from CSV file"""
    try:
        # Check if file exists
        csv_path = 'dataset/person.csv'
        if not os.path.exists(csv_path):
            print(f"Error: File not found at {csv_path}")
            return None
            
        df = pd.read_csv(csv_path)
        
        # Calculate monthly averages
        avg_salary = df['Salary (₹)'].mean()
        avg_expenses = df['Total Expenses (₹)'].mean()
        avg_savings = df['Savings (₹)'].mean()
        savings_goal = df['User Savings Goal (₹)'].iloc[-1]  # Get the latest savings goal
        
        # Calculate expense breakdown
        expense_categories = {
            'Rent': df['Rent (₹)'].mean(),
            'Utilities': df['Electricity Bill (₹)'].mean() + df['Water Bill (₹)'].mean(),
            'Grocery': df['Grocery (₹)'].mean(),
            'Transportation': df['Transportation (₹)'].mean(),
            'Entertainment': df['Entertainment (₹)'].mean(),
            'Healthcare': df['Healthcare (₹)'].mean(),
            'Miscellaneous': df['Miscellaneous (₹)'].mean()
        }
        
        # Calculate savings rate
        savings_rate = (avg_savings / avg_salary * 100) if avg_salary > 0 else 0
        
        # Calculate month-over-month growth
        df = df.sort_values('Month')
        current_month_savings = df['Savings (₹)'].iloc[-1]
        previous_month_savings = df['Savings (₹)'].iloc[-2] if len(df) > 1 else 0
        savings_growth = ((current_month_savings - previous_month_savings) / previous_month_savings * 100) if previous_month_savings > 0 else 0
        
        # Get spending patterns
        spending_pattern = []
        for month in df['Month'].unique():
            month_data = df[df['Month'] == month]
            spending_pattern.append({
                'month': month,
                'expenses': float(month_data['Total Expenses (₹)'].iloc[0]),
                'savings': float(month_data['Savings (₹)'].iloc[0])
            })
        
        # Get improvement tips
        latest_tips = df['Savings Improvement Tips'].iloc[-1]
        suggested_changes = df['Suggested Changes'].iloc[-1]
        
        return {
            'monthly_income': round(avg_salary, 2),
            'monthly_expenses': round(avg_expenses, 2),
            'monthly_savings': round(avg_savings, 2),
            'savings_goal': round(savings_goal, 2),
            'savings_rate': round(savings_rate, 1),
            'savings_growth': round(savings_growth, 1),
            'expense_breakdown': {k: round(v, 2) for k, v in expense_categories.items()},
            'spending_pattern': spending_pattern,
            'improvement_tips': latest_tips,
            'suggested_changes': suggested_changes
        }
    except Exception as e:
        print(f"Error processing individual data: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generate_individual_recommendations(individual_data):
    """Generate AI-powered recommendations for better personal finance management"""
    recommendations = []
    
    # Analyze savings rate
    if individual_data['savings_rate'] < 20:
        recommendations.append({
            'type': 'savings',
            'priority': 'high',
            'message': 'Your savings rate is below recommended levels. Consider reducing non-essential expenses.',
            'action': 'Review and optimize monthly expenses'
        })
    
    # Compare with savings goal
    if individual_data['monthly_savings'] < individual_data['savings_goal']:
        recommendations.append({
            'type': 'goal',
            'priority': 'high',
            'message': 'You are currently below your savings goal.',
            'action': 'Identify additional saving opportunities'
        })
    
    # Analyze expense categories
    expense_breakdown = individual_data['expense_breakdown']
    income = individual_data['monthly_income']
    
    # Check rent expense (should be less than 30% of income)
    if expense_breakdown['Rent'] > (income * 0.3):
        recommendations.append({
            'type': 'housing',
            'priority': 'medium',
            'message': 'Your rent expenses exceed 30% of your income.',
            'action': 'Consider housing alternatives or additional income sources'
        })
    
    # Check entertainment expenses (should be less than 10% of income)
    if expense_breakdown['Entertainment'] > (income * 0.1):
        recommendations.append({
            'type': 'lifestyle',
            'priority': 'medium',
            'message': 'Entertainment expenses are higher than recommended.',
            'action': 'Review and optimize entertainment spending'
        })
    
    # Add improvement tips from data
    if individual_data['improvement_tips']:
        recommendations.append({
            'type': 'custom',
            'priority': 'medium',
            'message': individual_data['improvement_tips'],
            'action': individual_data['suggested_changes']
        })
    
    # Sort recommendations by priority
    recommendations.sort(key=lambda x: x['priority'] == 'high', reverse=True)
    return recommendations

# Routes
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('user_type_selection'))

@app.route('/user-type-selection')
def user_type_selection():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('user_type_selection.html')

@app.route('/login/<user_type>', methods=['GET', 'POST'])
def login(user_type):
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember-me') == 'on'
        
        user = User.query.filter_by(email=email, user_type=user_type).first()
        
        if user and user.verify_password(password):
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if next_page and url_for('static', filename='') not in next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash(get_text('invalid_credentials'), 'error')
    
    return render_template('login.html', user_type=user_type)

@app.route('/register/<user_type>', methods=['GET', 'POST'])
def register(user_type):
    # Validate user type
    if user_type not in ['farmer', 'individual']:
        flash('Invalid user type', 'error')
        return redirect(url_for('base'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        # Validate required fields
        if not all([email, password, name]):
            flash('All fields are required', 'error')
            return redirect(url_for('register', user_type=user_type))
        
        # Validate email format
        if not validate_email(email):
            flash('Invalid email format', 'error')
            return redirect(url_for('register', user_type=user_type))
            
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register', user_type=user_type))
        
        # Create new user
        user = User(
            email=email,
            name=name,
            user_type=user_type
        )
        user.password = password
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login', user_type=user_type))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration', 'error')
            return redirect(url_for('register', user_type=user_type))
    
    return render_template('register.html', user_type=user_type)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('base'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type == 'farmer':
        # Get agricultural data
        farm_data = process_agricultural_data()
        if farm_data is None:
            flash('Error loading agricultural data', 'error')
            farm_data = {
                'total_area': 0,
                'total_yield': 0,
                'water_usage': 0,
                'crop_health': 0,
                'crops': [],
                'fertilizer_usage': 0,
                'pesticide_usage': 0,
                'fertilizer_percentage': 0,
                'pesticide_percentage': 0,
                'water_efficiency': 0
            }
        
        # Generate recommendations
        recommendations = generate_farming_recommendations(farm_data)
        print(farm_data,recommendations)
        
        # Get transactions
        transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
        
        # Calculate financial statistics
        total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
        total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
        remaining_balance = total_income - total_expenses
        
        # Calculate monthly statistics
        current_month = datetime.utcnow().month
        current_year = datetime.utcnow().year
        monthly_income = sum(t.amount for t in transactions 
                           if t.transaction_type == 'income' 
                           and t.date.month == current_month 
                           and t.date.year == current_year)
        monthly_expenses = sum(t.amount for t in transactions 
                             if t.transaction_type == 'expense' 
                             and t.date.month == current_month 
                             and t.date.year == current_year)
        
        # Calculate category-wise expenses
        category_expenses = {}
        for transaction in transactions:
            if transaction.transaction_type == 'expense':
                if transaction.category not in category_expenses:
                    category_expenses[transaction.category] = 0
                category_expenses[transaction.category] += transaction.amount
        
        # Calculate expense trends (last 3 months)
        expense_trends = []
        for i in range(3):
            month = current_month - i
            year = current_year
            if month <= 0:
                month += 12
                year -= 1
            
            monthly_total = sum(t.amount for t in transactions 
                              if t.transaction_type == 'expense' 
                              and t.date.month == month 
                              and t.date.year == year)
            expense_trends.append({
                'month': datetime(year, month, 1).strftime('%B %Y'),
                'amount': monthly_total
            })
        
        return render_template('farmer_dashboard.html',
                             farm_data=farm_data,
                             recommendations=recommendations,
                             transactions=transactions,
                             total_income=total_income,
                             total_expenses=total_expenses,
                             remaining_balance=remaining_balance,
                             monthly_income=monthly_income,
                             monthly_expenses=monthly_expenses,
                             category_expenses=category_expenses,
                             expense_trends=expense_trends)
    elif current_user.user_type == 'company':
        # Company dashboard
        company_data = process_company_data()
        if company_data is None:
            flash('Error loading company data', 'error')
            company_data = {
                'total_revenue': 0,
                'total_expenses': 0,
                'net_profit': 0,
                'profit_margin': 0,
                'departments': [],
                'resource_utilization': 0,
                'employee_satisfaction': 0,
                'customer_satisfaction': 0,
                'revenue_growth': 0
            }
        
        recommendations = generate_company_recommendations(company_data)
        
        # Get transactions
        transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
        
        # Calculate financial statistics
        total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
        total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
        remaining_balance = total_income - total_expenses
        
        # Calculate monthly statistics
        current_month = datetime.utcnow().month
        current_year = datetime.utcnow().year
        monthly_income = sum(t.amount for t in transactions 
                           if t.transaction_type == 'income' 
                           and t.date.month == current_month 
                           and t.date.year == current_year)
        monthly_expenses = sum(t.amount for t in transactions 
                             if t.transaction_type == 'expense' 
                             and t.date.month == current_month 
                             and t.date.year == current_year)
        
        return render_template('company_dashboard.html',
                             company_data=company_data,
                             recommendations=recommendations,
                             transactions=transactions,
                             total_income=total_income,
                             total_expenses=total_expenses,
                             remaining_balance=remaining_balance,
                             monthly_income=monthly_income,
                             monthly_expenses=monthly_expenses)
    else:  # individual dashboard
        try:
            # Get transactions
            transactions = Transaction.query.filter_by(
                user_id=current_user.id
            ).order_by(Transaction.date.desc()).all()

            # Calculate totals
            total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
            total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
            remaining_balance = total_income - total_expenses

            # Calculate monthly totals
            current_month = datetime.utcnow().month
            current_year = datetime.utcnow().year
            monthly_transactions = [
                t for t in transactions 
                if t.date.month == current_month and t.date.year == current_year
            ]
            
            monthly_income = sum(t.amount for t in monthly_transactions if t.transaction_type == 'income')
            monthly_expenses = sum(t.amount for t in monthly_transactions if t.transaction_type == 'expense')

            # Calculate category expenses
            category_expenses = {}
            for transaction in transactions:
                if transaction.transaction_type == 'expense':
                    category = transaction.category or 'Other'
                    category_expenses[category] = category_expenses.get(category, 0) + transaction.amount

            # Get individual financial data
            individual_data = process_individual_data()
            if individual_data is None:
                individual_data = {
                    'monthly_income': monthly_income or 0,
                    'monthly_expenses': monthly_expenses or 0,
                    'monthly_savings': (monthly_income - monthly_expenses) if monthly_income and monthly_expenses else 0,
                    'savings_goal': 0,
                    'savings_rate': 0,
                    'savings_growth': 0,
                    'expense_breakdown': category_expenses or {},
                    'spending_pattern': [],
                    'improvement_tips': '',
                    'suggested_changes': ''
                }

            # Generate recommendations
            recommendations = generate_individual_recommendations(individual_data)

            return render_template('individual_dashboard.html',
                                individual_data=individual_data,
                                recommendations=recommendations,
                                transactions=transactions,
                                total_income=total_income,
                                total_expenses=total_expenses,
                                remaining_balance=remaining_balance,
                                monthly_income=monthly_income,
                                monthly_expenses=monthly_expenses,
                                category_expenses=category_expenses)

        except Exception as e:
            print(f"Error in individual dashboard: {str(e)}")
            flash('An error occurred while loading the dashboard', 'error')
            return render_template('individual_dashboard.html',
                                individual_data={
                                    'monthly_income': 0,
                                    'monthly_expenses': 0,
                                    'monthly_savings': 0,
                                    'savings_goal': 0,
                                    'savings_rate': 0,
                                    'savings_growth': 0,
                                    'expense_breakdown': {},
                                    'spending_pattern': [],
                                    'improvement_tips': '',
                                    'suggested_changes': ''
                                },
                                recommendations=[],
                                transactions=[],
                                total_income=0,
                                total_expenses=0,
                                remaining_balance=0,
                                monthly_income=0,
                                monthly_expenses=0,
                                category_expenses={})

@app.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    try:
        amount = float(request.form.get('amount'))
        category = request.form.get('category')
        description = request.form.get('description')
        transaction_type = request.form.get('transaction_type')
        
        if amount <= 0:
            flash('Amount must be greater than 0', 'error')
            return redirect(url_for('dashboard'))
        
        new_transaction = Transaction(
            user_id=current_user.id,
            amount=amount,
            category=category,
            description=description,
            transaction_type=transaction_type
        )
        
        db.session.add(new_transaction)
        db.session.commit()
        
        flash('Transaction added successfully!', 'success')
    except ValueError:
        flash('Invalid amount. Please enter a valid number.', 'error')
    except Exception as e:
        flash('An error occurred while adding the transaction.', 'error')
    
    return redirect(url_for('dashboard'))

@app.context_processor
def utility_processor():
    def get_translated_text(key):
        return get_text(key, session.get('lang', 'en'))
    return dict(get_text=get_translated_text)

@app.route('/set_language/<lang>')
def set_language(lang):
    session['lang'] = lang
    return redirect(request.referrer or url_for('home'))

@app.route('/individual/dashboard')
@login_required
def individual_dashboard():
    """Individual dashboard endpoint"""
    try:
        if current_user.user_type != 'individual':
            flash('Unauthorized access', 'error')
            return redirect(url_for('dashboard'))
        
        # Initialize default values
        total_income = 0
        total_expenses = 0
        remaining_balance = 0
        monthly_income = 0
        monthly_expenses = 0
        category_expenses = {}
        transactions = []

        try:
            # Get transactions from database
            transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
            
            # Calculate financial statistics
            total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
            total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
            remaining_balance = total_income - total_expenses
            
            # Calculate monthly statistics
            current_month = datetime.utcnow().month
            current_year = datetime.utcnow().year
            monthly_transactions = [t for t in transactions 
                                 if t.date.month == current_month 
                                 and t.date.year == current_year]
            
            monthly_income = sum(t.amount for t in monthly_transactions if t.transaction_type == 'income')
            monthly_expenses = sum(t.amount for t in monthly_transactions if t.transaction_type == 'expense')
            
            # Calculate category-wise expenses
            category_expenses = {}
            for transaction in transactions:
                if transaction.transaction_type == 'expense':
                    category = transaction.category or 'Other'
                    if category not in category_expenses:
                        category_expenses[category] = 0
                    category_expenses[category] += transaction.amount
                    
        except Exception as e:
            print(f"Database error: {str(e)}")
            flash('Error loading transaction data', 'error')

        # Get individual financial data from CSV
        individual_data = process_individual_data()
        if individual_data is None:
            individual_data = {
                'monthly_income': monthly_income or 0,
                'monthly_expenses': monthly_expenses or 0,
                'monthly_savings': (monthly_income - monthly_expenses) if monthly_income and monthly_expenses else 0,
                'savings_goal': 0,
                'savings_rate': 0,
                'savings_growth': 0,
                'expense_breakdown': category_expenses or {},
                'spending_pattern': [],
                'improvement_tips': '',
                'suggested_changes': ''
            }
        
        # Generate recommendations
        recommendations = generate_individual_recommendations(individual_data)
        
        return render_template('individual_dashboard.html',
                             individual_data=individual_data,
                             recommendations=recommendations,
                             transactions=transactions,
                             total_income=total_income,
                             total_expenses=total_expenses,
                             remaining_balance=remaining_balance,
                             monthly_income=monthly_income,
                             monthly_expenses=monthly_expenses,
                             category_expenses=category_expenses)

    except Exception as e:
        print(f"Error in individual_dashboard: {str(e)}")
        flash('An error occurred while loading the dashboard', 'error')
        return render_template('individual_dashboard.html',
                             individual_data={
                                 'monthly_income': 0,
                                 'monthly_expenses': 0,
                                 'monthly_savings': 0,
                                 'savings_goal': 0,
                                 'savings_rate': 0,
                                 'savings_growth': 0,
                                 'expense_breakdown': {},
                                 'spending_pattern': [],
                                 'improvement_tips': '',
                                 'suggested_changes': ''
                             },
                             recommendations=[],
                             transactions=[],
                             total_income=0,
                             total_expenses=0,
                             remaining_balance=0,
                             monthly_income=0,
                             monthly_expenses=0,
                             category_expenses={})

def calculate_growth_rate(monthly_data):
    """Calculate growth rate from monthly data"""
    if not monthly_data or len(monthly_data) < 2:
        return 0
    
    recent_months = monthly_data[-2:]
    previous = recent_months[0]['revenue']
    current = recent_months[1]['revenue']
    
    if previous == 0:
        return 0
        
    return round(((current - previous) / previous) * 100, 2)

def calculate_cash_flow(monthly_data):
    """Calculate cash flow from monthly data"""
    if not monthly_data:
        return 0
        
    recent_month = monthly_data[-1]
    return round(recent_month['revenue'] - recent_month['cost'] - recent_month['expenses'], 2)

@app.route("/base")
def base():
    return render_template("user_type_selection.html") 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 
