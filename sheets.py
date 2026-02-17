import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import SPREADSHEET_ID

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)

def get_list(col_letter):
    sheet = spreadsheet.worksheet("Списки")
    col = ord(col_letter.upper()) - 64
    return [v for v in sheet.col_values(col)[1:] if v]

def append_income(row):
    sheet = spreadsheet.worksheet("Приходы")
    sheet.append_row([""] + row)
