import csv, sys, os
from argparse import ArgumentParser
from datetime import datetime
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()

CSV_FILE = "records.csv"
FIELDS = ["datetime", "type", "amount", "category", "note"]

def ensure_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(FIELDS)

def add_record(rec_type: str, amount: float, category: str, note: str):
    ensure_csv()
    try:
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().isoformat(), rec_type, amount, category, note])
        emoji = "💸" if rec_type == "expense" else "💰"
        console.print(f"{emoji} Logged {amount} as [bold]{rec_type}[/] in [bold]{category}[/]")
    except Exception as e:
        console.print(f"[red]Error logging record: {e}[/]")

def summary():
    ensure_csv()
    table = Table(title="Summary by Category & Type", box=box.ROUNDED, style="cyan")
    table.add_column("Type", style="bold")
    table.add_column("Category")
    table.add_column("Total", justify="right")
    totals = {}
    try:
        with open(CSV_FILE) as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["type"], row["category"])
                totals[key] = totals.get(key, 0) + float(row["amount"])
        for (typ, cat), tot in sorted(totals.items()):
            table.add_row(typ, cat, f"{tot:.2f}")
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error reading summary: {e}[/]")

def list_records():
    ensure_csv()
    table = Table(title="All Records", box=box.SIMPLE_HEAVY)
    for field in FIELDS:
        table.add_column(field.capitalize())
    try:
        with open(CSV_FILE) as f:
            reader = csv.DictReader(f)
            for row in reader:
                color = "red" if row["type"] == "expense" else "green"
                table.add_row(
                    row["datetime"], 
                    f"[{color}]{row['type']}[/{color}]",
                    row["amount"], 
                    row["category"], 
                    row["note"]
                )
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error listing records: {e}[/]")

def help_cmd():
    help_text = """
[bold cyan]TBudget Help[/bold cyan]

[bold]Commands:[/bold]
  add-expense [amount] [category] [--note NOTE]   Add an expense
  add-income  [amount] [category] [--note NOTE]   Add an income
  summary                                         Show summary by category and type
  list                                            List all records
  help                                            Show this help message

[bold]Examples:[/bold]
  tbudget add-expense 12.5 food --note "Lunch"
  tbudget add-income 1000 salary --note "Paycheck"
  tbudget summary
  tbudget list
"""
    console.print(Panel(help_text, title="TBudget Help", style="magenta"))

def main():
    p = ArgumentParser(prog="TBudget", add_help=False)
    sub = p.add_subparsers(dest="cmd")
    a1 = sub.add_parser("add-expense")
    a1.add_argument("amount", type=float)
    a1.add_argument("category")
    a1.add_argument("--note", default="")
    a2 = sub.add_parser("add-income")
    a2.add_argument("amount", type=float)
    a2.add_argument("category")
    a2.add_argument("--note", default="")
    sub.add_parser("summary")
    sub.add_parser("list")
    sub.add_parser("help")
    args = p.parse_args()

    if args.cmd == "add-expense":
        add_record("expense", args.amount, args.category, args.note)
    elif args.cmd == "add-income":
        add_record("income", args.amount, args.category, args.note)
    elif args.cmd == "summary":
        summary()
    elif args.cmd == "list":
        list_records()
    elif args.cmd == "help" or args.cmd is None:
        help_cmd()
    else:
        console.print("[red]Unknown command. Use 'help' for usage.[/]")
        sys.exit(1)

if __name__ == "__main__":
    main()