from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    avg,
    min as spark_min,
    max as spark_max,
    count
)

spark = SparkSession.builder \
    .appName("EDA_METR_LA_SPEED") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

path = "hdfs://192.168.134.130:9000/DA_BigData/processed/metr_la_long"

df = spark.read.parquet(path)

print("=" * 60)
print("EDA METR-LA - SPEED")
print("=" * 60)

print(f"So dong: {df.count()}")
print(f"So cot : {len(df.columns)}")

# Thống kê tốc độ tổng quát
stats = df.select(
    count("*").alias("records"),
    spark_min("speed").alias("min_speed"),
    spark_max("speed").alias("max_speed"),
    avg("speed").alias("avg_speed")
)

print("\nThong ke tong quat:")
stats.show(truncate=False)

# Percentile
quantiles = df.approxQuantile(
    "speed",
    [0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99],
    0.01
)

labels = [
    "P01", "P05", "P10",
    "P25", "P50", "P75",
    "P90", "P95", "P99"
]

print("\nPercentile speed:")
for label, value in zip(labels, quantiles):
    print(f"{label}: {value:.2f}")

# Tốc độ trung bình theo giờ
print("\nToc do trung binh theo gio:")

hourly = df.groupBy("hour") \
    .agg(
        avg("speed").alias("avg_speed"),
        count("*").alias("records")
    ) \
    .orderBy("hour")

hourly.show(24, truncate=False)

# Các sensor có tốc độ trung bình thấp nhất
print("\n10 sensor co toc do trung binh thap nhat:")

sensor_avg = df.groupBy("sensor_id") \
    .agg(
        avg("speed").alias("avg_speed")
    ) \
    .orderBy(col("avg_speed").asc())

sensor_avg.show(10, truncate=False)

print("=" * 60)
print("EDA HOAN TAT")
print("=" * 60)

spark.stop()