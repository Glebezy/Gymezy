.PHONY: test test-cov run run-test install clean allure

# Переменные окружения
ENV_TEST := ENV=test
ENV_PROD := ENV=prod

# Переменные  Allure
ALLURE_DIR=./allure-results
ALLURE_REPORT=./allure-report

# Тестирование
test:
	$(ENV_TEST) python -m pytest --alluredir=$(ALLURE_DIR) -v

# Просмотр отчёта
allure:
	allure serve $(ALLURE_DIR)

# Очистка Allure результатов
clean-allure:
	rm -rf $(ALLURE_DIR) $(ALLURE_REPORT)

# Запуск приложения
run:
	$(ENV_PROD) python app.py

run-test:
	$(ENV_TEST) python app.py

# Установка зависимостей
install:
	pip install -r requirements.txt

# Очистка
clean: clean-allure
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache

# Помощь
help:
	@echo "Доступные команды:"
	@echo "  make test       - запустить тесты"
	@echo "  make allure      - просмотр отчета"
	@echo "  make run        - запуск в production"
	@echo "  make run-test   - запуск в test"
	@echo "  make install    - установка зависимостей"
	@echo "  make clean      - очистка временных файлов"