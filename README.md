# Sales-manager
Sales-manager repo

This is a personal project. I sell some catalog products and need some automatation to generate reports and compute orders. So, I developed this simple project to help me in these tasks according to my needs. It is still being improved.

## Data format:
*Obs:* all files are used as *.tsv* instead of *.csv*
### clients.csv
Columns: `id`, `name`,	`revendor_id`

### brands.csv
Columns: `id`, `name`,	`profit`

### campaigns.csv
Columns: `id`,	`brand_id`,	`description`,	`request_date`,	`delivery_date`,	`catalog_request_date`,	`catalog_delivery_date`

### discounts.csv
Columns: `client_id`,	`brand_id`,	`discount`

### items.csv
Columns: `id`,	`campaign_id`,	`client_id`,	`product_id`,	`discount`,	`quantity`,	`status`

### products.csv
Columns: `id`,	`brand_id`,	`campaign_id`,	`page`,	`code`,	`description`,	`cost_price`,	`sale_price,`	`profit`

### revendors.csv
Columns: `id`,	`name`
