import os
from datetime import date, datetime
from functools import wraps
from decimal import Decimal
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    url_for,
    flash,
    session
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Secret key from environment or fallback
app.secret_key = os.environ.get("SECRET_KEY", "prod-session-key-multiuser-expense-tracker-2026")

def get_db_connection():
    """Connects to Neon PostgreSQL cloud database using DATABASE_URL."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url and os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("DATABASE_URL="):
                    db_url = line.strip().split("=", 1)[1]
                    break
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is missing.")
    
    # Strip channel_binding if present for standard psycopg2 compatibility
    if "channel_binding=" in db_url:
        db_url = db_url.replace("&channel_binding=require", "").replace("?channel_binding=require", "?").rstrip("?")
    
    return psycopg2.connect(db_url)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access your dashboard.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ---------------------------------------------------------
# HTML TEMPLATES (Embedded for clean, zero-dependency hosting)
# ---------------------------------------------------------

AUTH_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} — Personal Expense Tracker</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #f8fafc;
            --surface: #ffffff;
            --border: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --primary: #4f46e5;
            --primary-hover: #4338ca;
            --danger: #ef4444;
            --success: #10b981;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: var(--bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }
        .auth-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 36px;
            width: 100%;
            max-width: 440px;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.08);
        }
        .logo-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #e0e7ff;
            color: #3730a3;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 20px;
        }
        h1 { font-size: 24px; font-weight: 800; color: var(--text-main); margin-bottom: 8px; }
        p.subtitle { color: var(--text-muted); font-size: 14px; margin-bottom: 24px; }
        .form-group { margin-bottom: 18px; }
        label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 7px; }
        input {
            width: 100%;
            padding: 12px 14px;
            border: 1px solid var(--border);
            border-radius: 10px;
            font-size: 14px;
            font-family: inherit;
        }
        input:focus {
            outline: 2px solid #c7d2fe;
            border-color: var(--primary);
        }
        button.btn-primary {
            width: 100%;
            padding: 13px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.2s;
            margin-top: 10px;
        }
        button.btn-primary:hover { background: var(--primary-hover); }
        .auth-footer {
            margin-top: 24px;
            text-align: center;
            font-size: 14px;
            color: var(--text-muted);
        }
        .auth-footer a { color: var(--primary); font-weight: 700; text-decoration: none; }
        .alert {
            padding: 12px 16px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 20px;
        }
        .alert.error { background: #fee2e2; color: #991b1b; }
        .alert.success { background: #dcfce7; color: #166534; }
    </style>
</head>
<body>
    <div class="auth-card">
        <div class="logo-badge">💰 Personal Expense Tracker</div>
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

LOGIN_HTML = AUTH_LAYOUT.replace("{% block content %}{% endblock %}", """
        <h1>Welcome Back</h1>
        <p class="subtitle">Log in to view your personal expenses & budget</p>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% for category, message in messages %}
                <div class="alert {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endwith %}

        <form method="POST" action="{{ url_for('login') }}">
            <div class="form-group">
                <label>Email Address</label>
                <input type="email" name="email" required placeholder="you@example.com">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required placeholder="••••••••">
            </div>
            <button type="submit" class="btn-primary">Sign In</button>
        </form>

        <div class="auth-footer">
            Don't have an account? <a href="{{ url_for('register') }}">Create one here</a>
        </div>
""")

REGISTER_HTML = AUTH_LAYOUT.replace("{% block content %}{% endblock %}", """
        <h1>Create Account</h1>
        <p class="subtitle">Set up your private dashboard in seconds</p>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% for category, message in messages %}
                <div class="alert {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endwith %}

        <form method="POST" action="{{ url_for('register') }}">
            <div class="form-group">
                <label>Full Name</label>
                <input type="text" name="name" required placeholder="Tathagat Kamble">
            </div>
            <div class="form-group">
                <label>Email Address</label>
                <input type="email" name="email" required placeholder="you@example.com">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" minlength="6" required placeholder="At least 6 characters">
            </div>
            <button type="submit" class="btn-primary">Register Account</button>
        </form>

        <div class="auth-footer">
            Already have an account? <a href="{{ url_for('login') }}">Sign In</a>
        </div>
