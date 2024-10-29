# customers_modules.py

import sqlite3

def connect_db():
    """Функция для подключения к базе данных."""
    con = sqlite3.connect('theater.db')
    return con


def view_events():
    """Функция для отображения списка доступных спектаклей и выбора спектакля для покупки."""
    con = connect_db()
    curs = con.cursor()
    
    # Получаем все доступные спектакли
    curs.execute("SELECT id, name, price, date, free_slots FROM events WHERE free_slots > 0")
    events = curs.fetchall()
    
    if not events:
        print("Нет доступных спектаклей.")
        
        return  # Завершаем выполнение, если мероприятий нет

    print("Доступные спектакли:")
    for event in events:
        print(f"ID: {event[0]}, Название: {event[1]}, Цена: {event[2]}, Дата: {event[3]}, Свободные места: {event[4]}")
    
    # Теперь можно безопасно запросить ID события
    event_id = input("Введите ID спектакля, на который хотите купить билет: ")
    
    # Проверяем, что выбранный спектакль существует
    curs.execute("SELECT name, price, free_slots FROM events WHERE id = ?", (event_id,))
    selected_event = curs.fetchone()
    
    if selected_event:
        event_name, event_price, free_slots = selected_event
        if free_slots > 0:
            # Запуск регистрации пользователя
            register_customer(event_id, event_name, event_price)
        else:
            print("К сожалению, на выбранный спектакль нет доступных мест.")
    else:
        print("Спектакль с таким ID не найден.")
    
    con.close()

def register_customer(event_id, event_name, event_price):
    """Функция для регистрации покупателя и создания заказа."""
    con = connect_db()
    curs = con.cursor()

    try:
        # Сбор данных покупателя
        name = input("Введите ваше имя: ")
        age = int(input("Введите ваш возраст: "))
        email = input("Введите вашу электронную почту: ")
        phone = input("Введите ваш телефон: ")
        
        # Вставка покупателя в таблицу customers, если его еще нет
        curs.execute("INSERT OR IGNORE INTO customers (name, age, email, phone) VALUES (?, ?, ?, ?)", 
                     (name, age, email, phone))
        
        # Получение ID клиента
        curs.execute("SELECT id FROM customers WHERE email = ?", (email,))
        customer_id = curs.fetchone()[0]
        
        # Создание заказа
        curs.execute('''
            INSERT INTO orders (event_id, customer_id, event_name, event_price)
            VALUES (?, ?, ?, ?)
        ''', (event_id, customer_id, event_name, event_price))
        
        # Уменьшаем количество доступных мест в спектакле на 1
        curs.execute("UPDATE events SET free_slots = free_slots - 1 WHERE id = ?", (event_id,))
        
        con.commit()
        print("Регистрация завершена, билет успешно куплен!")
        
    except Exception as e:
        print("Произошла ошибка во время регистрации:", e)
    
    con.close()


def cancel_ticket(order_id):
    """Функция для отмены покупки билета."""
    con = connect_db()
    curs = con.cursor()

    try:
        # Проверим, существует ли заказ с таким ID
        curs.execute("SELECT event_id FROM orders WHERE order_id = ?", (order_id,))
        result = curs.fetchone()

        if result:
            event_id = result[0]
            
            # Удаление заказа из таблицы orders
            curs.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
            
            # Увеличиваем количество доступных мест в соответствующем спектакле
            curs.execute("UPDATE events SET free_slots = free_slots + 1 WHERE id = ?", (event_id,))
            
            con.commit()
            print("Заказ успешно отменен.")
            return 1  # Успешная отмена
        else:
            print("Заказ с таким номером не найден.")
            return 0  # Заказ не найден
    
    except Exception as e:
        print("Ошибка при отмене заказа:", e)
        return 0  # В случае ошибки

    
    # Оставляем подключение открытым и возвращаемся в главное меню
