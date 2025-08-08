# TBudget

A terminal budget tracker with rich UI, budget alerts, recurring transactions, sparklines, and interactive shell.

## Features

- **Expense & Income Tracking**: Log categorized expenses and income.
- **Budget Limits & Alerts 🚨**: Set monthly and per-category budgets. Get warnings when you approach or exceed them.
- **Recurring Transactions 🔁**: Auto-log regular expenses/income (e.g., rent, subscriptions) on a schedule.
- **Graphs & Sparklines 📈**: See trends in your spending with sparklines in the summary.
- **Interactive Mode 🤖**: `tbudget shell` drops you into a REPL for fast entry and queries.
- **Rich UI**: Beautiful tables, colored output, and warnings using [Rich](https://github.com/Textualize/rich).

## Installation
### Method 1: Running the script
1. Clone this repo.
2. Install dependencies:
   ```
   pip install rich
   ```
3. Run with:
   ```
   python main.py [command]
   ```
### Method 2: Using the binary
1. Download the binary from the releases page
2. Run it from the terminal

## Usage

### Add Records

```sh
python main.py add-expense 12.5 food --note "Lunch"
python main.py add-income 1000 salary --note "Paycheck"
```

### Set Budgets

```sh
python main.py set-budget --monthly 500
python main.py set-budget --category food --amount 200
```

### Show Budgets

```sh
python main.py show-budgets
```

### Add Recurring Transactions

```sh
python main.py add-recurring expense 100 rent "Monthly rent" 1
python main.py add-recurring income 2000 salary "Monthly salary" 1
```

### Show Recurring Transactions

```sh
python main.py show-recurring
```

### List Records (with filters)

```sh
python main.py list --type expense --category food --from 2024-01-01 --min-amount 10
```

### Summary (with trends and filters)

```sh
python main.py summary --type expense --category food
```

### Interactive Shell

```sh
python main.py shell
```
Then type commands like:
```
> add-expense 5 coffee --note "Morning"
> summary
> set-budget --monthly 300
> exit
```

### Help

```sh
python main.py help
```

## Budget Alerts

- When you approach or exceed your monthly or category budget, you'll see a warning in red.

## Recurring Transactions

- Add recurring expenses/income with `add-recurring`.
- Each time you run TBudget, it checks if a recurring transaction is due and logs it automatically.

## Graphs & Sparklines

- The summary table includes a trend column with a sparkline or ASCII bar showing monthly totals.

## Data Files

- Records: `records.csv`
- Budgets: `budgets.json`
- Recurring: `recurring.json`

---

**TBudget** is a CLI tool for people who want a fast, powerful, and beautiful budget tracker in their terminal.
