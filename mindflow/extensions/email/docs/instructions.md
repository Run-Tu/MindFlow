# EMAIL APP
email = Email()
status = email.send("run-tu", title, content) # Sends an email to recipient
print(status) # {"state": "success"}
