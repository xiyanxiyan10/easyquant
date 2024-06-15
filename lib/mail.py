import smtplib
from email.mime.text import MIMEText

def qq_mail_send(sender, receivers, password, subject, content):

    # 向本地开发邮件服务器发送一条简单的文本信息

    # 发送者的邮箱  example.com是专门用于文档中的说明性示例的域名
    #sender = '931762054@qq.com'
    #password = 'xnsgcuuavelrbbdj'   # 发送者邮箱的授权码
    # 接收者的邮箱，接收者可以是多个，因此是一个列表
    #receivers = ['shliang0603@gmail.com']

    # 发送到服务器的文本信息
    #subject = '这个是邮件主题'
    #content = '这是使用python smtplib及email模块发送的邮件'
    msg = MIMEText(content)
    # print(msg, type(msg))  # This is test mail <class 'email.mime.text.MIMEText'>

    # msg['Subject']是发送邮件的主题
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receivers[0]


    # 发送邮件时qq邮箱，对应qq邮箱服务器域名时smtp.qq.com  对应端口时465
    with smtplib.SMTP_SSL(host='smtp.qq.com', port=465) as server:
        # 登录发送者的邮箱
        server.login(sender, password)

        # 开始发送邮件
        server.sendmail(sender, receivers, msg.as_string())
        #print("Successfully sent email")

if __name__ == '__main__':
    qq_mail_send('873706510@qq.com', ['873706510@qq.com'], 'rplqrvhknxgmbbdb', 'hudgegride', '3333-2222')
