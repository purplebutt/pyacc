import pandas as pd
import datetime as dt
import calendar as cld


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

def splitdata(all:pd.DataFrame):
    """
    split data by month
    """
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

def get_eom(df:pd.DataFrame) -> dt.datetime:
    base_date = df.loc[:,"Date"].iloc[0]
    calendar = cld.monthrange(base_date.year, base_date.month) 
    eom = dt.datetime(year=base_date.year, month=base_date.month, day=calendar[1])
    return eom

def mixdata():
    pandas_option(pd)
    x = read_data(SHEET_NAME)
    x = combine_data(x)
    x = fixed_data(x)
    return x

def make_closing(data):
    v = calc_il(data)   # ? get net income
    per = get_eom(data)    # ? get end of month date (because Net/Los summary entry always use end month date)
    closing = pd.DataFrame([
        [9999, "helper", "IS", "Net/Loss - Summary", "D", "HELPER", per, "Net/Loss-Summary", per.month, v[0]],
        [3999, "helper", "IS", "Net/Loss - Summary", "C", "HELPER", per, "Net/Loss-Summary", per.month, v[1]]
    ], columns=["index", "Group", "Report", "Account Name", "Normal", "Header", "Date", "Description", "month", "amount"])
    x = pd.concat([data, closing])
    return x


#! program main entrance
if __name__ == '__main__':
    md = mixdata()
    sd = splitdata(md) 
    for k, v in sd.items():
        v = make_closing(v)
        print("======================")
        print(v)
