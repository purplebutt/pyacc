import pandas as pd
import datetime as dt


# constants
XL_FILE = "jurnal.xls"
XL_CT = "closing_template.xls"
SHEET_NAME = ["AG", "COA", "JURNAL"]

def pandas_option(pd_obj):
    pd_obj.set_option("display.max_columns", None)
    pd_obj.set_option("display.width", None)

def read_data(sheet_name) -> (pd.DataFrame, pd.DataFrame):
    je = pd.read_excel(XL_FILE, sheet_name=sheet_name[2])
    coa = pd.read_excel(XL_FILE, sheet_name=sheet_name[1])
    ag = pd.read_excel(XL_FILE, sheet_name=sheet_name[0])
    return (ag, coa, je)

def split_by_month(all:pd.DataFrame):
    result = {}
    for d in all["month"].unique():
        result[d] = all.loc[all.month==d]
    return result

def combine_data(data: (pd.DataFrame, pd.DataFrame, pd.DataFrame)) -> pd.DataFrame:
    ag_coa = pd.DataFrame.join(self=data[0].set_index("Code"), other=data[1].set_index("Group"), how="left")
    all = pd.DataFrame.join(self=ag_coa.set_index("Acc Num"), other=data[2].set_index("Acc Number"), how="right")
    all = pd.DataFrame.reset_index(all)
    return all

def fixed_data(data: pd.DataFrame):
    # -> Add additional fields
    data["month"] = data["Date"].dt.month
    data["amount"] = data["DEBIT"]-data["CREDIT"]
    # -> Remove unnecessary fields
    pd.DataFrame.drop(data, columns=["DEBIT", "CREDIT"], inplace=True)
    return data

def calc_il(data: pd.DataFrame) -> (int, int):
    x = data.groupby(by=["Report"]).sum()
    return (x.iloc[0,2], x.iloc[1,2])


def run():
    pandas_option(pd)
    x = read_data(SHEET_NAME)
    x = combine_data(x)
    x = fixed_data(x)
    return x


def make_closing(data, date=None):
    v = calc_il(data)   # ? get net income
    # -> Update juga data bulan dan tanggal yang masih kosong
    closing = pd.DataFrame([
        [9999, "helper", "IS", "Net/Loss - Summary", "D", "HELPER", "", "Net/Loss-Summary", 1, v[0]],
        [3999, "helper", "IS", "Net/Loss - Summary", "C", "HELPER", "", "Net/Loss-Summary", 1, v[1]]
    ], columns=["index", "Group", "Report", "Account Name", "Normal", "Header", "Date", "Description", "month", "amount"])
    x = pd.concat([data, closing])
    return x


#! program main entrance
if __name__ == '__main__':
    x = run()
    sd = split_by_month(x)
    for k, v in sd.items():
        print(f"Period: {k}")
        v = make_closing(v)
        print("======================")
        print(v)