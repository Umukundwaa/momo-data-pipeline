DROP DATABASE IF EXISTS momo_data_pipeline;
CREATE DATABASE momo_data_pipeline;
USE momo_data_pipeline;

CREATE TABLE `users` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Primary key — auto increments',
  `phone_number` VARCHAR(20) UNIQUE NOT NULL COMMENT 'MoMo phone number — unique per user',
  `full_name` VARCHAR(64) COMMENT 'Full name if available from SMS body',
  `account_type` VARCHAR(16) NOT NULL DEFAULT 'personal' COMMENT 'personal | merchant | bank — identifies the type of MoMo account',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when user was first seen in the system'
);

CREATE TABLE `transaction_categories` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Primary key — auto increments',
  `category_name` VARCHAR(64) NOT NULL COMMENT 'Human readable name e.g. Incoming Money',
  `category_code` VARCHAR(16) UNIQUE NOT NULL COMMENT 'Short code used in ETL logic e.g. INCOMING | TRANSFER | PAYMENT | BANK | AIRTIME | FEE | OTHER',
  `description` TEXT COMMENT 'Detailed explanation of what this category means and how it is identified from SMS text',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when category was added'
);

CREATE TABLE `transactions` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Primary key — auto increments',
  `user_id` INT NOT NULL COMMENT 'FK → users — the main account holder involved in this transaction',
  `category_id` INT NOT NULL COMMENT 'FK → transaction_categories — the type of this transaction',
  `transaction_ref` VARCHAR(64) UNIQUE NOT NULL COMMENT 'Unique MoMo transaction ID extracted from SMS e.g. TXN123456789',
  `amount` DECIMAL(15,2) NOT NULL COMMENT 'Transaction amount in RWF — stored as decimal for precision',
  `fee` DECIMAL(10,2) DEFAULT 0 COMMENT 'Transaction fee charged by MTN in RWF — 0 if no fee',
  `sender_phone` VARCHAR(20) COMMENT 'Normalized phone number of the sender — extracted from SMS body',
  `receiver_phone` VARCHAR(20) COMMENT 'Normalized phone number of the receiver — extracted from SMS body',
  `transaction_date` DATETIME NOT NULL COMMENT 'Original date and time of the transaction from SMS — normalized by clean_normalize.py',
  `raw_sms_body` TEXT COMMENT 'Original unmodified SMS message text — kept for debugging and reprocessing',
  `status` VARCHAR(16) NOT NULL DEFAULT 'completed' COMMENT 'completed | failed | pending — transaction outcome',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when this record was inserted into the database by load_db.py',
CHECK (`amount` > 0)
);

CREATE TABLE `system_logs` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Primary key — auto increments',
  `transaction_id` INT COMMENT 'FK → transactions — NULL if log is not related to a specific transaction',
  `log_level` VARCHAR(16) NOT NULL COMMENT 'INFO | WARNING | ERROR — severity of the log entry',
  `process_name` VARCHAR(64) NOT NULL COMMENT 'Name of the ETL script that generated this log e.g. parse_xml | clean_normalize | categorize | load_db',
  `message` TEXT NOT NULL COMMENT 'Detailed description of what happened — error message or success confirmation',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when this log entry was created'
);

