import pandas as pd
import os

path1 = r"c:\Users\MSI\Desktop\FinanceETLHub\data\raw\online_retail.xlsx"
path2 = r"c:\Users\MSI\Desktop\FinanceETLHub\online+retail\Online Retail.xlsx"

def check_file(path):
    if os.path.exists(path):
        df = pd.read_excel(path)
        return df['InvoiceDate'].min(), df['InvoiceDate'].max(), len(df)
    return None

print(f"File 1: {check_file(path1)}")
print(f"File 2: {check_file(path2)}")
