# Smart meters

Landlords tend to have difficulties managing tenants regarding utility payments. This application centralizes the
management of electric meters through allowing managers create logical groups of meters, 
explicitly set their electric prices and handle meter recharging.

## Features
* Registration of managers (Landlords)
* Registration of Super admins and admins
* Recharge meters
* CRUD of meters
* CRUD of Users
* Payment logs
* Meter recharge token log
* Discern percentage of profits that goes to the managers and the system (Service providers)

## Running the application
`pip install -r requirements.txt`
`python manage.py runserver`

Interact with application through web browser from: http://localhost:8000/