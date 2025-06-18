# pg_dump --schema-only -U postgres -h localhost -d dvd-rental > schema.sql
DDL_STR = """
CREATE TABLE actor (
    actor_id SERIAL PRIMARY KEY,
    first_name VARCHAR(45) NOT NULL,
    last_name VARCHAR(45) NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(25) NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE language (
    language_id SERIAL PRIMARY KEY,
    name CHAR(20) NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE film (
    film_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    release_year INTEGER,
    language_id SMALLINT NOT NULL REFERENCES language(language_id),
    rental_duration SMALLINT NOT NULL DEFAULT 3,
    rental_rate NUMERIC(4,2) NOT NULL DEFAULT 4.99,
    length SMALLINT,
    replacement_cost NUMERIC(5,2) NOT NULL DEFAULT 19.99,
    rating mpaa_rating DEFAULT 'G',
    last_update TIMESTAMP NOT NULL DEFAULT now(),
    special_features TEXT[],
    fulltext TSVECTOR NOT NULL
);

CREATE TABLE film_actor (
    actor_id SMALLINT NOT NULL REFERENCES actor(actor_id),
    film_id SMALLINT NOT NULL REFERENCES film(film_id),
    last_update TIMESTAMP NOT NULL DEFAULT now(),
    PRIMARY KEY (actor_id, film_id)
);

CREATE TABLE film_category (
    film_id SMALLINT NOT NULL REFERENCES film(film_id),
    category_id SMALLINT NOT NULL REFERENCES category(category_id),
    last_update TIMESTAMP NOT NULL DEFAULT now(),
    PRIMARY KEY (film_id, category_id)
);

CREATE TABLE country (
    country_id SERIAL PRIMARY KEY,
    country VARCHAR(50) NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE city (
    city_id SERIAL PRIMARY KEY,
    city VARCHAR(50) NOT NULL,
    country_id SMALLINT NOT NULL REFERENCES country(country_id),
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE address (
    address_id SERIAL PRIMARY KEY,
    address VARCHAR(50) NOT NULL,
    address2 VARCHAR(50),
    district VARCHAR(20) NOT NULL,
    city_id SMALLINT NOT NULL REFERENCES city(city_id),
    postal_code VARCHAR(10),
    phone VARCHAR(20) NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE staff (
    staff_id SERIAL PRIMARY KEY,
    first_name VARCHAR(45) NOT NULL,
    last_name VARCHAR(45) NOT NULL,
    address_id SMALLINT NOT NULL REFERENCES address(address_id),
    email VARCHAR(50),
    store_id SMALLINT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT true,
    username VARCHAR(16) NOT NULL,
    password VARCHAR(40),
    last_update TIMESTAMP NOT NULL DEFAULT now(),
    picture BYTEA
);

CREATE TABLE store (
    store_id SERIAL PRIMARY KEY,
    manager_staff_id SMALLINT NOT NULL REFERENCES staff(staff_id),
    address_id SMALLINT NOT NULL REFERENCES address(address_id),
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE customer (
    customer_id SERIAL PRIMARY KEY,
    store_id SMALLINT NOT NULL,
    first_name VARCHAR(45) NOT NULL,
    last_name VARCHAR(45) NOT NULL,
    email VARCHAR(50),
    address_id SMALLINT NOT NULL REFERENCES address(address_id),
    activebool BOOLEAN NOT NULL DEFAULT true,
    create_date DATE NOT NULL DEFAULT ('now'::text)::date,
    last_update TIMESTAMP DEFAULT now(),
    active INTEGER
);

CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    film_id SMALLINT NOT NULL REFERENCES film(film_id),
    store_id SMALLINT NOT NULL,
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE rental (
    rental_id SERIAL PRIMARY KEY,
    rental_date TIMESTAMP NOT NULL,
    inventory_id INTEGER NOT NULL REFERENCES inventory(inventory_id),
    customer_id SMALLINT NOT NULL REFERENCES customer(customer_id),
    return_date TIMESTAMP,
    staff_id SMALLINT NOT NULL REFERENCES staff(staff_id),
    last_update TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE payment (
    payment_id SERIAL PRIMARY KEY,
    customer_id SMALLINT NOT NULL REFERENCES customer(customer_id),
    staff_id SMALLINT NOT NULL REFERENCES staff(staff_id),
    rental_id INTEGER NOT NULL REFERENCES rental(rental_id),
    amount NUMERIC(5,2) NOT NULL,
    payment_date TIMESTAMP NOT NULL
);

CREATE TYPE mpaa_rating AS ENUM ('G', 'PG', 'PG-13', 'R', 'NC-17');
"""