""")


DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personal Expense Tracker — Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg: #f8fafc;
            --surface: #ffffff;
            --border: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --primary: #4f46e5;
            --primary-hover: #4338ca;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
            --shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.06);
            --radius-lg: 16px;
            --radius-md: 10px;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: var(--bg);
            color: var(--text-main);
            min-height: 100vh;
            padding-bottom: 60px;
        }

        .navbar {
            background: var(--surface);
            border-bottom: 1px solid var(--border);
            padding: 14px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 50;
        }

        .nav-brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 800;
            font-size: 18px;
            color: var(--text-main);
        }

        .nav-user {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .user-pill {
            font-size: 13px;
            font-weight: 600;
            background: #f1f5f9;
            padding: 6px 14px;
            border-radius: 9999px;
            color: var(--text-main);
        }

        .btn-logout {
            font-size: 13px;
            font-weight: 600;
            color: var(--danger);
            text-decoration: none;
            padding: 6px 12px;
            border-radius: 8px;
            border: 1px solid #fee2e2;
            transition: 0.2s;
        }
        .btn-logout:hover { background: #fee2e2; }

        .container {
            max-width: 1240px;
            margin: 0 auto;
            padding: 28px 20px;
        }

        /* Flash Alerts */
        .alert {
            padding: 12px 18px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 22px;
        }
        .alert.success { background: #dcfce7; color: #166534; }
        .alert.error { background: #fee2e2; color: #991b1b; }

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
            position: relative;
            overflow: hidden;
        }

        .stat-card::before {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; height: 4px;
        }

        .stat-card.income::before { background: var(--success); }
        .stat-card.expense::before { background: var(--danger); }
        .stat-card.balance::before { background: var(--primary); }
        .stat-card.savings::before { background: var(--warning); }

        .stat-label {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .stat-value {
            font-size: 28px;
            font-weight: 800;
            margin: 8px 0;
        }

        .stat-sub { font-size: 12px; color: var(--text-muted); }

        /* Forms Layout */
        .forms-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 28px;
        }

        @media (max-width: 860px) {
            .forms-grid { grid-template-columns: 1fr; }
        }

        .panel-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 24px;
            box-shadow: var(--shadow-sm);
        }

        .panel-card h2 {
            font-size: 17px;
            font-weight: 700;
            margin-bottom: 16px;
            color: var(--text-main);
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
            margin-bottom: 14px;
        }

        .form-group {
            margin-bottom: 14px;
        }

        label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 6px;
            color: var(--text-main);
        }

        input, select {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            background: white;
        }

        input:focus, select:focus {
            outline: 2px solid #c7d2fe;
            border-color: var(--primary);
        }

        button.btn-submit {
            padding: 11px 18px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.2s;
        }

        button.btn-submit:hover { background: var(--primary-hover); }

        button.btn-danger-outline {
            background: transparent;
            color: var(--danger);
            border: 1px solid #fee2e2;
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
        }
        button.btn-danger-outline:hover { background: #fee2e2; }

        /* Charts */
        .charts-grid {
            display: grid;
            grid-template-columns: 1.4fr 1fr;
            gap: 20px;
            margin-bottom: 28px;
        }

        @media (max-width: 960px) {
            .charts-grid { grid-template-columns: 1fr; }
        }

        .chart-container {
            position: relative;
            height: 270px;
            width: 100%;
        }

        /* Table */
        .table-responsive {
            overflow-x: auto;
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            margin-top: 14px;
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
            border-bottom: 1px solid var(--border);
        }

        td {
            padding: 13px 16px;
            border-bottom: 1px solid var(--border);
            vertical-align: middle;
        }

        tr:last-child td { border-bottom: none; }
        tr:hover td { background: #f8fafc; }

        .cat-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            background: #e0e7ff;
            color: #3730a3;
        }

        .action-links {
            display: flex;
            gap: 12px;
            font-size: 13px;
        }

        .action-links a { color: var(--primary); text-decoration: none; font-weight: 600; }
        .action-links button {
            background: none;
            border: none;
            color: var(--danger);
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            padding: 0;
            font-family: inherit;
        }
    </style>
</head>
<body>
    <!-- Top Navbar -->
    <header class="navbar">
        <div class="nav-brand">
            <span>💰</span> Personal Expense Tracker
        </div>
        <div class="nav-user">
            <span class="user-pill">👤 {{ session.get('user_name', 'User') }}</span>
            <a href="{{ url_for('logout') }}" class="btn-logout">Sign Out</a>
        </div>
    </header>

    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% for category, message in messages %}
                <div class="alert {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endwith %}

        <!-- Stat Cards -->
        <div class="stats-grid">
            <div class="stat-card income">
                <span class="stat-label">Total Income</span>
                <div class="stat-value" style="color: var(--success);">₹{{ "{:,.2f}".format(total_income) }}</div>
                <div class="stat-sub">Lifetime earnings recorded</div>
            </div>

            <div class="stat-card expense">
                <span class="stat-label">Total Expenses</span>
                <div class="stat-value" style="color: var(--danger);">₹{{ "{:,.2f}".format(total_expenses) }}</div>
                <div class="stat-sub">Lifetime outgoings recorded</div>
            </div>

            <div class="stat-card balance">
                <span class="stat-label">Net Balance</span>
                <div class="stat-value" style="color: var(--primary);">₹{{ "{:,.2f}".format(balance) }}</div>
                <div class="stat-sub">Available savings balance</div>
            </div>

            <div class="stat-card savings">
                <span class="stat-label">Savings Rate</span>
                <div class="stat-value" style="color: var(--warning);">{{ savings_rate }}%</div>
                <div class="stat-sub">Target: &gt; 30%</div>
            </div>
        </div>

        <!-- Add Expense and Add Income Forms -->
        <div class="forms-grid">
            <!-- Add Expense -->
            <div class="panel-card">
                <h2>➕ Add New Expense</h2>
                <form method="POST" action="{{ url_for('add_expense') }}">
                    <div class="form-row">
                        <div>
                            <label>Amount (₹)</label>
                            <input type="number" step="0.01" name="amount" required placeholder="e.g. 450">
                        </div>
                        <div>
                            <label>Category</label>
                            <select name="category_id" required>
                                {% for cat in categories %}
                                    <option value="{{ cat[0] }}">{{ cat[1] }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>

                    <div class="form-row">
                        <div>
                            <label>Date</label>
                            <input type="date" name="expense_date" value="{{ today }}" required>
                        </div>
                        <div>
                            <label>Payment Method</label>
                            <select name="payment_method">
                                <option value="UPI">UPI / GPay / PhonePe</option>
                                <option value="Cash">Cash</option>
                                <option value="Credit Card">Credit Card</option>
                                <option value="Debit Card">Debit Card</option>
                                <option value="Net Banking">Net Banking</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Description (Optional)</label>
                        <input type="text" name="description" placeholder="e.g. Dinner with team">
                    </div>

                    <button type="submit" class="btn-submit">Save Expense</button>
                </form>
            </div>

            <!-- Add Income -->
            <div class="panel-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <h2 style="margin-bottom: 0;">💵 Add Income</h2>
                    <form method="POST" action="{{ url_for('reset_income') }}" onsubmit="return confirm('Reset all your income records? This action cannot be undone.');">
                        <button type="submit" class="btn-danger-outline">Reset My Income</button>
                    </form>
                </div>
                <form method="POST" action="{{ url_for('add_income') }}">
                    <div class="form-row">
                        <div>
                            <label>Source</label>
                            <input type="text" name="source" required placeholder="e.g. Salary, Freelance">
                        </div>
                        <div>
                            <label>Amount (₹)</label>
                            <input type="number" step="0.01" name="amount" required placeholder="e.g. 50000">
                        </div>
                    </div>

                    <div class="form-row">
                        <div>
                            <label>Date</label>
                            <input type="date" name="income_date" value="{{ today }}" required>
                        </div>
                        <div>
                            <label>Description (Optional)</label>
                            <input type="text" name="description" placeholder="e.g. Monthly stipend">
                        </div>
                    </div>

                    <button type="submit" class="btn-submit">Save Income</button>
                </form>
            </div>
        </div>

        <!-- Charts Grid -->
        <div class="charts-grid">
            <div class="panel-card">
                <h2>📊 Monthly Expenses (Last 6 Months)</h2>
                <div class="chart-container">
                    <canvas id="monthlyChart"></canvas>
                </div>
            </div>

            <div class="panel-card">
                <h2>🍩 Expenses by Category</h2>
                <div class="chart-container">
                    <canvas id="categoryChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Recent Expenses Table -->
        <div class="panel-card">
            <h2>📝 Your Recent Expenses</h2>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Description</th>
                            <th>Category</th>
                            <th>Payment Method</th>
                            <th>Amount</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% if recent_expenses %}
                            {% for e in recent_expenses %}
                            <tr>
                                <td>{{ e[1] }}</td>
                                <td>{{ e[5] or '—' }}</td>
                                <td><span class="cat-badge">{{ e[2] }}</span></td>
                                <td style="color: var(--text-muted);">{{ e[4] or '—' }}</td>
                                <td style="font-weight: 700; color: var(--danger);">- ₹{{ "{:,.2f}".format(e[3]) }}</td>
                                <td>
                                    <div class="action-links">
                                        <a href="{{ url_for('edit_expense', expense_id=e[0]) }}">Edit</a>
                                        <form method="POST" action="{{ url_for('delete_expense', expense_id=e[0]) }}" onsubmit="return confirm('Delete this expense?');" style="display:inline;">
                                            <button type="submit">Delete</button>
                                        </form>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        {% else %}
                            <tr>
                                <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 24px;">
                                    No expenses added yet! Use the form above to add your first expense.
                                </td>
                            </tr>
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Chart Scripts -->
    <script>
        // Doughnut Chart
        const catLabels = {{ category_labels | tojson }};
        const catValues = {{ category_values | tojson }};
        const catCtx = document.getElementById('categoryChart').getContext('2d');
        
        if (catLabels.length > 0) {
            new Chart(catCtx, {
                type: 'doughnut',
                data: {
                    labels: catLabels,
                    datasets: [{
                        data: catValues,
                        backgroundColor: ['#6366f1', '#ec4899', '#f59e0b', '#06b6d4', '#8b5cf6', '#10b981', '#64748b', '#ef4444', '#14b8a6'],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } }
                }
            });
        } else {
            catCtx.font = "14px 'Plus Jakarta Sans', sans-serif";
            catCtx.fillStyle = "#94a3b8";
            catCtx.textAlign = "center";
            catCtx.fillText("No category expense data yet", 150, 130);
        }

        // Monthly Bar Chart
        const monthLabels = {{ month_labels | tojson }};
        const monthValues = {{ month_values | tojson }};
        const monthCtx = document.getElementById('monthlyChart').getContext('2d');
        
        if (monthLabels.length > 0) {
            new Chart(monthCtx, {
                type: 'bar',
                data: {
                    labels: monthLabels,
                    datasets: [{
                        label: 'Expenses (₹)',
                        data: monthValues,
                        backgroundColor: '#6366f1',
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { grid: { display: false } },
                        y: { grid: { color: '#f1f5f9' } }
                    }
                }
            });
        } else {
            monthCtx.font = "14px 'Plus Jakarta Sans', sans-serif";
            monthCtx.fillStyle = "#94a3b8";
            monthCtx.textAlign = "center";
            monthCtx.fillText("No monthly expense history yet", 250, 130);
        }
    </script>
</body>
</html>
"""

