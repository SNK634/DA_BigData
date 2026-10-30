from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

spark = SparkSession.builder \
    .appName("RandomForest_Congestion_Prediction") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

input_path = (
    "hdfs://192.168.134.130:9000/"
    "DA_BigData/processed/metr_la_features"
)

model_path = (
    "hdfs://192.168.134.130:9000/"
    "DA_BigData/output/models/random_forest"
)

prediction_path = (
    "hdfs://192.168.134.130:9000/"
    "DA_BigData/output/random_forest_predictions"
)

TEST_START = "2012-06-01 00:00:00"

print("=" * 70)
print("RANDOM FOREST - CONGESTION PREDICTION +15 MINUTES")
print("=" * 70)

df = spark.read.parquet(input_path)

# ---------------------------------------------------------
# 1. Chia train/test giống baseline
# ---------------------------------------------------------

train_df = df.filter(
    col("timestamp") < lit(TEST_START).cast("timestamp")
)

test_df = df.filter(
    col("timestamp") >= lit(TEST_START).cast("timestamp")
)

train_count = train_df.count()
test_count = test_df.count()

print(f"Train records: {train_count}")
print(f"Test records : {test_count}")

# ---------------------------------------------------------
# 2. Features
#
# KHÔNG dùng future_speed_15m
# ---------------------------------------------------------

feature_cols = [
    "speed",
    "lag_speed_5m",
    "lag_speed_10m",
    "lag_speed_15m",
    "hour",
    "minute",
    "day_of_week_num"
]

print("\nFeatures:")
for feature in feature_cols:
    print(f"- {feature}")

assembler = VectorAssembler(
    inputCols=feature_cols,
    outputCol="features"
)

# ---------------------------------------------------------
# 3. Random Forest
#
# Cấu hình vừa phải cho VM 4GB RAM
# ---------------------------------------------------------

rf = RandomForestClassifier(
    labelCol="label",
    featuresCol="features",
    predictionCol="prediction",
    numTrees=30,
    maxDepth=8,
    maxBins=32,
    seed=42
)

pipeline = Pipeline(
    stages=[
        assembler,
        rf
    ]
)

# ---------------------------------------------------------
# 4. Train
# ---------------------------------------------------------

print("\nDang train Random Forest...")

model = pipeline.fit(train_df)

print("Train hoan tat.")

# ---------------------------------------------------------
# 5. Predict
# ---------------------------------------------------------

print("\nDang predict test set...")

predictions = model.transform(test_df)

# ---------------------------------------------------------
# 6. Evaluation
# ---------------------------------------------------------

accuracy_eval = MulticlassClassificationEvaluator(
    labelCol="label",
    predictionCol="prediction",
    metricName="accuracy"
)

precision_eval = MulticlassClassificationEvaluator(
    labelCol="label",
    predictionCol="prediction",
    metricName="weightedPrecision"
)

recall_eval = MulticlassClassificationEvaluator(
    labelCol="label",
    predictionCol="prediction",
    metricName="weightedRecall"
)

f1_eval = MulticlassClassificationEvaluator(
    labelCol="label",
    predictionCol="prediction",
    metricName="f1"
)

accuracy = accuracy_eval.evaluate(predictions)
precision = precision_eval.evaluate(predictions)
recall = recall_eval.evaluate(predictions)
f1 = f1_eval.evaluate(predictions)

print("\n" + "=" * 70)
print("RANDOM FOREST METRICS")
print("=" * 70)

print(f"Accuracy           : {accuracy:.4f}")
print(f"Weighted Precision : {precision:.4f}")
print(f"Weighted Recall    : {recall:.4f}")
print(f"Weighted F1        : {f1:.4f}")

# ---------------------------------------------------------
# 7. Confusion matrix
# ---------------------------------------------------------

print("\nConfusion matrix:")
print("label: 0=HIGH, 1=MEDIUM, 2=LOW")

predictions.groupBy(
    "label",
    "prediction"
).count().orderBy(
    "label",
    "prediction"
).show(20, truncate=False)

# ---------------------------------------------------------
# 8. Feature importance
# ---------------------------------------------------------

rf_model = model.stages[-1]

importances = rf_model.featureImportances

print("\nFeature importance:")

feature_importance = list(
    zip(feature_cols, importances)
)

feature_importance.sort(
    key=lambda x: x[1],
    reverse=True
)

for feature, importance in feature_importance:
    print(f"{feature:<20}: {importance:.6f}")

# ---------------------------------------------------------
# 9. Lưu model
# ---------------------------------------------------------

print("\nDang luu model...")

model.write() \
    .overwrite() \
    .save(model_path)

print(f"Model path: {model_path}")

# ---------------------------------------------------------
# 10. Lưu prediction cần thiết
# ---------------------------------------------------------

predictions.select(
    "timestamp",
    "sensor_id",
    "speed",
    "target_congestion_15m",
    "label",
    "prediction",
    "probability"
).write \
    .mode("overwrite") \
    .parquet(prediction_path)

print(f"Prediction path: {prediction_path}")

print("=" * 70)
print("RANDOM FOREST HOAN TAT")
print("=" * 70)

spark.stop()