USE `crm_demo`;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `account_addresses`;
DROP TABLE IF EXISTS `account_status_history`;
DROP TABLE IF EXISTS `account_tags`;
DROP TABLE IF EXISTS `activities`;
DROP TABLE IF EXISTS `activity_participants`;
DROP TABLE IF EXISTS `case_comments`;
DROP TABLE IF EXISTS `case_status_history`;
DROP TABLE IF EXISTS `contact_addresses`;
DROP TABLE IF EXISTS `contact_tags`;
DROP TABLE IF EXISTS `contract_lines`;
DROP TABLE IF EXISTS `customer_health_scores`;
DROP TABLE IF EXISTS `email_events`;
DROP TABLE IF EXISTS `email_messages`;
DROP TABLE IF EXISTS `invoice_lines`;
DROP TABLE IF EXISTS `knowledge_articles`;
DROP TABLE IF EXISTS `lead_conversions`;
DROP TABLE IF EXISTS `meeting_attendees`;
DROP TABLE IF EXISTS `meetings`;
DROP TABLE IF EXISTS `notes`;
DROP TABLE IF EXISTS `price_book_items`;
DROP TABLE IF EXISTS `quote_items`;
DROP TABLE IF EXISTS `renewals`;
DROP TABLE IF EXISTS `satisfaction_surveys`;
DROP TABLE IF EXISTS `tags`;
DROP TABLE IF EXISTS `tasks`;

SET FOREIGN_KEY_CHECKS = 1;
