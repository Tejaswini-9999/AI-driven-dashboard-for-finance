# Financial Tracking Dashboard

A Flask-based web application for tracking personal and business finances. The application provides separate dashboards for individuals and companies, with features for tracking income, expenses, and financial metrics.

## Features

### Individual Dashboard
- Track personal income and expenses
- Categorize transactions
- View financial summary
- Monitor spending patterns

### Company Dashboard
- Track business revenue and expenses
- Monitor profit margins
- View financial metrics and charts
- Categorize business transactions
- Analyze spending patterns

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd fintech-hackathon
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python app.py
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

1. Visit the home page and select your account type (Individual or Company)
2. Create an account or log in
3. Start adding transactions
4. View your financial dashboard with statistics and charts

## Technologies Used

- Flask
- SQLAlchemy
- Tailwind CSS
- Chart.js
- Python 3.x

## Project Structure

```
fintech-hackathon/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── templates/         # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── individual_dashboard.html
│   └── company_dashboard.html
└── README.md
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 