I would like to generate an ER diagram where there are the following tables:
orders, payments, payout, payment_methods_dim, psp_dim, customer_dim. 

- The `orders` table should include: `order_id` (PK), `order_amount`, `order_date`, `customer_id` (FK), and `payment_method` (FK).
- The `payments` table should include: `payment_id` (PK), a unique `transaction_key`, `payment_method_id` (FK), and `psp_id` (FK).
- The `payout` table should include: `payment_id` (FK), `amount`, and `payout_date`.
- The `payment_methods_dim` table should include: `id` (PK) and `method_name`.
- The `psp_dim` table should include: `id` (PK) and `psp_name`.
- The `customer_dim` table should include: `customer_id` (PK), `customer_name`, and `email`.

Please generate the ER diagram using Mermaid.js syntax with the following structure:
- Use `erDiagram` as the starting keyword.
- Define entities with their attributes inside curly braces.
- Use `"PK"` and `"FK"` in quotes to mark primary and foreign keys.
- Define relationships between entities with proper cardinality and labels.