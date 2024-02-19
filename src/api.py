from abc import ABC, abstractmethod
from typing import Dict, Any
import requests
from requests.exceptions import RequestException


class JobServiceAPI(ABC):
    """
    Абстрактный класс, определяющий интерфейс для работы с API сервисов вакансий.
    """

    @abstractmethod
    def get_vacancies(self, search_query: str, page: int) -> Dict[str, Any]:
        """
        Получение списка вакансий по заданным критериям.
        :param search_query: Строка поискового запроса.
        :param page: Номер страницы результатов поиска.
        :return: Словарь с данными вакансий.
        """
        pass

    @abstractmethod
    def get_vacancy_details(self, vacancy_id: str) -> Dict[str, Any]:
        """
        Получение детальной информации о конкретной вакансии.
        :param vacancy_id: Идентификатор вакансии.
        :return: Словарь с детальной информацией о вакансии.
        """
        pass


class HeadHunterAPI(JobServiceAPI):
    """
    Класс для работы с API hh.ru.
    Реализует методы абстрактного класса JobServiceAPI для получения данных с hh.ru.
    """

    def __init__(self):
        self.base_url = 'https://api.hh.ru/vacancies'

    def get_vacancies(self, search_query: str, page: int = 0) -> Dict[str, Any]:
        params = {
            'text': search_query,
            'page': page,
            'per_page': 100  # Количество результатов на странице
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Если запрос не успешен, вызывается исключение
            return response.json()
        except RequestException as e:
            print(f"Ошибка при запросе вакансий с сайта hh.ru: {e}")
            return {}

    def get_vacancy_details(self, vacancy_id: str) -> Dict[str, Any]:
        try:
            response = requests.get(f'{self.base_url}/{vacancy_id}')
            response.raise_for_status()  # Если запрос не успешен, вызывается исключение
            return response.json()
        except RequestException as e:
            print(f"Ошибка при запросе деталей вакансии с сайта hh.ru: {e}")
            return {}