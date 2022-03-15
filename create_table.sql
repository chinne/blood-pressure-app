CREATE TABLE IF NOT EXISTS puls_data (
	'date' timestamp,
	'time' text,
	systolic smallint,
	diastolic smallint,
	pulse smallint,
	notes text,
	measurement_method text,
	row_hash text,
    last_update timestamp default now()
);