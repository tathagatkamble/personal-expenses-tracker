
from flask import Flask, render_template_string, request, redirect, url_for, flash
from db import get_connection
from datetime import date

app = Flask(__name__)
app.secret_key = "dev-only-change-this-before-deployment"

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Personal Expense Tracker</title>
    
<style>
    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        padding: 28px;
        background: #f4f7fb;
        color: #172033;
        font-family: Arial, Helvetica, sans-serif;
    }

    h1 {
        margin-bottom: 8px;
        font-size: 30px;
    }

    h2 {
        margin-top: 0;
        font-size: 20px;
    }

    .panel, .card, .summary-card {
        background: #ffffff;
        border: 1px solid #e6eaf0;
        border-radius: 14px;
        padding: 22px;
        margin: 20px 0;
        box-shadow: 0 4px 16px rgba(20, 35, 60, 0.05);
    }

    .cards, .summary-cards, .stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
        gap: 16px;
        margin: 22px 0;
    }

    .label {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 10px;
    }

    .amount {
        font-size: 27px;
        font-weight: 700;
        overflow-wrap: anywhere;
    }

    label {
        display: block;
        margin: 14px 0 7px;
        font-weight: 600;
        font-size: 14px;
    }

    input, select {
        width: 100%;
        max-width: 100%;
        padding: 11px 12px;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        background: white;
        font-size: 15px;
    }

    input:focus, select:focus {
        outline: 2px solid #bfdbfe;
        border-color: #3b82f6;
    }

    button {
        padding: 11px 17px;
        margin-top: 14px;
        border: 0;
        border-radius: 8px;
        background: #2563eb;
        color: white;
        font-weight: 600;
        cursor: pointer;
    }

    button:hover {
        background: #1d4ed8;
    }

    .btn-danger {
        background: #dc2626;
        color: white;
    }

    .btn-danger:hover {
        background: #b91c1c;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        background: white;
    }

    th, td {
        padding: 13px 12px;
        border-bottom: 1px solid #e8edf4;
        text-align: left;
        vertical-align: top;
    }

    th {
        background: #f8fafc;
        color: #475569;
        font-size: 13px;
    }

    a {
        color: #2563eb;
        text-decoration: none;
        font-weight: 600;
    }

    .success {
        color: #166534;
        background: #dcfce7;
        padding: 12px;
        border-radius: 8px;
    }

    .error {
        color: #991b1b;
        background: #fee2e2;
        padding: 12px;
        border-radius: 8px;
    }

    @media (max-width: 700px) {
        body {
            padding: 14px;
        }

        h1 {
            font-size: 25px;
        }

        .panel, .card, .summary-card {
            padding: 15px;
        }

        table {
            display: block;
            overflow-x: auto;
            white-space: nowrap;
        }
    }
</style>
</head>
<body>
    <h1>Personal Expense Tracker</h1>
    <p>Your financial overview</p>

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% for category, message in messages %}
            <p class="{{ category }}">{{ message }}</p>
        {% endfor %}
    {% endwith %}

    {% if error %}
        <p class="error">{{ error }}</p>
    {% else %}
        <div class="cards">
            <div class="card">
                <div class="label">Total Expenses</div>
                <div class="amount">₹{{ "%.2f"|format(total_expenses) }}</div>
            </div>
            <div class="card">
                <div class="label">Total Income</div>
                <div class="amount">₹{{ "%.2f"|format(total_income) }}</div>
            </div>
            <div class="card">
                <div class="label">Balance</div>
                <div class="amount">₹{{ "%.2f"|format(total_income - total_expenses) }}</div>
            </div>
        </div>

<div class="panel">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px;">
        <h2 style="margin: 0;">Add Income</h2>
        <form action="{{ url_for('reset_income') }}" method="POST" style="margin: 0;"
              onsubmit="return confirm('Are you sure you want to delete all income records? This action cannot be undone.');">
            <button type="submit" class="btn-danger" style="margin: 0;">Reset Income</button>
        </form>
    </div>

    <form action="{{ url_for('add_income') }}" method="POST">
        <label>Income Source</label>
        <select name="source" required>
            <option value="">Select source</option>
            <option value="Salary">Salary</option>
            <option value="Freelancing">Freelancing</option>
            <option value="Scholarship">Scholarship</option>
            <option value="Business">Business</option>
            <option value="Other">Other</option>
        </select>

        <label>Amount Received (₹)</label>
        <input type="number" name="amount"
               min="0.01" step="0.01" required>

        <label>Date Received</label>
        <input type="date" name="income_date"
               value="{{ today }}" required>

        <label>Description</label>
        <input type="text" name="description"
               maxlength="200"
               placeholder="e.g. October salary">

        <button type="submit">Save Income</button>
    </form>
