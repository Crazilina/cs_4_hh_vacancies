from abc import ABC, abstractmethod
import json
from pathlib import Path
from typing import List, Dict, Any
from src.vacancy import Vacancy


class VacancyManagerAbstract(ABC):
    """Абстрактный класс для управления вакансиями."""

    @abstractmethod
    def add_vacancy(self, vacancy: Vacancy) -> None:
        """Добавляет вакансию."""
        pass

    @abstractmethod
    def get_vacancies(self, filters: dict = None) -> List[Vacancy]:
        """Возвращает список вакансий, соответствующих заданным фильтрам."""
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy_id: str) -> None:
        """Удаляет вакансию по идентификатору."""
        pass


class VacancyManagerJSON(VacancyManagerAbstract):
    """Класс для управления вакансиями с хранением данных в формате JSON."""

    def __init__(self, file_path: str):
        """
        Инициализирует менеджер вакансий с указанием пути к файлу JSON.

        Args:
            file_path (str): Путь к файлу JSON.
        """
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)  # Создание директории, если не существует
        if not self.file_path.exists():
            self.file_path.write_text(json.dumps([]))  # Создание пустого файла, если не существует

    def _load_vacancies(self) -> List[Dict[str, Any]]:
        """Загружает список вакансий из JSON-файла."""
        with self.file_path.open('r', encoding='utf-8') as file:
            return json.load(file)

    def _save_vacancies(self, vacancies: List[Dict[str, Any]]) -> None:
        """Сохраняет список вакансий в JSON-файл."""
        with self.file_path.open('w', encoding='utf-8') as file:
            json.dump(vacancies, file, ensure_ascii=False, indent=4)

    def add_vacancy(self, vacancy: Vacancy) -> None:
        """
        Добавляет новую вакансию в JSON-файл.

        Args:
            vacancy (Vacancy): Объект вакансии для добавления.
        """
        vacancies = self._load_vacancies()
        vacancies.append(vacancy.to_dict())  # Преобразование вакансии в словарь
        self._save_vacancies(vacancies)

    def get_vacancies(self, filters: dict = None) -> List[Dict]:
        """
        Возвращает отфильтрованный список вакансий в виде словарей, соответствующих заданным фильтрам.

        Args:
            filters (dict, optional): Словарь с критериями фильтрации. Defaults to None.

        Returns:
            List[Dict]: Список отфильтрованных вакансий в виде словарей.
        """
        vacancies = self._load_vacancies()

        if filters:
            # Применяем фильтры
            filtered_vacancies = [vac for vac in vacancies if self._matches_filters(vac, filters)]
        else:
            # Если фильтры не заданы, возвращаем все вакансии
            filtered_vacancies = vacancies

        return filtered_vacancies

    def _matches_filters(self, vacancy: Dict, filters: Dict[str, Any]) -> bool:
        """
        Проверяет, соответствует ли вакансия заданным фильтрам.

        Args:
            vacancy (Dict): Словарь с данными вакансии для проверки.
            filters (Dict[str, Any]): Словарь с критериями фильтрации.

        Returns:
            bool: Возвращает True, если вакансия соответствует всем фильтрам.
        """
        for key, value in filters.items():
            # Проверяем соответствие значения фильтра значению в словаре вакансии
            if vacancy.get(key) != value:
                return False
        return True

    def delete_vacancy(self, vacancy_id: str) -> None:
        """
        Удаляет вакансию из JSON-файла по идентификатору.

        Args:
            vacancy_id (str): Идентификатор вакансии для удаления.
        """
        vacancies = self._load_vacancies()
        vacancies = [vac for vac in vacancies if vac['id'] != vacancy_id]
        self._save_vacancies(vacancies)

    def delete_vacancies_by_indexes(self, indexes: List[int]) -> None:
        """
        Удаляет вакансии из JSON-файла по списку индексов.

        Args:
            indexes (List[int]): Список индексов вакансий для удаления.
        """
        vacancies = self._load_vacancies()

        # Удаление вакансий, индекс которых не входит в список индексов для удаления
        # Учитываем, что пользовательские индексы начинаются с 1
        vacancies_to_keep = [vac for idx, vac in enumerate(vacancies, start=1) if idx not in indexes]
        self._save_vacancies(vacancies_to_keep)


    @staticmethod
    def compare_salaries(salary1, salary2):
        if salary1 is not None and salary2 is not None:
            if salary1 > salary2:
                return "выше"
            elif salary1 < salary2:
                return "ниже"
        elif salary1 is not None and salary2 is None:
            return "выше"
        elif salary1 is None and salary2 is not None:
            return "ниже"
        return None

    def compare_vacancies_salary(self, index1: int, index2: int) -> str:
        vacancies = self._load_vacancies()

        try:
            vacancy1 = vacancies[index1 - 1]
            vacancy2 = vacancies[index2 - 1]

            messages = []  # Используем список для сбора сообщений

            # Сравнение минимальных зарплат
            min_salary_comparison = self.compare_salaries(vacancy1.get('salary_from'), vacancy2.get('salary_from'))
            if min_salary_comparison:
                messages.append(
                    f"Минимальная зарплата в вакансии '{vacancy1['name']}' "
                    f"{min_salary_comparison} чем в '{vacancy2['name']}'. "
                )
            elif vacancy1.get('salary_from') is None and vacancy2.get('salary_from') is None:
                messages.append("Минимальная зарплата в обеих вакансиях не указана.")
            elif vacancy1.get('salary_from') or None and vacancy2.get('salary_from') is None:
                messages.append(
                    "Сравнение минимальных зарплат отсутствует из-за "
                    "неполных данных по зарплате в одной или обеих вакансиях."
                )
            # Сравнение максимальных зарплат
            max_salary_comparison = self.compare_salaries(vacancy1.get('salary_to'), vacancy2.get('salary_to'))
            if max_salary_comparison:
                messages.append(
                    f"Максимальная зарплата в вакансии '{vacancy1['name']}' "
                    f"{max_salary_comparison} чем в '{vacancy2['name']}'."
                )
            elif vacancy1.get('salary_to') is None and vacancy2.get('salary_to') is None:
                messages.append("Максимальная зарплата в обеих вакансиях не указана.")
            elif vacancy1.get('salary_to') is None or vacancy2.get('salary_to') is None:
                messages.append(
                    "Сравнение максимальных зарплат отсутствует из-за "
                    "неполных данных по зарплате в одной или обеих вакансиях."
                )

            if not messages:
                return "Зарплаты в вакансиях не указаны или их невозможно сравнить."

            return '\n'.join(messages)  # Соединяем сообщения переводом строки

        except IndexError:
            return "Одна из указанных вакансий не существует в сохранённом файле."
