/* ============================================================================
   SQL SERVER SCHEMA DISCOVERY TOOLKIT

   Read-only templates for investigating an unfamiliar relational schema.
   Every object name and searched value below is a fictional placeholder.
   Use only with an authorized read-only account.
   ============================================================================ */


/* BLOCK 1 -- Column inventory ------------------------------------------------
   Confirm the columns and declared types for one table.
*/
DECLARE @schema1 SYSNAME = 'YOUR_SCHEMA';
DECLARE @table1  SYSNAME = 'YOUR_TABLE';

SELECT
    ORDINAL_POSITION,
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = @schema1
  AND TABLE_NAME = @table1
ORDER BY ORDINAL_POSITION;
GO


/* BLOCK 2 -- Bounded row inspection -----------------------------------------
   Inspect a small sample for a key already understood through an authorized
   source. The searched value is parameterized.
*/
DECLARE @schema2 SYSNAME = 'YOUR_SCHEMA';
DECLARE @table2  SYSNAME = 'YOUR_TABLE';
DECLARE @keycol2 SYSNAME = 'YOUR_KEY_COLUMN';
DECLARE @keyval2 NVARCHAR(100) = 'YOUR_KNOWN_KEY';

DECLARE @sql2 NVARCHAR(MAX) =
    'SELECT TOP (50) * FROM ' + QUOTENAME(@schema2) + '.' + QUOTENAME(@table2) +
    ' WHERE ' + QUOTENAME(@keycol2) + ' = @value';

EXEC sp_executesql @sql2, N'@value NVARCHAR(100)', @value = @keyval2;
GO


/* BLOCK 3 -- Value search within one table ----------------------------------
   Find text columns containing a known value when its field is unknown.
*/
DECLARE @schema3 SYSNAME = 'YOUR_SCHEMA';
DECLARE @table3 SYSNAME = 'YOUR_TABLE';
DECLARE @searchval3 NVARCHAR(100) = 'YOUR_KNOWN_VALUE';
DECLARE @sql3 NVARCHAR(MAX) = '';

