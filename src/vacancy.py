from datetime import datetime
from typing import Dict, Optional


class Vacancy:
    """
    Класс Vacancy предназначен для хранения и обработки информации о вакансиях.

    Атрибуты:
    - id (str): Уникальный идентификатор вакансии.
    - name (str): Название вакансии.
    - url (str): Ссылка на вакансию.
    - salary_from (Optional[int]): Минимальная зарплата.
    - salary_to (Optional[int]): Максимальная зарплата.
    - description (str): Описание вакансии.
    - employer (str): Название работодателя.
    - city (str): Город.
    - published_at (str): Дата публикации вакансии.
    - experience (str): Требуемый опыт работы.
    - employment_type (str): Тип занятости.
    - schedule (str): График работы.

    Методы:
    - __init__: Конструктор класса.
    - _parse_salary: Вспомогательный метод для парсинга зарплаты.
    - format_published_date: Метод для форматирования даты публикации.
    - to_dict: Преобразует объект вакансии в словарь.
    """

    def __init__(self, vacancy_data: Dict):
        """
        Инициализирует объект Vacancy с данными из словаря.

        :param vacancy_data: Словарь с данными о вакансии.
        """
        self.id = vacancy_data.get('id')
        self.name = vacancy_data.get('name')
        self.url = vacancy_data.get('alternate_url')
        self.salary_from, self.salary_to, self.salary_str = self.parse_salary(vacancy_data.get('salary'))
        # Исправление здесь, добавляем проверку на None и возвращаем пустую строку вместо None
        self.description = " ".join(filter(None, [
            vacancy_data.get('snippet', {}).get('requirement', ''),
            vacancy_data.get('snippet', {}).get('responsibility', '')
        ])).strip()
        self.employer = vacancy_data.get('employer', {}).get('name')
        self.city = vacancy_data.get('area', {}).get('name')
        self.published_at = vacancy_data.get('published_at')
        self.experience = vacancy_data.get('experience', {}).get('name')
        self.employment_type = vacancy_data.get('employment', {}).get('name')
        self.schedule = vacancy_data.get('schedule', {}).get('name')

    def parse_salary(self, salary_data: Optional[Dict]) -> (int, int, str):
        """
        Парсит информацию о зарплате из данных вакансии, валидируя и приводя к единообразному формату.

        :param salary_data: Словарь с данными о зарплате.
        :return: Кортеж, содержащий минимальную и максимальную зарплаты как целые числа, и строку для отображения.
        """
        if salary_data is not None and ('from' in salary_data or 'to' in salary_data):
            salary_from = salary_data.get('from', 0)
            salary_to = salary_data.get('to', 0)
            salary_str = "от {} до {} {}".format(salary_from if salary_from else '___',
                                                 salary_to if salary_to else '___',
                                                 salary_data.get('currency', ''))
            return salary_from, salary_to, salary_str.strip()
        else:
            return 0, 0, "Зарплата не указана"

    def compare_salary_to(self, other) -> str:
        """
        Сравнивает зарплату этой вакансии с зарплатой другой вакансии, включая названия вакансий в вывод.

        :param other: Экземпляр Vacancy для сравнения.
        :return: Строка с результатом сравнения, указывающая, в какой вакансии зарплата выше или что зарплаты равны.
        """
        if self.salary_from == other.salary_from and self.salary_to == other.salary_to:
            return f"Зарплаты в вакансиях '{self.name}' и '{other.name}' равны."

        message = ""
        if self.salary_from is not None and other.salary_from is not None:
            if self.salary_from > other.salary_from:
                message += f"Минимальная зарплата в вакансии '{self.name}' выше, чем в '{other.name}'. "
            elif self.salary_from < other.salary_from:
                message += f"Минимальная зарплата в вакансии '{other.name}' выше, чем в '{self.name}'. "

        if self.salary_to is not None and other.salary_to is not None:
            if self.salary_to > other.salary_to:
                message += f"Максимальная зарплата в вакансии '{self.name}' выше, чем в '{other.name}'."
            elif self.salary_to < other.salary_to:
                message += f"Максимальная зарплата в вакансии '{other.name}' выше, чем в '{self.name}'."

        if not message:
            # Сценарий, когда одна из зарплат не указана, и сравнение невозможно
            message = "Невозможно сравнить зарплаты из-за отсутствия данных в одной из вакансий."

        return message.strip()

    def format_published_date(self) -> str:
        """
        Форматирует дату публикации вакансии для вывода пользователю.

        :return: Строка с датой публикации в формате "DD.MM.YYYY" или относительном формате.
        """
        published_date = datetime.strptime(self.published_at, "%Y-%m-%dT%H:%M:%S%z")
        now = datetime.now(published_date.tzinfo)
        delta = now - published_date

        if delta.days < 1:
            return "сегодня"
        elif delta.days == 1:
            return "вчера"
        elif delta.days < 8:
            days = delta.days
            if days == 1:
                return "1 день назад"
            elif 1 < days < 5:
                return f"{days} дня назад"
            else:
                return f"{days} дней назад"
        else:
            return published_date.strftime("%d.%m.%Y")

    def to_dict(self) -> Dict:
        """
        Преобразует объект вакансии в словарь для сериализации в JSON.

        :return: Словарь с данными о вакансии.
        """
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'salary_from': self.salary_from,
            'salary_to': self.salary_to,
            'description': self.description,
            'employer': self.employer,
            'city': self.city,
            'published_at': self.published_at,  # Сохраняем дату в формате ISO
            'experience': self.experience,
            'employment_type': self.employment_type,
            'schedule': self.schedule
        }
