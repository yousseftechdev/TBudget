# TBudget Test Commands

## 1. Add Expense & Income
```
python main.py add-expense 12.5 food --note "Lunch"
python main.py add-income 1000 salary --note "Paycheck"
```

## 2. List Records
```
python main.py list
python main.py list --type expense
python main.py list --category food
```

## 3. Summary
```
python main.py summary
python main.py summary --type expense
python main.py summary --category food
```

## 4. Graphs
```
python main.py graph
python main.py graph --type expense
python main.py graph --by category
```

## 5. Set Budgets
```
python main.py set-budget --monthly 500
python main.py set-budget --category food --amount 200
python main.py show-budgets
```

## 6. Recurring Transactions
```
python main.py add-recurring expense 50 food "Monthly food" 1
python main.py show-recurring
```

## 7. Delete/Edit Records
```
python main.py list
python main.py delete 1
python main.py edit 2 note "Updated note"
python main.py rm 2
python main.py mod 1 category "groceries"
```

## 8. Search Records
```
python main.py search Lunch
python main.py find Paycheck
```

## 9. Password Protection
```
python main.py set-password
# Restart app and try any command to check password prompt
```

## 10. Shell Mode
```
python main.py shell
# Then try: add-expense 5 snack --note "Chips"
#           list
#           help
#           exit
```

## 11. Help