CREATE TABLE `tags` (
  `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Primary key — auto increments',
  `tag_name` VARCHAR(32) UNIQUE NOT NULL COMMENT 'Short label applied to transactions e.g. large-amount | frequent-sender | suspicious | weekend | recurring',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when this tag was created'
);

CREATE TABLE `transaction_tags` (
  `transaction_id` INT NOT NULL COMMENT 'FK → transactions — which transaction this tag belongs to',
  `tag_id` INT NOT NULL COMMENT 'FK → tags — which tag is being applied',
  PRIMARY KEY (`transaction_id`, `tag_id`)
);

CREATE UNIQUE INDEX `idx_users_phone` ON `users` (`phone_number`);

CREATE INDEX `idx_users_account_type` ON `users` (`account_type`);

CREATE UNIQUE INDEX `idx_categories_code` ON `transaction_categories` (`category_code`);

CREATE INDEX `idx_categories_name` ON `transaction_categories` (`category_name`);

CREATE UNIQUE INDEX `idx_transactions_ref` ON `transactions` (`transaction_ref`);

CREATE INDEX `idx_transactions_user` ON `transactions` (`user_id`);

CREATE INDEX `idx_transactions_category` ON `transactions` (`category_id`);

CREATE INDEX `idx_transactions_date` ON `transactions` (`transaction_date`);

CREATE INDEX `idx_transactions_status` ON `transactions` (`status`);

CREATE INDEX `idx_transactions_sender` ON `transactions` (`sender_phone`);

CREATE INDEX `idx_transactions_receiver` ON `transactions` (`receiver_phone`);

CREATE INDEX `idx_logs_transaction_id` ON `system_logs` (`transaction_id`);

CREATE INDEX `idx_logs_level` ON `system_logs` (`log_level`);

CREATE INDEX `idx_logs_process` ON `system_logs` (`process_name`);

CREATE INDEX `idx_logs_created_at` ON `system_logs` (`created_at`);

CREATE UNIQUE INDEX `idx_tags_name` ON `tags` (`tag_name`);

CREATE INDEX `idx_tt_transaction` ON `transaction_tags` (`transaction_id`);

CREATE INDEX `idx_tt_tag` ON `transaction_tags` (`tag_id`);

ALTER TABLE `users` COMMENT = 'Stores every unique phone number involved in MoMo transactions — both senders and receivers. A user is created the first time their phone number appears in the XML data. account_type distinguishes personal wallets from merchant codes and bank accounts.';

ALTER TABLE `transaction_categories` COMMENT = 'Lookup table seeded once with all MoMo transaction types. The ETL categorize.py script reads SMS body text and assigns one of these categories to every transaction. category_code is used in application logic; category_name is shown on the dashboard.';

ALTER TABLE `transactions` COMMENT = 'Core table of the entire system. Every MoMo SMS message becomes one row here after passing through the ETL pipeline. transaction_ref ensures no duplicate records are inserted (upsert logic in load_db.py). raw_sms_body is stored for auditability and allows reprocessing if categorization logic changes.';

ALTER TABLE `system_logs` COMMENT = 'Tracks everything the ETL pipeline does. Every time a script runs it writes here — successes, warnings, and errors. log_level = ERROR means a transaction failed to process and may appear in dead_letter/. log_level = WARNING means data was suspicious but still processed. This table is the digital version of etl.log file.';

ALTER TABLE `tags` COMMENT = 'Flexible labeling system for transactions. Tags allow multiple labels on a single transaction without changing the main schema. Examples: large-amount (over 100,000 RWF), suspicious (unusual pattern), recurring (same sender every week). One tag can be applied to many transactions — this is one side of the M:N relationship.';

ALTER TABLE `transaction_tags` COMMENT = 'Junction table that resolves the Many-to-Many relationship between transactions and tags. One transaction can have many tags. One tag can belong to many transactions. This table holds only foreign keys — no extra data needed. The composite primary key (transaction_id + tag_id) prevents duplicate tag.';

ALTER TABLE `transactions` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `transactions` ADD FOREIGN KEY (`category_id`) REFERENCES `transaction_categories` (`id`);

ALTER TABLE `system_logs` ADD FOREIGN KEY (`transaction_id`) REFERENCES `transactions` (`id`);

ALTER TABLE `transaction_tags` ADD FOREIGN KEY (`transaction_id`) REFERENCES `transactions` (`id`);

ALTER TABLE `transaction_tags` ADD FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`);

-- SAMPLE DATA

INSERT INTO users (phone_number, full_name, account_type)
VALUES
('0788000001','Alice Uwase','personal'),
('0788000002','Bob Mugisha','personal'),
('0788000003','MTN Store Kigali','merchant'),
('0788000004','BK Bank','bank'),
('0788000005','Eric Ndayisaba','personal');


INSERT INTO transaction_categories
(category_name, category_code, description)
VALUES
('Incoming Money','INCOMING','Received money'),
('Transfer','TRANSFER','Sent money'),
('Payment','PAYMENT','Merchant payment'),
('Bank Transfer','BANK','Bank deposit/withdrawal'),
('Airtime Purchase','AIRTIME','Bought airtime');


INSERT INTO transactions
(user_id, category_id, transaction_ref,
 amount, fee, sender_phone,
 receiver_phone, transaction_date,
 raw_sms_body, status)
VALUES
(1,1,'TXN001',5000,0,'0788000002','0788000001',
'2026-05-18 09:00:00',
'You have received 5000 RWF from Bob',
'completed'),

(2,2,'TXN002',3000,30,'0788000002','0788000005',
'2026-05-18 10:00:00',
'You sent 3000 RWF to Eric',
'completed'),

(3,3,'TXN003',12000,100,'0788000001','0788000003',
'2026-05-18 11:00:00',
'Payment to merchant',
'completed'),

(4,4,'TXN004',50000,0,'0788000004','0788000001',
'2026-05-18 12:00:00',
'Bank transfer successful',
'pending'),

(5,5,'TXN005',1000,0,'0788000005','MTN',
'2026-05-18 13:00:00',
'Airtime purchase',
'failed');


INSERT INTO system_logs
(transaction_id, log_level, process_name, message)
VALUES
(1,'INFO','parse_xml','Transaction parsed successfully'),
(2,'INFO','clean_normalize','Phone numbers normalized'),
(3,'INFO','categorize','Transaction categorized'),
(4,'WARNING','load_db','Pending confirmation'),
(5,'ERROR','load_db','Transaction failed');


INSERT INTO tags (tag_name)
VALUES
('large-amount'),
('suspicious'),
('weekend'),
('recurring'),
('frequent-sender');


INSERT INTO transaction_tags
(transaction_id, tag_id)
VALUES
(1,3),
(2,4),
(3,1),
(4,2),
(5,5);
