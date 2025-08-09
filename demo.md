# TBudget Demo Commands

Below is a list of commands you can use to demo TBudget's features. Run each command in your terminal from the project directory.

## Add Expense & Income

- `python main.py add-expense 12.5 food --note "Lunch"`
- `python main.py add-income 1000 salary --note "Paycheck"`

## List Records

- `python main.py list`
- `python main.py list --type expense`
- `python main.py list --category food`

## Summary

- `python main.py summary`
- `python main.py summary --type expense`
- `python main.py summary --category food`

## Graphs

- `python main.py graph`
- `python main.py graph --type expense`
- `python main.py graph --by category`

## Set Budgets

- `python main.py set-budget --monthly 500`
- `python main.py set-budget --category food --amount 200`
- `python main.py show-budgets`

## Recurring Transactions

- `python main.py add-recurring expense 50 food "Monthly food" 1`
- `python main.py show-recurring`

## Delete/Edit Records

- `python main.py list`
- `python main.py delete 1`
- `python main.py edit 2 note "Updated note"`
- `python main.py rm 2`
- `python main.py mod 1 category "groceries"`

## Search Records

- `python main.py search Lunch`
- `python main.py find Paycheck`

## Currency Conversion

- `python main.py convert-currency 100 USD EUR`

## AI Assistant

- `python main.py ai-assistant message "How much did I spend on food last month?"`

## Shell Mode

- `python main.py shell`
  - Then try:
    - `add-expense 5 snack --note "Chips"`
    - `list`
    - `help`
    - `exit`

## Help

- `python main.py help`