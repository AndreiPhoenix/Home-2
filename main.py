from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, validator
import json
from datetime import datetime
import re
import os

app = FastAPI()


class Reason(str):
    NO_NETWORK = "нет доступа к сети"
    PHONE_NOT_WORKING = "не работает телефон"
    NO_EMAIL_RECEIVE = "не приходят письма"


class Subscriber(BaseModel):
    surname: str
    name: str
    birth_date: str
    phone: str
    email: EmailStr
    reason: Reason
    problem_detected_at: str

    @validator('surname', 'name')
    def check_name(cls, value):
        if not re.match(r'^[А-ЯЁ][а-яё]+$', value):
            raise ValueError('Должно содержать только кириллицу и начинаться с заглавной буквы')
        return value

    @validator('birth_date')
    def check_birth_date(cls, value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Дата должна быть в формате YYYY-MM-DD')
        return value

    @validator('phone')
    def check_phone(cls, value):
        if not re.match(r'^\+?[0-9]{10,15}$', value):
            raise ValueError('Номер телефона должен содержать только цифры и начинаться с + или без него')
        return value

    @validator('problem_detected_at')
    def check_problem_detected_at(cls, value):
        try:
            datetime.strptime(value, '%Y-%m-%d %H:%M')
        except ValueError:
            raise ValueError('Дата и время должны быть в формате YYYY-MM-DD HH:MM')
        return value


@app.post('/submit')
async def submit_subscriber(subscriber: Subscriber):
    subscriber_data = subscriber.dict()

    file_path = 'subscribers.json'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    data.append(subscriber_data)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return {"message": "Данные успешно сохранены", "data": subscriber_data}
