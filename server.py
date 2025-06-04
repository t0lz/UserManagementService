import grpc
import sqlite3
from concurrent import futures
import time
import user_pb2
import user_pb2_grpc
from hashlib import sha256
import uuid


class UserService(user_pb2_grpc.UserServiceServicer):
    def __init__(self):
        self.conn = sqlite3.connect('users.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                passwordHash TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def CreateUser(self, request, context):
        user_id = str(uuid.uuid4())
        password_hash = sha256(request.passwordHash.encode('utf-8')).hexdigest()
        try:
            self.cursor.execute('''
                INSERT INTO users (id, name, email, passwordHash, role) 
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, request.name, request.email, password_hash, request.role))
            self.conn.commit()
            user = user_pb2.User(id=user_id, name=request.name, email=request.email, passwordHash=password_hash,
                                 role=request.role)
            return user_pb2.UserResponse(user=user)
        except sqlite3.IntegrityError:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("Пользователь с таким email уже существует")
            return user_pb2.UserResponse()

    def GetUser(self, request, context):
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (request.id,))
        user_row = self.cursor.fetchone()
        if user_row:
            user = user_pb2.User(id=user_row[0], name=user_row[1], email=user_row[2], passwordHash=user_row[3],
                                 role=user_row[4])
            return user_pb2.UserResponse(user=user)
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Пользователь не найден")
        return user_pb2.UserResponse()

    def UpdateUser(self, request, context):
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (request.id,))
        if not self.cursor.fetchone():
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Пользователь не найден")
            return user_pb2.UserResponse()
        password_hash = sha256(request.passwordHash.encode('utf-8')).hexdigest()
        self.cursor.execute('''
            UPDATE users SET name = ?, email = ?, passwordHash = ?, role = ? WHERE id = ?
        ''', (request.name, request.email, password_hash, request.role, request.id))
        self.conn.commit()

        user = user_pb2.User(id=request.id, name=request.name, email=request.email, passwordHash=password_hash,
                             role=request.role)
        return user_pb2.UserResponse(user=user)

    def DeleteUser(self, request, context):
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (request.id,))
        if not self.cursor.fetchone():
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Пользователь не найден")
            return user_pb2.Empty()
        self.cursor.execute('DELETE FROM users WHERE id = ?', (request.id,))
        self.conn.commit()
        return user_pb2.Empty()

    def ListUsers(self, request, context):
        self.cursor.execute('SELECT * FROM users')
        rows = self.cursor.fetchall()
        users = [
            user_pb2.User(id=row[0], name=row[1], email=row[2], passwordHash=row[3], role=row[4])
            for row in rows
        ]
        return user_pb2.ListUsersResponse(users=users)

    def Login(self, request, context):
        password_hash = sha256(request.passwordHash.encode('utf-8')).hexdigest()
        self.cursor.execute('SELECT * FROM users WHERE email = ? AND passwordHash = ?', (request.email, password_hash))
        user_row = self.cursor.fetchone()
        if user_row:
            return user_pb2.LoginResponse(token="dummy-jwt-token")
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        context.set_details("Неверные учетные данные")
        return user_pb2.LoginResponse()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Сервер запущен на порту 50051")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()