DOCUMENT_STR = """
Business Terminology and Definitions for DVD Rental Database:

1. Film Attributes:
- Rental Duration: Number of days a film can be rented before late fees apply
- Rental Rate: Daily cost to rent a film (in USD)
- Replacement Cost: Amount charged if film is not returned (in USD)
- Rating: MPAA film rating (G, PG, PG-13, R, NC-17)

2. Inventory Management:
- In-Stock: Film is available when inventory_in_stock() returns TRUE
- Out-of-Stock: Film is rented out when inventory_in_stock() returns FALSE

3. Rental Operations:
- Active Customer: Customer with activebool = TRUE and at least one rental in past year
- Late Return: When return_date exceeds rental_date + rental_duration
- Overdue Fee: $1 per day late, plus replacement cost if >2x rental_duration

4. Financial Metrics:
- Customer Balance: Calculated by get_customer_balance() function
- Total Sales: Sum of all payment amounts by time period
- Store Revenue: Gross payments collected per store location

5. Performance Indicators:
- Film Popularity: Measured by rental frequency
- Category Performance: Sales by film category (see sales_by_film_category view)
- Staff Performance: Rental and payment processing volume per staff member

6. Customer Metrics:
- Loyalty Status: Based on monthly_purchases and dollar_amount_purchased
- Rewards Eligibility: Determined by rewards_report() function

7. Store Operations:
- Manager: Staff member with manager_staff_id in store table
- Inventory Count: Number of films per store (by inventory table)

8. Reporting Views:
- Film List: Shows films with actors and categories
- Customer List: Active customers with contact info
- Sales Reports: By store, category, and time period

Business Rules:
1. A film must belong to at least one category
2. A rental must be associated with a payment
3. Staff can only process payments for their own store
4. Customers with balance > $50 cannot rent new films
5. PG-13 rated films cannot be rented by customers under 13
"""

QUERIES_ARR = [
    """
    SELECT customer_id, first_name, last_name, email 
    FROM customer 
    WHERE activebool = TRUE 
    ORDER BY last_name, first_name
    """,
    """
    SELECT c.customer_id, c.first_name, c.last_name, 
           a.address, a.phone, city.city, country.country
    FROM customer c
    JOIN address a ON c.address_id = a.address_id
    JOIN city ON a.city_id = city.city_id
    JOIN country ON city.country_id = country.country_id
    WHERE c.customer_id = 123
    """,
    """
    SELECT f.film_id, f.title, f.rating, f.rental_rate, 
           COUNT(i.inventory_id) AS in_stock_count
    FROM film f
    JOIN inventory i ON f.film_id = i.film_id
    WHERE i.store_id = 1
    AND inventory_in_stock(i.inventory_id)
    GROUP BY f.film_id
    HAVING COUNT(i.inventory_id) > 0
    ORDER BY f.title
    """,
    """
    SELECT f.title, c.name AS category, f.rental_rate, f.rating
    FROM film f
    JOIN film_category fc ON f.film_id = fc.film_id
    JOIN category c ON fc.category_id = c.category_id
    WHERE f.rating = 'PG-13'
    AND f.rental_rate < 3.00
    ORDER BY f.title
    """,
    """
    SELECT r.rental_id, f.title, 
           r.rental_date, r.return_date,
           p.amount, p.payment_date
    FROM rental r
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film f ON i.film_id = f.film_id
    JOIN payment p ON r.rental_id = p.rental_id
    WHERE r.customer_id = 456
    ORDER BY r.rental_date DESC
    LIMIT 10
    """,
    """
    SELECT DATE_TRUNC('month', payment_date) AS month,
           SUM(amount) AS total_sales,
           COUNT(*) AS transaction_count
    FROM payment
    GROUP BY DATE_TRUNC('month', payment_date)
    ORDER BY month DESC
    """,
    """
    SELECT s.staff_id, s.first_name, s.last_name,
           COUNT(r.rental_id) AS rentals_processed,
           SUM(p.amount) AS payments_collected
    FROM staff s
    LEFT JOIN rental r ON s.staff_id = r.staff_id
    LEFT JOIN payment p ON s.staff_id = p.staff_id
    WHERE DATE_TRUNC('month', r.rental_date) = DATE_TRUNC('month', CURRENT_DATE)
    GROUP BY s.staff_id
    ORDER BY payments_collected DESC
    """,
    """
    SELECT s.store_id, 
           COUNT(DISTINCT c.customer_id) AS active_customers,
           COUNT(DISTINCT i.inventory_id) AS total_inventory,
           SUM(p.amount) AS monthly_revenue
    FROM store s
    LEFT JOIN customer c ON s.store_id = c.store_id AND c.activebool = TRUE
    LEFT JOIN inventory i ON s.store_id = i.store_id
    LEFT JOIN rental r ON i.inventory_id = r.inventory_id
    LEFT JOIN payment p ON r.rental_id = p.rental_id
    WHERE DATE_TRUNC('month', p.payment_date) = DATE_TRUNC('month', CURRENT_DATE)
    GROUP BY s.store_id
    """,
    """
    SELECT f.film_id, f.title, 
           COUNT(r.rental_id) AS rental_count,
           SUM(p.amount) AS total_revenue
    FROM film f
    JOIN inventory i ON f.film_id = i.film_id
    JOIN rental r ON i.inventory_id = r.inventory_id
    JOIN payment p ON r.rental_id = p.rental_id
    WHERE r.rental_date BETWEEN '2023-01-01' AND '2023-12-31'
    GROUP BY f.film_id
    ORDER BY rental_count DESC
    LIMIT 10
    """,
    """
    SELECT c.customer_id, 
           c.first_name || ' ' || c.last_name AS customer_name,
           COUNT(r.rental_id) AS total_rentals,
           SUM(p.amount) AS total_spending,
           get_customer_balance(c.customer_id, CURRENT_DATE) AS current_balance
    FROM customer c
    JOIN rental r ON c.customer_id = r.customer_id
    JOIN payment p ON r.rental_id = p.rental_id
    WHERE c.activebool = TRUE
    GROUP BY c.customer_id
    ORDER BY total_spending DESC
    LIMIT 20
    """
]