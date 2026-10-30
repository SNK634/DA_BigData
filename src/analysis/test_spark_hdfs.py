from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("DA_BigData_Test") \
    .getOrCreate()

path = "hdfs://192.168.134.130:9000/user/osboxes/test/hdfs_test.txt"

df = spark.read.text(path)

print("===== TEST PROJECT DA_BIGDATA =====")
df.show(truncate=False)

print("So dong:", df.count())

spark.stop()