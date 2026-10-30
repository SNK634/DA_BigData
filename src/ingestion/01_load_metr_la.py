from pyspark.sql import SparkSession
from pyspark.sql.functions import col, isnan, when, count

spark = SparkSession.builder \
    .appName("Load_METR_LA") \
    .getOrCreate()

path = "hdfs://192.168.134.130:9000/DA_BigData/raw/METR-LA.csv"

df = spark.read.csv(
    path,
    header=True,
    inferSchema=True
)

print("===== METR-LA DATASET =====")

print("\nSo dong:")
print(df.count())

print("\nSo cot:")
print(len(df.columns))

print("\nSchema:")
df.printSchema()

print("\n5 dong dau:")
df.show(5, truncate=False)

print("\nDanh sach cot:")
print(df.columns)

print("\nMissing values:")
df.select([
    count(
        when(
            col(c).isNull() | isnan(col(c)),
            c
        )
    ).alias(c)
    for c in df.columns
]).show(truncate=False)

spark.stop()