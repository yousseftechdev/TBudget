import csv, sys, os, json
from argparse import ArgumentParser
from datetime import datetime, date
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich import box
from rich.prompt import Prompt
from rich.live import Live
from rich.progress import BarColumn, Progress
from rich.text import Text
import shlex

console = Console()

CSV_FILE = "records.csv"
BUDGET_FILE = "budgets.json"
RECUR_FILE = "recurring.json"
FIELDS = ["datetime", "type", "amount", "category", "note"]
PASSWORD_FILE = "password.txt"

def ensure_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(FIELDS)

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        try:
            return json.load(f)
        except Exception:
            return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def get_month(dt):
    return dt.strftime("%Y-%m")

def check_budgets(amount, category, dt, budgets):
    alerts = []
    month = get_month(dt)
    # Monthly total
    monthly_total = 0
    cat_total = 0
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE) as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    rdt = datetime.fromisoformat(row["datetime"])
                    if get_month(rdt) == month and row["type"] == "expense":
                        monthly_total += float(row["amount"])
                        if row["category"] == category:
                            cat_total += float(row["amount"])
                except Exception:
                    continue
    # Check monthly
    if "monthly" in budgets:
        limit = budgets["monthly"]
        if monthly_total + amount > limit:
            alerts.append(f"[bold red]🚨 Monthly budget exceeded! ({monthly_total+amount:.2f}/{limit})[/]")
        elif monthly_total + amount > 0.9 * limit:
            alerts.append(f"[red]⚠️ Near monthly budget! ({monthly_total+amount:.2f}/{limit})[/]")
    # Check category
    if "categories" in budgets and category in budgets["categories"]:
        limit = budgets["categories"][category]
        if cat_total + amount > limit:
            alerts.append(f"[bold red]🚨 {category} budget exceeded! ({cat_total+amount:.2f}/{limit})[/]")
        elif cat_total + amount > 0.9 * limit:
            alerts.append(f"[red]⚠️ Near {category} budget! ({cat_total+amount:.2f}/{limit})[/]")
    return alerts

def add_record(rec_type: str, amount: float, category: str, note: str):
    ensure_csv()
    dt = datetime.now()
    budgets = load_json(BUDGET_FILE, {})
    alerts = []
    if rec_type == "expense":
        alerts = check_budgets(amount, category, dt, budgets)
    try:
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([dt.isoformat(), rec_type, amount, category, note])
        emoji = "💸" if rec_type == "expense" else "💰"
        console.print(f"{emoji} Logged {amount} as [bold]{rec_type}[/] in [bold]{category}[/]")
        for alert in alerts:
            console.print(alert)
    except Exception as e:
        console.print(f"[red]Error logging record: {e}[/]")

def set_budget(monthly=None, category=None, amount=None):
    budgets = load_json(BUDGET_FILE, {})
    if monthly is not None:
        budgets["monthly"] = monthly
        console.print(f"[green]Set monthly budget to {monthly}[/]")
    if category and amount is not None:
        if "categories" not in budgets:
            budgets["categories"] = {}
        budgets["categories"][category] = amount
        console.print(f"[green]Set budget for [bold]{category}[/] to {amount}[/]")
    save_json(BUDGET_FILE, budgets)

def show_budgets():
    budgets = load_json(BUDGET_FILE, {})
    table = Table(title="Budgets", box=box.ROUNDED)
    table.add_column("Type")
    table.add_column("Category")
    table.add_column("Limit", justify="right")
    if "monthly" in budgets:
        table.add_row("Monthly", "-", str(budgets["monthly"]))
    if "categories" in budgets:
        for cat, amt in budgets["categories"].items():
            table.add_row("Category", cat, str(amt))
    console.print(table)

def add_recurring(rec_type, amount, category, note, day):
    recurs = load_json(RECUR_FILE, [])
    recurs.append({
        "type": rec_type,
        "amount": amount,
        "category": category,
        "note": note,
        "day": day
    })
    save_json(RECUR_FILE, recurs)
    console.print(f"[green]Added recurring {rec_type} of {amount} in {category} on day {day}[/]")

def process_recurring():
    recurs = load_json(RECUR_FILE, [])
    today = date.today()
    ensure_csv()
    added = 0
    for recur in recurs:
        try:
            recur_day = int(recur["day"])
            if today.day == recur_day:
                already = False
                with open(CSV_FILE) as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        rdt = datetime.fromisoformat(row["datetime"])
                        if (rdt.date() == today and
                            row["type"] == recur["type"] and
                            row["category"] == recur["category"] and
                            float(row["amount"]) == float(recur["amount"]) and
                            row["note"] == recur["note"]):
                            already = True
                            break
                if not already:
                    add_record(recur["type"], float(recur["amount"]), recur["category"], recur["note"])
                    added += 1
        except Exception:
            continue
    if added:
        console.print(f"[cyan]{added} recurring transactions processed.[/]")

