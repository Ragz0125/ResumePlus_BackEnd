from utils import mailjet

def send_email(user, subject: str, body: str):
    
    print(user.email)
    data = {
        "Messages": [
            {
                "From": {
                    "Email": "raghav.rajaraman@gmail.com",
                    "Name": "Recruiter via ResumePlus"
                },
                "To": [
                    {
                        "Email": "raghav.rajaraman@gmail.com",
                        "Name": "Raghav Rajaraman"
                    }
                ],
                "ReplyTo": {
                    "Email": user.email,
                    "Name": ""
                },
                "Subject": subject,
                "TextPart": body,
            }
        ]
    }

    result = mailjet.send.create(data=data)

    print("Status:", result.status_code)
    print("Response object:", result)
    print("Response text:", result.text)
    print("Response content:", result.content)

    return {
        "success": result.status_code in [200, 201],
        "message": "Email sent successfully"
    }