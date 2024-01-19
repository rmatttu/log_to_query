# log_to_query

Query log(placeholder query + params) to query.

```log
2024-01-01 02:03:04.567 DEBUG 1234 --- [nio-8080-exec-1] j.s.r.mapper.MyMapper.update : ==>  Preparing: UPDATE my_table SET name = ?, value = ? WHERE id = ?
2024-01-19 16:59:18.846 DEBUG 1234 --- [nio-8080-exec-1] j.s.r.mapper.MyMapper.update : ==> Parameters: test(String), 1234(Integer), 5678(Long)
```

↓

```sql
UPDATE my_table SET name = "test", value = 1234 WHERE id = 5678;
```

## Usage

```bash
python log_to_query.py "<placeholder_query>" "<params_text>"
```

Sample

```bash
python log_to_query.py \
  "2024-01-01 02:03:04.567 DEBUG 1234 --- [nio-8080-exec-1] j.s.r.mapper.MyMapper.update : ==>  Preparing: UPDATE my_table SET name = ?, value = ? WHERE id = ?" \
  "2024-01-19 16:59:18.846 DEBUG 1234 --- [nio-8080-exec-1] j.s.r.mapper.MyMapper.update : ==> Parameters: test(String), 1234(Integer), 5678(Long)"
```

## Requirements

## Installation

## License

## Author

## References
