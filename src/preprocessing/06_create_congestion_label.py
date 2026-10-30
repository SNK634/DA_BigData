from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    when,
    lead,
    count,
    lit
)
from pyspark.sql.window import Window

spark = SparkSession.builder \
    .appName("Create_Congestion_Label") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

input_path = (
    "hdfs://192.168.134.130:9000/"
    "DA_BigData/processed/metr_la_long"
)

output_path = (
    "hdfs://192.168.134.130:9000/"
    "DA_BigData/processed/metr_la_labeled"
)

print("=" * 65)
print("CREATE CONGESTION LABEL")
print("=" * 65)

# -------------------------------------------------
# 1. Đọc dữ liệu long format
# -------------------------------------------------

df = spark.read.parquet(input_path)

total_rows = df.count()

print(f"Tong record ban dau: {total_rows}")

# -------------------------------------------------
# 2. Loại speed = 0
#    Xem như dữ liệu sensor bất thường/không hợp lệ
# -------------------------------------------------

df = df.filter(col("speed") > 0)

valid_rows = df.count()

print(f"Record speed > 0: {valid_rows}")
print(f"Record bi loai   : {total_rows - valid_rows}")

# -------------------------------------------------
# 3. Tìm ngưỡng theo phân phối dữ liệu
#
#    Dùng tercile để 3 lớp tương đối cân bằng:
#    <= P33      : HIGH congestion
#    P33 - P66   : MEDIUM congestion
#    > P66       : LOW congestion
# -------------------------------------------------

thresholds = df.approxQuantile(
    "speed",
    [0.33, 0.66],
    0.001
)

p33 = thresholds[0]
p66 = thresholds[1]

print("\nNguong congestion:")
print(f"P33 = {p33:.2f}")
print(f"P66 = {p66:.2f}")

# -------------------------------------------------
# 4. Tạo congestion tại thời điểm hiện tại
# -------------------------------------------------

df = df.withColumn(
    "congestion_current",
    when(
        col("speed") <= lit(p33),
        "HIGH"
    ).when(
        col("speed") <= lit(p66),
        "MEDIUM"
    ).otherwise(
        "LOW"
    )
)

# -------------------------------------------------
# 5. Tạo target tương lai 15 phút
#
# METR-LA có khoảng cách 5 phút:
#
# t
# t+5
# t+10
# t+15  -> lead(..., 3)
# -------------------------------------------------

window_sensor = Window \
    .partitionBy("sensor_id") \
    .orderBy("timestamp")

df = df.withColumn(
    "target_congestion_15m",
    lead(
        "congestion_current",
        3
    ).over(window_sensor)
)

# Bỏ 3 record cuối của mỗi sensor
# vì không có dữ liệu tương lai 15 phút
df = df.dropna(
    subset=["target_congestion_15m"]
)

# -------------------------------------------------
# 6. Kiểm tra phân phối nhãn hiện tại
# -------------------------------------------------

print("\nPhan bo congestion hien tai:")

df.groupBy("congestion_current") \
    .agg(count("*").alias("records")) \
    .orderBy("congestion_current") \
    .show()

# -------------------------------------------------
# 7. Kiểm tra phân phối target
# -------------------------------------------------

print("\nPhan bo target +15 phut:")

df.groupBy("target_congestion_15m") \
    .agg(count("*").alias("records")) \
    .orderBy("target_congestion_15m") \
    .show()

# -------------------------------------------------
# 8. Xem dữ liệu mẫu
# -------------------------------------------------

print("\n10 record mau:")

df.select(
    "timestamp",
    "sensor_id",
    "speed",
    "hour",
    "day_of_week",
    "congestion_current",
    "target_congestion_15m"
).show(
    10,
    truncate=False
)

print(f"\nTong record sau labeling: {df.count()}")

# -------------------------------------------------
# 9. Lưu Parquet lên HDFS
# -------------------------------------------------

print("\nDang ghi labeled dataset vao HDFS...")

df.write \
    .mode("overwrite") \
    .partitionBy("date") \
    .parquet(output_path)

print("\nDa luu:")
print(output_path)

print("=" * 65)
print("CREATE CONGESTION LABEL HOAN TAT")
print("=" * 65)

spark.stop()