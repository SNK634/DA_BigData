from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Evaluate_Models") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

data = [
    (
        "Persistence Baseline",
        0.7361,
        0.7361,
        0.7361,
        0.7361
    ),
    (
        "Random Forest",
        0.7704,
        0.7745,
        0.7704,
        0.7718
    )
]

columns = [
    "model",
    "accuracy",
    "weighted_precision",
    "weighted_recall",
    "weighted_f1"
]

df = spark.createDataFrame(
    data,
    columns
)

print("\nBang so sanh:")
df.show(truncate=False)

baseline_accuracy = 0.7361
rf_accuracy = 0.7704

baseline_f1 = 0.7361
rf_f1 = 0.7718

accuracy_improvement = (
    rf_accuracy - baseline_accuracy
) * 100

f1_improvement = (
    rf_f1 - baseline_f1
) * 100

print(
    f"Accuracy improvement: "
    f"{accuracy_improvement:.2f} percentage points"
)

print(
    f"F1 improvement      : "
    f"{f1_improvement:.2f} percentage points"
)

print("\nBest model: RANDOM FOREST")

output_path = (
    "hdfs://192.168.134.130:9000/"
    "DA_BigData/output/model_comparison"
)

df.coalesce(1) \
    .write \
    .mode("overwrite") \
    .option("header", True) \
    .csv(output_path)

print("\nDa luu:")
print(output_path)

print("=" * 70)
print("MODEL COMPARISON HOAN TAT")
print("=" * 70)

spark.stop()