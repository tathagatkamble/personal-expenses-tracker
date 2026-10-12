from flask import Flask, render_template_string, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "demo-session-secret-key-expense-tracker"

# In-memory sample data (Safe for public demo - zero connection to local SQL Server)
SAMPLE_INCOME = 75000.00
SAMPLE_CATEGORIES = [
    {"name": "Housing & Rent", "amount": 18000.00, "color": "#6366f1"},
    {"name": "Food & Dining", "amount": 9400.00, "color": "#ec4899"},
    {"name": "Utilities & Bills", "amount": 4850.00, "color": "#f59e0b"},
    {"name": "Transportation", "amount": 3500.00, "color": "#06b6d4"},
    {"name": "Entertainment", "amount": 4200.00, "color": "#8b5cf6"},
    {"name": "Healthcare", "amount": 2100.00, "color": "#10b981"},
    {"name": "Shopping & Misc", "amount": 1200.00, "color": "#64748b"},
]

SAMPLE_MONTHS = [
    {"month": "Nov", "income": 72000, "expenses": 41500},
    {"month": "Dec", "income": 75000, "expenses": 48200},
    {"month": "Jan", "income": 74000, "expenses": 40100},
    {"month": "Feb", "income": 75000, "expenses": 42800},
    {"month": "Mar", "income": 78000, "expenses": 45300},
    {"month": "Apr", "income": 75000, "expenses": 43250},
]

SAMPLE_EXPENSES = [
    {"id": 1, "date": "2026-04-11", "category": "Food & Dining", "description": "Grocery shopping at D-Mart", "amount": 3450.00, "payment_method": "UPI"},
    {"id": 2, "date": "2026-04-10", "category": "Utilities & Bills", "description": "High-speed Fiber Internet Bill", "amount": 1199.00, "payment_method": "Net Banking"},
    {"id": 3, "date": "2026-04-09", "category": "Transportation", "description": "Fuel refill (Petrol)", "amount": 2200.00, "payment_method": "Credit Card"},
    {"id": 4, "date": "2026-04-07", "category": "Entertainment", "description": "Weekend movie tickets & snacks", "amount": 1250.00, "payment_method": "UPI"},
    {"id": 5, "date": "2026-04-05", "category": "Food & Dining", "description": "Team lunch at Bistro", "amount": 1680.00, "payment_method": "UPI"},
    {"id": 6, "date": "2026-04-03", "category": "Healthcare", "description": "Pharmacy medicines & vitamins", "amount": 950.00, "payment_method": "Debit Card"},
    {"id": 7, "date": "2026-04-01", "category": "Housing & Rent", "description": "Monthly Apartment Rent", "amount": 18000.00, "payment_method": "Bank Transfer"},
]

