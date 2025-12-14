class Company:
    def __init__(self, symbol, name):
        self.symbol = symbol
        self.name = name


class FinancialStatement:
    def __init__(self, company, year, income_statement, balance_sheet, cash_flow_statement):
        self.company = company
        self.year = year
        self.income_statement = income_statement
        self.balance_sheet = balance_sheet
        self.cash_flow_statement = cash_flow_statement


class IncomeStatement:
    def __init__(self, revenue, gross_profit, operating_income, net_income):
        self.revenue = revenue
        self.gross_profit = gross_profit
        self.operating_income = operating_income
        self.net_income = net_income


class BalanceSheet:
    def __init__(self, total_assets, total_liabilities, shareholders_equity):
        self.total_assets = total_assets
        self.total_liabilities = total_liabilities
        self.shareholders_equity = shareholders_equity


class CashFlowStatement:
    def __init__(self, operating_cash_flow, investing_cash_flow, financing_cash_flow):
        self.operating_cash_flow = operating_cash_flow
        self.investing_cash_flow = investing_cash_flow
        self.financing_cash_flow = financing_cash_flow