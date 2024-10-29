# admin_modules.py

import sqlite3

def connect_db():
    """Функция для подключения к базе данных."""
    con = sqlite3.connect('theater.db')
    return con


def get_current_events():
    """Вывести список актуальных спектаклей."""
    con = connect_db()
    curs = con.cursor()
    curs.execute("SELECT id, name, price, date, free_slots FROM events WHERE free_slots > 0 AND date >= DATE('now')")
    events = curs.fetchall()
    con.close()
    return events


def add_event(name, price, date, free_slots):
    """Добавить спектакль в таблицу events."""
    con = connect_db()
    curs = con.cursor()
    curs.execute(
        "INSERT INTO events (name, price, date, free_slots) VALUES (?, ?, ?, ?)",
        (name, price, date, free_slots)
    )
    con.commit()
    con.close()
    print(f"Спектакль '{name}' добавлен.")


def delete_event(event_id):
    """Удалить спектакль из таблицы events."""
    con = connect_db()
    curs = con.cursor()
    curs.execute("DELETE FROM events WHERE id = ?", (event_id,))
    con.commit()
    con.close()
    print(f"Спектакль с ID {event_id} удален.")


def get_all_customers():
    """Получить список всех покупателей."""
    con = connect_db()
    curs = con.cursor()
    curs.execute("SELECT id, name, age, email, phone FROM customers")
    customers = curs.fetchall()
    con.close()
    return customers


def get_customers_for_event(event_id):
    """Получить список всех покупателей, зарегистрированных на конкретный спектакль."""
    con = connect_db()
    curs = con.cursor()
    curs.execute("""
        SELECT customers.id, customers.name, customers.age, customers.email, customers.phone
        FROM customers
        JOIN orders ON customers.id = orders.customer_id
        WHERE orders.event_id = ?
    """, (event_id,))
    customers = curs.fetchall()
    con.close()
    return customers


def get_customers_not_for_event(event_id):
    """Получить список всех покупателей, не зарегистрированных на конкретный спектакль."""
    con = connect_db()
    curs = con.cursor()
    curs.execute("""
        SELECT customers.id, customers.name, customers.age, customers.email, customers.phone
        FROM customers
        LEFT JOIN orders ON customers.id = orders.customer_id AND orders.event_id = ?
        WHERE orders.event_id IS NULL
    """, (event_id,))
    customers = curs.fetchall()
    con.close()
    return customers


def get_events_ranked_by_tickets():
    """Получить ранжированный список спектаклей по количеству проданных билетов."""
    con = connect_db()
    curs = con.cursor()
    curs.execute("""
        SELECT events.name, COUNT(orders.order_id) as tickets_sold
        FROM events
        LEFT JOIN orders ON events.id = orders.event_id
        GROUP BY events.id
        ORDER BY tickets_sold DESC
    """)
    ranked_events = curs.fetchall()
    con.close()
    return ranked_events


def get_events_ranked_by_revenue():
    """Получить ранжированный список спектаклей по сумме полученной за продажи билетов."""
    con = connect_db()
    curs = con.cursor()
    curs.execute("""
        SELECT events.name, SUM(events.price) as revenue
        FROM events
        JOIN orders ON events.id = orders.event_id
        GROUP BY events.id
        ORDER BY revenue DESC
    """)
    ranked_events = curs.fetchall()
    con.close()
    return ranked_events
