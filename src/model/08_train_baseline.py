from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    when,
    count,
    lit,
    min as spark_min,
    max as spark_max
)
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

spark = SparkSession.builder \
    .appName("Baseline_Congestion_Prediction") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

input_path = (
    "hdfs://192.168.134.130:9000/"
    "DA_BigData/processed/metr_la_features"
)

output_path = (
    "hdfs://192.168.134.130:9000/"
    "DA_BigData/output/baseline_metrics"
)

# Ngưỡng đã xác định trước đó
P33 = 59.75
P66 = 65.44

# Giữ cố định cutoff này cho các model sau
TEST_START = "2012-06-01 00:00:00"

print("=" * 70)
print("BASELINE - CONGESTION PREDICTION +15 MINUTES")
print("=" * 70)

df = spark.read.parquet(input_path)

print(f"Tong record: {df.count()}")

print("\nKhoang thoi gian dataset:")
df.select(
    spark_min("timestamp").alias("from"),
    spark_max("timestamp").alias("to")
).show(truncate=False)

# ---------------------------------------------------------
# 1. Chia train/test theo thời gian
# Không randomSplit để tránh temporal leakage
# ---------------------------------------------------------

train_df = df.filter(
    col("timestamp") < lit(TEST_START).cast("timestamp")
)

test_df = df.filter(
    col("timestamp") >= lit(TEST_START).cast("timestamp")
)

train_count = train_df.count()
test_count = test_df.count()

print(f"\nTrain records: {train_count}")
print(f"Test records : {test_count}")
print(f"Test bat dau : {TEST_START}")

# ---------------------------------------------------------
# 2. Baseline:
# dự đoán congestion sau 15 phút bằng trạng thái hiện tại
#
# HIGH   -> 0
# MEDIUM -> 1
# LOW    -> 2
# ---------------------------------------------------------

predictions = test_df.withColumn(
    "prediction",
    when(
        col("speed") <= P33,
        0.0
    ).when(
        col("speed") <= P66,
        1.0
    ).otherwise(
        2.0
    )
)

# ---------------------------------------------------------
# 3. Metrics
# ---------------------------------------------------------

accuracy_evaluator = MulticlassClassificationEvaluator(
    labelCol="label",
    predictionCol="prediction",
    metricName="accuracy"
)

f1_evaluator = MulticlassClassificationEvaluator(
    labelCol="label",
    predictionCol="prediction",
    metricName="f1"
)

precision_evaluator = MulticlassClassificationEvaluator(
    labelCol="label",
    predictionCol="prediction",
    metricName="weightedPrecision"
)

recall_evaluator = MulticlassClassificationEvaluator(
    labelCol="label",
    predictionCol="prediction",
    metricName="weightedRecall"
)

accuracy = accuracy_evaluator.evaluate(predictions)
f1 = f1_evaluator.evaluate(predictions)
precision = precision_evaluator.evaluate(predictions)
recall = recall_evaluator.evaluate(predictions)

print("\n" + "=" * 70)
print("BASELINE METRICS")
print("=" * 70)

print(f"Accuracy           : {accuracy:.4f}")
print(f"Weighted Precision : {precision:.4f}")
print(f"Weighted Recall    : {recall:.4f}")
print(f"Weighted F1        : {f1:.4f}")

# ---------------------------------------------------------
# 4. Confusion matrix
# ---------------------------------------------------------

print("\nConfusion matrix:")
print("label: 0=HIGH, 1=MEDIUM, 2=LOW")

predictions.groupBy(
    "label",
    "prediction"
).agg(
    count("*").alias("records")
).orderBy(
    "label",
    "prediction"
).show(20, truncate=False)

# ---------------------------------------------------------
# 5. Lưu metrics để model sau so sánh
# ---------------------------------------------------------

metrics_df = spark.createDataFrame([
    (
        "PersistenceBaseline",
        accuracy,
        precision,
        recall,
        f1,
        train_count,
        test_count
    )
], [
    "model",
    "accuracy",
    "weighted_precision",
    "weighted_recall",
    "weighted_f1",
    "train_records",
    "test_records"
])

metrics_df.coalesce(1) \
    .write \
    .mode("overwrite") \
    .option("header", True) \
    .csv(output_path)

print("\nDa luu metrics:")
print(output_path)

print("=" * 70)
print("BASELINE HOAN TAT")
print("=" * 70)

spark.stop()