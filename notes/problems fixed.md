2019-09-28
There were two entries for the same assignment. This made it so line-ish 138
```python
        if (int(row['chapter']) == int(float(row_p['end_chapter']))) and (str(row['problem']) == str(row_p['end_problem'])):
            try:
                row_p = next(df_p_g)[1]
            except:
                print('boom!')
```
didn't work correctly so row_p wouldn't update with the next assignment.