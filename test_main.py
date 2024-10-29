import pytest
import sqlite3
from unittest.mock import patch
from customers_modules import view_events, register_customer, cancel_ticket
from admin_modules import (
    get_current_events, add_event, delete_event, get_all_customers,
    get_customers_for_event, get_customers_not_for_event,
    get_events_ranked_by_tickets, get_events_ranked_by_revenue
)

@pytest.fixture(scope='function')
def db_connection():
    """Создает временную базу данных для тестирования."""
    connection = sqlite3.connect(':memory:')  # Используем in-memory базу данных
    cursor = connection.cursor()
    
    cursor.execute('''
        CREATE TABLE events (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            date TEXT NOT NULL,
            free_slots INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            email TEXT,
            phone TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            event_id INTEGER,
            event_name TEXT,
            event_price REAL,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    ''')
    
    connection.commit()
    yield connection
    connection.close()

def test_view_events_no_events(db_connection):
    """Тест для функции view_events без доступных спектаклей."""
    with patch('builtins.print') as mock_print:
        view_events()
        mock_print.assert_called_with("Нет доступных спектаклей.")

def test_view_events_with_events(db_connection):
    add_event("Test Event", 100.0, "2024-11-01", 5)

    with patch('builtins.print') as mocked_print:
        view_events()  # Вызываем функцию
        mocked_print.assert_any_call('ID: 1, Название: Test Event, Цена: 100.0, Дата: 2024-11-01, Свободные места: 5')

def test_register_customer(db_connection):
    """Тест для функции register_customer."""
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO events (name, price, date, free_slots) VALUES (?, ?, ?, ?)",
                   ("Test Event", 100.0, "2024-11-01", 5))
    db_connection.commit()

    with patch('builtins.input', side_effect=["John Doe", 30, "john.doe@example.com", "1234567890"]), patch('builtins.print') as mock_print:
        register_customer(1, "Test Event", 100.0)
        mock_print.assert_called_with("Регистрация завершена, билет успешно куплен!")

def test_cancel_ticket_no_order(db_connection):
    """Тест для функции cancel_ticket без существующего заказа."""
    with patch('builtins.input', side_effect=["999"]), patch('builtins.print') as mock_print:
        cancel_ticket()
        mock_print.assert_called_with("Заказ с таким номером не найден.")

def test_cancel_ticket_with_order(db_connection):
    add_event("Test Event", 100.0, "2023-10-01", 5)
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO customers (name, age, email, phone) VALUES (?, ?, ?, ?)", ("John Doe", 30, "john@example.com", "1234567890"))
    cursor.execute("INSERT INTO orders (customer_id, event_id) VALUES (?, ?)", (1, 1))
    db_connection.commit()
    
    result = cancel_ticket(1)  # Указываем ID заказа для отмены
    assert result == 1  # Ожидаем успешное удаление

