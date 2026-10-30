from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    lag,
    lead,
    unix_timestamp,
    hour,
    dayofweek,
    minute,
    when,
    count
)
from pyspark.sql.window import Window

spark = SparkSession.builder \
    .appName("Prepare_METR_LA_Features") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

input_path = (
    "hdfs://192.168.134.130:9000/"
    "DA_BigData/processed/metr_la_long"
)

output_path = (
    "hdfs://192.168.134.130:9000/"
    "DA_BigData/processed/metr_la_features"
)

# Ngưỡng đã xác định ở bước 06
P33 = 59.75
P66 = 65.44

print("=" * 70)
print("PREPARE FEATURES FOR CONGESTION PREDICTION")
print("=" * 70)

df = spark.read.parquet(input_path)

print(f"Tong record dau vao: {df.count()}")

# ---------------------------------------------------------
# 1. Window theo từng sensor, giữ nguyên timeline gốc
# ---------------------------------------------------------

w = Window \
    .partitionBy("sensor_id") \
    .orderBy("timestamp")

# ---------------------------------------------------------
# 2. Tạo lag tốc độ
# METR-LA: mỗi record cách nhau 5 phút
# ---------------------------------------------------------

df = df \
    .withColumn("lag_speed_5m", lag("speed", 1).over(w)) \
    .withColumn("lag_speed_10m", lag("speed", 2).over(w)) \
    .withColumn("lag_speed_15m", lag("speed", 3).over(w))

# timestamp tương ứng của lag
df = df \
    .withColumn("lag_ts_5m", lag("timestamp", 1).over(w)) \
    .withColumn("lag_ts_10m", lag("timestamp", 2).over(w)) \
    .withColumn("lag_ts_15m", lag("timestamp", 3).over(w))

# ---------------------------------------------------------
# 3. Tạo future speed +15 phút
# ---------------------------------------------------------

df = df \
    .withColumn("future_speed_15m", lead("speed", 3).over(w)) \
    .withColumn("future_ts_15m", lead("timestamp", 3).over(w))

# ---------------------------------------------------------
# 4. Kiểm tra khoảng cách thời gian chính xác
# ---------------------------------------------------------

df = df \
    .withColumn(
        "gap_5m",
        unix_timestamp("timestamp")
        - unix_timestamp("lag_ts_5m")
    ) \
    .withColumn(
        "gap_10m",
        unix_timestamp("timestamp")
        - unix_timestamp("lag_ts_10m")
    ) \
    .withColumn(
        "gap_15m",
        unix_timestamp("timestamp")
        - unix_timestamp("lag_ts_15m")
    ) \
    .withColumn(
        "future_gap_15m",
        unix_timestamp("future_ts_15m")
        - unix_timestamp("timestamp")
    )

# ---------------------------------------------------------
# 5. Chỉ giữ record có timeline liên tục:
#
# 5 phút  = 300 giây
# 10 phút = 600 giây
# 15 phút = 900 giây
# ---------------------------------------------------------

df = df.filter(
    (col("gap_5m") == 300) &
    (col("gap_10m") == 600) &
    (col("gap_15m") == 900) &
    (col("future_gap_15m") == 900)
)

# ---------------------------------------------------------
# 6. Loại speed = 0 ở current / lag / future
# ---------------------------------------------------------

df = df.filter(
    (col("speed") > 0) &
    (col("lag_speed_5m") > 0) &
    (col("lag_speed_10m") > 0) &
    (col("lag_speed_15m") > 0) &
    (col("future_speed_15m") > 0)
)

# ---------------------------------------------------------
# 7. Feature thời gian
# ---------------------------------------------------------

df = df \
    .withColumn("hour", hour("timestamp")) \
    .withColumn("minute", minute("timestamp")) \
    .withColumn("day_of_week_num", dayofweek("timestamp"))

# ---------------------------------------------------------
# 8. Tạo target congestion tại t + 15 phút
# ---------------------------------------------------------

df = df.withColumn(
    "target_congestion_15m",
    when(
        col("future_speed_15m") <= P33,
        "HIGH"
    ).when(
        col("future_speed_15m") <= P66,
        "MEDIUM"
    ).otherwise(
        "LOW"
    )
)

# Numeric label:
# HIGH   = 0
# MEDIUM = 1
# LOW    = 2
df = df.withColumn(
    "label",
    when(
        col("target_congestion_15m") == "HIGH", 0.0
    ).when(
        col("target_congestion_15m") == "MEDIUM", 1.0
    ).otherwise(2.0)
)

# ---------------------------------------------------------
# 9. Chỉ giữ các cột thực sự cần cho ML
# ---------------------------------------------------------

features_df = df.select(
    "timestamp",
    "sensor_id",

    "speed",
    "lag_speed_5m",
    "lag_speed_10m",
    "lag_speed_15m",

    "hour",
    "minute",
    "day_of_week_num",

    "future_speed_15m",
    "target_congestion_15m",
    "label"
)

# ---------------------------------------------------------
# 10. Kiểm tra output
# ---------------------------------------------------------

total_output = features_df.count()

print(f"\nTong record sau feature engineering: {total_output}")

print("\nSchema:")
features_df.printSchema()

print("\n10 record mau:")
features_df.show(10, truncate=False)

print("\nPhan bo target:")
features_df.groupBy(
    "target_congestion_15m"
).agg(
    count("*").alias("records")
).orderBy(
    "target_congestion_15m"
).show()

# ---------------------------------------------------------
# 11. Lưu Parquet lên HDFS
# ---------------------------------------------------------

print("\nDang ghi feature dataset vao HDFS...")

features_df.write \
    .mode("overwrite") \
    .parquet(output_path)

print("\nDa luu:")
print(output_path)

print("=" * 70)
print("PREPARE FEATURES HOAN TAT")
print("=" * 70)

spark.stop()