from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    when,
    count,
    avg
)

spark = SparkSession.builder \
    .appName("Save_Final_Predictions") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

input_path = (
    "hdfs://192.168.134.130:9000/"
    "DA_BigData/output/random_forest_predictions"
)

output_parquet = (
    "hdfs://192.168.134.130:9000/"
    "DA_BigData/output/final_predictions"
)

output_csv = (
    "hdfs://192.168.134.130:9000/"
    "DA_BigData/output/final_predictions_csv"
)

print("=" * 70)
print("FINAL PREDICTION OUTPUT")
print("=" * 70)

df = spark.read.parquet(input_path)

print(f"Tong prediction: {df.count()}")

# Chuyển numeric prediction -> tên mức ùn tắc
df = df.withColumn(
    "predicted_congestion_15m",
    when(col("prediction") == 0.0, "HIGH")
    .when(col("prediction") == 1.0, "MEDIUM")
    .otherwise("LOW")
)

# Đánh dấu dự đoán đúng/sai
df = df.withColumn(
    "is_correct",
    when(
        col("label") == col("prediction"),
        1
    ).otherwise(0)
)

final_df = df.select(
    "timestamp",
    "sensor_id",
    "speed",
    "target_congestion_15m",
    "predicted_congestion_15m",
    "is_correct"
)

print("\nSchema output:")
final_df.printSchema()

print("\n10 prediction mau:")
final_df.show(10, truncate=False)

print("\nPhan bo prediction:")

final_df.groupBy(
    "predicted_congestion_15m"
).agg(
    count("*").alias("records")
).orderBy(
    "predicted_congestion_15m"
).show()

print("\nDo chinh xac output:")

final_df.select(
    avg("is_correct").alias("accuracy")
).show()

# Lưu Parquet đầy đủ
final_df.write \
    .mode("overwrite") \
    .parquet(output_parquet)

print("\nDa luu Parquet:")
print(output_parquet)

# CSV cho người làm giao diện / báo cáo
final_df.coalesce(1) \
    .write \
    .mode("overwrite") \
    .option("header", True) \
    .csv(output_csv)

print("\nDa luu CSV:")
print(output_csv)

print("=" * 70)
print("FINAL OUTPUT HOAN TAT")
print("=" * 70)

spark.stop()