DEMO_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personal Expense Tracker — Interactive Demo</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg: #f8fafc;
            --surface: #ffffff;
            --surface-subtle: #f1f5f9;
            --border: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --primary: #4f46e5;
            --primary-hover: #4338ca;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.06), 0 8px 10px -6px rgba(15, 23, 42, 0.04);
            --radius-lg: 16px;
            --radius-md: 10px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            min-height: 100vh;
            line-height: 1.5;
            padding-bottom: 60px;
        }

        /* Top Demo Notice Banner */
        .demo-banner {
            background: linear-gradient(90deg, #1e1b4b 0%, #312e81 100%);
            color: #ffffff;
            padding: 12px 20px;
            text-align: center;
            font-size: 14px;
            font-weight: 500;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }

        .demo-pill {
            background: #f59e0b;
            color: #78350f;
            padding: 2px 10px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-right: 8px;
            display: inline-block;
        }

        .container {
            max-width: 1240px;
            margin: 0 auto;
            padding: 28px 20px;
        }

        /* Header */
        .app-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 28px;
        }

        .title-group h1 {
            font-size: 26px;
            font-weight: 800;
            color: var(--text-main);
            letter-spacing: -0.02em;
        }

        .title-group p {
            color: var(--text-muted);
            font-size: 14px;
            margin-top: 2px;
        }

        .badge-academic {
            background: #e0e7ff;
            color: #3730a3;
            font-size: 12px;
            font-weight: 600;
            padding: 6px 14px;
            border-radius: 9999px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        /* Stat Cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 18px;
            margin-bottom: 28px;
        }

        .stat-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 22px;
            box-shadow: var(--shadow-sm);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            position: relative;
            overflow: hidden;
        }

        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow);
        }

        .stat-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
        }

        .stat-card.income::before { background: var(--success); }
        .stat-card.expense::before { background: var(--danger); }
        .stat-card.balance::before { background: var(--primary); }
        .stat-card.savings::before { background: var(--warning); }

        .stat-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }

        .stat-label {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .stat-icon {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }

        .income .stat-icon { background: #dcfce7; color: #166534; }
        .expense .stat-icon { background: #fee2e2; color: #991b1b; }
        .balance .stat-icon { background: #e0e7ff; color: #4338ca; }
        .savings .stat-icon { background: #fef3c7; color: #92400e; }

        .stat-value {
            font-size: 28px;
            font-weight: 800;
            color: var(--text-main);
            letter-spacing: -0.02em;
        }

        .stat-subtitle {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 6px;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        /* Charts Section */
        .charts-grid {
            display: grid;
            grid-template-columns: 1.4fr 1fr;
            gap: 20px;
            margin-bottom: 28px;
        }

        @media (max-width: 960px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }
        }

        .chart-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 24px;
            box-shadow: var(--shadow-sm);
        }

        .chart-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 18px;
        }

        .chart-header h2 {
            font-size: 17px;
            font-weight: 700;
            color: var(--text-main);
        }

        .chart-container {
            position: relative;
            height: 280px;
            width: 100%;
        }

        /* Table Card */
        .table-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 24px;
            box-shadow: var(--shadow-sm);
        }

        .table-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 20px;
        }

        .table-header h2 {
            font-size: 17px;
            font-weight: 700;
            color: var(--text-main);
        }

        .table-responsive {
            overflow-x: auto;
            border-radius: var(--radius-md);
            border: 1px solid var(--border);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            text-align: left;
        }

        th {
            background: #f8fafc;
            color: var(--text-muted);
            font-weight: 600;
            padding: 12px 16px;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid var(--border);
        }

        td {
            padding: 14px 16px;
            border-bottom: 1px solid var(--border);
            color: var(--text-main);
            vertical-align: middle;
        }

        tr:last-child td {
            border-bottom: none;
        }

        tr:hover td {
            background: #f8fafc;
        }

        .category-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            background: #f1f5f9;
            color: #334155;
        }

        .amount-col {
            font-weight: 700;
            color: var(--danger);
            text-align: right;
        }

        .th-right {
            text-align: right;
        }

        /* Footer */
        .footer {
            margin-top: 40px;
            text-align: center;
            font-size: 13px;
            color: var(--text-muted);
        }

        .footer a {
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <!-- Top Notice Banner -->
    <div class="demo-banner">
        <span class="demo-pill">DEMO MODE</span>
        <strong>All figures are sample data.</strong>
        Local Microsoft SQL Server connection is disabled for public web access.
    </div>

    <div class="container">
        <!-- Header -->
        <header class="app-header">
            <div class="title-group">
                <h1>Personal Expense Tracker</h1>
                <p>B.Tech IT Final Year Project Dashboard Demo</p>
            </div>
            <div class="badge-academic">
                <span>🎓</span> Final Year Project Demo
            </div>
        </header>

        <!-- Stat Cards -->
        <div class="stats-grid">
            <div class="stat-card income">
                <div class="stat-header">
                    <span class="stat-label">Monthly Income</span>
                    <div class="stat-icon">₹</div>
                </div>
                <div class="stat-value">₹{{ "{:,.2f}".format(total_income) }}</div>
                <div class="stat-subtitle">April 2026 Salary / Inflows</div>
            </div>

            <div class="stat-card expense">
                <div class="stat-header">
                    <span class="stat-label">Total Expenses</span>
                    <div class="stat-icon">📉</div>
                </div>
                <div class="stat-value">₹{{ "{:,.2f}".format(total_expenses) }}</div>
                <div class="stat-subtitle">Total April outgoings</div>
            </div>

            <div class="stat-card balance">
                <div class="stat-header">
                    <span class="stat-label">Net Balance</span>
                    <div class="stat-icon">💰</div>
                </div>
                <div class="stat-value">₹{{ "{:,.2f}".format(balance) }}</div>
                <div class="stat-subtitle">Available savings this month</div>
            </div>

            <div class="stat-card savings">
                <div class="stat-header">
                    <span class="stat-label">Savings Rate</span>
                    <div class="stat-icon">⚡</div>
                </div>
                <div class="stat-value">{{ savings_rate }}%</div>
                <div class="stat-subtitle">Health metric (Target: &gt; 30%)</div>
            </div>
        </div>

        <!-- Charts Grid -->
        <div class="charts-grid">
            <!-- Monthly Bar Chart -->
            <div class="chart-card">
                <div class="chart-header">
                    <h2>6-Month Cash Flow (Income vs Expenses)</h2>
                </div>
                <div class="chart-container">
                    <canvas id="monthlyBarChart"></canvas>
                </div>
            </div>

            <!-- Doughnut Chart -->
            <div class="chart-card">
                <div class="chart-header">
                    <h2>Expense by Category</h2>
                </div>
                <div class="chart-container">
                    <canvas id="categoryDoughnutChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Recent Sample Expenses Table -->
        <div class="table-card">
            <div class="table-header">
                <h2>Recent Sample Expenses</h2>
                <span style="font-size: 13px; color: var(--text-muted);">Showing 7 verified sample records</span>
            </div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Description</th>
                            <th>Category</th>
                            <th>Payment Method</th>
                            <th class="th-right">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for expense in expenses %}
                        <tr>
                            <td style="font-weight: 500;">{{ expense.date }}</td>
                            <td>{{ expense.description }}</td>
                            <td>
                                <span class="category-badge">{{ expense.category }}</span>
                            </td>
                            <td style="color: var(--text-muted);">{{ expense.payment_method }}</td>
                            <td class="amount-col">- ₹{{ "{:,.2f}".format(expense.amount) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Footer -->
        <footer class="footer">
            <p>Personal Expense Tracker &bull; Developed by Tathagat Kamble &bull; Built with Flask &bull; Free Cloud Demo on Render</p>
        </footer>
    </div>

    <!-- Chart Configuration Scripts -->
    <script>
        // Category Doughnut Chart
        const catLabels = {{ category_labels | tojson }};
        const catAmounts = {{ category_amounts | tojson }};
        const catColors = {{ category_colors | tojson }};

        const ctxDoughnut = document.getElementById('categoryDoughnutChart').getContext('2d');
        new Chart(ctxDoughnut, {
            type: 'doughnut',
            data: {
                labels: catLabels,
                datasets: [{
                    data: catAmounts,
                    backgroundColor: catColors,
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                            padding: 14,
                            font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return ' ' + context.label + ': ₹' + Number(context.raw).toLocaleString('en-IN');
                            }
                        }
                    }
                },
                cutout: '68%'
            }
        });

        // Monthly Bar Chart
        const months = {{ month_labels | tojson }};
        const monthlyIncomes = {{ month_incomes | tojson }};
        const monthlyExpenses = {{ month_expenses | tojson }};

        const ctxBar = document.getElementById('monthlyBarChart').getContext('2d');
        new Chart(ctxBar, {
            type: 'bar',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'Income (₹)',
                        data: monthlyIncomes,
                        backgroundColor: '#10b981',
                        borderRadius: 6
                    },
                    {
                        label: 'Expenses (₹)',
                        data: monthlyExpenses,
                        backgroundColor: '#f43f5e',
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            boxWidth: 12,
                            font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return ' ' + context.dataset.label + ': ₹' + Number(context.raw).toLocaleString('en-IN');
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false }
                    },
                    y: {
                        grid: { color: '#f1f5f9' },
                        ticks: {
                            callback: function(value) {
                                return '₹' + (value / 1000) + 'k';
                            }
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    total_income = SAMPLE_INCOME
    total_expenses = sum(item["amount"] for item in SAMPLE_CATEGORIES)
    balance = total_income - total_expenses
    savings_rate = round((balance / total_income) * 100, 1) if total_income > 0 else 0

    category_labels = [c["name"] for c in SAMPLE_CATEGORIES]
    category_amounts = [c["amount"] for c in SAMPLE_CATEGORIES]
    category_colors = [c["color"] for c in SAMPLE_CATEGORIES]

    month_labels = [m["month"] for m in SAMPLE_MONTHS]
    month_incomes = [m["income"] for m in SAMPLE_MONTHS]
    month_expenses = [m["expenses"] for m in SAMPLE_MONTHS]

    return render_template_string(
        DEMO_HTML,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        savings_rate=savings_rate,
        expenses=SAMPLE_EXPENSES,
        category_labels=category_labels,
        category_amounts=category_amounts,
        category_colors=category_colors,
        month_labels=month_labels,
        month_incomes=month_incomes,
        month_expenses=month_expenses
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