SELECT @sql3 = @sql3 +
    'SELECT ''' + REPLACE(COLUMN_NAME, '''', '''''') + ''' AS found_in_column, ' +
    'COUNT(*) AS hits FROM ' + QUOTENAME(@schema3) + '.' + QUOTENAME(@table3) +
    ' WHERE ' + QUOTENAME(COLUMN_NAME) + ' = @value HAVING COUNT(*) > 0 UNION ALL '
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = @schema3
  AND TABLE_NAME = @table3
  AND DATA_TYPE IN ('nvarchar', 'varchar', 'char', 'nchar');

IF LEN(@sql3) > 10
BEGIN
    SET @sql3 = LEFT(@sql3, LEN(@sql3) - 10);
    EXEC sp_executesql @sql3, N'@value NVARCHAR(100)', @value = @searchval3;
END
ELSE
    SELECT 'No candidate text columns found' AS result;
GO


/* BLOCK 4 -- Filtered value search across a schema --------------------------
   This can be expensive. Set a narrow table-name pattern before execution.
*/
DECLARE @schema4 SYSNAME = 'YOUR_SCHEMA';
DECLARE @searchval4 NVARCHAR(100) = 'YOUR_KNOWN_VALUE';
DECLARE @table_pattern4 NVARCHAR(100) = 'YOUR_TABLE_PREFIX%';
DECLARE @sql4 NVARCHAR(MAX) = '';

SELECT @sql4 = @sql4 +
    'SELECT ''' + REPLACE(c.TABLE_NAME, '''', '''''') + ''' AS table_name, ' +
    '''' + REPLACE(c.COLUMN_NAME, '''', '''''') + ''' AS column_name, ' +
    'COUNT(*) AS hits FROM ' + QUOTENAME(c.TABLE_SCHEMA) + '.' + QUOTENAME(c.TABLE_NAME) +
    ' WHERE ' + QUOTENAME(c.COLUMN_NAME) + ' = @value HAVING COUNT(*) > 0 UNION ALL '
FROM INFORMATION_SCHEMA.COLUMNS AS c
JOIN INFORMATION_SCHEMA.TABLES AS t
  ON t.TABLE_SCHEMA = c.TABLE_SCHEMA
 AND t.TABLE_NAME = c.TABLE_NAME
 AND t.TABLE_TYPE = 'BASE TABLE'
WHERE c.TABLE_SCHEMA = @schema4
  AND c.TABLE_NAME LIKE @table_pattern4
  AND c.DATA_TYPE IN ('nvarchar', 'varchar', 'char', 'nchar')
  AND c.CHARACTER_MAXIMUM_LENGTH >= LEN(@searchval4);

IF LEN(@sql4) > 10
BEGIN
    SET @sql4 = LEFT(@sql4, LEN(@sql4) - 10);
    EXEC sp_executesql @sql4, N'@value NVARCHAR(100)', @value = @searchval4;
END
ELSE
    SELECT 'No candidate columns matched the filter' AS result;
GO


/* BLOCK 5 -- Table-name search ----------------------------------------------
   Locate candidate objects before assuming a documented name exists.
*/
DECLARE @schema5 SYSNAME = 'YOUR_SCHEMA';
DECLARE @fragment5 NVARCHAR(100) = 'YOUR_FRAGMENT';

SELECT TABLE_SCHEMA, TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = @schema5
  AND TABLE_TYPE = 'BASE TABLE'
  AND TABLE_NAME LIKE '%' + @fragment5 + '%'
ORDER BY TABLE_NAME;
GO


/* BLOCK 6 -- Text-column population profile ---------------------------------
   Report fill rate and distinct cardinality for text columns.
*/
DECLARE @schema6 SYSNAME = 'YOUR_SCHEMA';
DECLARE @table6 SYSNAME = 'YOUR_TABLE';
DECLARE @sql6 NVARCHAR(MAX) = '';

SELECT @sql6 = @sql6 +
    'SELECT ''' + REPLACE(COLUMN_NAME, '''', '''''') + ''' AS column_name, ' +
    'COUNT(*) AS total_rows, ' +
    'SUM(CASE WHEN ' + QUOTENAME(COLUMN_NAME) + ' IS NULL OR LTRIM(RTRIM(' +
    QUOTENAME(COLUMN_NAME) + ')) = '''' THEN 0 ELSE 1 END) AS populated_rows, ' +
    'CAST(100.0 * SUM(CASE WHEN ' + QUOTENAME(COLUMN_NAME) +
    ' IS NULL OR LTRIM(RTRIM(' + QUOTENAME(COLUMN_NAME) +
    ')) = '''' THEN 0 ELSE 1 END) / NULLIF(COUNT(*), 0) AS DECIMAL(5,1)) AS fill_pct, ' +
    'COUNT(DISTINCT ' + QUOTENAME(COLUMN_NAME) + ') AS distinct_values ' +
    'FROM ' + QUOTENAME(@schema6) + '.' + QUOTENAME(@table6) + ' UNION ALL '
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = @schema6
  AND TABLE_NAME = @table6
  AND DATA_TYPE IN ('nvarchar', 'varchar', 'char', 'nchar');

IF LEN(@sql6) > 10
BEGIN
    SET @sql6 = LEFT(@sql6, LEN(@sql6) - 10);
    SET @sql6 = 'SELECT * FROM (' + @sql6 +
                ') AS profile ORDER BY fill_pct DESC, distinct_values DESC';
    EXEC sp_executesql @sql6;
END
ELSE
    SELECT 'No text columns found' AS result;
GO


/* BLOCK 7 -- Caller-selected flag interaction profile -----------------------
   Profile related low-cardinality fields jointly. The placeholder flags do
   not represent any real application or production interpretation.
*/
DECLARE @schema7 SYSNAME = 'YOUR_SCHEMA';
DECLARE @table7 SYSNAME = 'YOUR_TABLE';
DECLARE @flag7a SYSNAME = 'STATUS_FLAG_A';
DECLARE @flag7b SYSNAME = 'STATUS_FLAG_B';
DECLARE @flag7c SYSNAME = 'STATUS_FLAG_C';

DECLARE @sql7 NVARCHAR(MAX) =
    'SELECT ' + QUOTENAME(@flag7a) + ', ' + QUOTENAME(@flag7b) + ', ' +
    QUOTENAME(@flag7c) + ', COUNT(*) AS row_count, ' +
    'CAST(100.0 * COUNT(*) / NULLIF(SUM(COUNT(*)) OVER (), 0) AS DECIMAL(5,2)) ' +
    'AS pct_of_total FROM ' + QUOTENAME(@schema7) + '.' + QUOTENAME(@table7) +
    ' GROUP BY ' + QUOTENAME(@flag7a) + ', ' + QUOTENAME(@flag7b) + ', ' +
    QUOTENAME(@flag7c) + ' ORDER BY row_count DESC';

EXEC sp_executesql @sql7;
GO


/* BLOCK 8 -- Sentinel-date detection ----------------------------------------
   The caller supplies the sentinel. 1753-01-01 is a fabricated demonstration
   default based on SQL Server's legacy datetime boundary, not observed data.
*/
DECLARE @schema8 SYSNAME = 'YOUR_SCHEMA';
DECLARE @table8 SYSNAME = 'YOUR_TABLE';
DECLARE @sentinel8 DATE = '1753-01-01';
DECLARE @sql8 NVARCHAR(MAX) = '';

SELECT @sql8 = @sql8 +
    'SELECT ''' + REPLACE(COLUMN_NAME, '''', '''''') + ''' AS column_name, ' +
    'COUNT(*) AS total_rows, ' +
    'SUM(CASE WHEN ' + QUOTENAME(COLUMN_NAME) + ' <= @sentinel THEN 1 ELSE 0 END) ' +
    'AS sentinel_rows, ' +
    'SUM(CASE WHEN ' + QUOTENAME(COLUMN_NAME) + ' IS NULL THEN 1 ELSE 0 END) AS null_rows, ' +
    'CAST(100.0 * SUM(CASE WHEN ' + QUOTENAME(COLUMN_NAME) +
    ' <= @sentinel THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) AS DECIMAL(5,1)) ' +
    'AS sentinel_pct FROM ' + QUOTENAME(@schema8) + '.' + QUOTENAME(@table8) +
    ' UNION ALL '
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = @schema8
  AND TABLE_NAME = @table8
  AND DATA_TYPE IN ('date', 'datetime', 'datetime2', 'smalldatetime');

IF LEN(@sql8) > 10
BEGIN
    SET @sql8 = LEFT(@sql8, LEN(@sql8) - 10);
    SET @sql8 = 'SELECT * FROM (' + @sql8 +
                ') AS dates ORDER BY sentinel_pct DESC';
    EXEC sp_executesql @sql8, N'@sentinel DATE', @sentinel = @sentinel8;
END
ELSE
    SELECT 'No date columns found' AS result;
GO


/* BLOCK 9 -- Candidate join-key evidence ------------------------------------
   Sample distinct values from a caller-selected source key and measure overlap
   against text columns in a caller-selected target table. Overlap is evidence,
   not proof; independently verify grain and join cardinality.
*/
DECLARE @schema9 SYSNAME = 'YOUR_SCHEMA';
DECLARE @source_table9 SYSNAME = 'YOUR_SOURCE_TABLE';
DECLARE @source_key9 SYSNAME = 'YOUR_SOURCE_KEY';
DECLARE @target_table9 SYSNAME = 'YOUR_TARGET_TABLE';
DECLARE @sample_size9 INT = 200;
DECLARE @sql9 NVARCHAR(MAX) = '';

SELECT @sql9 = @sql9 +
    'SELECT ''' + REPLACE(COLUMN_NAME, '''', '''''') + ''' AS candidate_column, ' +
    'COUNT(DISTINCT target.' + QUOTENAME(COLUMN_NAME) + ') AS matched_values, ' +
    'CAST(100.0 * COUNT(DISTINCT target.' + QUOTENAME(COLUMN_NAME) +
    ') / NULLIF(@sample_size, 0) AS DECIMAL(5,1)) AS overlap_pct ' +
    'FROM ' + QUOTENAME(@schema9) + '.' + QUOTENAME(@target_table9) + ' AS target ' +
    'WHERE target.' + QUOTENAME(COLUMN_NAME) + ' IN (SELECT TOP (@sample_size) ' +
    QUOTENAME(@source_key9) + ' FROM ' + QUOTENAME(@schema9) + '.' +
    QUOTENAME(@source_table9) + ' WHERE ' + QUOTENAME(@source_key9) +
    ' IS NOT NULL GROUP BY ' + QUOTENAME(@source_key9) + ') ' +
    'HAVING COUNT(*) > 0 UNION ALL '
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = @schema9
  AND TABLE_NAME = @target_table9
  AND DATA_TYPE IN ('nvarchar', 'varchar', 'char', 'nchar');

IF LEN(@sql9) > 10
BEGIN
    SET @sql9 = LEFT(@sql9, LEN(@sql9) - 10);
    SET @sql9 = 'SELECT * FROM (' + @sql9 +
                ') AS joins ORDER BY overlap_pct DESC';
    EXEC sp_executesql @sql9, N'@sample_size INT', @sample_size = @sample_size9;
END
ELSE
    SELECT 'No candidate text columns found' AS result;
GO
