<p align=center><img src=_src/assets/official_logo.png><p>

# <h1 align=center> **REST API for an Elevator Dataset Generator** </h1>

# Introduction

This repository aims to create an API to track an elevator status in order to create a dataset that will be used for a prediction engine. The information is stored in PostgreSQL database. It also contains a synthetic data generator that create a table with information of the floor that it was demanded, the floor that will go and the timestamp.

# Run the code

This code was developed using Python 3.10.12.

## Set environment variables

The first thing you have to do in order to run the code is to create a `.env` file with the following content:

```
# Database connection
DB_NAME=<database-name>
DB_USER=<username>
DB_PASS=<password>
DB_HOST=<ip addr>
DB_PORT=<db port>
```

Example:
```
# Database connection
DB_NAME=test1
DB_USER=citric
DB_PASS=citric
DB_HOST=localhost
DB_PORT=5432
```

>Note: Take in mind that DB_USER, DB_NAME and DB_PASS environment variable must be the same that variables defined in `docker-compose.yml` file named POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB.

## Virtual environment

Create a vrtual environment in order to install all the dependencies.

```
virtualenv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Run PostgreSQL

In order to run the following code it is necesary to run PostgreSQL using the `docker-compose.yml` file provided in the repository.

### Running the docker container

```
docker compose up -d --build
```

## Run the API

To run the API service:

```
uvicorn api.main:app --reload
```

To access the API locally http://127.0.0.1:8000/docs.
There you can find all the API documentation and endpoints.

### API endpoints

The API contains the following topics:

- Elevator:
    - Get all elements of the database
    - Create a new element
    - Get an element by ID
    - Update an element by ID
    - Delete an element by ID

The elevator endpoints are the following:

<p align=center><img src=_src/assets/api.png><p> 


## Load database

The script to load the database has diffent parameters. Run the following code to see the parameters:

```
python3 load_database.py -h
```

* -t, --total_floor: Total building floor. Default value **10**.
* -d, --data_lenght: Data lenght to store in DB. Default value **20**.
* -n, --min_num_people: Minimun number of people per floor. Default value **1**.
* -o, --max_num_people: Maximun number of people per floor. Default value **10**.
* -p, --min_avg_age: Minimun average age per floor. Default value **18**.
* -q, --max_avg_age: Maximun average age per floor. Default value **90**.


Run the script to load the database with default parameters:

```
python3 load_database.py
```

Run the script to load the database with custom parameters:

```
 python3 load_database.py -t 20 -d 5000 -n 12 -o 15 -p 20 -q 75
```


# Download dataset

In order to get the whole dataset you can get all the elements of the database and click download.

<p align=center><img src=_src/assets/database.png><p>


# Synthetic dataset generation script code explanation

## Step 1

The business rules and entry parameters are loaded in constants variables.

## Step 2

Create a random list that contains an average of people living in each floor. A floor with more people is more likely to be used than floors with low people. Minimun and maximun amount of people are entry values or they can be used the default values. Min 1, Max 10.

<p align=center><img src=_src/assets/people_list.png><p>

## Step 3

Create a random list that contains an age average of people living in each floor. A floor with people that exceed a limit age the elevator frequency use goes down compared with floors with younger people. Minimun and maximun age average are entry values or they can be used the default values. Min 18, Max 90.

<p align=center><img src=_src/assets/age_list.png><p>

## Step 4

A weight list is created using a business rules **weight_floot_0**. The ground floor is more likely to be used than the other floors because everybody goes to that floor. This weight represent the probability to appear in the list of probable floors.<br> 

Example:<br>
weight_floot_0 = 0.5<br>
**1-weight_floot_0** = 0.5 is divided into the amount of floor and it is loaded into the probabilities floor list.

<p align=center><img src=_src/assets/weight_floor.png><p>

>Note 1: This list will be used to generate a random list of floor that people go based on this list of probabilities. It will be used a Numpy function called [Choice](https://numpy.org/doc/stable/reference/random/generated/numpy.random.choice.html).

### Step 4.1

It has added the option of a garage floor.To represent this floor a new business rule has added with the name **weight_garage_1**. If this value is equal to 0 means that there isn´t a garage floor, otherwise, if this value is greater than 0 there is a garage and the array is as follow.

<p align=center><img src=_src/assets/garage.png><p>

## Step 5

A weight list is created taking into account the amount of people living per floor.

<p align=center><img src=_src/assets/weight_avg_people.png><p>

## Step 6

A weight list is created taking into account the average people age living per floor.
For this list will be used the following business rules:

- **weight_young**: The young people is more likely to use the elevator because are more active than eldest. This weight is used to calculate the following factors:<br>
**factor_old** = (1 - weight_young) / (Amount of floor that average people age exceed an age limit (old_people_limit))<br>
**factor_young** = weight_young / (Amount of floor that average people age **does not** exceed an age limit)

- **old_people_limit**: People older than this limit is considered old. The elevator use frequency decrease

For this example:<br>
weight_young: 0.7<br>
old_people_limit: 60<br>
factor_old = (1 - 0.7) / 5 where 5 is for Floor 1, 3, 4, 7 and 9<br>
factor_young = 0.7 / 5 where 5 is for Floor 2, 5, 6, 8 and 10<br>

<p align=center><img src=_src/assets/weight_avg_age.png><p>

## Step 7

Create a list of probable next floor. To create this list will be used the weight list created in step 4.

Dataset lenght = 10 values

<p align=center><img src=_src/assets/next_floor.png><p>

>Note: Due to the high probability value of ground floor in the weight floor list, the value 0 predominates.

## Step 8

Create a demanding floor list. To create this list will be used the weight list created in step 4, 5 and 6. It will create an intermediate weight list that will contain the sum of each factor per floor affected by a new weight set them in the business rules.<br>
Each factor of this list will be done as follow:

Example floor 0:<br>
```
weight_demanding_floor[0] = weight_floor[0] * WEIGHT_FLOOR + weight_avg_people[0] * WEIGHT_PEOPLE + weigth_avg_age[0] * WEIGHT_AGE
```

Where:<br>
WEIGHT_FLOOR: Defined as 0.5 in business rules file. This weight means that the weight floor list is the 50% of the total list.<br>
WEIGHT_PEOPLE: Defined as 0.3 in business rules file. This weight means that the weight people per floor list is the 30% of the total list.<br>
WEIGHT_AGE: Defined as 0.2 in business rules file. This weight means that the weight avg people age per floor list is the 20% of the total list.<br>

To create this list also takes into account that the elevator cannot be called from the same floor. For this condition it will be used the next floor list created in step 7.

Dataset lenght = 10 values

<p align=center><img src=_src/assets/demand_list.png><p>

>Note: The floor 10 is the one which is more frequent due to the amount of people living there and the average age per floor is under the limit of 60 years old, so, it is considered that young people live there.

## Step 9

Create a list of secuenced timestamp. 

## Step 10

Load the dataset in the database with the following columns:

- Next floor
- Demaning floor
- Timestamp


# Testing

To test the API endpoint run the following command:

```
pytest
```

This will test the endpoint to create a new element in the database and the endpoint to delete a component of the database.

# Testing automation

This solution provides a testing automation pipeline in `.github/workflows` folder. This script will be launched in every pull and push request.

This pipeline need to configure `Secrets and variables` in github.

The secrets must be the same as set in the `.env` file, previously explained.

## Secrets and varaible configuration

Github -> Settings -> Secrets and variables -> Actions -> New repository secret

```
DB_NAME=<database-name>
DB_USER=<username>
DB_PASS=<password>
DB_HOST=<ip addr>
DB_PORT=<db port>
```
