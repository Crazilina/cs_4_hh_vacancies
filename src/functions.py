from datetime import datetime
import re
from .vacancy import Vacancy


def get_filters():
    filters_list = {
        "1": "зарплата от",
        "2": "зарплата до",
        "3": "город",
        "4": "дата публикации",
        "5": "опыт работы"
    }

    print("Доступные фильтры:")
    for key, value in filters_list.items():
        print(f"{key}. {value}")

    filter_choice = input("Выберите фильтры (через пробел): ")
    filters = {}
    for choice in filter_choice.split():
        if choice in filters_list:
            filter_name = filters_list[choice]
            if filter_name == "дата публикации":
                date_input = input(f"Введите {filter_name} в формате DD.MM.YYYY: ")
                # Проверка соответствия введенной даты формату
                try:
                    datetime.strptime(date_input, "%d.%m.%Y")
                    filters[filter_name] = date_input
                except ValueError:
                    print("Дата введена в некорректном формате. Пожалуйста, используйте формат ДД.ММ.ГГГГ.")
                    return None
            else:
                filters[filter_name] = input(f"Введите {filter_name}: ")

    return filters


def clean_highlight_tags(text):
    """Удаляет теги подсветки поисковых слов из текста."""
    # Используем регулярное выражение с обратными ссылками для сохранения оригинального регистра
    cleaned_text = re.sub(r'<highlighttext>(.*?)</highlighttext>', lambda match: match.group(1), text)
    return cleaned_text


def print_vacancy_details(vacancy):
    formatted_date = vacancy.format_published_date()
    print(f"""
    ID: {vacancy.id}
    Название: {vacancy.name}
    Ссылка: {vacancy.url}
    Зарплата: от {vacancy.salary_from or "не указана"} до {vacancy.salary_to or "не указана"}
    Описание: {clean_highlight_tags(vacancy.description)}
    Работодатель: {vacancy.employer}
    Город: {vacancy.city}
    Дата публикации: {formatted_date}
    Опыт работы: {vacancy.experience}
    Тип занятости: {vacancy.employment_type}
    График работы: {vacancy.schedule}
    """)


def continue_with_saved_file(vacancy_manager):
    while True:
        # Запрашиваем у пользователя дальнейшие действия с сохраненными вакансиями
        print("Выберите действие:")
        print("1. Вывести полученные вакансии")
        print("2. Сравнить вакансии по зарплате")
        print("3. Удалить одну или несколько вакансий")
        print("4. Выйти")

        action_choice = input("Введите номер выбранного действия: ")

        if action_choice == '1':
            # Вывести полученные вакансии
            saved_vacancies = vacancy_manager.get_vacancies()
            for index, vacancy_data in enumerate(saved_vacancies, start=1):
                published_date = datetime.strptime(vacancy_data['published_at'], "%Y-%m-%dT%H:%M:%S%z")
                formatted_date = published_date.strftime("%d.%m.%Y")  # Форматируем дату в нужный вид
                print(f"Вакансия {index}:")
                print(f"ID: {vacancy_data['id']}")
                print(f"Название: {vacancy_data['name']}")
                print(f"Ссылка: {vacancy_data['url']}")
                print(
                    f"Зарплата: от {vacancy_data['salary_from'] or 'не указана'} "
                    f"до {vacancy_data['salary_to'] or 'не указана'}")
                print(f"Описание: {clean_highlight_tags(vacancy_data['description'])}")
                print(f"Работодатель: {vacancy_data['employer']}")
                print(f"Город: {vacancy_data['city']}")
                print(f"Дата публикации: {formatted_date}")
                print(f"Опыт работы: {vacancy_data['experience']}")
                print(f"Тип занятости: {vacancy_data['employment_type']}")
                print(f"График работы: {vacancy_data['schedule']}")
                print()  # Печатаем пустую строку между вакансиями для лучшей читаемости

        elif action_choice == '2':
            # Предложить пользователю ввести номера вакансий для сравнения
            print("Введите номера вакансий для сравнения (через пробел): ")
            vacancies_to_compare = input().split()

            if len(vacancies_to_compare) != 2:
                print("Пожалуйста, введите два номера вакансий для сравнения.")
            else:
                try:
                    vacancy_index_1, vacancy_index_2 = map(int, vacancies_to_compare)

                    # Используем метод compare_vacancies_salary для сравнения зарплат вакансий
                    comparison_result = vacancy_manager.compare_vacancies_salary(vacancy_index_1, vacancy_index_2)
                    print(comparison_result)

                except ValueError:
                    print("Ошибка ввода. Убедитесь, что вводите числа, разделенные пробелами.")

        elif action_choice == '3':
            # Вывод количества вакансий до удаления
            saved_vacancies = vacancy_manager.get_vacancies()
            print(f"Всего вакансий в файле: {len(saved_vacancies)}.")

            # Запросить у пользователя номера вакансий для удаления
            indexes_to_delete = input("Введите номера вакансий для удаления (через пробел): ")
            indexes_to_delete = [int(index.strip()) for index in indexes_to_delete.split()]

            # Вызвать метод удаления вакансий из менеджера вакансий
            vacancy_manager.delete_vacancies_by_indexes(indexes_to_delete)

            # Вывод количества вакансий после удаления
            saved_vacancies_after_deletion = vacancy_manager.get_vacancies()
            print(f"Удаление вакансий выполнено. Осталось вакансий в файле: {len(saved_vacancies_after_deletion)}.")

        elif action_choice == '4':
            print("Выход из программы выполнен. До свидания!")
            break  # Выход из цикла, если пользователь выбрал выход

        else:
            print("Некорректный выбор. Пожалуйста, выберите существующий номер действия.")


# Функция для фильтрации вакансий
def filter_vacancies(vacancies, filters):
    filtered_vacancies = [Vacancy(vac_data) for vac_data in vacancies]

    for filter_name, filter_val in filters.items():
        if filter_name == 'зарплата от':
            filtered_vacancies = [vac for vac in filtered_vacancies if
                                  vac.salary_from and vac.salary_from >= int(filter_val)]
        elif filter_name == 'зарплата до':
            filtered_vacancies = [vac for vac in filtered_vacancies if
                                  vac.salary_to and vac.salary_to <= int(filter_val)]
        elif filter_name == 'город':
            filtered_vacancies = [vac for vac in filtered_vacancies if vac.city.lower() == filter_val.lower()]
        elif filter_name == 'дата публикации':
            user_date = datetime.strptime(filter_val, "%d.%m.%Y").strftime("%Y-%m-%d")
            filtered_vacancies = [vac for vac in filtered_vacancies if vac.published_at.startswith(user_date)]
        elif filter_name == 'опыт работы':
            filtered_vacancies = [vac for vac in filtered_vacancies if vac.experience.lower() == filter_val.lower()]

    if not filtered_vacancies:
        print("Нет вакансий, соответствующих указанным фильтрам.")

    return filtered_vacancies


# Функция для вывода топ N вакансий
def print_top_vacancies(vacancies, top_n):
    sorted_vacancies = sorted(vacancies, key=lambda v: (v.salary_from or 0, v.salary_to or 0), reverse=True)[:top_n]
    print("\nТоп вакансий по вашему запросу:")
    for index, vac in enumerate(sorted_vacancies, start=1):
        print(f"Вакансия №{index}")
        print_vacancy_details(vac)  # Эта функция уже должна быть определена в src/functions.py
        print()