def summary(filter_type=None, filter_category=None, date_from=None, date_to=None):
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
                if filter_type and row["type"] != filter_type:
                    continue
                if filter_category and row["category"] != filter_category:
                    continue
                if date_from or date_to:
                    try:
                        dt = datetime.fromisoformat(row["datetime"])
                    except Exception:
                        continue
                    if date_from and dt < date_from:
                        continue
                    if date_to and dt > date_to:
                        continue
                key = (row["type"], row["category"])
                totals[key] = totals.get(key, 0) + float(row["amount"])
        for (typ, cat), tot in sorted(totals.items()):
            table.add_row(typ, cat, f"{tot:.2f}")
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error reading summary: {e}[/]")

def graph(filter_type=None, filter_category=None, by="month"):
    ensure_csv()
    # Default to "expense" if no type is specified
    if filter_type is None:
        filter_type = "expense"
    if by == "category":
        # Aggregate by category
        cat_totals = {}
        try:
            with open(CSV_FILE) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if filter_type and row["type"] != filter_type:
                        continue
                    if filter_category and row["category"] != filter_category:
                        continue
                    cat = row["category"]
                    cat_totals[cat] = cat_totals.get(cat, 0) + float(row["amount"])
            if not cat_totals:
                console.print("[yellow]No data to graph.[/]")
                return
            max_val = max(cat_totals.values())
            bar_width = 40
            console.print(f"[bold cyan]Totals by category for type={filter_type}[/bold cyan]")
            for cat, v in sorted(cat_totals.items(), key=lambda x: -x[1]):
                bar_len = int((v / max_val) * bar_width) if max_val > 0 else 0
                bar = "█" * bar_len
                console.print(f"{cat:15} | {bar} {v:.2f}")
        except Exception as e:
            console.print(f"[red]Error generating graph: {e}[/]")
    else:
        # Aggregate by month (default)
        monthly = {}
        try:
            with open(CSV_FILE) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if filter_type and row["type"] != filter_type:
                        continue
                    if filter_category and row["category"] != filter_category:
                        continue
                    try:
                        dt = datetime.fromisoformat(row["datetime"])
                    except Exception:
                        continue
                    month = dt.strftime("%Y-%m")
                    monthly[month] = monthly.get(month, 0) + float(row["amount"])
            if not monthly:
                console.print("[yellow]No data to graph.[/]")
                return
            # Sort months
            months = sorted(monthly.keys())
            vals = [monthly[m] for m in months]
            max_val = max(vals)
            bar_width = 40
            console.print(f"[bold cyan]Monthly totals for type={filter_type}, category={filter_category or 'any'}[/bold cyan]")
            for m in months:
                v = monthly[m]
                bar_len = int((v / max_val) * bar_width) if max_val > 0 else 0
                bar = "█" * bar_len
                console.print(f"{m} | {bar} {v:.2f}")
        except Exception as e:
            console.print(f"[red]Error generating graph: {e}[/]")

def list_records(filter_type=None, filter_category=None, date_from=None, date_to=None, min_amount=None, max_amount=None):
    ensure_csv()
    table = Table(title="All Records", box=box.SIMPLE_HEAVY)
    for field in FIELDS:
        table.add_column(field.capitalize())
    try:
        with open(CSV_FILE) as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Filtering
                if filter_type and row["type"] != filter_type:
                    continue
                if filter_category and row["category"] != filter_category:
                    continue
                if date_from or date_to:
                    try:
                        dt = datetime.fromisoformat(row["datetime"])
                    except Exception:
                        continue
                    if date_from and dt < date_from:
                        continue
                    if date_to and dt > date_to:
                        continue
                try:
                    amt = float(row["amount"])
                except Exception:
                    continue
                if min_amount is not None and amt < min_amount:
                    continue
                if max_amount is not None and amt > max_amount:
                    continue
                color = "red" if row["type"] == "expense" else "green"
                try:
                    dt_disp = datetime.fromisoformat(row["datetime"]).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    dt_disp = row["datetime"]
                table.add_row(
                    dt_disp,
                    f"[{color}]{row['type']}[/{color}]",
                    row["amount"],
                    row["category"],
                    row["note"]
                )
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error listing records: {e}[/]")

def delete_record(record_id):
    ensure_csv()
    rows = []
    deleted = False
    with open(CSV_FILE) as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            if i == record_id:
                deleted = True
                continue
            rows.append(row)
    if deleted:
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        console.print(f"[green]Deleted record #{record_id}.[/]")
    else:
        console.print(f"[red]Record #{record_id} not found.[/]")

