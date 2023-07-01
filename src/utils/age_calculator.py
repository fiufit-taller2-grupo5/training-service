from datetime import datetime

def calculate_age(birthdate):
    # Convert birthdate string to datetime object
    birthdate = datetime.strptime(birthdate, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Get the current date and time
    current_date = datetime.now()

    # Calculate the difference between the current date and the birthdate
    age = current_date.year - birthdate.year

    # Check if the birthdate has not yet occurred this year
    if current_date.month < birthdate.month:
        age -= 1
    elif current_date.month == birthdate.month and current_date.day < birthdate.day:
        age -= 1

    return age