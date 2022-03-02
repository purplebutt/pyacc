import pandas as pd
import datetime as dt


# constants
XL_FILE = "jurnal.xls"
SHEET_NAME = ["COA", "JURNAL"]

def pandas_option(pd_obj):
    pd_obj.set_option("display.max_columns", None)
    pd_obj.set_option("display.width", None)

def dt_by_month(all:pd.DataFrame):
    result = {}
    for d in all["month"].unique():
        result[d] = all.loc[all.month==d]
    return result

def read_data(sheet_name) -> (pd.DataFrame, pd.DataFrame):
    jurnal = pd.read_excel(XL_FILE, sheet_name=sheet_name[1])
    coa = pd.read_excel(XL_FILE, sheet_name=sheet_name[0])
    return (jurnal, coa)

def combine_data(data: (pd.DataFrame, pd.DataFrame)) -> pd.DataFrame:
    all = pd.DataFrame.join(self=data[0].set_index("Acc Number"), other=data[1].set_index("Acc Num"), how="left")
    all["month"] = all["Date"].dt.month
    all["amount"] = all["DEBIT"]-all["CREDIT"]
    return all

def run():
    # pandas_option(pd)
    # jurnal = pd.read_excel(XL_FILE, sheet_name=SHEET_NAME[1])
    # coa = pd.read_excel(XL_FILE, sheet_name=SHEET_NAME[0])
    # * read data
    dt_tup=read_data(SHEET_NAME)
    # all = pd.DataFrame.join(self=jurnal.set_index("Acc Number"), other=coa.set_index("Acc Num"), how="left")
    # all["month"] = all["Date"].dt.month
    # all["amount"] = all["DEBIT"]-all["CREDIT"]
    all=combine_data(dt_tup)

    x = dt_by_month(all)  # parse transactions data into dictionary
    for i in range(len(x)):
        x[i+1] = x[i+1].groupby("Account Name").sum()
        x[i+1] = x[i+1].join(other=dt_tup[1].set_index("Account Name"), how="left", rsuffix="coa")
        x[i+1].drop(columns=["month", "Normal","DEBIT", "CREDIT"], inplace=True)
        pd.DataFrame.sort_values(x[i+1], "Acc Num", inplace=True)
        pd.DataFrame.reset_index(self=x[i+1],inplace=True)
        pd.DataFrame.set_index(self=x[i+1], keys="Acc Num", inplace=True)
        new_clm_order = ["Group", "Header", "Account Name", "amount"]
        x[i+1] = x[i+1].reindex(columns=new_clm_order)
    return x

#! program main entrance
if __name__ == '__main__':
    x=run()
    print_result(x)