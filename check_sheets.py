import pandas as pd
path = r"c:\Users\MSI\Desktop\FinanceETLHub\online+retail\Online Retail.xlsx"
xl = pd.ExcelFile(path)
print(xl.sheet_names)
