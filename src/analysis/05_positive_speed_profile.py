from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, min as spark_min, max as spark_max

spark = SparkSession.builder \
    .appName("Positive_Speed_Profile") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

path = "hdfs://192.168.134.130:9000/DA_BigData/processed/metr_la_long"

df = spark.read.parquet(path)

total = df.count()

zero_count = df.filter(col("speed") == 0).count()

positive_df = df.filter(col("speed") > 0)

positive_count = positive_df.count()

print("=" * 60)
print("POSITIVE SPEED PROFILE")
print("=" * 60)

print(f"Tong record       : {total}")
print(f"Record speed = 0  : {zero_count}")
print(f"Record speed > 0  : {positive_count}")

print(f"Ty le speed = 0   : {(zero_count / total) * 100:.2f}%")

print("\nThong ke speed > 0:")

positive_df.select(
    count("*").alias("records"),
    spark_min("speed").alias("min_speed"),
    spark_max("speed").alias("max_speed"),
    avg("speed").alias("avg_speed")
).show(truncate=False)

quantiles = positive_df.approxQuantile(
    "speed",
    [0.05, 0.10, 0.15, 0.20, 0.25, 0.50, 0.75],
    0.001
)

labels = [
    "P05", "P10", "P15",
    "P20", "P25", "P50", "P75"
]

print("\nPercentile speed > 0:")

for label, value in zip(labels, quantiles):
    print(f"{label}: {value:.2f}")

print("=" * 60)

spark.stop()