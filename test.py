import smtplib

my_email = "kelehsaev.2007@gmail.com"
my_password = "lfze nkkt xhuk rkhy"
smtpObj = smtplib.SMTP(host='smtp.gmail.com', port=587)
smtpObj.starttls()
smtpObj.login(my_email, my_password)
"<html><body><img src='logo.png'></img><p>Пользователь {name}<br>С почтой {email_address}<br>Оставил новую идею:<br>{idea_text}</p></body></html>"
templs = ["apodova@mail.ru"]
smtpObj.sendmail(my_email, templs,
                 "Здравствуйте, данное письмо является проверочным написаным с помощью Python кода, отвечать на него не нужно".encode(
                     'utf-8'))
smtpObj.quit()
