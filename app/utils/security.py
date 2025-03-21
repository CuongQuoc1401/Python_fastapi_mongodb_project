# Trong ứng dụng thực tế, bạn nên sử dụng thư viện hashing (ví dụ: bcrypt)
# để mã hóa mật khẩu thay vì lưu trữ mật khẩu thuần túy.
def verify_password(stored_password, provided_password):
    return stored_password == provided_password