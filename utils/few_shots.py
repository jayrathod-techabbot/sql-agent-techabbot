shots = [
    {
        "Question": "List the customer name",
        "SQLQuery": "SELECT name FROM customer LIMIT 5",
        "SQLResult": "[('Alice Johnson',), ('Bob Smith',), ('Charlie Brown',), ('Diana Prince',), ('Ethan Hunt',)]",
        "Answer": "The customer names are Alice Johnson, Bob Smith, Charlie Brown, Diana Prince, and Ethan Hunt.",
    },
    {
        "Question": "Revenue for the Last 3 Years",
        "SQLQuery": "SELECT SUM(amount) AS last_3_year_revenue FROM invoice WHERE invoice_date >= CURDATE() - INTERVAL 3 YEAR;",
        "SQLResult": "130600",
        "Answer": "The total revenue for the last 3 years is 130600.",
    },
    {
        "Question": "which product is sold most in last 6 months?.",
        "SQLQuery": "SELECT ol.product, SUM(ol.qty) AS total_qty FROM order_line ol JOIN order_header oh ON ol.order_id = oh.order_id WHERE oh.order_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)  and oh.status = 'completed' GROUP BY ol.product ORDER BY total_qty DESC ;",
        "SQLResult": "[]",
        "Answer": "No products have been sold in the last 6 months.",
    },
    {
        "Question": "which product is sold most in last 18 months?",
        "SQLQuery": "SELECT ol.product, SUM(ol.qty) AS total_qty FROM order_line ol JOIN order_header oh ON ol.order_id = oh.order_id WHERE oh.order_date BETWEEN DATE_SUB('2025-12-09', INTERVAL 18 MONTH) AND '2025-12-09' GROUP BY ol.product ORDER BY total_qty DESC LIMIT 1;",
        "SQLResult": "[('Wireless Mouse',29)]",
        "Answer": "The product sold most in the last 18 months is Wireless Mouse (29 units).",
    },
]
