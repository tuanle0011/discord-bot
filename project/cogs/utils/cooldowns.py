# utils/cooldowns.py
# Hiện tại, các cooldown được xử lý trực tiếp bởi @commands.cooldown decorator.
# Nếu bạn cần một hệ thống cooldown phức tạp hơn hoặc tùy chỉnh,
# bạn có thể thêm các hàm vào đây. Ví dụ:

# import datetime
# cooldowns = {}

# def is_on_cooldown(user_id, command_name, duration=3):
#     now = datetime.datetime.now().timestamp()
#     if user_id not in cooldowns:
#         cooldowns[user_id] = {}
#     return command_name in cooldowns[user_id] and now - cooldowns[user_id][command_name] < duration

# def apply_cooldown(user_id, command_name, duration=3):
#     if user_id not in cooldowns:
#         cooldowns[user_id] = {}
#     cooldowns[user_id][command_name] = datetime.datetime.now().timestamp()

# Đối với bot của bạn, bạn đã xử lý cooldown trong on_command_error và các @commands.cooldown decorator.
# Nên file này có thể trống hoặc không cần thiết lúc này.
