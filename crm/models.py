from pydantic import BaseModel
from datetime import datetime, date


class User(BaseModel):
    login: str
    password: str
    firstName: str | None = None
    lastName: str | None = None
    email: str | None = None
    phone: str | None = None
    roles: list | None = None


class Reminder(BaseModel):
    description: str
    when: datetime | None = None
    status: bool | None = True  # True - active, False - done
    # todo: add what is needed


class Comment(BaseModel):
    comment: str
    dataTime: datetime | None = None
    addedBy: User | None = None
    details: str | None = None


class WeekDays(BaseModel):
    Sunday: bool = False
    Monday: bool = False
    Tuesday: bool = False
    Wednesday: bool = False
    Thursday: bool = False
    Friday: bool = False
    Saturday: bool = False


class Group(BaseModel):
    id: int
    name: str
    teacher: str | None = None
    whatsApp: str | None = None
    slack: str | None = None
    skype: str | None = None
    startDate: date | None = None
    expectedFinishDate: date | None = None
    lessonsDays: WeekDays
    webinarDays: WeekDays
    studentsList: list | None = []
    reminders: list | None = []
    active: bool = False
    autoArchive: bool = False


class Payment(BaseModel):
    id: int
    date: datetime
    type: str
    amount: float
    details: str | None = None
    description: str


class Contact(BaseModel):
    id: int
    name: str
    surname: str | None = None
    email: str | None = None
    phone: str
    city: str | None = None
    course: str | None = None
    source: str | None = None
    status: str | None = None
    comments: list | None = []
    reminders: list | None = []


class Student(Contact):
    teudatZeut: int
    group: Group
    groupHistory: list | None = []
    courseFee: int | None = None
    payments: list | None = None
    documents: bool | None = False


class Lecturer(BaseModel):
    pass
