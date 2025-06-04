import grpc
import user_pb2
import user_pb2_grpc
import sqlite3

def clear_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users')
    conn.commit()
    conn.close()

def run():
    clear_database()
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = user_pb2_grpc.UserServiceStub(channel)

            # Тест 1: Создание пользователя (Обычный случай)
            print("Тестирование создания пользователя...")
            try:
                response = stub.CreateUser(user_pb2.CreateUserRequest(
                    name="Иван Иванов",
                    email="ivan@example.com",
                    passwordHash="пароль123",
                    role="user"
                ))
                print(f"Создание пользователя успешно: {response.user}")
                user_id = response.user.id
            except grpc.RpcError as e:
                print(f"Ошибка создания пользователя: {e.details()}")

            # Тест 2: Создание пользователя (Дублирующийся email)
            print("\nТестирование создания пользователя с дублирующимся email...")
            try:
                response = stub.CreateUser(user_pb2.CreateUserRequest(
                    name="Иван Дубликат",
                    email="ivan@example.com",
                    passwordHash="пароль123",
                    role="user"
                ))
                print(f"Создание пользователя (дубликат) успешно: {response.user}")
            except grpc.RpcError as e:
                print(f"Ошибка создания пользователя (дубликат): {e.details()}")

            # Тест 3: Получение пользователя (Существующий пользователь)
            print("\nТестирование получения существующего пользователя...")
            try:
                response = stub.GetUser(user_pb2.GetUserRequest(id=user_id))
                print(f"Получение пользователя успешно: {response.user}")
            except grpc.RpcError as e:
                print(f"Ошибка получения пользователя: {e.details()}")

            # Тест 4: Получение пользователя (Несуществующий пользователь)
            print("\nТестирование получения несуществующего пользователя...")
            try:
                response = stub.GetUser(user_pb2.GetUserRequest(id="несуществующий-id"))
                print(f"Получение пользователя (несуществующий) успешно: {response.user}")
            except grpc.RpcError as e:
                print(f"Ошибка получения пользователя (несуществующий): {e.details()}")

            # Тест 5: Обновление пользователя (Существующий пользователь)
            print("\nТестирование обновления существующего пользователя...")
            try:
                response = stub.UpdateUser(user_pb2.UpdateUserRequest(
                    id=user_id,
                    name="Иван Обновленный",
                    email="ivan_updated@example.com",
                    passwordHash="новыйпароль",
                    role="admin"
                ))
                print(f"Обновление пользователя успешно: {response.user}")
            except grpc.RpcError as e:
                print(f"Ошибка обновления пользователя: {e.details()}")

            # Тест 6: Обновление пользователя (Несуществующий пользователь)
            print("\nТестирование обновления несуществующего пользователя...")
            try:
                response = stub.UpdateUser(user_pb2.UpdateUserRequest(
                    id="несуществующий-id",
                    name="Иван Обновленный",
                    email="ivan_updated@example.com",
                    passwordHash="новыйпароль",
                    role="admin"
                ))
                print(f"Обновление пользователя (несуществующий) успешно: {response.user}")
            except grpc.RpcError as e:
                print(f"Ошибка обновления пользователя (несуществующий): {e.details()}")

            # Тест 7: Вход (Правильные учетные данные)
            print("\nТестирование входа с правильными учетными данными...")
            try:
                response = stub.Login(user_pb2.LoginRequest(
                    email="ivan_updated@example.com",
                    passwordHash="новыйпароль"
                ))
                print(f"Вход успешен: {response.token}")
            except grpc.RpcError as e:
                print(f"Ошибка входа: {e.details()}")

            # Тест 8: Вход (Неверные учетные данные)
            print("\nТестирование входа с неверными учетными данными...")
            try:
                response = stub.Login(user_pb2.LoginRequest(
                    email="ivan_updated@example.com",
                    passwordHash="неверныйпароль"
                ))
                print(f"Вход (неверные данные) успешен: {response.token}")
            except grpc.RpcError as e:
                print(f"Ошибка входа (неверные данные): {e.details()}")

            # Тест 9: Список пользователей
            print("\nТестирование списка пользователей...")
            try:
                response = stub.ListUsers(user_pb2.Empty())
                print("Список пользователей успешно получен:")
                for user in response.users:
                    print(user)
            except grpc.RpcError as e:
                print(f"Ошибка получения списка пользователей: {e.details()}")

            # Тест 10: Удаление пользователя (Существующий пользователь)
            print("\nТестирование удаления существующего пользователя...")
            try:
                response = stub.DeleteUser(user_pb2.DeleteUserRequest(id=user_id))
                print("Удаление пользователя успешно")
            except grpc.RpcError as e:
                print(f"Ошибка удаления пользователя: {e.details()}")

            # Тест 11: Удаление пользователя (Несуществующий пользователь)
            print("\nТестирование удаления несуществующего пользователя...")
            try:
                response = stub.DeleteUser(user_pb2.DeleteUserRequest(id=user_id))
                print("Удаление пользователя (несуществующий) успешно")
            except grpc.RpcError as e:
                print(f"Ошибка удаления пользователя (несуществующий): {e.details()}")

    except Exception as e:
        print(f"Не удалось подключиться к серверу: {str(e)}")

if __name__ == '__main__':
    run()