EDIT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Expense</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #f8fafc; padding: 40px 20px; display: flex; justify-content: center; }
        .edit-card { background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 32px; width: 100%; max-width: 500px; box-shadow: 0 4px 16px rgba(0,0,0,0.06); }
        h1 { font-size: 20px; font-weight: 800; margin-bottom: 20px; }
        .form-group { margin-bottom: 16px; }
        label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
        input, select { width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; box-sizing: border-box; }
        .btn-group { display: flex; gap: 12px; margin-top: 24px; }
        button { flex: 1; padding: 12px; background: #4f46e5; color: white; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; }
        a { flex: 1; padding: 12px; background: #f1f5f9; color: #475569; text-align: center; text-decoration: none; border-radius: 8px; font-weight: 700; }
    </style>
</head>
<body>
    <div class="edit-card">
        <h1>✏️ Edit Expense</h1>
        <form method="POST">
            <div class="form-group">
                <label>Amount (₹)</label>
                <input type="number" step="0.01" name="amount" value="{{ expense[1] }}" required>
            </div>
            <div class="form-group">
                <label>Category</label>
                <select name="category_id" required>
                    {% for c in categories %}
                        <option value="{{ c[0] }}" {% if c[0] == expense[2] %}selected{% endif %}>{{ c[1] }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label>Date</label>
                <input type="date" name="expense_date" value="{{ expense[3] }}" required>
            </div>
            <div class="form-group">
                <label>Payment Method</label>
                <select name="payment_method">
                    <option value="UPI" {% if expense[4] == 'UPI' %}selected{% endif %}>UPI / GPay / PhonePe</option>
                    <option value="Cash" {% if expense[4] == 'Cash' %}selected{% endif %}>Cash</option>
                    <option value="Credit Card" {% if expense[4] == 'Credit Card' %}selected{% endif %}>Credit Card</option>
                    <option value="Debit Card" {% if expense[4] == 'Debit Card' %}selected{% endif %}>Debit Card</option>
                    <option value="Net Banking" {% if expense[4] == 'Net Banking' %}selected{% endif %}>Net Banking</option>
                </select>
            </div>
            <div class="form-group">
                <label>Description</label>
                <input type="text" name="description" value="{{ expense[5] or '' }}">
            </div>
            <div class="btn-group">
                <button type="submit">Update Expense</button>
                <a href="{{ url_for('home') }}">Cancel</a>
            </div>
        </form>
    </div>
</body>
</html>
"""


# ---------------------------------------------------------
# AUTHENTICATION ROUTES
# ---------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template_string(REGISTER_HTML, title="Register")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template_string(REGISTER_HTML, title="Register")

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Check existing email
                cur.execute("SELECT user_id FROM users WHERE email = %s", (email,))
                if cur.fetchone():
                    flash("An account with that email already exists. Please log in.", "error")
                    return redirect(url_for("login"))

                # Hash password securely
                hashed_pw = generate_password_hash(password)

                cur.execute(
                    "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING user_id",
                    (name, email, hashed_pw)
                )
                user_id = cur.fetchone()[0]
                conn.commit()

                # Log user in
                session["user_id"] = user_id
                session["user_name"] = name
                session["user_email"] = email
                flash(f"Welcome, {name}! Your account has been created.", "success")
                return redirect(url_for("home"))
        finally:
            conn.close()

    return render_template_string(REGISTER_HTML, title="Register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id, name, password FROM users WHERE email = %s", (email,))
                user = cur.fetchone()

                if not user or not check_password_hash(user[2], password):
                    flash("Invalid email or password. Please try again.", "error")
                    return render_template_string(LOGIN_HTML, title="Sign In")

                # Successful login
                session["user_id"] = user[0]
                session["user_name"] = user[1]
                session["user_email"] = email
                flash(f"Welcome back, {user[1]}!", "success")
                return redirect(url_for("home"))
        finally:
            conn.close()

    return render_template_string(LOGIN_HTML, title="Sign In")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out successfully.", "success")
    return redirect(url_for("login"))


# ---------------------------------------------------------
# DASHBOARD & FINANCIAL ROUTES (STRICTLY ISOLATED BY USER_ID)
# ---------------------------------------------------------

@app.route("/")
@login_required
def home():
    user_id = session["user_id"]
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Total expenses (strictly filtered by logged-in user_id)
            cur.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id = %s",
                (user_id,)
            )
            total_expenses = float(cur.fetchone()[0])

            # 2. Total income (strictly filtered by logged-in user_id)
            cur.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM income WHERE user_id = %s",
                (user_id,)
            )
            total_income = float(cur.fetchone()[0])

            # 3. Balance & Savings Rate
            balance = total_income - total_expenses
            savings_rate = round((balance / total_income) * 100, 1) if total_income > 0 else 0

            # 4. Recent expenses for this user
            cur.execute("""
                SELECT 
                    e.expense_id,
                    e.expense_date,
                    c.category_name,
                    e.amount,
                    e.payment_method,
                    e.description
                FROM expenses e
                LEFT JOIN categories c ON e.category_id = c.category_id
                WHERE e.user_id = %s
                ORDER BY e.expense_date DESC, e.expense_id DESC
                LIMIT 10
            """, (user_id,))
            recent_expenses = [
                (
                    row[0],
                    row[1].isoformat() if hasattr(row[1], 'isoformat') else str(row[1]),
                    row[2] or "Uncategorized",
                    float(row[3]),
                    row[4],
                    row[5]
                )
                for row in cur.fetchall()
            ]

            # 5. Categories list for form
            cur.execute("SELECT category_id, category_name FROM categories ORDER BY category_name")
            categories = cur.fetchall()

            # 6. Expenses by Category (Doughnut Chart data)
            cur.execute("""
                SELECT 
                    c.category_name,
                    SUM(e.amount) AS cat_total
                FROM expenses e
                INNER JOIN categories c ON e.category_id = c.category_id
                WHERE e.user_id = %s
                GROUP BY c.category_id, c.category_name
                ORDER BY cat_total DESC
            """, (user_id,))
            cat_rows = cur.fetchall()
            category_labels = [row[0] for row in cat_rows]
            category_values = [float(row[1]) for row in cat_rows]

            # 7. Monthly Expenses for the last 6 months (Bar Chart data)
            cur.execute("""
                SELECT 
                    TO_CHAR(expense_date, 'Mon YYYY') AS month_label,
                    DATE_TRUNC('month', expense_date) AS month_start,
                    SUM(amount) AS monthly_total
                FROM expenses
                WHERE user_id = %s
                GROUP BY month_label, month_start
                ORDER BY month_start ASC
                LIMIT 6
            """, (user_id,))
            month_rows = cur.fetchall()
            month_labels = [row[0] for row in month_rows]
            month_values = [float(row[2]) for row in month_rows]

        return render_template_string(
            DASHBOARD_HTML,
            total_expenses=total_expenses,
            total_income=total_income,
            balance=balance,
            savings_rate=savings_rate,
            recent_expenses=recent_expenses,
            categories=categories,
            category_labels=category_labels,
            category_values=category_values,
            month_labels=month_labels,
            month_values=month_values,
            today=date.today().isoformat()
        )
    finally:
        conn.close()


@app.route("/add-expense", methods=["POST"])
@login_required
def add_expense():
    user_id = session["user_id"]
    try:
        amount = float(request.form["amount"])
        category_id = int(request.form["category_id"])
        expense_date = date.fromisoformat(request.form["expense_date"])
        payment_method = request.form.get("payment_method", "").strip()
        description = request.form.get("description", "").strip()

        if amount <= 0:
            flash("Amount must be greater than zero.", "error")
            return redirect(url_for("home"))

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO expenses (user_id, category_id, amount, expense_date, payment_method, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_id, category_id, amount, expense_date, payment_method or None, description or None))
                conn.commit()
            flash("Expense added successfully!", "success")
        finally:
            conn.close()

    except Exception as e:
        app.logger.exception("Error adding expense")
        flash("Could not save expense. Please check your inputs.", "error")

    return redirect(url_for("home"))


@app.route("/edit-expense/<int:expense_id>", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):
    user_id = session["user_id"]
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if request.method == "POST":
                amount = float(request.form["amount"])
                category_id = int(request.form["category_id"])
                expense_date = date.fromisoformat(request.form["expense_date"])
                payment_method = request.form.get("payment_method", "").strip()
                description = request.form.get("description", "").strip()

                if amount <= 0:
                    flash("Amount must be greater than zero.", "error")
                    return redirect(url_for("edit_expense", expense_id=expense_id))

                cur.execute("""
                    UPDATE expenses 
                    SET amount = %s, category_id = %s, expense_date = %s, payment_method = %s, description = %s
                    WHERE expense_id = %s AND user_id = %s
                """, (amount, category_id, expense_date, payment_method or None, description or None, expense_id, user_id))
                conn.commit()

                flash("Expense updated successfully!", "success")
                return redirect(url_for("home"))

            # GET: Fetch expense strictly belonging to this user
            cur.execute("""
                SELECT expense_id, amount, category_id, expense_date, payment_method, description
                FROM expenses
                WHERE expense_id = %s AND user_id = %s
            """, (expense_id, user_id))
            row = cur.fetchone()

            if not row:
                flash("Expense not found or unauthorized.", "error")
                return redirect(url_for("home"))

            expense = (
                row[0],
                float(row[1]),
                row[2],
                row[3].isoformat() if hasattr(row[3], 'isoformat') else str(row[3]),
                row[4],
                row[5]
            )

            cur.execute("SELECT category_id, category_name FROM categories ORDER BY category_name")
            categories = cur.fetchall()

        return render_template_string(EDIT_HTML, expense=expense, categories=categories)
    finally:
        conn.close()


@app.route("/delete-expense/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense(expense_id):
    user_id = session["user_id"]
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM expenses WHERE expense_id = %s AND user_id = %s", (expense_id, user_id))
            conn.commit()
            if cur.rowcount:
                flash("Expense deleted successfully.", "success")
            else:
                flash("Expense not found.", "error")
    finally:
        conn.close()

    return redirect(url_for("home"))


@app.route("/add-income", methods=["POST"])
@login_required
def add_income():
    user_id = session["user_id"]
    try:
        source = request.form.get("source", "").strip()
        amount = float(request.form["amount"])
        income_date = date.fromisoformat(request.form["income_date"])
        description = request.form.get("description", "").strip()

        if not source or amount <= 0:
            flash("Enter a valid income source and amount.", "error")
            return redirect(url_for("home"))

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO income (user_id, source, amount, income_date, description)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, source, amount, income_date, description or None))
                conn.commit()
            flash("Income recorded successfully!", "success")
        finally:
            conn.close()

    except Exception:
        app.logger.exception("Error adding income")
        flash("Could not save income. Please check your inputs.", "error")

    return redirect(url_for("home"))


@app.route("/reset-income", methods=["POST"])
@login_required
def reset_income():
    user_id = session["user_id"]
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Strictly reset income only for the active user
            cur.execute("DELETE FROM income WHERE user_id = %s", (user_id,))
            conn.commit()
        flash("Your income records have been reset.", "success")
    finally:
        conn.close()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
