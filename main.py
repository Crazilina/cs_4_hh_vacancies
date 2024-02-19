from src.api import HeadHunterAPI
from src.functions import get_filters, print_top_vacancies, filter_vacancies, continue_with_saved_file
from src.vacancy_manager import VacancyManagerJSON


def user_interaction():
    hh_api = HeadHunterAPI()

    # Запрос ключевого слова у пользователя для поиска вакансий
    keyword = input("Введите ключевое слово для поиска вакансий: ")
    hh_vacancies_json = hh_api.get_vacancies(keyword)
    hh_vacancies = hh_vacancies_json.get('items', [])  # Предполагаем, что данные вакансий находятся в ключе 'items'

    if not hh_vacancies:
        print("Вакансии по вашему запросу не найдены.")
        return

    filters = get_filters()
    if filters is None:
        print("Прекращаем выполнение, фильтры не были корректно введены.")
        return

    filtered_vacancies = filter_vacancies(hh_vacancies, filters)
    if not filtered_vacancies:
        print("Нет вакансий, соответствующих указанным фильтрам.")
        return

    top_n = int(input("Введите количество вакансий для отображения: "))
    print_top_vacancies(filtered_vacancies, top_n)

    save_choice = input("Хотите сохранить отфильтрованные вакансии в файл? (да/нет): ").lower()
    if save_choice == 'да':
        # Запрос имени файла
        file_name = input("Введите имя файла для сохранения: ")
        file_path = f"data/{file_name}.json"
        vacancy_manager = VacancyManagerJSON(file_path)
        vacancies_count = len(filtered_vacancies)  # Подсчитываем количество вакансий
        for vac in filtered_vacancies:
            vacancy_manager.add_vacancy(vac)
        print(f"Файл с именем '{file_name}.json' создан и сохранен. Сохранено вакансий: {vacancies_count}.")

        # Предложить пользователю работать с сохраненным файлом
        continue_choice = input("Хотите продолжить работу с сохраненным файлом? (да/нет): ").lower()
        if continue_choice == 'да':
            continue_with_saved_file(vacancy_manager)
        else:
            print("Работа с сохраненным файлом завершена. Надеемся, наш сервис был вам полезен!")
    else:
        print("Ваш запрос обработан. Сохранение вакансий пропущено. Спасибо за использование нашего сервиса!")


if __name__ == "__main__":
    user_interaction()
