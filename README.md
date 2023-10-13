# Smart meters

Before the inception of smart electric meters, all tenants managed by a particular landlord used one energy meter and consequently, landlords set their rent fee inclusive of the estimated cost of electrical energy that will be used by a tenant. Different tenants consume different amounts of electricity and having flat fee charged on each tenant is cheaty. This is not only unfair to tenants but also sometimes unjust to the landlords because the estimated cost may be less.

This is where this system intervenes to address the predicaments of both the landlords and tenants. In collaboration with smart electric meter vendor companies, each tenant is given a registered energy meter. Each tenant can recharge their own meter(s) through a USSD code(*211#). The system also includes a pricing feature that allows landloards to set the price of one unit of energy(1KwH) and subsequently, they can maximize their earnings. In addtion to that, landlords can also keep track of their earnings(electricity bills paid by tenants), and cash it out through the system.

## Features

* Registration of managers (Landlords)
* Registration of Admnistrators
* Recharging meters
* Registration of meter vendors
* CRUD of meters
* CRUD of Users(Managers, Admins)
* Transaction history
* Recharge token history
* Landlord earnings collection, and cash out

## Running the application

### Install dependencies

`pip install -r requirements.txt`

### Set up the environment

Create a .env file in the `config` directory that defines variables in the `config/.env.example` file.

### Create a super admin user

A super admin user has the ultimate authority in the system. He is different from the Django super user. You will need a super admin account to CRUD all objects in the system.

`python manage.py createsuperadmin`

The prompts are similar to the ones presented to you when you run `python manage.py createsuperuser`

### Run the development server

`python manage.py runserver`

Access the application using a browser through the address: http://localhost:8000 and login using the credentials of the super admin you created in the preceding step.
