import pytest
import sqlite3
from customers_modules import view_events, register_customer, cancel_ticket
from admin_modules import (
    add_event,
    delete_event,
    get_current_events,
    get_all_customers,
    get_customers_for_event,
    get_customers_not_for_event,
    get_events_ranked_by_tickets,
    get_events_ranked_by_revenue,
)

@pytest.fixture(scope='function')
def db_connection():
    """Создает временную базу данных для тестирования."""
    connection = sqlite3.connect(':memory:')  # Используем in-memory базу данных
    cursor = connection.cursor()
    
    # Создаем необходимые таблицы
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

def test_add_event(db_connection):
    """Тест для функции add_event."""
    add_event("Test Event", 100.0, "2024-11-01", 5)

    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM events WHERE name = 'Test Event'")
    event = cursor.fetchone()

    assert event is not None  # Убедимся, что событие действительно было добавлено
    assert event[1] == "Test Event"
    assert event[2] == 100.0

def test_delete_event(db_connection):
    """Тест для функции delete_event."""
    add_event("Test Event", 100.0, "2024-11-01", 5)

    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM events WHERE name = 'Test Event'")
    event = cursor.fetchone()
    
    assert event is not None  # Убедимся, что событие было добавлено успешно
    event_id = event[0]

    delete_event(event_id)

    cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    event_after_deletion = cursor.fetchone()

    assert event_after_deletion is None

def test_get_current_events(db_connection):
    """Тест для функции get_current_events."""
    add_event("Current Event", 100.0, "2024-11-01", 5)  # Актуальное
    add_event("Expired Event", 50.0, "2020-01-01", 0)  # Неактуальное

    events = get_current_events()

    assert len(events) == 1  # Должен вернуть только "Current Event"
    assert events[0][1] == "Current Event"  # Проверка по названию

def test_get_all_customers(db_connection):
    """Тест для функции get_all_customers."""
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO customers (name, age, email, phone) VALUES (?, ?, ?, ?)", ("John Doe", 30, "john@example.com", "1234567890"))
    db_connection.commit()
    
    customers = get_all_customers()

    assert len(customers) == 1
    assert customers[0][1] == "John Doe"

def test_get_customers_for_event(db_connection):
    """Тест для функции get_customers_for_event."""
    cursor = db_connection.cursor()
    add_event("Test Event", 100.0, "2024-11-01", 5)
    
    cursor.execute("INSERT INTO customers (name, age, email, phone) VALUES (?, ?, ?, ?)", ("John Doe", 30, "john@example.com", "1234567890"))
    cursor.execute("INSERT INTO orders (customer_id, event_id) VALUES (?, ?)", (1, 1))
    db_connection.commit()
    
    customers = get_customers_for_event(1)

    assert len(customers) == 1
    assert customers[0][1] == "John Doe"

def test_get_customers_not_for_event(db_connection):
    """Тест для функции get_customers_not_for_event."""
    cursor = db_connection.cursor()
    cursor.execute("INSERT INTO events (name, price, date, free_slots) VALUES (?, ?, ?, ?)", ("Test Event", 100.0, "2024-11-01", 5))
    cursor.execute("INSERT INTO customers (name, age, email, phone) VALUES (?, ?, ?, ?)", ("John Doe", 30, "john@example.com", "1234567890"))
    cursor.execute("INSERT INTO orders (customer_id, event_id) VALUES (?, ?)", (1, 1))  # Классический случай
    
    cursor.execute("INSERT INTO customers (name, age, email, phone) VALUES (?, ?, ?, ?)", ("Jane Doe", 25, "jane@example.com", "0987654321"))
    db_connection.commit()
    
    customers = get_customers_not_for_event(1)

    assert len(customers) == 1
    assert customers[0][1] == "Jane Doe"

def test_get_events_ranked_by_tickets(db_connection):
    """Тест для функции get_events_ranked_by_tickets."""
    add_event("Highly Popular Event", 100.0, "2024-11-01", 5)
    # Добавьте дополнительные заказы и события, чтобы протестировать

    ranked_events = get_events_ranked_by_tickets()

    assert len(ranked_events) == 1
    assert ranked_events[0][0] == "Highly Popular Event"

def test_get_events_ranked_by_revenue(db_connection):
    """Тест для функции get_events_ranked_by_revenue."""
    add_event("Test Event", 100.0, "2024-11-01", 5)
    # Добавьте заказы, чтобы протестировать доходы

    ranked_events = get_events_ranked_by_revenue()

    assert len(ranked_events) == 1
    assert ranked_events[0][0] == "Test Event"