def edit_record(record_id, field, value):
    ensure_csv()
    rows = []
    edited = False
    with open(CSV_FILE) as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            if i == record_id:
                if field in FIELDS:
                    row[field] = value
                    edited = True
            rows.append(row)
    if edited:
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        console.print(f"[green]Edited record #{record_id}: set {field} to {value}.[/]")
    else:
        console.print(f"[red]Record #{record_id} not found or invalid field.[/]")

def search_records(keyword):
    ensure_csv()
    table = Table(title=f"Search Results for '{keyword}'", box=box.SIMPLE_HEAVY)
    for field in FIELDS:
        table.add_column(field.capitalize())
    found = False
    with open(CSV_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if any(keyword.lower() in str(row[field]).lower() for field in FIELDS):
                found = True
                color = "red" if row["type"] == "expense" else "green"
                try:
                    dt_disp = datetime.fromisoformat(row["datetime"]).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    dt_disp = row["datetime"]
                table.add_row(
                    dt_disp,
                    f"[{color}]{row['type']}[/{color}]",
                    row["amount"],
                    row["category"],
                    row["note"]
                )
    if found:
        console.print(table)
    else:
        console.print(f"[yellow]No records found for '{keyword}'.[/]")

def help_cmd():
    help_text = """
[bold cyan]TBudget Help[/bold cyan]

[bold]Commands:[/bold]
  add-expense [amount] [category] [--note NOTE]   Add an expense
  add-income  [amount] [category] [--note NOTE]   Add an income
  summary [filters]                               Show summary by category and type
  list [filters]                                  List all records (with filters)
  graph [--type TYPE] [--category CAT] [--by BY]  Show bar graph by month or category
  set-budget --monthly AMOUNT                     Set monthly budget
  set-budget --category CAT --amount AMOUNT       Set category budget
  show-budgets                                    Show all budgets
  add-recurring [expense|income] AMOUNT CAT NOTE DAY  Add recurring transaction (day=1-31)
  show-recurring                                  List recurring transactions
  delete [record_id]                              Delete a record by its number (see list)
  edit [record_id] [field] [value]                Edit a record field by its number
  search [keyword]                                Search records by keyword
  shell                                           Enter interactive mode
  help                                            Show this help message

[bold]Aliases:[/bold]
  rm = delete
  mod = edit
  find = search

[bold]Filters:[/bold]
  --type [expense|income]      Filter by record type
  --category CATEGORY          Filter by category
  --by [month|category]        Graph by month (default) or by category
  --from YYYY-MM-DD            Filter from date
  --to YYYY-MM-DD              Filter to date
  --min-amount AMOUNT          Minimum amount
  --max-amount AMOUNT          Maximum amount

[bold]Examples:[/bold]
  tbudget add-expense 12.5 food --note "Lunch"
  tbudget add-income 1000 salary --note "Paycheck"
  tbudget set-budget --monthly 500
  tbudget set-budget --category food --amount 200
  tbudget add-recurring expense 100 rent "Monthly rent" 1
  tbudget summary --type expense --category food
  tbudget graph --type expense --category food
  tbudget graph --type expense --by category
  tbudget list --min-amount 10 --from 2024-01-01
  tbudget delete 3
  tbudget edit 2 note "Corrected note"
  tbudget search lunch
  tbudget shell
"""
    console.print(Panel(help_text, title="TBudget Help", style="green"))

def show_recurring():
    recurs = load_json(RECUR_FILE, [])
    table = Table(title="Recurring Transactions", box=box.ROUNDED)
    table.add_column("Type")
    table.add_column("Amount")
    table.add_column("Category")
    table.add_column("Note")
    table.add_column("Day")
    for r in recurs:
        table.add_row(r["type"], str(r["amount"]), r["category"], r["note"], str(r["day"]))
    console.print(table)

class RichArgumentParser(ArgumentParser):
    def error(self, message):
        console.print(f"[bold red]Error:[/] {message}")
        sys.exit(2)

def shell():
    console.print(Panel("[bold cyan]Welcome to TBudget Shell![/bold cyan]\nType 'help' for commands, 'exit' to quit.\nType 'clear' to clear the screen.", style="blue"))
    while True:
        try:
            cmd = Prompt.ask("[bold green]>[/bold green]")
            if cmd.strip() in ("exit", "quit"):
                break
            if cmd.strip() == "clear":
                console.clear()
                continue
            if not cmd.strip():
                continue
            args = shlex.split(cmd)  # Use shlex.split for proper argument parsing
            # Simulate sys.argv
            try:
                main(args, shell_mode=True)
            except SystemExit:
                # Don't exit the shell on error
                continue
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            console.print(f"[red]Shell error: {e}[/]")

def main(argv=None, shell_mode=False):
    process_recurring()
    p = RichArgumentParser(prog="TBudget", add_help=False)
    sub = p.add_subparsers(dest="cmd")
    a1 = sub.add_parser("add-expense")
    a1.add_argument("amount", type=float)
    a1.add_argument("category")
    a1.add_argument("--note", default="")
    a2 = sub.add_parser("add-income")
    a2.add_argument("amount", type=float)
    a2.add_argument("category")
    a2.add_argument("--note", default="")
    s = sub.add_parser("summary")
    s.add_argument("--type", choices=["expense", "income"], help="Filter by record type")
    s.add_argument("--category", help="Filter by category")
    s.add_argument("--from", dest="date_from", help="Filter from date (YYYY-MM-DD)")
    s.add_argument("--to", dest="date_to", help="Filter to date (YYYY-MM-DD)")
    l = sub.add_parser("list")
    l.add_argument("--type", choices=["expense", "income"], help="Filter by record type")
    l.add_argument("--category", help="Filter by category")
    l.add_argument("--from", dest="date_from", help="Filter from date (YYYY-MM-DD)")
    l.add_argument("--to", dest="date_to", help="Filter to date (YYYY-MM-DD)")
    l.add_argument("--min-amount", type=float, help="Show only records with amount >= this value")
    l.add_argument("--max-amount", type=float, help="Show only records with amount <= this value")
    g = sub.add_parser("graph")
    g.add_argument("--type", choices=["expense", "income"], help="Filter by record type")
    g.add_argument("--category", help="Filter by category")
    g.add_argument("--by", choices=["month", "category"], default="month", help="Graph by month or by category")
    sb = sub.add_parser("set-budget")
    sb.add_argument("--monthly", type=float, help="Set monthly budget")
    sb.add_argument("--category", help="Set category budget")
    sb.add_argument("--amount", type=float, help="Budget amount for category")
    sub.add_parser("show-budgets")
    ar = sub.add_parser("add-recurring")
    ar.add_argument("type", choices=["expense", "income"])
    ar.add_argument("amount", type=float)
    ar.add_argument("category")
    ar.add_argument("note")
    ar.add_argument("day", type=int, help="Day of month (1-31)")
    sub.add_parser("show-recurring")
    sub.add_parser("shell")
    sub.add_parser("help")
    sub.add_parser("delete").add_argument("record_id", type=int)
    sub.add_parser("rm").add_argument("record_id", type=int)  # Alias
    e = sub.add_parser("edit")
    e.add_argument("record_id", type=int)
    e.add_argument("field")
    e.add_argument("value")
    me = sub.add_parser("mod")
    me.add_argument("record_id", type=int)
    me.add_argument("field")
    me.add_argument("value")
    sub.add_parser("search").add_argument("keyword")
    sub.add_parser("find").add_argument("keyword")
    if argv is None:
        argv = sys.argv[1:]
    args = p.parse_args(argv)

    if args.cmd == "add-expense":
        add_record("expense", args.amount, args.category, args.note)
    elif args.cmd == "add-income":
        add_record("income", args.amount, args.category, args.note)
    elif args.cmd == "summary":
        date_from = datetime.fromisoformat(args.date_from) if args.date_from else None
        date_to = datetime.fromisoformat(args.date_to) if args.date_to else None
        summary(
            filter_type=args.type,
            filter_category=args.category,
            date_from=date_from,
            date_to=date_to,
        )
    elif args.cmd == "list":
        date_from = datetime.fromisoformat(args.date_from) if args.date_from else None
        date_to = datetime.fromisoformat(args.date_to) if args.date_to else None
        list_records(
            filter_type=args.type,
            filter_category=args.category,
            date_from=date_from,
            date_to=date_to,
            min_amount=args.min_amount,
            max_amount=args.max_amount,
        )
    elif args.cmd == "graph":
        graph(
            filter_type=args.type,
            filter_category=args.category,
            by=args.by,
        )
    elif args.cmd == "set-budget":
        if args.monthly is not None:
            set_budget(monthly=args.monthly)
        elif args.category and args.amount is not None:
            set_budget(category=args.category, amount=args.amount)
        else:
            console.print("[red]Specify --monthly or both --category and --amount[/]")
    elif args.cmd == "show-budgets":
        show_budgets()
    elif args.cmd == "add-recurring":
        add_recurring(args.type, args.amount, args.category, args.note, args.day)
    elif args.cmd == "show-recurring":
        show_recurring()
    elif args.cmd == "shell":
        shell()
    elif args.cmd == "help" or args.cmd is None:
        help_cmd()
    elif args.cmd in ("delete", "rm"):
        delete_record(args.record_id)
    elif args.cmd in ("edit", "mod"):
        edit_record(args.record_id, args.field, args.value)
    elif args.cmd in ("search", "find"):
        search_records(args.keyword)
    elif shell_mode:
        console.print("[red]Unknown command.[/]")

if __name__ == "__main__":
    main()