</div>
        <div class="panel">
            <h2>Add an Expense</h2>
            <form action="{{ url_for('add_expense') }}" method="POST">
                <label>Amount (₹)</label>
                <input type="number" name="amount" min="0.01" step="0.01" required>

                <label>Category</label>
                <select name="category_id" required>
                    <option value="">Select category</option>
                    {% for category in categories %}
                        <option value="{{ category[0] }}">{{ category[1] }}</option>
                    {% endfor %}
                </select>

                <label>Expense Date</label>
                <input type="date" name="expense_date" value="{{ today }}" required>

                <label>Payment Method</label>
                <select name="payment_method">
                    <option value="">Select payment method</option>
                    <option>Cash</option>
                    <option>UPI</option>
                    <option>Debit Card</option>
                    <option>Credit Card</option>
                    <option>Bank Transfer</option>
                    <option>Other</option>
                </select>

                <label>Description</label>
                <input type="text" name="description" maxlength="200"
                       placeholder="e.g. Lunch or bus fare">

                <button type="submit">Save Expense</button>
            </form>
        </div>
        
        <div class="cards">
            <div class="panel">
                <h2>Expenses by Category</h2>
                <canvas id="categoryChart"></canvas>
            </div>

            <div class="panel">
                <h2>Monthly Expenses</h2>
                <canvas id="monthlyChart"></canvas>
            </div>
        </div>

        <h2>Recent Expenses</h2>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Category</th>
                        <th>Amount</th>
                        <th>Payment</th>
                        <th>Description</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in recent_expenses %}
                    
                     <tr>
                          <td>{{ item[1] }}</td>
                          <td>{{ item[2] }}</td>
                          <td>₹{{ "%.2f"|format(item[3]) }}</td>
                          <td>{{ item[4] or "-" }}</td>
                          <td>{{ item[5] or "-" }}</td>
                          <td>
                               <a href="{{ url_for('edit_expense', expense_id=item[0]) }}">
                                    Edit
                              </a>

                         <form action="{{ url_for('delete_expense', expense_id=item[0]) }}"
                           method="POST"
                          onsubmit="return confirm('Are you sure you want to delete this expense?');">
                         <button type="submit">Delete</button>
                        </form>
                      </td>
                  </tr>
                    {% else %}
                    <tr><td colspan="6">No expenses recorded yet.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% endif %}

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>
        const categoryLabels = {{ category_labels | tojson }};
        const categoryValues = {{ category_values | tojson }};
        const monthLabels = {{ month_labels | tojson }};
        const monthValues = {{ month_values | tojson }};

        const categoryCanvas = document.getElementById("categoryChart");

        if (categoryCanvas) {
            new Chart(categoryCanvas, {
                type: "doughnut",
                data: {
                    labels: categoryLabels,
                    datasets: [{
                        label: "Expenses",
                        data: categoryValues
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: "bottom"
                        }
                    }
                }
            });
        }

        const monthlyCanvas = document.getElementById("monthlyChart");

        if (monthlyCanvas) {
            new Chart(monthlyCanvas, {
                type: "bar",
                data: {
                    labels: monthLabels,
                    datasets: [{
                        label: "Monthly expenses (₹)",
                        data: monthValues
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
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
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Edit Expense</title>
</head>
<body>
    <h1>Edit Expense</h1>

    <form method="POST">
        <label>Amount (₹)</label><br>
        <input type="number" name="amount" min="0.01" step="0.01"
               value="{{ expense[1] }}" required><br><br>

        <label>Category</label><br>
        <select name="category_id" required>
            {% for category in categories %}
                <option value="{{ category[0] }}"
                    {% if category[0] == expense[2] %}selected{% endif %}>
                    {{ category[1] }}
                </option>
            {% endfor %}
        </select><br><br>

        <label>Expense Date</label><br>
        <input type="date" name="expense_date"
               value="{{ expense[3] }}" required><br><br>

        <label>Payment Method</label><br>
        <select name="payment_method">
            {% for method in ["Cash", "UPI", "Debit Card",
                              "Credit Card", "Bank Transfer", "Other"] %}
                <option value="{{ method }}"
                    {% if method == expense[4] %}selected{% endif %}>
                    {{ method }}
                </option>
            {% endfor %}
        </select><br><br>

        <label>Description</label><br>
        <input type="text" name="description" maxlength="200"
               value="{{ expense[5] or '' }}"><br><br>

        <button type="submit">Update Expense</button>
        <a href="{{ url_for('home') }}">Cancel</a>
    </form>
</body>
</html>
"""



@app.route("/")
def home():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            # 1. Total expenses
            cursor.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM dbo.expenses"
            )
            total_expenses = float(cursor.fetchone()[0])

            # 2. Total income
            cursor.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM dbo.income"
            )
            total_income = float(cursor.fetchone()[0])

            # 3. Recent expenses
            cursor.execute("""
                SELECT TOP 10
                    e.expense_id,
                    e.expense_date,
                    c.category_name,
                    e.amount,
                    e.payment_method,
                    e.description
                FROM dbo.expenses AS e
                LEFT JOIN dbo.categories AS c
                    ON e.category_id = c.category_id
                ORDER BY e.expense_date DESC, e.expense_id DESC
            """)

            recent_expenses = [
                (
                    row[0],
                    str(row[1]),
                    row[2] or "Uncategorized",
                    float(row[3]),
                    row[4],
                    row[5]
                )
                for row in cursor.fetchall()
            ]

            # 4. Expense form categories
            cursor.execute("""
                SELECT category_id, category_name
                FROM dbo.categories
                ORDER BY category_name
            """)
            categories = cursor.fetchall()

            # 5. Doughnut chart: expenses by category
            cursor.execute("""
                SELECT
                    c.category_name,
                    SUM(e.amount) AS category_total
                FROM dbo.expenses AS e
                INNER JOIN dbo.categories AS c
                    ON e.category_id = c.category_id
                GROUP BY c.category_id, c.category_name
                ORDER BY category_total DESC
            """)

            category_rows = cursor.fetchall()
            category_labels = [row[0] for row in category_rows]
            category_values = [float(row[1]) for row in category_rows]

            # 6. Bar chart: monthly expenses for the last 6 months
            cursor.execute("""
                SELECT
                    CONVERT(char(7), month_start, 120) AS month_label,
                    SUM(amount) AS monthly_total
                FROM (
                    SELECT
                        DATEFROMPARTS(
                            YEAR(expense_date),
                            MONTH(expense_date),
                            1
                        ) AS month_start,
                        amount
                    FROM dbo.expenses
                    WHERE expense_date >= DATEADD(
                        MONTH, -5,
                        DATEFROMPARTS(
                            YEAR(GETDATE()),
                            MONTH(GETDATE()),
                            1
                        )
                    )
                ) AS monthly_data
                GROUP BY month_start
                ORDER BY month_start
            """)

            monthly_rows = cursor.fetchall()
            month_labels = [row[0] for row in monthly_rows]
            month_values = [float(row[1]) for row in monthly_rows]

        return render_template_string(
            DASHBOARD_HTML,
            total_expenses=total_expenses,
            total_income=total_income,
            recent_expenses=recent_expenses,
            categories=categories,
            today=date.today().isoformat(),
            category_labels=category_labels,
            category_values=category_values,
            month_labels=month_labels,
            month_values=month_values,
            error=None
        )

    except Exception:
        app.logger.exception("Failed to load dashboard")
        return render_template_string(
            DASHBOARD_HTML,
            total_expenses=0,
            total_income=0,
            recent_expenses=[],
            categories=[],
            today=date.today().isoformat(),
            category_labels=[],
            category_values=[],
            month_labels=[],
            month_values=[],
            error="Could not load data. Check the Flask terminal."
        ), 500
    
@app.route("/add-expense", methods=["POST"])
def add_expense():
    try:
        amount = float(request.form["amount"])
        category_id = int(request.form["category_id"])
        expense_date = date.fromisoformat(request.form["expense_date"])
        description = request.form.get("description", "").strip()
        payment_method = request.form.get("payment_method", "").strip()

        if amount <= 0:
            flash("Amount must be greater than zero.", "error")
            return redirect(url_for("home"))

        with get_connection() as connection:
            cursor = connection.cursor()

            # Temporary single-user setup for local testing.
            cursor.execute(
                "SELECT TOP 1 user_id FROM dbo.users ORDER BY user_id"
            )
            user = cursor.fetchone()

            if not user:
                flash("Create a user account before adding expenses.", "error")
                return redirect(url_for("home"))

            cursor.execute(
                "SELECT category_id FROM dbo.categories WHERE category_id = ?",
                (category_id,)
            )
            if not cursor.fetchone():
                flash("Please select a valid category.", "error")
                return redirect(url_for("home"))

            cursor.execute("""
                INSERT INTO dbo.expenses
                    (user_id, category_id, amount, expense_date,
                     payment_method, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user[0], category_id, amount, expense_date,
                payment_method or None, description or None
            ))

        flash("Expense saved successfully.", "success")

    except (ValueError, KeyError):
        flash("Please enter valid expense details.", "error")
    except Exception:
        app.logger.exception("Failed to add expense")
        flash("Could not save expense. Check the Flask terminal.", "error")

    return redirect(url_for("home"))

    
@app.route("/edit-expense/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                "SELECT TOP 1 user_id FROM dbo.users ORDER BY user_id"
            )
            user = cursor.fetchone()

            if not user:
                flash("No user account found.", "error")
                return redirect(url_for("home"))

            user_id = user[0]

            if request.method == "POST":
                amount = float(request.form["amount"])
                category_id = int(request.form["category_id"])
                expense_date = date.fromisoformat(
                    request.form["expense_date"]
                )
                payment_method = request.form.get(
                    "payment_method", ""
                ).strip()
                description = request.form.get(
                    "description", ""
                ).strip()

                if amount <= 0:
                    flash("Amount must be greater than zero.", "error")
                    return redirect(
                        url_for("edit_expense", expense_id=expense_id)
                    )

                cursor.execute(
                    "SELECT category_id FROM dbo.categories WHERE category_id = ?",
                    (category_id,)
                )
                if not cursor.fetchone():
                    flash("Select a valid category.", "error")
                    return redirect(
                        url_for("edit_expense", expense_id=expense_id)
                    )

                cursor.execute("""
                    UPDATE dbo.expenses
                    SET category_id = ?, amount = ?, expense_date = ?,
                        payment_method = ?, description = ?
                    WHERE expense_id = ? AND user_id = ?
                """, (
                    category_id, amount, expense_date,
                    payment_method or None, description or None,
                    expense_id, user_id
                ))

                if cursor.rowcount == 0:
                    flash("Expense not found.", "error")
                else:
                    flash("Expense updated successfully.", "success")

                return redirect(url_for("home"))

            cursor.execute("""
                SELECT expense_id, amount, category_id, expense_date,
                       payment_method, description
                FROM dbo.expenses
                WHERE expense_id = ? AND user_id = ?
            """, (expense_id, user_id))

            row = cursor.fetchone()
            if not row:
                flash("Expense not found.", "error")
                return redirect(url_for("home"))

            expense = (
                row[0], float(row[1]), row[2],
                row[3].isoformat(), row[4], row[5]
            )

            cursor.execute("""
                SELECT category_id, category_name
                FROM dbo.categories
                ORDER BY category_name
            """)
            categories = cursor.fetchall()

        return render_template_string(
            EDIT_HTML, expense=expense, categories=categories
        )

    except (ValueError, KeyError):
        flash("Please enter valid expense details.", "error")
        return redirect(url_for("home"))
    except Exception:
        app.logger.exception("Failed to edit expense")
        flash("Could not edit expense. Check the Flask terminal.", "error")
        return redirect(url_for("home"))


@app.route("/delete-expense/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute(
                "SELECT TOP 1 user_id FROM dbo.users ORDER BY user_id"
            )
            user = cursor.fetchone()

            if not user:
                flash("No user account found.", "error")
                return redirect(url_for("home"))

            cursor.execute("""
                DELETE FROM dbo.expenses
                WHERE expense_id = ? AND user_id = ?
            """, (expense_id, user[0]))

            if cursor.rowcount:
                flash("Expense deleted successfully.", "success")
            else:
                flash("Expense not found.", "error")

        return redirect(url_for("home"))

    except Exception:
        app.logger.exception("Failed to delete expense")
        flash("Could not delete expense. Check the Flask terminal.", "error")
        return redirect(url_for("home"))
    
@app.route("/add-income", methods=["POST"])
def add_income():
    try:
        source = request.form.get("source", "").strip()
        amount = float(request.form["amount"])
        income_date = date.fromisoformat(request.form["income_date"])
        description = request.form.get("description", "").strip()

        if not source or amount <= 0:
            flash("Enter a valid income source and amount.", "error")
            return redirect(url_for("home"))

        with get_connection() as connection:
            cursor = connection.cursor()

            # Use the existing test user for this local project.
            cursor.execute(
                "SELECT TOP 1 user_id FROM dbo.users ORDER BY user_id"
            )
            user = cursor.fetchone()

            if not user:
                flash("Create a user account first.", "error")
                return redirect(url_for("home"))

            cursor.execute("""
                INSERT INTO dbo.income
                    (user_id, source, amount, income_date, description)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user[0],
                source,
                amount,
                income_date,
                description or None
            ))

        flash("Income saved successfully.", "success")

    except (ValueError, KeyError):
        flash("Please enter valid income details.", "error")
    except Exception:
        app.logger.exception("Failed to add income")
        flash("Could not save income. Check the Flask terminal.", "error")

    return redirect(url_for("home"))


@app.route("/reset-income", methods=["POST"])
def reset_income():
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Delete records only from dbo.income
        cursor.execute("DELETE FROM dbo.income")

        # Commit transaction only after successful deletion
        connection.commit()
        flash("All income records have been reset successfully.", "success")

    except Exception:
        # Roll back transaction on error
        if connection:
            try:
                connection.rollback()
            except Exception:
                pass
        app.logger.exception("Failed to reset income")
        flash("Could not reset income. Check the Flask terminal.", "error")
    finally:
        if connection:
            connection.close()

    return redirect(url_for("home"))




if __name__ == "__main__":
    app.run(debug=True)
