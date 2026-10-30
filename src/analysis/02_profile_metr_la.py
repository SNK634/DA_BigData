from pyspark.sql import SparkSession
from pyspark.sql.functions import col, isnan, when, count

spark = SparkSession.builder \
    .appName("Profile_METR_LA") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

path = "hdfs://192.168.134.130:9000/DA_BigData/raw/METR-LA.csv"

df = spark.read.csv(
    path,
    header=True,
    inferSchema=True
)

rows = df.count()
cols = len(df.columns)

print("\n" + "=" * 60)
print("METR-LA DATA PROFILE")
print("=" * 60)

print(f"So dong: {rows}")
print(f"So cot : {cols}")

print("\n10 cot dau:")
print(df.columns[:10])

print("\n10 cot cuoi:")
print(df.columns[-10:])

print("\nSchema 5 cot dau:")
for field in df.schema.fields[:5]:
    print(f"{field.name}: {field.dataType}")

print("\n3 dong dau - chi 6 cot dau:")
df.select(df.columns[:6]).show(3, truncate=False)

missing_df = df.select([
    count(
        when(
            col(c).isNull() | isnan(col(c)),
            c
        )
    ).alias(c)
    for c in df.columns
])

missing_values = missing_df.collect()[0].asDict()

columns_with_missing = {
    k: v for k, v in missing_values.items()
    if v > 0
}

print("\nSo cot co missing:")
print(len(columns_with_missing))

print("\n10 cot co missing dau tien:")
for key, value in list(columns_with_missing.items())[:10]:
    print(f"{key}: {value}")

print("=" * 60)

spark.stop()