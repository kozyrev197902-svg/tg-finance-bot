import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import date

from config import BOT_TOKEN, SALON_REQUIRED_FOR
from sheets import get_list, append_income

class IncomeState(StatesGroup):
    date = State()
    target = State()
    amount = State()
    income_type = State()
    order = State()
    comment = State()
    salon = State()

def kb(values=None, extra=None):
    buttons = []
    if values:
        buttons += [[KeyboardButton(text=v)] for v in values]
    if extra:
        buttons.append([KeyboardButton(text=extra)])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(F.text == "/start")
async def start(msg: Message):
    await msg.answer("Выберите действие", reply_markup=kb(["➕ Приход"]))

@dp.message(F.text == "➕ Приход")
async def start_income(msg: Message, state: FSMContext):
    today = date.today().strftime("%d.%m.%Y")
    await state.update_data(date=today)
    await msg.answer(f"📅 Дата прихода: {today}", reply_markup=kb(["Сегодня"]))
    await state.set_state(IncomeState.date)

@dp.message(IncomeState.date)
async def income_date(msg: Message, state: FSMContext):
    d = date.today().strftime("%d.%m.%Y") if msg.text == "Сегодня" else msg.text
    await state.update_data(date=d)
    await msg.answer("Куда приход?", reply_markup=kb(get_list("A")))
    await state.set_state(IncomeState.target)

@dp.message(IncomeState.target)
async def income_target(msg: Message, state: FSMContext):
    await state.update_data(target=msg.text)
    await msg.answer("Введите сумму")
    await state.set_state(IncomeState.amount)

@dp.message(IncomeState.amount)
async def income_amount(msg: Message, state: FSMContext):
    await state.update_data(amount=msg.text.replace(" ", ""))
    await msg.answer("Тип прихода?", reply_markup=kb(get_list("D")))
    await state.set_state(IncomeState.income_type)

@dp.message(IncomeState.income_type)
async def income_type(msg: Message, state: FSMContext):
    await state.update_data(income_type=msg.text)
    await msg.answer("Номер заказа?", reply_markup=kb(extra="Пропустить"))
    await state.set_state(IncomeState.order)

@dp.message(IncomeState.order)
async def income_order(msg: Message, state: FSMContext):
    await state.update_data(order="" if msg.text == "Пропустить" else msg.text)
    await msg.answer("Комментарий?", reply_markup=kb(extra="Пропустить"))
    await state.set_state(IncomeState.comment)

@dp.message(IncomeState.comment)
async def income_comment(msg: Message, state: FSMContext):
    await state.update_data(comment="" if msg.text == "Пропустить" else msg.text)
    data = await state.get_data()

    if data["income_type"] in SALON_REQUIRED_FOR:
        await msg.answer("Выберите салон", reply_markup=kb(get_list("F")))
        await state.set_state(IncomeState.salon)
    else:
        await save_income(msg, state)

@dp.message(IncomeState.salon)
async def income_salon(msg: Message, state: FSMContext):
    await state.update_data(salon=msg.text)
    await save_income(msg, state)

async def save_income(msg: Message, state: FSMContext):
    data = await state.get_data()
    row = [
        data["date"],
        data["target"],
        data["amount"],
        data["income_type"],
        data.get("order", ""),
        data.get("comment", ""),
        data.get("salon", "")
    ]
    append_income(row)
    await msg.answer("✅ Приход записан")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
