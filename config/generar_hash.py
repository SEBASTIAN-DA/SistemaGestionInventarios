from bcrypt import hashpw, gensalt

password = "123456".encode("utf-8")
hashed = hashpw(password, gensalt())

print(hashed.decode())  