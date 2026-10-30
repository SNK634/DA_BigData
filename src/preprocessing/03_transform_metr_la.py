from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    expr,
    to_timestamp,
    hour,
    date_format,
    to_date
)

spark = SparkSession.builder \
    .appName("Transform_METR_LA") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

input_path = "hdfs://192.168.134.130:9000/DA_BigData/raw/METR-LA.csv"
output_path = "hdfs://192.168.134.130:9000/DA_BigData/processed/metr_la_long"

print("=" * 60)
print("BAT DAU TRANSFORM METR-LA")
print("=" * 60)

# 1. Đọc dữ liệu gốc
df = spark.read.csv(
    input_path,
    header=True,
    inferSchema=True
)

print(f"So dong goc: {df.count()}")
print(f"So cot goc : {len(df.columns)}")

# 2. Đổi tên cột thời gian
df = df.withColumnRenamed("_c0", "timestamp_raw")

# 3. Parse timestamp
df = df.withColumn(
    "timestamp",
    to_timestamp(col("timestamp_raw"), "yyyy-MM-dd HH:mm:ss")
)

sensor_columns = [
    c for c in df.columns
    if c not in ["timestamp_raw", "timestamp"]
]

print(f"So sensor: {len(sensor_columns)}")

# 4. Wide -> Long bằng stack
stack_expr = ", ".join([
    f"'{sensor}', `{sensor}`"
    for sensor in sensor_columns
])

long_df = df.select(
    "timestamp",
    expr(
        f"stack({len(sensor_columns)}, {stack_expr}) "
        f"as (sensor_id, speed)"
    )
)

# 5. Feature thời gian cơ bản
long_df = long_df \
    .withColumn("date", to_date(col("timestamp"))) \
    .withColumn("hour", hour(col("timestamp"))) \
    .withColumn("day_of_week", date_format(col("timestamp"), "E"))

# 6. Bỏ record lỗi/null nếu có
long_df = long_df.dropna(
    subset=["timestamp", "sensor_id", "speed"]
)

print("\nSchema sau transform:")
long_df.printSchema()

print("\n5 dong dau:")
long_df.show(5, truncate=False)

print("\nDang dem so record sau transform...")
row_count = long_df.count()

print(f"So dong sau transform: {row_count}")

# 7. Lưu Parquet trên HDFS
print("\nDang ghi Parquet vao HDFS...")

long_df.write \
    .mode("overwrite") \
    .partitionBy("date") \
    .parquet(output_path)

print("\nDa luu thanh cong:")
print(output_path)

print("=" * 60)
print("TRANSFORM HOAN TAT")
print("=" * 60)

spark.stop()