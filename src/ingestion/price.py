"""Strict source-price parser for independent QA of PostgreSQL outcome cleaning."""
import math
import re
PATTERN=re.compile(r'^[$]([0-9]+|[0-9]{1,3}(,[0-9]{3})+)([.][0-9]{2})?$')
def source_price(value):
    if value is None or value=='':return None,None
    if not PATTERN.fullmatch(value):raise ValueError('Unparseable nonempty source price; investigate without imputation')
    price=float(value.replace('$','').replace(',',''))
    return price,math.log(price) if price>0 else None
